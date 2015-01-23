#coding:utf-8

'''
Created on 30.09.2014

@author: tr0glo)|(I╠╣ 
'''

import os

from ru.curs.celesta.syscursors import UserRolesCursor, PermissionsCursor, RolesCursor
from common.sysfunctions import tableCursorImport
from common.dbutils import DataBaseXMLExchange
from java.io import FileOutputStream, FileInputStream
from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext


def importData(tableInstance, filePath):
    u'''Функция загрузки данных в БД''' 
    dataStream = FileInputStream(filePath)    
    exchange = DataBaseXMLExchange(dataStream, tableInstance)
    exchange.uploadXML()
    dataStream.close()
        
def exportData(tableInstance,path):
    dataStream= FileOutputStream(path)     
    exchange = DataBaseXMLExchange(dataStream, tableInstance)
    exchange.downloadXML()
    dataStream.close()
    
def initTables(context):
    filePath = os.path.dirname(os.path.abspath(__file__))
    
    initializationRequired = False
    
    roles = RolesCursor(context)
    
    
    if roles.tryGet('reader'):
        if roles.tryGet('editor'):
            if roles.count() == 2:
                initializationRequired = True
    if initializationRequired:
        importData(roles,filePath+'/roles.xml')
        
        userroles = UserRolesCursor(context)
        importData(userroles,filePath+'/userRoles.xml')    
        
        perms = PermissionsCursor(context)
        importData(perms,filePath+'/permissions.xml')
    
    
        
        importTables = [
                    {'grain':'security','table':'customPermsTypes'},
                    {'grain':'security','table':'customPerms'},
#                     {'grain':'security','table':'subjects'},
#                     {'grain':'security','table':'logins'},                    
                    {'grain':'security','table':'rolesCustomPerms'},
#                     {'grain':'workflow','table':'form'},
#                     {'grain':'workflow','table':'processes'},
#                     {'grain':'workflow','table':'matchingCircuit'},
#                     {'grain':'common','table':'numbersSeries'},
#                     {'grain':'common','table':'linesOfNumbersSeries'},
                    
                    #{'grain':'workflow','table':'userGroup'}
                    ]            
    
        for table in importTables:
            tableInstance = tableCursorImport(table['grain'], table['table'])(context)
            importData(tableInstance,filePath+'/'+table['table']+'.xml')
        context.commit()
        
def exportTables():
    a = Celesta.getInstance()
    conn = ConnectionPool.get()  
    sesContext = SessionContext('super', 'supersession')
    context = CallContext(conn, sesContext)
    
    filePath = os.path.dirname(os.path.abspath(__file__))
                                            
    perms = PermissionsCursor(context)
    exportData(perms,filePath+'/permissions.xml')
    
    roles = RolesCursor(context)
    exportData(roles,filePath+'/roles.xml')
    
    userroles = UserRolesCursor(context)
    exportData(userroles,filePath+'/userRoles.xml')
    
    exportTables = [
                    {'grain':'security','table':'customPermsTypes'},
                    {'grain':'security','table':'customPerms'},
                    {'grain':'security','table':'logins'},
                    {'grain':'security','table':'subjects'},
                    {'grain':'security','table':'rolesCustomPerms'},
                    {'grain':'workflow','table':'form'},
                    {'grain':'workflow','table':'matchingCircuit'},
                    {'grain':'workflow','table':'processes'},
                    {'grain':'common','table':'linesOfNumbersSeries'},
                    {'grain':'common','table':'numbersSeries'},
                    #{'grain':'workflow','table':'userGroup'}
                    ]
    
    for table in exportTables:
        tableInstance = tableCursorImport(table['grain'], table['table'])(context)
        exportData(tableInstance,filePath+'/'+table['table']+'.xml')
