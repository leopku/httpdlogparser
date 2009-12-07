#!/usr/bin/env python
import os.path
import logging
import sys
import re
from urllib import unquote
import MySQLdb
import datetime
import glob
from apachelogparser import GuestBase, ReportBase, apachelog

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
        if match:
            self.set_target_url(match.group('dest'))
            
            name = match.group('name')
            if name == 'undefined':
                name = None
            else:
                try:
                    name = unquote(name).decode('string_escape').decode('GBK')
                except Exception, err:
                    name = None
            self.set_name(name)
        
if __name__ == '__main__':
        
    logger = logging.getLogger('9949')
    logger.setLevel(logging.DEBUG)
    hdlr = logging.FileHandler(os.path.join(os.path.dirname(__file__), '%s.log' %os.path.basename(__file__)))

    hdlr.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s | %(lineno)s | %(message)s')
    hdlr.setFormatter(fmt)
    logger.addHandler(hdlr)
    
    try:
        conn = MySQLdb.connect(host='10.10.208.59',
                               user='httpdlog',
                               passwd='httpdlog',
                               db='9949',
                               charset='utf8')
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    except MySQLdb.Error, e:
        logger.critical('MySQL connection error! %s' % e)
        sys.exit(1)
    
    delta_one_day = datetime.timedelta(days=1)
    yesterday = datetime.date.today() - delta_one_day
    tomorrow = datetime.date.today() + delta_one_day

    logs = glob.glob('/Data/log/9949/9949.cn-access_log.%s??' % yesterday.strftime('%Y%m%d'))
    regex = r'POST /go\.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP'
    for log in logs:
        logger.info('[log file]%s' % log)
        parser = apachelog(log, guest9949, regex)
        guests = parser.parseFile()
        
        counts = {}
        date = None
        for guest in guests:
            counts[guest.target_url] = counts.get(guest.target_url, 0) + 1
            
            sql = "INSERT INTO log (ip, city, isp, date_c, dest, ref, agent, name) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (guest.ip, guest.city, guest.isp, guest.datetime.strftime('%Y-%m-%d %H:00:00'), guest.target_url, guest.referer, guest.agent, guest.name)
            cursor.execute(sql)