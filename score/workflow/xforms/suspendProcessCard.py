# coding: utf-8
'''
Created on 02.10.2014

@author: A.Vasilyev.
'''


import json

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

from java.io import InputStream, FileInputStream
from jarray import zeros

from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка отсановки процесса'''
    xformsdata = {"schema":{"@xmlns":'',
                            "data":{"@reason":''},
                            }
                  }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"#sorted":[{"main_context": "current"},
                                                                    {"datapanel":{"@type": "current",
                                                                                 "@tab": "current",
                                                                                 "element":{"@id": "launchedProcessesGrid",
                                                                                            "add_context": 'current'}
                                                                                 }
                                                                    }]}
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)



def cardSave(context, main, add, filterinfo, session, elementId, data):
    u'''Остановка процесса'''
    data_dict = json.loads(data)
    reason = data_dict["schema"]["data"]["@reason"]
    procId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    activiti = ActivitiObject()
    activiti.stopProcess(procId, reason)
