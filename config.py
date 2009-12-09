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
                     },
                'debug': {
                         'host': '10.10.208.59',
                         'user': 'httpdlog',
                         'passwd': 'httpdlog',
                         'db':'9949_test',
                         'logging_level': logging.DEBUG,
                         },
                'test':{
                         'host': '192.168.5.56',
                         'user': 'root',
                         'passwd': '123456',
                         'db': '9949',
                         'logging_level': logging.INFO
                         }
                }