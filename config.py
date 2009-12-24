#!/usr/bin/env python

import logging

RUN_ENV = 'debug'

class ConfigBase:
    pass

config_sets_9949 = {
               'production':{
                             'host':'10.10.208.59',
                             'user': 'httpdlog',
                             'passwd':'httpdlog',
                             'db':'9949',
                             'logging_level': logging.ERROR,
                             'mail_to': 'fengyue@360quan.com,zhangyuxiang@360quan.com,liujiejiao@360quan.com,liusong@360quan.com',
                             'mail_cc': 'dan@360quan.com,uzi.refaeli@360quan.com'
                     },
                'debug': {
                         'host': '10.10.208.59',
                         'user': 'httpdlog',
                         'passwd': 'httpdlog',
                         'db':'9949_test',
                         'logging_level': logging.DEBUG,
                         'mail_to': 'liusong@360quan.com',
                         'mail_cc': 'svn@360quan.com'
                         },
                'test':{
                         'host': '192.168.5.56',
                         'user': 'root',
                         'passwd': '123456',
                         'db': '9949',
                         'logging_level': logging.INFO,
                         'mail_to': 'liusong@360quan.com',
                         'mail_cc': 'svn@360quan.com'
                         }
                }