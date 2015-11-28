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
    @return <tt>list of tuples</tt>  спиcок кортежей вида (Cursor, list if string)
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


def deleteFromMappingTables(currentTable, ids, deleteMain=True):
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
        
        if deleteMain:
            currentTable.delete()


def deleteFromMappingTablesHierarchy(currentTable, ids):
    # получаем все коды Дьюи для ИД
    
    for column in currentTable.meta().getColumns():
            #получаем названия колонок с кодом дьюи и сортировкой
        if json.loads(currentTable.meta().getColumn(column).getCelestaDoc())['name'] == u'deweyCode':
            deweyColumn = column
        if json.loads(currentTable.meta().getColumn(column).getCelestaDoc())['name'] == u'sortNumber':
            sortColumn = column
    
    DEWEY_CODE_FIELD = deweyColumn
    DEWEY_SORT_FIELD = sortColumn
    
    allIds = []
    for pk in ids:
        currentTable.get(*pk)
        allIds.append((pk, getattr(currentTable, DEWEY_CODE_FIELD), getattr(currentTable, DEWEY_SORT_FIELD)))
    
    
#     print "!!!!!!!! H DELETE"
#     print allIds
    
    # сортируем по возрастанию и удаляем все подчинённые узлы, т.к. они всё равно будут удалены
    allIds.sort(key=lambda x: x[2])
    
#     print 'AFTER SORT'
#     print allIds
    
    # проходим по списку до тех пор, пока не останется дочерних элементов
    i = 0
    while i < len(allIds):
        curr = allIds[i]
        k = i + 1
        while k < len(allIds):
            if allIds[k][1].startswith(curr[1] + '.'):
                del allIds[k]
            else:
                k += 1
        i += 1
        
#     print 'AFTER CLEAN'
#     print allIds
    
    res = []
    # для каждого кода получаем всех потомков нв всех уровнях
    currentTable.orderBy(DEWEY_SORT_FIELD + ' asc')
    
#     print "CYCLE"
    
    for data in allIds:
#         print "parent = ", data[0] 
        
        res = [data[0]]
        
        currentTable.setFilter(DEWEY_CODE_FIELD, "'%s.'%%" % data[1])
        res += [rec._currentKeyValues() for rec in currentTable.iterate()]
        
#         print 'children = ', res
        
        # чистим маппинг-таблицы удаляемой ветки
        deleteFromMappingTables(currentTable, res, False)
        currentTable.get(*data[0])
        deleteNodeFromHierarchy(currentTable.callContext(), currentTable, DEWEY_CODE_FIELD, DEWEY_SORT_FIELD, True)
    
            
def cardDelDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    
#     print "!!!! DELETE"
#     print "session = ", session
#     print "main = ", main
#     print "add = ", add
#     
#     return
    
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    table_jsn = json.loads(currentTable.meta().getCelestaDoc())
    #признак иерархичности
    isHierarchical = table_jsn['isHierarchical'] == "true"
    selectedRecordsCoded = json.loads(session)['sessioncontext']['related']['gridContext']['selectedRecordId']
    if not isinstance(selectedRecordsCoded, list):
        selectedRecordsCoded = [selectedRecordsCoded]
    
    selectedRecords = [json.loads(base64.b64decode(r)) for r in selectedRecordsCoded]
    
    if isHierarchical:
        deleteFromMappingTablesHierarchy(currentTable, selectedRecords)
    else:
        deleteFromMappingTables(currentTable, selectedRecords, not isHierarchical)
    

def cardDelAllDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    
    mappingTables = getMappingTables(currentTable)
    
    for tbl, _ in mappingTables:
        tbl.deleteAll()
    
    currentTable.deleteAll()
    


if __name__ == '__main__':
    from ru.curs.celesta import Celesta
    from ru.curs.celesta import ConnectionPool
    from ru.curs.celesta import CallContext
    from ru.curs.celesta import SessionContext
    
    a = Celesta.getDebugInstance()
    conn = ConnectionPool.get()
    sesContext = SessionContext('super', 'testsession')
    context = CallContext(conn, sesContext)
    
    # удаление элемента 1.2.2 с ИД = 6
#     session =  '{"sessioncontext":{"sid":"super","userdata":"default","phone":"123-56-78","username":"super","fullusername":"–Р–ї–µ–Ї—Б–µ–є –Т. –Т–∞—Б–Є–ї—М–µ–≤","email":"12@yandex.ru","login":"super","sessionid":"8B9B06F1B482A287CFF30FE2B0847F4A","related":{"gridContext":{"parentId":"WzNd","currentColumnId":"deweyCode","gridFilterInfo":"","pageInfo":{"@size":"2147483646","@number":"1"},"liveInfo":{"@totalCount":"0","@pageNumber":"1","@offset":"0","@limit":"2147483646"},"partialUpdate":"false","currentDatapanelWidth":"1596","@id":"13","currentDatapanelHeight":"782","selectedRecordId":"WzZd","currentRecordId":"WzZd"}},"ip":"127.0.0.1"}}'
#     main =  '{"grain":"testsprav","table":"link_hierarch"}'
#     add =  'edit'
    

#     # удаление элемента 1.2 с ИД = 3 (потомки 5, 6, 7)
#     session =  '{"sessioncontext":{"sid":"super","userdata":"default","phone":"123-56-78","username":"super","fullusername":"–Р–ї–µ–Ї—Б–µ–є –Т. –Т–∞—Б–Є–ї—М–µ–≤","email":"12@yandex.ru","login":"super","sessionid":"8B9B06F1B482A287CFF30FE2B0847F4A","related":{"gridContext":{"parentId":"WzNd","currentColumnId":"deweyCode","gridFilterInfo":"","additional":"","pageInfo":{"@size":"2147483646","@number":"1"},"liveInfo":{"@totalCount":"0","@pageNumber":"1","@offset":"0","@limit":"2147483646"},"partialUpdate":"false","currentDatapanelWidth":"1596","@id":"13","currentDatapanelHeight":"782","selectedRecordId":"WzNd","currentRecordId":"WzNd"}},"ip":"127.0.0.1"}}'
#     main =  '{"grain":"testsprav","table":"link_hierarch"}'
#     add =  'edit'
# 
#     # удаление элементов без потомков на разных уровнях: 1.1 с ИД = 2 и 1.2.2 с ИД = 6 -
#     session =  '{"sessioncontext":{"sid":"super","userdata":"default","phone":"123-56-78","username":"super","fullusername":"–Р–ї–µ–Ї—Б–µ–є –Т. –Т–∞—Б–Є–ї—М–µ–≤","email":"12@yandex.ru","login":"super","sessionid":"8B9B06F1B482A287CFF30FE2B0847F4A","related":{"gridContext":{"parentId":"WzNd","currentColumnId":"deweyCode","gridFilterInfo":"","additional":"","pageInfo":{"@size":"2147483646","@number":"1"},"liveInfo":{"@totalCount":"0","@pageNumber":"1","@offset":"0","@limit":"2147483646"},"partialUpdate":"false","currentDatapanelWidth":"1596","@id":"13","currentDatapanelHeight":"782","selectedRecordId":["WzJd","WzZd"],"currentRecordId":"WzZd"}},"ip":"127.0.0.1"}}'
#     main =  '{"grain":"testsprav","table":"link_hierarch"}'
#     add =  'edit'
#     
#     # удаление элементов без потомков на разных уровнях: 1 c ИД = 1, 1.1 с ИД = 2, 1.2.2 с ИД = 6, 1.3.1 с ИД = 8
    session =  '{"sessioncontext":{"sid":"super","userdata":"default","phone":"123-56-78","username":"super","fullusername":"–Р–ї–µ–Ї—Б–µ–є –Т. –Т–∞—Б–Є–ї—М–µ–≤","email":"12@yandex.ru","login":"super","sessionid":"8B9B06F1B482A287CFF30FE2B0847F4A","related":{"gridContext":{"parentId":"WzRd","currentColumnId":"deweyCode","gridFilterInfo":"","additional":"","pageInfo":{"@size":"2147483646","@number":"1"},"liveInfo":{"@totalCount":"0","@pageNumber":"1","@offset":"0","@limit":"2147483646"},"partialUpdate":"false","currentDatapanelWidth":"1596","@id":"13","currentDatapanelHeight":"782","selectedRecordId":["WzFd","WzZd","WzJd","Wzhd"],"currentRecordId":"Wzhd"}},"ip":"127.0.0.1"}}'
    main =  '{"grain":"testsprav","table":"link_hierarch"}'
    add =  'edit'

    cardDelDataSave(context, main, add, session=session)
    context.commit()