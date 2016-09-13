# coding: utf-8
'''
Created on 07.11.2014

@author: tr0glo)|(I╠╣
'''

import json

from java.util import ArrayList

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord

from workflow.processUtils import ActivitiObject

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory

from java.io import ByteArrayInputStream

from workflow._workflow_orm import matchingCircuitCursor

from workflow.webtext.generateProcessImage import getProcessXML

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    pass

from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка разворачивания процесса по сгенерированному конструктором процессов описанию'''
    session = json.loads(session)
    processKey = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processKey']
    processName = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processName']
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    matchingCircuit.setRange('processKey',processKey)
    #Проверка, того что в параллельных согласованиях больше двух элементов и подсчёт максимального количества параллельных задач
    allowed = 'false'
    maxParallelTasks = ''
    if matchingCircuit.count() == 0:
        pass
    else:
        
        matchingCircuitClone.setRange('processKey',processKey)
        matchingCircuit.setRange('type','parallel')
        parallelFlag = True
        taskFlag = True
        maxParallelTasks = 1
        #Проверка на то, что в каждом параллельном согласовании не менее двух задач
        for matchingCircuit in matchingCircuit.iterate():
            matchingCircuitClone.setFilter('number',"'%s.'%%" % matchingCircuit.number)
            if matchingCircuitClone.count() < 2:
                parallelFlag = False
            if matchingCircuitClone.count() > maxParallelTasks:
                maxParallelTasks = matchingCircuitClone.count()
        if parallelFlag and taskFlag:
            allowed = 'true'
    
    
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "data":
                        {
                            "@allowed":allowed,
                            "@maxTasks":maxParallelTasks
                         }
                     }
                  }
    xformssettings = {"properties":
                        {"event":
                         [{"@name": "single_click",
                           "@linkId": "1",
                           "action":
                                {"#sorted":[{"main_context": "current"},
                                             {"datapanel":
                                                {"@type": "current",
                                                 "@tab": "current",
                                                 "element":
                                                 [
                                                    {"@id": 'matchingCircuitGrid',
                                                     "add_context": 'current'
                                                     },
                                                  {"@id": 'generateProcessDefinition',
                                                     "add_context": 'current'
                                                     }
                                                 ]
                                                 }
                                             }]}
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardSave(context, main, add, filterinfo, session, elementId, data):
    u'''Запуск процесса'''
    session = json.loads(session)
    data = json.loads(data)
    maxTasks = data["schema"]["data"]["@maxTasks"]
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    processKey = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processKey']
    processName = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processName']
    matchingCircuit.setRange('processKey',processKey)
    matchingCircuit.setRange('processKey',processKey)
    matchingCircuit.setFilter('number',"!%'.'%")
    matchingCircuit.orderBy('sort')
    matchingCircuitClone.setRange('processKey',processKey)
    #Генерация описания процесса
    stream = ByteArrayInputStream(getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName, int(maxTasks)).encode('utf-8'))
    #Разворачивание процесса
    processEngine = EngineFactory.getActivitiProcessEngine()
    repositoryService = processEngine.getRepositoryService()
    repositoryService.createDeployment().addInputStream(processName+'.bpmn', stream).deploy()
    return context.message(u'Процесс развёрнут')
    


