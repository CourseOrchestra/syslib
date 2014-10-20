# coding=UTF-8
'''
Created on 12.08.2014

@author: Rudenko
'''

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
import datetime

def groupSelector(context, main=None, add=None,  filterinfo=None, session=None, params=None, atr1=None, atr2=None, atr3=None, atr4=None):
    currentTable = relatedTableCursorImport('acrsprav', 'contrags')(context)
    relatedTable = relatedTableCursorImport('acrsprav', 'group_type')(context)
    records = dict()
    recordList = ArrayList()
    currentTable.setRange('org_type','1')
    for rec in currentTable.iterate():
        records[rec] = DataRecord()
        records[rec].setId(str(getattr(rec, 'id')))
        records[rec].setName(unicode(str(getattr(rec, 'name'))))
        
        refFieldId = getattr(rec, 'group_type')
        if refFieldId is not None and refFieldId!='':
            relatedTable.get(refFieldId)
            print str(getattr(relatedTable, 'name'))
            records[rec].addParameter('group_type', unicode(str(getattr(relatedTable, 'name'))))
        recordList.add(records[rec])
    records=recordList
    count=relatedTable.count()
    return ResultSelectorData(records, count)

def groupContragMultiSelector(context, main=None, add=None,  filterinfo=None, session=None, params=None, atr1=None, atr2=None, atr3=None, atr4=None):
    dom = minidom.parseString(params)
    for elem in dom.getElementsByTagName('id'):
        for child in elem.childNodes:
            groupId = child.nodeValue.strip()
    contrags = relatedTableCursorImport("acrsprav", "contrags")(context)
    group_orgs = relatedTableCursorImport("acrsprav", "group_orgs")(context)
    group_orgs.setFilter("gr_id", "'"+str(groupId)+"'")
    
    filterStr=''
    for rec in group_orgs.iterate():
        print getattr(rec, 'org_id')
        filterStr += '!'+str(getattr(rec, 'org_id'))+'&'
    filterStr +='!'+str(groupId)
    contrags.setFilter("id", filterStr)
    records = dict()
    recordList = ArrayList()
    
    for rec in contrags.iterate():
        print getattr(rec, 'id')
        records[rec] = DataRecord()
        records[rec].setId(str(getattr(rec, 'id')))
        records[rec].setName(unicode(str(getattr(rec, 'name'))))
        records[rec].addParameter('startdate', str(datetime.datetime.now().date()))
        recordList.add(records[rec])
    records=recordList
    
    count=contrags.count()
    
    return ResultSelectorData(records, count)
    
    
