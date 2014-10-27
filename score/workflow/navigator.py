# coding: utf-8
import simplejson as json
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
                                              "@name": u"Мои задачи",
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
                                              "@name": u"Завершенные задачи",
                                              "action":
                                                {"main_context": "current",
                                                 "datapanel":
                                                    {"@type": "workflow.datapanel.archiveTasks.archiveTasks.celesta",
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
    return myNavigator
