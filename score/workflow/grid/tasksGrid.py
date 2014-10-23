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

try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory


def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    activiti = ActivitiObject()
    tasksList = activiti.getUserAssTasks(sid)

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
               "ID":["ID"],
               "name":[u"Название задачи"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    processEngine = EngineFactory.getActivitiProcessEngine()
    taskService = processEngine.getTaskService();
    for tasks in tasksList:
        procDict = {}
        procDict[_header["id"][1]] = tasks.id
        task = taskService.createTaskQuery().taskId(tasks.id).singleResult()
#         process = task.getProcessInstanceId()
#         procDict[_header["process"][1]] = tasks.id
        procDict[_header["name"][1]] = tasks.name
        procDict[_header["properties"][1]] = {"event":{"@name":"row_single_click",
                                         "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Схема процесса"
                                                                             }
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "tasksImage"}
                                                                           }
                                                              }
                                                             ]
                                                  }
                                         }
                                }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1200px",
                                               "@gridHeight": "300",
                                               "@totalCount": len(tasksList),
                                               "@profile":"default.properties"},
                                "labels":{"header":"Список задач пользователя"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[]}}
    form = formCursor(context)
    form.get(1)

#     sAction = json.loads(form.sAction) if form.sAction is not None else None
    sAction = {"@show_in": "MODAL_WINDOW",
                          "#sorted":[{"main_context":"current"},
                                     {"modalwindow":{"@caption": "Изменение статуса",
                                                     "@height": "300",
                                                     "@width": "500"}
                                      },
                                     {"datapanel":{"@type": "current",
                                                   "@tab": "current",
                                                   "element": {"@id": "taskStatusCard"}
                                                   }
                                      }]
                          }


    data["gridtoolbar"]["item"].append({"@text":"Выполнить",
                                        "@hint":"Выполнить задачу",
                                        "@disable": style,
                                        "action": sAction})

    return XMLJSONConverter.jsonToXml(json.dumps(data))
