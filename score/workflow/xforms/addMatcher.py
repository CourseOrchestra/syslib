# coding: utf-8
'''
Created on 10.11.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json
import urlparse
import cgi

from common.hierarchy import generateSortValue,getNewItemInLevelInHierarchy

from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

import datetime

from common.numbersseries import getNextNo

from workflow.processUtils import ActivitiObject
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord
    
try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory
    
from workflow._workflow_orm import matchingCircuitCursor 
    
from java.io import InputStream, FileInputStream
from jarray import zeros

#from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка добавления и редактирования элементов в грид согласователей процесаа'''
    session = json.loads(session)
    add = json.loads(add)
    addContext = add[0]
    processKey = add[1]
    matchingCircuit = matchingCircuitCursor(context)
    if 'currentRecordId' in session["sessioncontext"]["related"]["gridContext"]:
        currentId = json.loads(session["sessioncontext"]["related"]["gridContext"]["currentRecordId"])
        id = currentId['id']
        matchingCircuit.get(processKey,id)
        name = matchingCircuit.sid
        if addContext == 'add':
            parentId = id
            parentName = name
            parallelAlignment = 'true'
            id = ''
            name = ''
        else:
            parentId = ''
            parentName = ''
            parallelAlignment = 'false'
    else:
        parallelAlignment = 'false'
        processKey
        id = ''
        name = ''
        parentId = ''
        parentName = 'Элемент верхнего уровня'
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{
                                "@id":id,
                                "@name":name,
                                "@parentName": parentName,
                                "@parentId" : parentId,
                                "@processKey" : processKey,
                                "@parallel": parallelAlignment,
                                "@isParallel": 'false',
                                "@add":addContext},                            
                        }
              }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":[
                                                                                {"@id":'matchingCircuitGrid'},
                                                                                ]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)
                 


def cardSave(context, main, add, filterinfo, session, elementId, data):
    u'''Сохранение согласователя'''
    #raise Exception(data)
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    data_dict = json.loads(data)
    processKey = data_dict["schema"]["data"]["@processKey"]
    parentId = data_dict["schema"]["data"]["@parentId"]
    sid = data_dict["schema"]["data"]["@name"]
    id = data_dict["schema"]["data"]["@id"]
    type = data_dict["schema"]["data"]["@add"]
    isParallel = data_dict["schema"]["data"]["@isParallel"]
    if type == 'edit':
        id = int(id)
        matchingCircuit.get(processKey,id)
        matchingCircuit.sid = sid
        matchingCircuit.update()
        return context.message(u'Элемент изменён')
    else:
        if parentId == '':
            numbersSerie = numbersSeriesCursor(context)
            linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
            if numbersSerie.tryGet(processKey):
                pass
            else:
                numbersSerie.id = processKey
                numbersSerie.description = u'Серия для задач процесса %s' % (processKey)
                numbersSerie.insert()
                linesOfNumbersSeries.seriesId = numbersSerie.id
                linesOfNumbersSeries.numberOfLine = 1
                linesOfNumbersSeries.startingDate = datetime.datetime.now()
                linesOfNumbersSeries.startingNumber = 1
                linesOfNumbersSeries.endingNumber = 100000
                linesOfNumbersSeries.incrimentByNumber = 1
                linesOfNumbersSeries.lastUsedNumber = 0
                linesOfNumbersSeries.isOpened = True
                linesOfNumbersSeries.lastUsedDate = datetime.datetime.now()
                linesOfNumbersSeries.prefix = ''
                linesOfNumbersSeries.postfix = ''
                linesOfNumbersSeries.isFixedLength = False
                linesOfNumbersSeries.insert()
            matchingCircuit.processKey = processKey
            matchingCircuit.id = getNextNo.getNextNoOfSeries(context,processKey)
            matchingCircuit.sid = sid
            if isParallel == 'true':
                matchingCircuit.type = 'parallel'
            else:
                matchingCircuit.type = 'user'
            matchingCircuitClone.setRange('processKey',processKey)
            matchingCircuitClone.setFilter('number',"!%'.'%")
            matchingCircuit.number = matchingCircuitClone.count() + 1
            matchingCircuit.insert()	
        else:
            parentId = int(parentId)
            matchingCircuit.setRange('processKey',processKey)
            matchingCircuit.get(processKey,parentId)
            number = getNewItemInLevelInHierarchy(context, matchingCircuit, 'number')
            matchingCircuit.processKey = processKey
            matchingCircuit.id = getNextNo.getNextNoOfSeries(context,processKey)
            matchingCircuit.sid = sid
            matchingCircuit.type = 'user'
            matchingCircuit.number = number
            matchingCircuit.insert()
            
            
def matchingCircuitPreInsert(rec):
    rec.sort = generateSortValue(unicode(rec.number))            