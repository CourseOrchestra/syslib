# coding: utf-8
import simplejson as json
import os
from security.functions import userHasPermission

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
    if 'urlparams' in session:
        drawProcess = False
        startProcess = False
        if isinstance(session['urlparams']['urlparam'],list):
            for params in session['urlparams']['urlparam']:
                if params['@name'] == 'mode':
                    if params['@value'] == '[image]':
                        drawProcess = True
                    elif params['@value'] == '[process]':
                        startProcess = True
#                 if params['@name'] == 'procInstId':
#                     procInstId = params['@name'][1:-1]
        if drawProcess:
            myNavigator = {
                               "group":{
                                        "@id": "workflow",
                                        "@name": u"Организация рабочего процесса",
                                        "@icon": "flowblock.png",
                                        "level1":[{
                                                  "@id": "drawProcesses",
                                                  "@selectOnLoad": "true",
                                                  "@name": u"Схема процесса",
                                                  "action":{"main_context": "current",
                                                             "datapanel":{"@type": "workflow.datapanel.processes.drawProcesses.celesta",
                                                                          "@tab": "schemaProcess"}
                                                             }
                                                  }]
                                        }
                               }
            return myNavigator
        if startProcess:
            filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datapanelSettings.json')
            f = open(filePath, 'r')
            datapanelSettings = json.loads(f.read())
            f.close()
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
    sid = session["sid"]
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
    if userHasPermission(context, sid, 'activeTasks'):
        myNavigator["group"]["level1"].append({"@id": "activeTasks",
                                              "@name": u"Текущие задачи",
                                              "action":
                                                {"main_context": "current",
                                                 "datapanel":
                                                    {"@type": "workflow.datapanel.activeTasks.activeTasks.celesta",
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
                                                    {"@type": "workflow.datapanel.archiveTasks.archiveTasks.celesta",
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
                                                    {"@type": "workflow.datapanel.allActiveTasks.allActiveTasks.celesta",
                                                     "@tab": "firstOrCurrent"
                                                     }
                                                 }
                                              })
    if userHasPermission(context, sid, 'operLog'):
        myNavigator["group"]["level1"].append({"@id": "operLog",
                                              "@name": u"Лог операций",
                                              "action":
                                                {"main_context": "current",
                                                 "datapanel":
                                                    {"@type": "workflow.datapanel.operLog.operLog.celesta",
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
    if 'urlparams' in session:
        if isinstance(session['urlparams']['urlparam'],list):
            for params in session['urlparams']['urlparam']:
                if params['@name'] == 'mode':
                    if params['@value'] == '[image]' or params['@value'] == '[process]' or params['@value'] == '[task]':
                        myNavigator["@hideOnLoad"] = "true"
    return myNavigator
