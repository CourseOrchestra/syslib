# coding: utf-8
'''
Created on 07.11.2014

@author: tr0glo)|(I╠╣
'''

import simplejson as json

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
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    pass

from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка выбора процесса'''

    xformsdata = {"schema":
                    {"@xmlns":"",
                     "data":
                        {
                         "@newProcess":"false",
                         "@processName": "",
                         "@processKey": "",
                         "@existing": "false"
                         }
                     }
                  }
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
                                     [
                                        {"@id": 'matchingCircuitGrid',
                                         "add_context": 'current'
                                         },
                                      {"@id": 'generateProcessDefinition',
                                         "add_context": 'current'
                                         },
                                      {"@id": 'generateProcessImage',
                                       "add_context":'current'}
                                     ]
                                     }
                                 }
                           },
                          {"@name": "single_click",
                           "@linkId": "2",
                           "action":
                                {"main_context": "current",
                                 "datapanel":
                                    {"@type": "current",
                                     "@tab": "current",
                                     "element":
                                     [
                                        {"@id": 'matchingCircuitGrid',
                                         "add_context": "hide"
                                         },
                                      {"@id": 'generateProcessDefinition',
                                         "add_context": "hide"
                                         },
                                      {"@id": 'generateProcessImage',
                                       "add_context":'hide'}
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
    u'''Действия после нажатия на кнопку 'Редактировать' или 'Создать процесс' в конструкторе процессов'''
    session = json.loads(session)
    data = json.loads(data)
    isNew = True if data["schema"]["data"]["@newProcess"] == 'true' else False
    processKey = data["schema"]["data"]["@processKey"]
    processName = data["schema"]["data"]["@processName"]
    if isNew:
        activiti = ActivitiObject()
        #Указанный ключ для нового процесса уже занят
        id = activiti.repositoryService.createProcessDefinitionQuery().processDefinitionKey(processKey).latestVersion().singleResult()
        if id is not None:
            return context.error(u'Процесс с таким ключом уже существует')

def processListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Функция count селектора исследований. '''
    activiti = ActivitiObject()
    #Получение списка развернутых процессов
    processesList = activiti.getActualVersionOfProcesses()
    recordList = ArrayList()
    for process in processesList[firstrecord:firstrecord+recordcount]:
        rec = DataRecord()
        rec.setId(process.key)
        rec.setName(process.name)
        rec.addParameter('existing', 'true')
        recordList.add(rec)
    return ResultSelectorData(recordList, len(processesList))

