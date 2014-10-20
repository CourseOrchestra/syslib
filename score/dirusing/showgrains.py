# coding: utf-8
'''
Created on 28.11.2013

@author: v.popov
'''

import os
import simplejson as json

def showGrains():
    u'''Функция читает файл с кортежем, в котором указано, какие гранулы отображать. '''

    result = json.load(open('%s\showgrains.json' % os.path.dirname(__file__)))
    return result

#print hideGrains()


