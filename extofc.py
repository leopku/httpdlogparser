#!/usr/bin/env python

from ofc2 import open_flash_chart

class extChart(open_flash_chart):
    #def __init__(self, title, style=None):
    #    open_flash_chart.__init__(title, style)
    
    def add_grid_line(self, line):
        try:
            self['rows'].append(line)
        except:
            self['rows'] = [line]