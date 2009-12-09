#!/usr/bin/env python
# -*- coding: utf8 -*-
from apachelogparser import apachelog
from logparser_9949 import Guest9949
import unittest

class log9949ParseTest(unittest.TestCase):
    def setUp(self):
        self.s = '222.35.169.141 - - [07/Dec/2009:18:00:00 +0800] "POST /go.html?name=17173&u=http://www.17173.com/ HTTP/1.1" 200 50 "http://www.9949.cn/?uid=desktop" "Mozilla/4.0 (compatible; MSIE 6.0; IQ 0.9.8.1322; zh_cn; Windows NT 5.1))"'
        self.regex = r'POST /go\.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP'
        self.parser = apachelog('', Guest9949, self.regex)
        self.g = self.parser.getGuestInfo(self.s)
        
    def testIP(self):
        self.failUnlessEqual(self.g.ip, '222.35.169.141')
        
    def testName(self):
        self.failUnlessEqual(self.g.name, '17173')
        
    def testCity(self):
        self.failUnlessEqual(self.g.city, '北京市')
        
    def testISP(self):
        self.failUnlessEqual(self.g.isp, '铁通ADSL')

class log9949AmazonTest(unittest.TestCase):
    def setUp(self):
        self.s = '121.204.244.51 - - [07/Dec/2009:23:53:03 +0800] "POST /go.html?name=\xd7\xbf\xd4\xbd\xd1\xc7\xc2\xed\xd1\xb7&u=http://www.amazon.cn/?source=heima8_134092 HTTP/1.1" 200 50 "http://www.9949.cn/" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)"'
        self.regex = r'POST /go\.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP'
        self.parser =  apachelog('', Guest9949, self.regex)
        self.guest = self.parser.getGuestInfo(self.s)
        
    def testIP(self):
        self.failUnlessEqual(self.guest.ip, '121.204.244.51')
        
    def testName(self):
        self.failUnlessEqual(self.guest.name, '卓越亚马逊')
        
    def testCity(self):
        self.failUnlessEqual(self.guest.city, '福建省厦门市')
        
    def testISP(self):
        self.failUnlessEqual(self.guest.isp, '电信')
        
if __name__ == '__main__':
    unittest.main()