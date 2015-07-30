# coding: utf-8
'''

@author: a.rudenko

'''
import simplejson as json
import base64

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
    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())


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

    if type(selectedRecordsCoded) is list:
        for selectedRecordCoded in selectedRecordsCoded:
            #print selectedRecordCoded
            #print "2"
            if isHierarchical == 'true':
                selectedRecordId = json.loads(base64.b64decode(selectedRecordCoded))
                currentTable.get(*selectedRecordId)
                deleteNodeFromHierarchy(context, currentTable, deweyColumn, sortColumn)
            else:
                selectedRecordId = json.loads(base64.b64decode(selectedRecordCoded))
                currentTable.get(*selectedRecordId)
                currentTable.delete()
    else:
        #print "1"
        if isHierarchical == 'true':
            selectedRecordId = json.loads(base64.b64decode(selectedRecordsCoded))
            currentTable.get(*selectedRecordId)
            deleteNodeFromHierarchy(context, currentTable, deweyColumn, sortColumn)
        else:
            selectedRecordId = json.loads(base64.b64decode(selectedRecordsCoded))
            currentTable.get(*selectedRecordId)
            currentTable.delete()

def cardDelAllDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    currentTable.deleteAll()
