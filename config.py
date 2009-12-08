#!/usr/bin/env python


class ConfigBase:
    pass

config_sets_9949 = {
               'production':{
                             'host':'10.10.208.59',
                             'user': 'httpdlog',
                             'passwd':'httpdlog',
                             'db':'9949',
                     },
                'debug': {
                         'host': '10.10.208.59',
                         'user': 'httpdlog',
                         'passwd': 'httpdlog',
                         'db':'9949_test',
                         },
                'test':{
                         'host': '192.168.5.56',
                         'user': 'root',
                         'passwd': '123456',
                         'db': '9949',
                         }
                }

