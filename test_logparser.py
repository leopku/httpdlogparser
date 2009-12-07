#!/usr/bin/env python
# -*- coding: utf8 -*-
from apachelogparser import apachelog
from logparser_9949 import guest9949
import unittest

class log9949ParseTest(unittest.TestCase):
    def setUp(self):
        self.s = '222.35.169.141 - - [07/Dec/2009:18:00:00 +0800] "POST /go.html?name=17173&u=http://www.17173.com/ HTTP/1.1" 200 50 "http://www.9949.cn/?uid=desktop" "Mozilla/4.0 (compatible; MSIE 6.0; IQ 0.9.8.1322; zh_cn; Windows NT 5.1))"'
        self.regex = r'POST /go\.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP'
        self.parser = apachelog('', guest9949, self.regex)
        self.g = self.parser.getGuestInfo(self.s)
        
    def testIP(self):
        self.failUnlessEqual(self.g.ip, '222.35.169.141')
        
    def testName(self):
        self.failUnlessEqual(self.g.name, '17173')
        
    def testCity(self):
        self.failUnlessEqual(self.g.city, '北京市')
        
    def testISP(self):
        self.failUnlessEqual(self.g.isp, '铁通ADSL')
        
if __name__ == '__main__':
    unittest.main()