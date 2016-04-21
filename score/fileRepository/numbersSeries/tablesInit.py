# coding: UTF-8

import os

from common.sysfunctions import tableCursorImport
from ru.curs.celesta.syscursors import UserRolesCursor, PermissionsCursor, RolesCursor
from common.dbutils import DataBaseXMLExchange
from java.io import FileOutputStream, FileInputStream


def importData(tableInstance, filePath, action):
    u'''Функция загрузки данных в БД'''

    dataStream = FileInputStream(filePath)
    exchange = DataBaseXMLExchange(dataStream, tableInstance)
    exchange.uploadXML(action)
    dataStream.close()


def exportData(tableInstance, path):
    dataStream = FileOutputStream(path)
    exchange = DataBaseXMLExchange(dataStream, tableInstance)
    exchange.downloadXML()
    dataStream.close()
    
    
def exportTables(context):
    u'''Функция экпорта данных из таблиц в xml'''

    filePath = os.path.dirname(os.path.abspath(__file__))

    exportTables = [{'grain':'common', 'table':'numbersSeries'},
                    {'grain':'common', 'table':'linesOfNumbersSeries'}]

    for table in exportTables:
        tableInstance = tableCursorImport(table['grain'], table['table'])(context)
        exportData(tableInstance, os.path.join(filePath, '%s.xml' % table['table']))

def initTables(context):
    u'''Функция инициализации таблиц'''
    filePath = os.path.dirname(os.path.abspath(__file__))

    importTables = [
                    {'grain': 'common',
                     'table': 'numbersSeries',
                     'action': 'i'
                     },
                    {'grain': 'common',
                     'table': 'linesOfNumbersSeries',
                     'action': 'i'
                     }
                    ]

    for table in importTables:       
        tableInstance = tableCursorImport(table['grain'], table['table'])(context)
        importData(tableInstance, os.path.join(filePath, '%s.xml' % table['table']), table.get('action') or 'ui')
