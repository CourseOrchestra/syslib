# coding: utf-8
'''
Created on 12.08.2014

@author: Rudenko
'''
import simplejson as json

from common.xmlutils import XMLJSONConverter
from common import navigator, sysfunctions
from common.sysfunctions import toHexForXml
from ru.curs.celesta import syscursors
from security import _security_orm
from security.functions import Settings
from security.setForeignKeys import setForeignKeys as setConstraint
from security.xform.users import employeesSubjectsPostInsert, employeesSubjectsPostUpdate, employeesSubjectsPreDelete

from common.sysfunctions import tableCursorImport
from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor
from ru.curs.celesta import Celesta
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList, htmlDecode

settings=Settings()

if not settings.loginIsSubject():
    employeesGrain=settings.getEmployeesParam("employeesGrain")
    employeesTable=settings.getEmployeesParam("employeesTable")
    
    employeesCursor=tableCursorImport(employeesGrain, employeesTable)
    
    employeesCursor.onPostInsert.append(employeesSubjectsPostInsert)
    employeesCursor.onPostUpdate.append(employeesSubjectsPostUpdate)
    employeesCursor.onPreDelete.append(employeesSubjectsPreDelete)
    
if not settings.isSystemInitialised():
    setConstraint() #функция устанавливает внешний ключ в таблицу subjects и меняет значение параметра isSystemInitialised на True
    a = Celesta.getInstance()
    adminUser = settings.getEmployeesParam("admin")
    conn = ConnectionPool.get()
    context = CallContext(conn, adminUser, a)
    numbersSeries = numbersSeriesCursor(context)
    linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
    numbersSeries.id = 'subjects'
    numbersSeries.description = 'subjects'
    if not numbersSeries.tryInsert():
        numbersSeries.update()
    linesOfNumbersSeries.seriesId = 'subjects'
    linesOfNumbersSeries.numberOfLine = 1
    linesOfNumbersSeries.startingDate = '2014-05-05 00:00:00'
    linesOfNumbersSeries.startingNumber = 10
    linesOfNumbersSeries.endingNumber = 100000
    linesOfNumbersSeries.incrimentByNumber = 1
    linesOfNumbersSeries.isOpened = True
    linesOfNumbersSeries.prefix = 'subject-'
    linesOfNumbersSeries.isFixedLength = False
    if not linesOfNumbersSeries.tryInsert():
        linesOfNumbersSeries.update()
    
    

def ctgNavigator(context, session):
    currentTable = relatedTableCursorImport("acrsprav", "contrag_type")(context)
    
    myNavigator = {
        "group":{
            "@id": "ctg",
             "@name": "Контрагенты",
             "level1":[{
                 "@id": "ctg_types",
                 "@name": "Контрагенты по типам",
                 "level2":[]}]
                
    }
                       
                       }
    myNavigator["group"]["level1"].append({"@id": "ctg_groups",
                 "@name": "Группы",
                 "action":{"main_context":None, "datapanel":{"@type":"ctg.datapanel.ctgdata.ctgGroupsDatapanel.celesta"}}})    

    if currentTable.canRead():
        
        for rec in currentTable.iterate():
            recId = getattr(rec, "id")
            name = getattr(rec, "name")
            main=u'{"grain":"acrsprav","table":"contrags", "contragTypeId":"'+str(recId)+'"}'
            data = {
                     "@id": "type"+str(recId),
                     "@name": name,
                     "action":{"main_context":main, "datapanel":{"@type":"ctg.datapanel.ctgdata.ctgdataDatapanel.celesta"}}
                     }
            myNavigator["group"]["level1"][0]["level2"].append(data)
          
        main=u'{"grain":"acrsprav","table":"contrags", "contragTypeId":"-1"}'
        data =  {
                     "@id": "type_all",
                     "@name": "Все",
                     "action":{"main_context":main, "datapanel":{"@type":"ctg.datapanel.ctgdata.ctgdataDatapanel.celesta"}}
                     }      
        myNavigator["group"]["level1"][0]["level2"].append(data)  
    else:
        myNavigator = {
        "group":{}}
    return myNavigator 

navigator.navigatorsParts['98'] = ctgNavigator