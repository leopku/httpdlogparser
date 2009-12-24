#!/usr/bin/env python
import os.path
import logging
import sys
import re
from urllib import unquote
import MySQLdb
import datetime
import chardet
import glob
import cjson
from ofc2 import *
from config import config_sets_9949, RUN_ENV
from extofc import extChart
from apachelogparser import GuestBase, apachelog

class Guest9949(GuestBase):
    """
    log example:
    222.35.169.141 - - [07/Dec/2009:18:00:00 +0800] "POST /go.html?name=17173&u=http://www.17173.com/ HTTP/1.1" 200 50 "http://www.9949.cn/?uid=desktop" "Mozilla/4.0 (compatible; MSIE 6.0; IQ 0.9.8.1322; zh_cn; Windows NT 5.1))"
    """
    def set_target_url(self, url):
        self.target_url = url
    
    def set_name(self, name):
        self.name = name
            
    def parseResource(self, regex):
        pattern = re.compile(regex)
        match = pattern.search(self.resource)
        result = False
        if match:
            result = True
            self.set_target_url(match.group('dest'))
            
            name = match.group('name')
            if name == 'undefined':
                name = None
            else:
                name = unquote(name)
                encoding = chardet.detect(name)['encoding']
                if encoding:
                    try:
                        name = name.decode('string_escape').decode(encoding)
                    except UnicodeDecodeError, err:
                        logging.critical('Exception while coding name: %s' % err)
                        logging.critical(name)
                        name = None
            self.set_name(name)
            self.set_location()
        return result
        
if __name__ == '__main__':
    
    if len(sys.argv) >=2:
        if sys.argv[1] in config_sets_9949.keys():
            RUN_ENV = sys.argv[1]
    
    LOG_FILENAME = os.path.join(os.path.dirname(__file__), '%s.log' %os.path.basename(__file__))
    LOG_FORMAT = '%(asctime)s | %(levelname)s |%(lineno)s | %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, level=config_sets_9949[RUN_ENV]['logging_level'], format=LOG_FORMAT)

    try:
        conn = MySQLdb.connect(host=config_sets_9949[RUN_ENV]['host'],
                               user=config_sets_9949[RUN_ENV]['user'],
                               passwd=config_sets_9949[RUN_ENV]['passwd'],
                               db=config_sets_9949[RUN_ENV]['db'],
                               charset='utf8')
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    except MySQLdb.Error, e:
        logging.critical('MySQL connection error! %s' % e)
        sys.exit(1)
    
    delta_one_day = datetime.timedelta(days=1)
    yesterday = datetime.date.today() - delta_one_day
    tomorrow = datetime.date.today() + delta_one_day

    logfiles = glob.glob('/Data/log/9949/9949.cn-access_log.%s??' % yesterday.strftime('%Y%m%d'))
    regex = r'POST /go\.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP'
    for logfile in logfiles:
        logging.info('[log file]%s' % logfile)
        parser = apachelog(logfile, Guest9949)
        guests = parser.parseFile(regex) 
        
        counts = {}
        date = None
         
        for guest in guests:
            
            counts[guest.target_url] = counts.get(guest.target_url, 0) + 1
            name = guest.name.replace("'", '"')
            sql = """INSERT INTO log (ip, city, isp, date_c, dest, ref, agent, name) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % (guest.ip, guest.city, guest.isp, guest.datetime.strftime('%Y-%m-%d %H:00:00'), guest.target_url, guest.referer, guest.agent, name)
            try:
                cursor.execute(sql)
            except:
                logging.exception(sql)    

    chart = extChart()
    chart.title = title(text='Report of Link Clicking')
    chart.bg_colour = '#FFFFFF' 
    chart.x_legend = x_legend(text='Days/Weeks/Monthes', style='{color: #736AFF;font-size: 12px;}')
    chart.y_legend = y_legend(text='click counts', style='{color: #736AFF;font-size: 12px;}')
    
    chart.y_axis = y_axis(grid_colour='#DDDDDD')
    chart.y_axis.stroke = 1
    chart.x_axis = x_axis(grid_colour='#DDDDDD')
    chart.x_axis.stroke = 1
    chart.x_axis.labels = x_axis_labels(labels=[str(7-i) for i in range(7)])
    
    periods = {'Day':'%Y-%m-%d', 'Week':'%u', 'Month':'%Y-%m'}
    colours = {'Day': '#ffae00', 'Week':'#52aa4b', 'Month': '#ff0000'}
    for period, format in periods.items():
        sql = "SELECT DATE_FORMAT(date_c, '%s') AS period, count(id) AS cnt FROM log WHERE date_c >= DATE_SUB(CURDATE(), INTERVAL 7 %s) GROUP BY period DESC;" % (format, period)
        logging.info('[counting sql]%s' % sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        l = line(text=period, colour=colours[period])
        l.dot_style = dot()
        
        rows_list = list(rows)
        values = [0 for _ in range(7)]
        for row in rows:
            index = rows_list.index(row)
            t = '%s:%s<br>#val#' %  (period, row['period'])
            
            values[-1-index] = dot_value(value=row['cnt'], tip=t)
            if row['cnt'] >= chart.y_axis.get('max', 0):
                chart.y_axis.max = row['cnt'] * 1.2
        l.values = values
        chart.add_element(l)
        
    sql = "SELECT name, dest, COUNT(id) AS cnt FROM log WHERE date_c BETWEEN '%s 00:00:00' AND '%s 00:00:00' GROUP BY dest ORDER BY cnt DESC;" % (yesterday.strftime('%Y-%m-%d'), datetime.date.today().strftime('%Y-%m-%d'))
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        gridline = {}
        gridline['name'] = row['name']
        gridline['dest'] = row['dest']
        gridline['count'] = row['cnt']
        chart.add_grid_line(gridline)
        
    reportfile = os.path.join(os.path.dirname(__file__), '9949', yesterday.strftime('%Y-%m-%d'))
    report  = open(reportfile, 'w+')
    report.write(cjson.encode(chart))
    report.close()
    
    mail_content = """
    The Report of Link Clicking.
    Date: %s
    Link: http://zx.360quan.com/stats.html?ofc=9949/%s
    """ % (yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'))
    mail_file = open('mail.txt', 'w+')
    mail_file.write(mail_content)
    mail_file.close()
    mail_cmd = 'mail -c %s -s "The Report of Link Clicking" %s < mail.txt' % (config_sets_9949[RUN_ENV]['mail_to'], config_sets_9949[RUN_ENV]['mail_cc'])