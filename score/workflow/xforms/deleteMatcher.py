# coding: utf-8
'''
Created on 10.11.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json
import urlparse
import cgi

from common.hierarchy import deleteNodeFromHierarchy

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
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{
                                "@id":id,
                                "@processKey" : processKey,
                                }                            
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
    data_dict = json.loads(data)
    processKey = data_dict["schema"]["data"]["@processKey"]
    id = int(data_dict["schema"]["data"]["@id"])
    matchingCircuit.setRange('processKey',processKey)
    matchingCircuit.get(processKey,id)
    deleteNodeFromHierarchy(context,matchingCircuit,'number','sort')
    return context.message(u'Элемент удалён')
            
          