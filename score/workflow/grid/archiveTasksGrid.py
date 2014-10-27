# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus
'''

import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from workflow._workflow_orm import formCursor
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    activiti = ActivitiObject()
    historyService = activiti.historyService
    tasksList = historyService.createHistoricTaskInstanceQuery().taskAssignee(sid).finished().list()
    variables = historyService.createHistoricVariableInstanceQuery()
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
#                "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "link": [u"Заявка"],
               "properties":[u"properties"]}


    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    runtimeService = activiti.runtimeService

    for tasks in tasksList:
        procDict = {}
        procDict[_header["id"][1]] = tasks.id
        processInstanceId = tasks.getProcessInstanceId()
        processInstance = activiti.runtimeService.createProcessInstanceQuery()\
            .processInstanceId(processInstanceId).singleResult()
        processDefinition = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(processInstance.getProcessDefinitionId()).singleResult()
        docName = ''
        docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
                              runtimeService.getVariable(processInstanceId, 'docName'))
        procDict[_header["process"][1]] = "%s: %s" % (processDefinition.getName(), docName)
#         procDict[_header["schema"][1]] = {"div":
#                                            {"@align": "center",
#                                             "img":
#                                             {"@src": "solutions/default/resources/flowblock.png", "@height": "20px"}}}
        procDict[_header["name"][1]] = tasks.name
        requestReference = runtimeService.getVariable(processInstanceId, 'requestReference')
        procDict[_header["link"][1]] = {"div":
                                             {"@align": "center",
                                              "a":{"@href": requestReference,
                                                   "@target": "_blank",
                                                   "img":
                                                        {"@src": "solutions/default/resources/imagesingrid/link.png",
                                                         "@height": "20px"}}}}

#         procDict[_header["properties"][1]] = {"event":
#                                               {"@name":"cell_single_click",
#                                                "@column": _header["schema"][0],
#                                                "action":
#                                                     {"@show_in": "MODAL_WINDOW",
#                                                      "#sorted":
#                                                         [{"main_context":"current"},
#                                                          {"modalwindow":
#                                                             {"@caption": "Схема процесса"
#                                                              }
#                                                           },
#                                                          {"datapanel":
#                                                             {"@type": "current",
#                                                              "@tab": "current",
#                                                              "element":
#                                                                 {"@id": "tasksImage"
#                                                                  }
#                                                              }
#                                                           }
#                                                          ]
#                                                      }
#                                                }
#                                               }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1000px",
                                               "@gridHeight": "500",
                                               "@totalCount": len(tasksList),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0], "@width": "40px", "type": "IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "280px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0], "@width": "650px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["link"][0],
                                                       "@width": "40px",
                                                       "type": "IMAGE"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

# def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
#     u'''Toolbar для грида. '''
#
#     if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
#         style = "true"
#     else:
#         style = "false"
#
#     data = {"gridtoolbar":{"item":[]}}
#
# #     sAction = json.loads(form.sAction) if form.sAction is not None else None
#     sAction = {"@show_in": "MODAL_WINDOW",
#                           "#sorted":[{"main_context":"current"},
#                                      {"modalwindow":{"@caption": "Изменение статуса",
#                                                      "@height": "300",
#                                                      "@width": "500"}
#                                       },
#                                      {"datapanel":{"@type": "current",
#                                                    "@tab": "current",
#                                                    "element": {"@id": "taskStatusCard"}
#                                                    }
#                                       }]
#                           }
#
#
#     data["gridtoolbar"]["item"].append({"@text":"Выполнить",
#                                         "@hint":"Выполнить задачу",
#                                         "@disable": style,
#                                         "action": sAction})
#
#     return XMLJSONConverter.jsonToXml(json.dumps(data))
