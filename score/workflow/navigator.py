# coding: utf-8
import simplejson as json
import os
from security.functions import userHasPermission
from workflow.processUtils import parse_json

def testNavigator(context, session):
    myNavigator = {"group":{"@id": "journals",
                            "@name": u"Тестовый пример",
                            "@icon": "journals.png",
                            "level1":[{"@id": "j1",
                                       "@name": u"Тест",
                                       "action":{"main_context": "current",
                                                 "datapanel":{"@type": "test.xml",
                                                              "@tab": "firstOrCurrent"}
                                                 }
                                       }]

                            }
                   }
    return myNavigator

def manageProcessesNav(context, session):

    session = json.loads(session)["sessioncontext"]
    if 'urlparams' in session and 'urlparam' in session['urlparams']:
        drawProcess = False
        startProcess = False
        documentTask = False
        drawTable = False
        if isinstance(session['urlparams']['urlparam'], list):
            for params in session['urlparams']['urlparam']:
                if params['@name'] == 'mode':
                    if params['@value'][0] == 'image':
                        drawProcess = True
                    elif params['@value'][0] == 'process':
                        startProcess = True
                    elif params['@value'][0] == 'task':
                        documentTask = True
                    elif params['@value'][0] == 'table':
                        drawTable = True
#                 if params['@name'] == 'procInstId':
#                     procInstId = params['@name'][1:-1]
        if drawProcess:
            myNavigator = {"group":
                           {"@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":
                                [{"@id": "drawProcesses",
                                  "@selectOnLoad": "true",
                                  "@name": u"Схема процесса",
                                  "action":
                                    {"main_context": "current",
                                     "datapanel":
                                        {"@type": "workflow.datapanel.processes.drawProcesses.celesta",
                                         "@tab": "schemaProcess"}
                                     }
                                  }]
                            }
                           }
            return myNavigator
        elif drawTable:
            myNavigator = {"group":
                           {"@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":
                                [{"@id": "drawTable",
                                  "@selectOnLoad": "true",
                                  "@name": u"Активные задачи",
                                  "action":
                                    {"main_context": "current",
                                     "datapanel":
                                        {"@type": "workflow.datapanel.tasks.drawTasksByProcId.celesta",
                                         "@tab": "firstOrCurrent"}}}]}}
            return myNavigator
        elif startProcess:
            filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datapanelSettings.json')
            datapanelSettings = parse_json(filePath)
            myNavigator = {
                               "group":{
                                        "@id": "workflow",
                                        "@name": u"Организация рабочего процесса",
                                        "@icon": "flowblock.png",
                                        "level1":[{
                                                  "@id": "startProcess",
                                                  "@selectOnLoad": "true",
                                                  "@name": u"Схема процесса",
                                                  "action":{"main_context": "current",
                                                             "datapanel":{"@type": datapanelSettings["startingProcess"],
                                                                          }
                                                             }
                                                  }]
                                        }
                               }
            return myNavigator
        elif documentTask:
            filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datapanelSettings.json')
            datapanelSettings = parse_json(filePath)
            myNavigator = {"group":
                           {"@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":
                                [{"@id": "startProcess",
                                  "@selectOnLoad": "true",
                                  "@name": u"Завершение задачи",
                                  "action":
                                    {"main_context": "current",
                                     "datapanel":{"@type": datapanelSettings["documentTask"]}}
                                  }]}}
            return myNavigator
    sid = session["sid"]
    # Пункт меню управление процессами
    myNavigator = {
                   "group":{
                            "@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":[{
                                      "@id": "w1",
                                      "@name": u"Управление процессами",
                                      "action":{"main_context": "current",
                                                 "datapanel":{"@type": "workflow.datapanel.processes.manageProcesses.celesta",
                                                              "@tab": "firstOrCurrent"}
                                                 }
                                      }]
                            }
                   }
    # Пункт меню редактирования процессов
    myNavigator["group"]["level1"].append({"@id": "editingProcesses",
                                          "@name": u"Редактирование процессов",
                                          "action":
                                            {"main_context": "current",
                                             "datapanel":
                                                {"@type": "workflow.datapanel.processes.editingProcesses.celesta",
                                                 "@tab": "firstOrCurrent"
                                                 }
                                             }
                                          })
    if userHasPermission(context, sid, 'activeTasks'):
        myNavigator["group"]["level1"].append({"@id": "activeTasks",
                                              "@name": u"Текущие задачи",
                                              "action":
                                                {"main_context": "current",
                                                 "datapanel":
                                                    {"@type": "workflow.datapanel.tasks.activeTasks.celesta",
                                                     "@tab": "firstOrCurrent"
                                                     }
                                                 }
                                              })

    if userHasPermission(context, sid, 'archiveTasks'):
        myNavigator["group"]["level1"].append({"@id": "archiveTasks",
                                              "@name": u"Выполненные задачи",
                                              "action":
                                                {"main_context": "current",
                                                 "datapanel":
                                                    {"@type": "workflow.datapanel.tasks.archiveTasks.celesta",
                                                     "@tab": "firstOrCurrent"
                                                     }
                                                 }
                                              })
    if userHasPermission(context, sid, 'allActiveTasks'):
        myNavigator["group"]["level1"].append({"@id": "allActiveTasks",
                                              "@name": u"Все задачи",
                                              "action":
                                                {"main_context": "current",
                                                 "datapanel":
                                                    {"@type": "workflow.datapanel.tasks.allActiveTasks.celesta",
                                                     "@tab": "firstOrCurrent"
                                                     }
                                                 }
                                              })
    return myNavigator

def navSettings(context, session):
    myNavigator = {
        "@width": "250px",
        "@hideOnLoad": "false"
    }
    session = json.loads(session)["sessioncontext"]
    if 'urlparams' in session and 'urlparam' in session['urlparams']:
        if isinstance(session['urlparams']['urlparam'], list):
            for params in session['urlparams']['urlparam']:
                if params['@name'] == 'mode':
                    if params['@value'][0] in ('image', 'process', 'task', 'table'):
                        myNavigator["@hideOnLoad"] = "true"
    return myNavigator
