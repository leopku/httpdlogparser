#!/usr/bin/env python
# coding: utf-8

from config import BEANSDB_CFG, BEANSDB_NUM

import os.path
from struct import unpack

import cjson

from pyip import IPInfo
import beansdb

class IPInfo_mem(IPInfo):
    '''从memcache中读取QQWry.Dat进行IP解析'''
    def __init__(self, key):
        ''' key is the key of QQWry.Dat in memcache'''
        self.mc = beansdb.Beansdb(BEANSDB_CFG, BEANSDB_NUM)
        img = self.mc.get(key)
        if img is None:
            f = file(os.path.join(os.path.dirname(__file__), 'QQWry.Dat'), 'rb')
            img = f.read()
            f.close()
            self.mc.set(key, img)
        self.img = img
        
        (self.firstIndex, self.lastIndex) = unpack('II', self.img[:8])
        self.indexCount = (self.lastIndex - self.firstIndex) / 7 + 1
        
    def getIPAddr(self, ip):
        location_dict = self.mc.get(ip)
        if location_dict is None:
            try:
                city, isp = super(IPInfo_mem, self).getIPAddr(ip)
                location_dict = {'CITY': city, 'ISP': isp}
                self.mc.set(ip, location_dict)
            except:
                location_dict = {}
        return location_dict