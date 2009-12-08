#!/usr/bin/env python
import os.path
import logging
import sys
import re
from urllib import unquote
import MySQLdb
import datetime
import glob
import cjson
from ofc2 import *
from config import config_sets_9949
from extofc import extChart
from apachelogparser import GuestBase, ReportBase, apachelog

RUN_ENV = 'test'

class guest9949(GuestBase):
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
                try:
                    name = unquote(name).decode('string_escape').decode('GBK')
                except Exception, err:
                    logging.critical('Exception while coding name: %s' % err)
                    name = None
            self.set_name(name)
            self.set_location()
        return result
        
if __name__ == '__main__':
    
    if len(sys.argv) >=2:
        if sys.argv[1] in config_sets_9949.keys():
            RUN_ENV = sys.argv[1]
    
    LOG_FILENAME = os.path.join(os.path.dirname(__file__), '%s.log' %os.path.basename(__file__))
    LOG_FORMAT = '%(asctime)s | %(lineno)s | %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format=LOG_FORMAT)

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
        parser = apachelog(logfile, guest9949, regex)
        guests = parser.parseFile() 
        
        counts = {}
        date = None
         
        for guest in guests:
            
            counts[guest.target_url] = counts.get(guest.target_url, 0) + 1
            
            sql = "INSERT INTO log (ip, city, isp, date_c, dest, ref, agent, name) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (guest.ip, guest.city, guest.isp, guest.datetime.strftime('%Y-%m-%d %H:00:00'), guest.target_url, guest.referer, guest.agent, guest.name)
            cursor.execute(sql)    

    chart = extChart()
    chart.title = title(text='Report of Link Clicking')
    chart.x_legend = x_legend(text='Days/Weeks/Monthes')
    chart.y_legend = y_legend(text='click counts')
    
    chart.y_axis = y_axis(grid_colour='#DDDDDD')
    chart.x_axis = x_axis(grid_colour='#DDDDDD')
    chart.x_axis.labels = x_axis_labels(labels=[i+1 for i in range(7)])
    
    periods = {'Day':'%Y-%m-%d', 'Week':'%u', 'Month':'%Y-%m'}
    colors = {'Day': '#ffae00', 'Week':'#52aa4b', 'Month': '#ff0000'}
    for period, format in periods.items():
        sql = "SELECT DATE_FORMAT(date_c, '%s') AS period, count(id) AS cnt FROM log WHERE date_c >= DATE_SUB(CURDATE(), INTERVAL 7 %s) GROUP BY period DESC;" % (format, period)
        logging.info('[counting sql]%s' % sql)
        cursor.execute(sql)
        rows = cursor.fectchall()
        
        l = line(text=period, colour=colors[period])
        l.dot_style = dot()
        
        rows_list = list(rows)
        values = [0 for _ in range(7)]
        for row in rows:
            index = rows_list.index(row)
            t = '%s:%s<br>#val#' %  (period, row['period'])
            
            values[-1-index] = dot_style(value=row['cnt'], tip=t)
        l.values = values
        
    sql = "SELECT name, dest, COUNT(id) AS cnt FROM log WHERE date_c BETWEEN '%s 00:00:00' AND '%s 00:00:00' GROUP BY dest ORDER BY cnt DESC;" % (yesterday.strftime('%Y-%m-%d'), datetime.date.today().strftime('%Y-%m-%d'))
    cursor.execute(sql)
    rows = cursor.fectchall()
    for row in rows:
        gridline = {}
        gridline['name'] = row['name']
        gridline['dest'] = row['dest']
        gridline['count'] =  row['cnt']
        chart.add_grid_line(gridline)
        
    reportfile = os.path.join(os.path.dirname(__file__), '9949', day.strftime('%Y-%m-%d'))
    report  = open(reportfile, 'w+')
    report.write(cjson.encode(chart))
    report.close()