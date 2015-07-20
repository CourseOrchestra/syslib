# coding: utf-8
'''
Created on 25.12.2014

@author: tr0glo)|(I╠╣
'''

import simplejson as json
from java.util import ArrayList

from common import hierarchy

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    pass

from ru.curs.celesta.showcase.utils import XMLJSONConverter

from common import hierarchy

from workflow._workflow_orm import matchingCircuitCursor

def cardData(context, main, add, filterinfo=None, session=None, elementId=None):

    xformsdata = {"schema":
                  {"@xmlns":"",
                   "info":
                    {"@parallelId": "",
                     "@parallelName": ""}}}
    xformssettings = {"properties":
                       {"event":
                        [{"@name": "single_click",
                         "@linkId": "1",
                         "action":
                          {"main_context": "current",
                           "datapanel":
                            {"@type": "current",
                             "@tab": "current",
                             "element":
                                [{"@id": "matchingCircuitGrid",
                                  "add_context": '',
                                  "@keep_user_settings": "true"},
                                  {"@id":'generateProcessImage'},
                                  {"@id":'generateProcessDefinition'}]}}}]}}
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitParent = matchingCircuitCursor(context)
    session = json.loads(session)["sessioncontext"]
    currentRec= json.loads(session['related']['gridContext']['currentRecordId'])
    processKey = currentRec["procKey"]
    id = currentRec["id"]
    matchingCircuit.get(processKey,id)
    matchingCircuit.setRange('processKey',processKey)
    parallelId = int(json.loads(xformsdata)["schema"]["info"]["@parallelId"])
    matchingCircuitParent.get(processKey,parallelId)
    hierarchy.shiftNodeToOtherLevelInHierarchy(context, matchingCircuit, 'number', 'sort', matchingCircuitParent.number)


def parallelListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Селектор пользователей, доступных для назначения на задачи. '''
    session = json.loads(session)["sessioncontext"]
    matchingCircuit = matchingCircuitCursor(context)
    currentRec= json.loads(session['related']['gridContext']['currentRecordId'])
    processKey = currentRec["procKey"]
    id = currentRec["id"]
    matchingCircuit.setRange('processKey',processKey)
    matchingCircuit.setRange('type','parallel')
    filterString = curvalue.replace("'", "''") + "'%"
    if not startswith:
        filterString = "@%'" + filterString
    else:
        filterString = "@'" + filterString
    recCount = matchingCircuit.count()
    matchingCircuit.setFilter('number',filterString)
    matchingCircuit.limit(firstrecord,recordcount)
    recordList = ArrayList()
    for matchingCircuit in matchingCircuit.iterate():
        rec = DataRecord()
        rec.setId(unicode(matchingCircuit.id))
        rec.setName(u'Параллельное согласование '+unicode(matchingCircuit.number))
        recordList.add(rec)
    return ResultSelectorData(recordList, recCount)