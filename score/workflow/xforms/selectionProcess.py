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

from workflow._workflow_orm import statusModelCursor,processStatusModelCursor, matchingCircuitCursor, processesCursor

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
                         "@modelId": "",
                         "@modelName": "",
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
    #processStatusModel = processStatusModelCursor(context)
    matchingCircuit = matchingCircuitCursor(context)
    isNew = True if data["schema"]["data"]["@newProcess"] == 'true' else False
    processKey = data["schema"]["data"]["@processKey"]
    processName = data["schema"]["data"]["@processName"]
    #modelId = data["schema"]["data"]["@modelId"]
    #processStatusModel.setRange('processKey',processKey)
    deleteFlag = True
#     if processStatusModel.count() == 0:
#         processStatusModel.processKey = processKey
#         processStatusModel.modelId = modelId
#         processStatusModel.insert()
#     else:
#         processStatusModel.first()
#         if processStatusModel.modelId == modelId:
#             deleteFlag = False
#         processStatusModel.modelId = modelId
#         processStatusModel.update()
#     if deleteFlag:
#         matchingCircuit.setRange('processKey',processKey)
#         for matchingCircuit in matchingCircuit.iterate():
#             matchingCircuit.statusId = None
#             matchingCircuit.modelId = None
#             matchingCircuit.update()
    if isNew:
        activiti = ActivitiObject()
        #Указанный ключ для нового процесса уже занят
        id = activiti.repositoryService.createProcessDefinitionQuery().processDefinitionKey(processKey).latestVersion().singleResult()
        processes = processesCursor(context)
        if processes.tryGet(processKey):
            return context.error(u'Процесс с таким ключом уже существует.')
        if id is not None:
            processes.processKey = processKey
            processes.processName = processName
            processes.insert()
            return context.message(u'Процесс с таким ключом развёрнут. При редактировании процесса описание процесса будет сформировано по схеме согласования, а старое описание процесса будет удалено.')        
        processes.processKey = processKey
        processes.processName = processName
        processes.insert()

def processListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Селектор развернутых процессов. '''
    processes = processesCursor(context)
    #Получение списка развернутых процессов
    recordList = ArrayList()
    processes.limit(firstrecord,recordcount)
    filterString = curvalue.replace("'", "''") + "'%"
    if not startswith:
        filterString = "@%'" + filterString
    else:
        filterString = "@'" + filterString
    processes.setFilter('processName', filterString)
    for process in processes.iterate():
        rec = DataRecord()
        rec.setId(process.processKey)
        rec.setName(process.processName)
        rec.addParameter('existing', 'true')
        recordList.add(rec)
    return ResultSelectorData(recordList, processes.count())


def modelListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Селектор статусных моделей. '''
    statusModel = statusModelCursor(context)
    filterString = curvalue.replace("'", "''") + "'%"
    if not startswith:
        filterString = "@%'" + filterString
    else:
        filterString = "@'" + filterString
    recCount = statusModel.count()
    statusModel.setFilter('name',filterString)
    statusModel.limit(firstrecord,recordcount)
    recordList = ArrayList()
    for statusModel in statusModel.iterate():
        rec = DataRecord()
        rec.setId(statusModel.id)
        rec.setName(statusModel.name)
        recordList.add(rec)
    return ResultSelectorData(recordList, recCount)
