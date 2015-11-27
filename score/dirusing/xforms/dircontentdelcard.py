# coding: utf-8
'''

@author: a.rudenko

'''
import json
import base64
from common.sysfunctions import tableCursorImport
from itertools import izip

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
try:
    from ru.curs.celesta.showcase.utils import XMLJSONConverter
    from ru.curs.showcase.core import UserMessage
except:
    pass
from common.hierarchy import deleteNodeFromHierarchy


from dirusing.commonfunctions import relatedTableCursorImport

#from common import webservicefunc
import xml.dom.minidom

def cardDelData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}}
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
    #return UserMessage(u"TEST3", u"%s" % (session))
    #print XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse()
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def getMappingTables(currentTable):
    """ Возвращает список инстанцированных курсоров таблиц маппинга
    для всех refList полей таблицы currentTable и для каждого - список
    полей, являющихся внешним ключём на currentTable
    
    @param currentTable курсор основной таблицы справочника
    @return <tt>list of tuples</tt>  спиок кортежей вида (Cursor, list if string)
    """
    m = currentTable.meta()
    
    cols = m.getColumns()
    cols = filter(lambda x: 'refMappingTable' in m.getColumn(x).getCelestaDoc(), cols)
    
    res = []
    for c in [m.getColumn(colName) for colName in cols]:
        tableName = json.loads(c.getCelestaDoc())['refMappingTable']
        grainName = m.getGrain().getName()
        
        c = tableCursorImport(grainName, tableName)(currentTable.callContext())
        
        foreignKeys = c.meta().getForeignKeys()
        
        fkCols = []
        for foreignKey in foreignKeys:
            if foreignKey.getReferencedTable() == m:
                fkCols = foreignKey.getColumns()
                break
        
        res.append((c, fkCols))
        
    return res


def deleteFromMappingTables(currentTable, ids):
    """Удаляет данные из таблиц маппинга.
    
    @param currentTable курсор основной таблицы справочника
    @param ids (list of PK) список идентификаторов записей для удаления 
    """
    mappingTables = getMappingTables(currentTable)
    if not mappingTables:
        return
    
    
    currentTablePKs = []
    currentTablePKObject = currentTable.meta().getPrimaryKey()
    for key in currentTablePKObject:
        currentTablePKs.append(key)
    
    # для каждого ИД получаем запись, чтобы корректно скопировать значения 
    
    
    for pk in ids:
        currentTable.get(*pk)
    
        for c, fkCols in mappingTables:
            for foreignKeyColumn, key in izip(fkCols, currentTablePKs):
                c.setRange(foreignKeyColumn, getattr(currentTable, key))
            c.deleteAll()
        
        currentTable.delete()
        
            
def cardDelDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    table_jsn = json.loads(currentTable.meta().getCelestaDoc())
    #признак иерархичности
    isHierarchical = table_jsn['isHierarchical']
    if isHierarchical == 'true':
        for column in currentTable.meta().getColumns():
            #получаем названия колонок с кодом дьюи и сортировкой
            if json.loads(currentTable.meta().getColumn(column).getCelestaDoc())['name'] == u'deweyCode':
                deweyColumn = column
            if json.loads(currentTable.meta().getColumn(column).getCelestaDoc())['name'] == u'sortNumber':
                sortColumn = column
    selectedRecordsCoded = json.loads(session)['sessioncontext']['related']['gridContext']['selectedRecordId']
    if not isinstance(selectedRecordsCoded, list):
        selectedRecordsCoded = [selectedRecordsCoded]
    
#     for selectedRecordCoded in selectedRecordsCoded:
#         #print selectedRecordCoded
#         #print "2"
#         if isHierarchical == 'true':
#             selectedRecordId = json.loads(base64.b64decode(selectedRecordCoded))
#             currentTable.get(*selectedRecordId)
#             deleteNodeFromHierarchy(context, currentTable, deweyColumn, sortColumn)
#         else:
#             selectedRecordId = json.loads(base64.b64decode(selectedRecordCoded))
#             currentTable.get(*selectedRecordId)
#             currentTable.delete()
    
    
    selectedRecords = [json.loads(base64.b64decode(r)) for r in selectedRecordsCoded]
    
    if isHierarchical == 'false':
        deleteFromMappingTables(currentTable, selectedRecords)
    
#     for recId in selectedRecords:
#         if isHierarchical == 'true':
#             # здесь tryGet, т.к. могут быть выбраны несколько записей в одной иерархии, и, если
#             # родитель удалён, записи уже не существует.
#             if currentTable.tryGet(*recId):
#                 deleteNodeFromHierarchy(context, currentTable, deweyColumn, sortColumn)
#         else:
#             currentTable.get(*recId)
#             currentTable.delete()


def cardDelAllDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    currentTable.deleteAll()
