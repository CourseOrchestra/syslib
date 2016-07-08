# coding: utf-8
import simplejson as json
import os
from security.functions import userHasPermission
try:
    from workflow.processUtils import  ActivitiObject, getLinkPermisson, parse_json
except:
    print "Activiti not initialized"
from workflow._workflow_orm import formCursor


def testNavigator(context, session):
    myNavigator = {"group":{"@id": "journals",
                            "@name": u"Тестовый пример",
                            "@icon": "journals.png",
                            "level1":[{"@id": "j1",
                                       "@name": u"Тест",
                                       "action":{"#sorted":[{"main_context": "current"},
                                                             {"datapanel":{"@type": "test.xml",
                                                                          "@tab": "firstOrCurrent"}
                                                             }]}
                                       }]

                            }
                   }
    return myNavigator

def manageProcessesNav(context, session):
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    if 'urlparams' in session and 'urlparam' in session['urlparams']:
        drawProcess = False
        startProcess = False
        documentTask = False
        drawTable = False
        processKey = None
        processId = None
        taskId = None
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
                if params['@name'] == 'processKey':
                    processKey = params['@value'][0]
                if params['@name'] == 'processId':
                    processId = params['@value'][0]
                if params['@name'] == 'taskId':
                    taskId = params['@value'][0]
#                 if params['@name'] == 'procInstId':
#                     procInstId = params['@name'][1:-1]
        if drawProcess:
            if processId is not None:
                if not getLinkPermisson(context, sid, 'instanceImage', processKey, processId, taskId):
                    return context.message(u'У вас нет разрешения на просмотр данной страницы')
            if processKey is not None:
                if not getLinkPermisson(context, sid, 'processImage', processKey, processId, taskId):
                    return context.message(u'У вас нет разрешения на просмотр данной страницы')                
            myNavigator = {"group":
                           {"@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":
                                [{"@id": "drawProcesses",
                                  "@selectOnLoad": "true",
                                  "@name": u"Схема процесса",
                                  "action":
                                    {"#sorted":[{"main_context": "current"},
                                                 {"datapanel":
                                                    {"@type": "workflow.datapanel.processes.drawProcesses.celesta",
                                                     "@tab": "schemaProcess"}
                                                 }]}
                                  }]
                            }
                           }
            return myNavigator
        elif drawTable:
            if not getLinkPermisson(context, sid, 'table', processKey, processId, taskId):
                return context.message(u'У вас нет разрешения на просмотр данной страницы')             
            myNavigator = {"group":
                           {"@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":
                                [{"@id": "drawTable",
                                  "@selectOnLoad": "true",
                                  "@name": u"Активные задачи",
                                  "action":
                                    {"#sorted":[{"main_context": "current"},
                                                 {"datapanel":
                                                    {"@type": "workflow.datapanel.tasks.drawTasksByProcId.celesta",
                                                     "@tab": "firstOrCurrent"}}]}}]}}
            return myNavigator
        elif documentTask or startProcess:
            if startProcess:
                if not getLinkPermisson(context, sid, 'process', processKey, processId, taskId):
                    return context.message(u'У вас нет разрешения на просмотр данной страницы')
            if documentTask:
                if not getLinkPermisson(context, sid, 'task', processKey, processId, taskId):
                    return context.message(u'У вас нет разрешения на просмотр данной страницы')                       
            formType = 'startingProcess' if startProcess else 'documentTask'
            myNavigator = {"group":
                           {"@id": "workflow",
                            "@name": u"Организация рабочего процесса",
                            "@icon": "flowblock.png",
                            "level1":
                                [{"@id": "startProcess",
                                  "@selectOnLoad": "true",
                                  "@name": u"Схема процесса",
                                  "action":
                                    {"#sorted":[{"main_context": "current"},
                                                 {"datapanel":
                                                    {"@type": datapanelSetup(context, formType, session)}}]}}]}}
            return myNavigator
#         elif documentTask:
#             filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datapanelSettings.json')
#             datapanelSettings = parse_json(filePath)
#             myNavigator = {"group":
#                            {"@id": "workflow",
#                             "@name": u"Организация рабочего процесса",
#                             "@icon": "flowblock.png",
#                             "level1":
#                                 [{"@id": "startProcess",
#                                   "@selectOnLoad": "true",
#                                   "@name": u"Завершение задачи",
#                                   "action":
#                                     {"main_context": "current",
#                                      "datapanel":{"@type": datapanelSettings["documentTask"]}}
#                                   }]}}
            return myNavigator
    sid = session["sid"]
    # Пункт меню управление процессами
    emptyNavigatorFlag = True
    myNavigator = {
                       "group":{
                                "@id": "workflow",
                                "@name": u"Организация рабочего процесса",
                                "@icon": "flowblock.png",
                                "level1":[
                                          ]
                                }
                       }
    if userHasPermission(context, sid, 'processManagement'):
        emptyNavigatorFlag = False
        myNavigator["group"]["level1"].append({
                                          "@id": "w1",
                                          "@name": u"Управление процессами",
                                          "action":{"#sorted":[{"main_context": "current"},
                                                                 {"datapanel":{"@type": "workflow.datapanel.processes.manageProcesses.celesta",
                                                                              "@tab": "firstOrCurrent"}
                                                                 }]}
                                          })
    # Пункт меню редактирования процессов
    if userHasPermission(context, sid, 'processDesigner'):
        emptyNavigatorFlag = False
        myNavigator["group"]["level1"].append({"@id": "editingProcesses",
                                              "@name": u"Конструктор процессов",
                                              "action":
                                                {"#sorted":[{"main_context": "current"},
                                                             {"datapanel":
                                                                {"@type": "workflow.datapanel.processes.editingProcesses.celesta",
                                                                 "@tab": "firstOrCurrent"
                                                                 }
                                                             }]}
                                              })
    if userHasPermission(context,sid,'userGroups'):
        emptyNavigatorFlag = False
        myNavigator["group"]["level1"].append({
                                          "@id": "userGroups",
                                          "@name": u"Группы пользователей",
                                          "action":{"#sorted":[{"main_context": "current"},
                                                                 {"datapanel":{"@type": "workflow.datapanel.processes.userGroups.celesta",
                                                                              "@tab": "firstOrCurrent"}
                                                                 }]}
                                          })
    if userHasPermission(context, sid, 'activeTasks'):
        emptyNavigatorFlag = False
        myNavigator["group"]["level1"].append({"@id": "activeTasks",
                                              "@name": u"Текущие задачи",
                                              "@selectOnLoad": "true",
                                              "action":
                                                {"#sorted":[{"main_context": "current"},
                                                             {"datapanel":
                                                                {"@type": "workflow.datapanel.tasks.activeTasks.celesta",
                                                                 "@tab": "firstOrCurrent"
                                                                 }
                                                             }]}
                                              })

    if userHasPermission(context, sid, 'archiveTasks'):
        emptyNavigatorFlag = False
        myNavigator["group"]["level1"].append({"@id": "archiveTasks",
                                              "@name": u"Выполненные задачи",
                                              "action":
                                                {"#sorted":[{"main_context": "current"},
                                                             {"datapanel":
                                                                {"@type": "workflow.datapanel.tasks.archiveTasks.celesta",
                                                                 "@tab": "firstOrCurrent"
                                                                 }
                                                             }]}
                                              })
    if userHasPermission(context, sid, 'allActiveTasks'):
        emptyNavigatorFlag = False
        myNavigator["group"]["level1"].append({"@id": "allActiveTasks",
                                              "@name": u"Все задачи",
                                              "action":
                                                {"#sorted":[{"main_context": "current"},
                                                             {"datapanel":
                                                                {"@type": "workflow.datapanel.tasks.allActiveTasks.celesta",
                                                                 "@tab": "firstOrCurrent"
                                                                 }
                                                             }]}
                                              })
    if emptyNavigatorFlag:
        return {"group":None}
    else:
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

def datapanelSetup(context, formType, session):
    activiti = ActivitiObject()
    processId = None
    processKey = None
    for params in session['urlparams']['urlparam']:
        if params['@name'] == 'taskId':
            taskId = params['@value'][0]
        elif params['@name'] == 'processId':
            processId = params['@value'][0]
        elif params['@name'] == 'processKey':
            processKey = params['@value'][0]
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datapanelSettings.json')
    datapanelSettings = parse_json(context)
    try:
        if 'Task' in formType:
            task = activiti.taskService.createTaskQuery().taskId(taskId).singleResult()
            formKey = task.getFormKey()
        elif not processKey:
            processInstance = activiti.runtimeService.createProcessInstanceQuery()\
                .processInstanceId(processId).singleResult()
            formKey = activiti.formService.getStartFormData(processInstance.getProcessDefinitionId()).getFormKey()
        else:
#             processDefinitions = activiti.repositoryService.createProcessDefinitionQuery()\
#                 .processDefinitionKey(processKey).list()
#             for processDefinition in processDefinitions:
#                 formKey = activiti.formService.getStartFormData(processDefinition.getProcessDefinitionId()).getFormKey()
#                 if formKey is not None:
#                     break
            form = formCursor(context)
            form.setRange('processKey', processKey)
            form.setRange('isStartForm', True)
            form.first()
            formKey = form.id
        return datapanelSettings['manual'][formKey]
    except:
        return datapanelSettings["default"][formType]