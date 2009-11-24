#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pyip
import MySQLdb
import time
import datetime
import smtplib
import glob
import os
import os.path
import simplejson as json
from urllib import unquote

IPFILE = os.path.join(os.path.dirname(__file__), 'QQWry.Dat')

class Client:
    """ client infomation """
    
    def __init__(self):
        self.ip = None
        self.city = None
        self.isp = None
        self.datetime = None
        # self.loadtime = None
        self.ref = None
        self.name = None
        self.agent = None
        self.dest = None

class HttpdLogParser:
    """ parser logs generated by httpd and generate a report. """
    
    def __init__(self, logfile):
        self.logfile = logfile
        self.clients = []
        
    def _splitlog(self):
        f = open(self.logfile, 'r')
        for line in f.xreadlines():
            info = line.split('"')
                
    def parseLog(self):
        f = open(self.logfile, 'r')
        for line in f.xreadlines():
            client = Client()
            info = line.split('"')

            pattern = re.compile(r'POST /go.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP')
            m = pattern.search(info[1])
            client.ref = info[3]
            if m:
                client.dest = m.group('dest')
                name = m.group('name')
                if name == 'undefined'
                    name = None
                else:
                    name = unquote(name.decode('GB2312').encode('UTF-8'))
                client.name = name

                client.agent = info[-2]
                ip_datetime = info[0].split(' ')
                client.ip = ip_datetime[0]
                
                i = pyip.IPInfo(IPFILE)
                city, isp = i.getIPAddr(client.ip)
                client.city = city.decode('utf8')
                client.isp = isp.decode('utf8')
                
                dt = ip_datetime[3]
                dt = dt[-(len(dt)-1):]
                
                t = time.strptime(dt, '%d/%b/%Y:%H:%M:%S')
                client.datetime = datetime.datetime(*t[:6])

                self.clients.append(client)
            
        return self.clients

def genReport(day, cursor):
    report = os.path.join(os.path.dirname(__file__), '9949', day.strftime('%Y-%m-%d'))
    f_report  = open(report, 'w+')
    chart = {}
    
    chart['title']={}
    chart['title']['text']='User Clicks.'
    chart['title']['style']='{font-size:20px; color:#0000ff; font-family: Verdana; text-align: center;}'
    
    chart['x_legend']={}
    chart['x_legend']['text']='Days/Weeks/Monthes' 
    chart['x_legend']['style']='{color: #736AFF;font-size: 12px;}'
    chart['y_legend']={}
    chart['y_legend']['text']='click counts'
    chart['y_legend']['style']='{color:#736AFF; font-size: 12px;}'
    
    chart['x_axis'] = {}
    chart['x_axis']['stroke'] = 1
    chart['x_axis']['labels'] = {}
    chart['x_axis']['labels']['rotate'] = 0
    chart['x_axis']['labels']['labels'] = ["7","6", "5", "4", "3", "2", "1"]
    
    chart['y_axis'] = {}
    chart['y_axis']['stroke'] = 1
    chart['y_axis']['visible'] = True
    chart['y_axis']['offset'] = False
    chart['y_axis']['max'] =  50
    
    chart['elements']=[]
    d = datetime.timedelta(days=1)
    nextday = day + d

    periods = {'Day':'%Y-%m-%d', 'Week':'%u', 'Month':'%Y-%m'}
    colors = {'Day': '#ffae00', 'Week':'#52aa4b', 'Month': '#ff0000'}
    lines = {}
    chart['rows'] = []
    for period,format in periods.items():
        sql = "SELECT name, dest, date_c, DATE_FORMAT(date_c, '%s') AS period, count(id) AS cnt FROM log GROUP BY period DESC;" % format
        logger.info(sql)
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        lines[period] = {}
        lines[period]['type'] = 'line'
        lines[period]['colour'] = colors[period]
        lines[period]['text'] = period
        lines[period]['dot-style'] = {}
        lines[period]['dot-style']['type'] = 'solid-dot'
        lines[period]['values'] = [0 for _ in range(7)]
       
        if period == 'Day':
            chart['total'] = chart.get('total',0) + len(rows)
	
        rows_list = list(rows)
        for row in rows:
            index = rows_list.index(row)
            lines[period]['values'][-1-index] = {}
            lines[period]['values'][-1-index]['value'] = row['cnt']
            lines[period]['values'][-1-index]['tip'] = '%s:%s<br>#val#' % (period, row['period'])
            
            if row['cnt'] > chart['y_axis']['max']:
                chart['y_axis']['max'] = row['cnt'] + 1000
        chart['elements'].append(lines[period])

    sql = "SELECT name, dest, COUNT(id) AS cnt FROM log WHERE date_c BETWEEN '%s 00:00:00' AND '%s 00:00:00' GROUP BY dest ORDER BY cnt DESC;" % (day.strftime('%Y-%m-%d'), nextday.strftime('%Y-%m-%d'))
    logger.info('[grid sql]%s' % sql)
    cursor.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        r = {}
        r['name'] = row['name']
        r['dest'] = row['dest']
        r['count'] = row['cnt']
        chart['rows'].append(r)                
       
    f_report.write(json.dumps(chart))
    f_report.close()

if __name__ == '__main__':
    import sys
    import logging
    
    logger = logging.getLogger('stats')
    logger.setLevel(logging.DEBUG)
    hdlr = logging.FileHandler(os.path.join(os.path.dirname(__file__), '%s.log' %os.path.basename(__file__)))
    hdlr.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s | %(lineno)s | %(message)s')
    hdlr.setFormatter(fmt)
    logger.addHandler(hdlr)
    
    delta_one_day = datetime.timedelta(days=1)
    yesterday = datetime.date.today() - delta_one_day
    tomorrow = datetime.date.today() + delta_one_day

    try:
        conn = MySQLdb.connect(host='10.10.208.59',
                               user='httpdlog',
                               passwd='httpdlog',
                               db='9949',
                               charset='utf8')
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    except MySQLdb.Error, e:
        print 'Connecting MySQL error!'
        sys.exit(1)
        
    logs = glob.glob('/Data/log/9949/9949.cn-access_log.%s??' % yesterday.strftime('%Y%m%d'))
    
    for log in logs:
        logger.info('[log file]%s' % log)
        hlp =  HttpdLogParser(log)
        clients = hlp.parseLog()

        counts = {}
        date = None
        for client in clients:
            counts[client.dest] = counts.get(client.dest, 0) + 1
            date = client.datetime 
            sql = "INSERT INTO log (ip, city, isp, date_c, dest, ref, agent, name) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (client.ip, client.city, client.isp, client.datetime.strftime('%Y-%m-%d %H:00:00'), client.dest, client.ref, client.agent, client.name)
            cursor.execute(sql)
    
    genReport(yesterday ,cursor)
    cursor.close()
    conn.close()
    
    msg = """
    The Report of Link Clicking.
    Date: %s
    Link: <a href='http://zx.360quan.com/stats.html?ofc=9949/%s' target='_blank'>view report</a>
    """ % (yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'))
    f_mail = open('mail.txt', 'w+')
    f_mail.write(msg)
    f_mail.close()
    r = os.popen('mail -c fengyue@360quan.com,zhangyuxiang@360quan.com,liusong@360quan.com -s "The Report of Link Clicking" dan@360quan.com,uzi.refaeli@360quan.com < mail.txt')    
