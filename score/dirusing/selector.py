# coding=UTF-8


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from ru.curs.showcase.core.selector import ResultSelectorData
from ru.curs.showcase.core.jython import DataSelectorAttributes
from ru.beta2.extra.gwt.ui.selector.api import DataRecord
from java.util import ArrayList 
try:
    from ru.curs.showcase.core import UserMessage
except:
    pass
import simplejson as json
import base64
from xml.dom import minidom
from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders

def selector(context, main=None, add=None,  filterinfo=None, session=None, params=None, curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
   
    dom = minidom.parseString(params)
    for elem in dom.getElementsByTagName('dbFieldName'):
        for child in elem.childNodes:
            dbFieldName = child.nodeValue.strip()
    
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    column_jsn = json.loads(currentTable.meta().getColumn(dbFieldName).getCelestaDoc())
    refTableName = column_jsn["refTable"]
    refTableColumn = column_jsn["refTableColumn"]
    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
    records = dict()
    recordList = ArrayList()
    recordcount=relatedTable.count() if (relatedTable.count()>0) else 0
    firstrecord=0
    relatedTable.limit(firstrecord, recordcount)
    relatedTable.setFilter(refTableColumn, """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    relatedTable.orderBy(refTableColumn)
    for rec in relatedTable.iterate():
        keys = relatedTable.meta().getPrimaryKey()
        for item in keys:
            key = item
            
        refTableColumnId = getattr(rec, key)
        refTableColumnValue = getattr(rec, refTableColumn)
        print refTableColumnId, refTableColumnValue
        records[rec] = DataRecord()
        if str(refTableColumnId):
            refTableColumnId = str(refTableColumnId)
        records[rec].setId(refTableColumnId)
        records[rec].setName(refTableColumnValue)
        recordList.add(records[rec])
        
    
    records=recordList
  
    count=relatedTable.count()
    return ResultSelectorData(records, count)

def multiSelector(context, main=None, add=None,  filterinfo=None, session=None, params=None, curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    dom = minidom.parseString(params)
    for elem in dom.getElementsByTagName('dbFieldName'):
        for child in elem.childNodes:
            dbFieldName = child.nodeValue.strip()
    
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    
    column_jsn = json.loads(currentTable.meta().getColumn(dbFieldName).getCelestaDoc())
    refTableName = column_jsn["refTable"]
    records = dict()
    recordList = ArrayList()
    
    refTableColumn = column_jsn["refTableColumn"]
    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
    
    relatedTablePKs = relatedTable.meta().getPrimaryKey()
    
    recordcount=relatedTable.count() if (relatedTable.count()>0) else 0
    firstrecord=0
    relatedTable.limit(firstrecord, recordcount)
    relatedTable.setFilter(refTableColumn, """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    relatedTable.orderBy(refTableColumn)
    
    for rec in relatedTable.iterate():
        relatedTablePKValues = []
        for pkValue in relatedTablePKs:
            relatedTablePKValues.extend([getattr(relatedTable, pkValue)])
           
        
        jsondump = json.dumps(relatedTablePKValues)
        
        currentRecordCoded=base64.b64encode(str(jsondump))
        
        #currentRecordDecoded = base64.b64decode(currentRecordCoded)
       
        refTableColumnValue = getattr(relatedTable, refTableColumn)
        records[rec] = DataRecord()
        records[rec].setId(currentRecordCoded)
        
        records[rec].setName(refTableColumnValue)
        
        recordList.add(records[rec])
    records=recordList
    
    count=relatedTable.count()
    
    return ResultSelectorData(records, count)
    
    
