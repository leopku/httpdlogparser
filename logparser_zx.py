#!/usr/bin/env python

import os
import os.path
import re
import sys
import logging
import glob
import datetime

import MySQLdb
import cjson

import ofc2
from extofc import extChart
from config import RUN_ENV, config_sets_zx
from apachelogparser import GuestBase, apachelog

class GuestZX(GuestBase):
    def set_loadtime(self, time):
        self.loadtime = time
    
    def sef_referer(self, referer):
        self.referer = referer
        
    def set_domain(self, domain):
        self.domain = domain
        
    def parseResource(self, regex):
        pattern = re.compile(regex)
        match = pattern.search(self.resource)
        result = False
        if match:
            result = True
            self.set_loadtime(match.group('time'))
            self.set_referer(match.group('ref'))
            self.set_domain(match.group('domain'))
            self.set_location()
        return result
    
if __name__ == '__main__':
    if len(sys.argv) >=2:
        if sys.argv[1] in config_sets_zx.keys():
            RUN_ENV = sys.argv[1]
            
    LOG_FILENAME = os.path.join(os.path.dirname(__file__), '%s.log' %os.path.basename(__file__))
    LOG_FORMAT = '%(asctime)s | %(levelname)s |%(lineno)s | %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, level=config_sets_zx[RUN_ENV]['logging_level'], format=LOG_FORMAT)
    
    try:
        conn = MySQLdb.connect(host=config_sets_zx[RUN_ENV]['host'],
                               user=config_sets_zx[RUN_ENV]['user'],
                               passwd=config_sets_zx[RUN_ENV]['passwd'],
                               db=config_sets_zx[RUN_ENV]['db'],
                               charset='utf8')
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    except MySQLdb.Error, e:
        logging.critical('MySQL connection error! %s' % e)
        sys.exit(1)
        
    delta_one_day = datetime.timedelta(days=1)
    yesterday = datetime.date.today() - delta_one_day
    tomorrow = datetime.date.today() + delta_one_day
    
    logs = glob.glob('/logs/zx_360quan-access_log.%s??' % yesterday.strftime('%Y%m%d'))
    regex = r't=(?P<time>\d+)&r=(?P<ref>http://(?P<domain>\S+?).360quan.com\S+)'
    for log in logs:
        logging.info('[log file]%s' % log)
        parser = apachelog(log, GuestZX)
        guests = parser.parseFile(regex)
        
        for guest in guests:
            sql = "INSERT INTO log (ip, city, isp, date_c, loadtime, domain, ref, agent) VALUES ('%s', '%s', '%s', '%s', %d, '%s', '%s', '%s');" % \
                (guest.ip, guest.city, guest.isp, guest.dateteime.strftime('%Y-%m-%d %H:00:00'), guest.loadtime, guest.domain, guest.referer, guest.agent)

            try:
                cursor.execute(sql)
            except:
                logging.exception(sql)
                
    chart = extChart()
    chart.title = ofc2.title(text='Report for Load Time', style='{font-size:20px; color:#0000ff; font-family: Verdana; text-align: center;}')
    chart.bg_colour = '#FFFFFF'
    chart.x_legend = ofc2.x_legend(text='Date: %s' % yesterday.strftime('%Y-%m-%d'), style='{color: #736AFF;font-size: 12px;}')
    chart.y_legend = ofc2.y_legend(text='time(ms)', style='{color:#736AFF; font-size: 12px;}')
    
    chart.y_axis = ofc2.y_axis(grid_colour='#DDDDDD', stroke=1, max=50)
    chart.x_axis = ofc2.x_axis(grid_colour='#DDDDDD', stroke=1)
    
    per_ten_min_list = ["00:00","01: 00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00","08:00", \
                    "09:00", "10:00", "11:00", "12:00", "13:00", "14:00","15:00", "16:00", \
                    "17:00", "18:00", "19:00", "20:00", "21:00","22:00", "23:00"]
    chart.x_axis.labels = ofc2.x_axis_labels(labels=per_ten_min_list, rotate=45)
    
    domains = ['www', 'my', 'www1']
    COLOURS = {'www': '#ffae00', 'my':'#52aa4b', 'www1': '#ff0000'}
    
    for domain in domains:
        sql = 'SELECT ip, city, isp, date_c, loadtime, domain, ref FROM log WHERE domain="%s" AND date_c BETWEEN "%s 00:00:00" AND "%s 00:00:00"' % \
            (domain, yesterday.strftime('%Y-%m-%d'), datetime.date.today.strftime('%Y-%m-%d'))
        try:
            cursor.execute(sql)
        except:
            logging.error(sql)
        
        rows = cursor.fetchall()
        chart_line = ofc2.line(text=domain, colour=COLOURS[domain])
        chart_line.dot_style = ofc2.dot()
        
        values = [0 for _ in range(24)]
        for row in rows:
            grid_line = {}
            grid_line['domain'] = domain
            grid_line['city'] = row['city']
            grid_line['isp'] = row['isp']
            grid_line['datetime'] = row['date_c'].strftime('%m/%d/%Y %H:%M:%S')
            grid_line['time'] = row['loadtime']
            grid_line['ref'] = row['ref']
            chart.add_grid_line(grid_line)
            
            index = row['date_c'].hour
            lt = values[index]
            if lt:
                lt = (lt + row['loadtime'])/2
            else:
                lt = row['loadtime']
            values[index] = lt
            
            if lt > chart.y_axis.max:
                chart.y_axis.max = lt + 10**(len(str(lt))-1)
            
            chart_line.values = values
            chart.add_element(chart_line)
    reportfile = os.path.join(os.path.dirname(__file__), 'data', yesterday.strftime('%Y-%m-%d'))
    report = open(reportfile, 'w+')
    report.write(cjson.encode(chart))
    report.close()
    
    mail_content="""
    The average response time report.
    Date: \t%s
    Link: \thttp://zx.360quan.com/stats.html?ofc=data/%s
    """ % (yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'))
    mail_file = open('mail.txt', 'w+')
    mail_file.write(mail_content)
    mail_file.close()
    
    mail_cmd = 'mail -c %s -s "The Report of Link Clicking" %s < mail.txt' % (config_sets_zx[RUN_ENV]['mail_to'], config_sets_zx[RUN_ENV]['mail_cc'])
    os.popen(mail_cmd)