# coding: utf-8
'''
Created on 02.10.2014

@author: A.Vasilyev.
'''


import simplejson as json

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

# from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка стандартного запуска процесса'''
    if add != "added":
        xformsdata = {"schema":{"@xmlns":'',
                                "data":{"@type":'hide'},
                                }
                      }
    else:
        xformsdata = {"schema":{"@xmlns":'',
                                "data":{"@type":'add'},
                                }
                      }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":{"@id":'standardStartProcess',
                                                                                "add_context":"added"}
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)



def cardSave(context, main, add, filterinfo, session, elementId, data):
    u'''Запуск процесса'''
    session = json.loads(session)['sessioncontext']
    if isinstance(session['urlparams']['urlparam'], list):
        for params in session['urlparams']['urlparam']:
            if params['@name'] == 'processKey':
                processKey = params['@value'][0]
    activiti = ActivitiObject()
    process = activiti.repositoryService.createProcessDefinitionQuery().processDefinitionKey(processKey).latestVersion().singleResult()
    variables = {"processDescription":process.name,
                 "initiator":'admin',
                 "dean":'admin',
                 "lawyer":'admin',
                 "service":'admin',
                 "final":'admin'}
    # vars = {"initiator":'cock',"troll":'stock'}
    activiti.runtimeService.startProcessInstanceByKey(processKey, variables)
    return context.message(u'Процесс запущен')
