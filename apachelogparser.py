#!/usr/bin/env python

import os
import os.path
import pyip_mem
import time
import datetime
#import simplejson

#IPDATA = os.path.join(os.path.dirname(__file__), 'QQWry.Dat')
#IPINFO = pyip.IPInfo(IPDATA)
IPINFO = pyip_mem.IPInfo_mem('QQWry')

class GuestBase:
    """
    Suggest to derive a subclass from GuestBase.
    if you wanna parse more information for guest visited,
    define a method named parseResource in the subclass.
    Giving a regular expression parameter to the method and
    if matched, return True. Otherwise, return False please. 
    
    example:
    
    class SubGuest(GuestBase):
        def parseResource(self, regex)
            # give a regex to define how to parse.
            pattern = re.compile(regex)
            match = pattern.search(self.resource)
            
            result = False
            if match:
                result = True
                # get the infomation you wanted.
                self.info1 = m.group(1)
                self.info2 = m.group(2)
                
            # DON'T forget return the result
            return result
    """
    def set_ip(self, ip):
        self.ip = ip
        
    def set_time(self, dt):
        self.datetime = dt
        
    def set_resource(self, resource):
        self.resource  = resource
        
    def set_referer(self, referer):
        self.referer = referer
    
    def set_agent(self, agent):
        self.agent = agent
        
    def set_location(self):
#        try:
#            city, isp = IPINFO.getIPAddr_dict(self.ip)
#            self.city = city.decode('utf-8')
#            self.isp = isp.decode('utf-8')
#        except:
#            pass
        try:
            loc = IPINFO.getIPAddr_dict(self.ip)
            self.city = loc['CITY'].decode('utf-8')
            self.isp = loc['ISP'].decode('utf-8')
        except:
            pass
        
class apachelog:
    """ apache log file class """
    
    def __init__(self, log_filename, guest_class):
        self.log_filename = log_filename
        self.guest_class = guest_class
        self.guest_list = []
        
    def parseFile(self, regex):
        f = open(self.log_filename, 'r')
        for line in f.xreadlines():
            g = self.getGuestInfo(line)
            try:
                # parse more info.
                if g.parseResource(regex):
                    self.guest_list.append(g)
            except AttributeError:
                self.guest_list.append(g)
        f.close()
        return self.guest_list
    
    def getGuestInfo(self, string):
        
        guest = self.guest_class()
        info = string.split('"')
        # ip and datetime
        ip_datetime = info[0].split(' ')
        guest.set_ip(ip_datetime[0])
        dt = ip_datetime[3]
        dt = dt[-(len(dt)-1):]
        t = time.strptime(dt, '%d/%b/%Y:%H:%M:%S')
        guest.set_time(datetime.datetime(*t[:6]))
        # resource name
        guest.set_resource(info[1])
        guest.set_referer(info[3])
        # agent
        guest.set_agent(info[-2])

        return guest

class ReportBase:
    
    def __init__(self, report_filename, chart):
        self.filename = report_filename
        self.chart = chart
        
    def generateReport(self):
        pass
