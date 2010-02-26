#!/usr/bin/env python

import copy
import logging

RUN_ENV = 'debug'

class ConfigBase:
    def __init__(self):
        self.host = '10.10.208.59'
        self.user = 'httpdlog'
        self.passwd = 'httpdlog'
        self.mail_to = 'fengyue@360quan.com,zhangyuxiang@360quan.com,liusong@360quan.com'
        self.mail_cc = 'dan@360quan.com,uzi.refaeli@360quan.com'

class ConfigZXBase(ConfigBase):
    def __init__(self, run_env):
        pass
    
config_sets_base = {
               'production':{
                             'host':'10.10.208.59',
                             'user': 'httpdlog',
                             'passwd':'httpdlog',
                             'db': '',
                             'logging_level': logging.ERROR,
                             'mail_to': 'fengyue@360quan.com, liusong@360quan.com',
                             'mail_cc': 'dan@360quan.com,uzi.refaeli@360quan.com'
                     },
                'debug': {
                         'host': '10.10.208.59',
                         'user': 'httpdlog',
                         'passwd': 'httpdlog',
                         'db':'',
                         'logging_level': logging.DEBUG,
                         'mail_to': 'liusong@360quan.com',
                         'mail_cc': 'svn@360quan.com'
                         },
                'test':{
                         'host': '192.168.5.56',
                         'user': 'root',
                         'passwd': '123456',
                         'db': '',
                         'logging_level': logging.INFO,
                         'mail_to': 'liusong@360quan.com',
                         'mail_cc': 'svn@360quan.com'
                         }
                }

# config enviroment for 9949
config_sets_9949 = copy.deepcopy(config_sets_base)
config_sets_9949['production']['db'] = '9949'
config_sets_9949['production']['mail_to'] += ', liujiejiao@360quan.com, , chenjianyu@360quan.com, zhanglei02@360quan.com'

config_sets_9949['debug']['db'] = '9949_test'

config_sets_9949['test']['db'] = '9949'

#config enviroment for zx
config_sets_zx = copy.deepcopy(config_sets_base)
config_sets_zx['production']['db'] = 'httpdlog'
config_sets_zx['debug']['db'] = 'httpdlog_test'
config_sets_zx['test']['db'] = 'httpdlog'

BEANSDB_NUM = 16
BEANSDB_CFG = {
               "localhost:7902": range(BEANSDB_NUM), 
               }
