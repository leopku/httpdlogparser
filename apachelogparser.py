#!/usr/bin/env python

import os
import re
import os.path
import simplejson

class Visitor:
    pass
        
class apachelog:
    """ apache log file class """
    
    def __init__(self, log_filename):
        self.log_filename = log_filename
        self.visitor_list = []
        
    def parsefile(self):
        f = open(self.log_filename, 'r')
        for line in f.xreadlines():
            v = self.parseoneline(line)
            self.visitor_list.append(v)
        f.close()
        return self.visitor_list
    
    def parseoneline(self, string):
        visitor = Visitor()
        info = string.split('"')
        # ip and datetime
        ip_datetime = info[0].split(' ')
        visitor.ip = ip_datetime[0]
        dt = ip_datetime[3]
        dt = dt[-(len(dt)-1):]
        t = time.strptime(dt, '%d/%b/%Y:%H:%M:%S')
        visitor.datetime = datetime.datetime(*t[:6])
        # resource name
        visitor.resource = info[1]
        visitor.referer = info[3]
        # agent
        visitor.agent = info[-2]
        return visitor