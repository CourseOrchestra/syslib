# coding: utf-8
'''
Created on 03.02.2016

@author: s.gavrilov
'''

from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

import datetime

def fileInit(context):
    numbersSeries = numbersSeriesCursor(context)
    linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
    files_name = 'filesNS'
    file_vers_name = 'fileVerNS'

    numbersSeries.id = files_name
    numbersSeries.description = 'filesNS'
    
    if not numbersSeries.tryInsert():
        numbersSeries.update()
        
    if not linesOfNumbersSeries.tryGet(files_name, 1):
        now = datetime.datetime.now()
        linesOfNumbersSeries.seriesId = files_name
        linesOfNumbersSeries.numberOfLine = 1                
        linesOfNumbersSeries.startingDate = now
        linesOfNumbersSeries.startingNumber = 1
        linesOfNumbersSeries.endingNumber = 1000000
        linesOfNumbersSeries.incrimentByNumber = 1
        linesOfNumbersSeries.isOpened = True
        linesOfNumbersSeries.prefix = files_name + '-'
        linesOfNumbersSeries.postfix = '#'
        linesOfNumbersSeries.isFixedLength = False
        linesOfNumbersSeries.insert()
        
    numbersSeries.id = file_vers_name
    numbersSeries.description = file_vers_name
    
    if not numbersSeries.tryInsert():
        numbersSeries.update()
        
    if not linesOfNumbersSeries.tryGet(file_vers_name, 1):
        now = datetime.datetime.now()
        linesOfNumbersSeries.seriesId = file_vers_name
        linesOfNumbersSeries.numberOfLine = 1                
        linesOfNumbersSeries.startingDate = now
        linesOfNumbersSeries.startingNumber = 1
        linesOfNumbersSeries.endingNumber = 10000000
        linesOfNumbersSeries.incrimentByNumber = 1
        linesOfNumbersSeries.isOpened = True
        linesOfNumbersSeries.prefix = file_vers_name + '-'
        linesOfNumbersSeries.postfix = '#'
        linesOfNumbersSeries.isFixedLength = False
        linesOfNumbersSeries.insert()