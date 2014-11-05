# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus

задачи, на которые пользователь назначен
задачи, у которых он кандидат
задачи, у которых кандидат - его группа
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

from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor
from security._security_orm import loginsCursor

def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    activiti = ActivitiObject()
    userRoles = UserRolesCursor(context)
    roles = RolesCursor(context)
    u'''получение данных из фильтра'''
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        processName = ' '.join(info["@process"].split())
    else:
        taskName = '%'
        processName = ''
    userRoles.setRange('userid', sid)

    rolesList = []
    if userRoles.tryFirst():
        while True:
            rolesList.append(userRoles.roleid)
            if not userRoles.next():
                break
#     задачи, у которых кандидат - группа
    groupTasksList = activiti.taskService.createTaskQuery().taskCandidateGroupIn(rolesList).taskNameLike(taskName).list()
#     задачи, у которых кандидат или исполнитель - юзер
    userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid).taskNameLike(taskName).list()
    taskDict = {}
#     чтобы не дублировались задачи
    for task in userTasksList:
        taskDict[task.id] = task
    for task in groupTasksList:
        if task.id not in taskDict:
            taskDict[task.id] = task
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
               "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "assign":[u"Принять"],
               "process": [u"Название процесса"],
               "finish": [u"Выполнить"],
               "reassing": [u"Переназначить"],
               "userAss": [u"Назначена на"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

    runtimeService = activiti.runtimeService
    taskService = activiti.taskService
    logins = loginsCursor(context)

#     Проходим по таблице и заполняем data
    for task in taskDict.values():
#         смотрим связи задачи
        identityLinks = taskService.getIdentityLinksForTask(task.id)
        taskDict = {}
#         отображается немного разное в зав-ти юзер или группа
        for link in identityLinks:
            if link.userId == sid:
                logins.setRange("subjectId", sid)
                logins.first()
                if not (link.type == 'candidate' and _header["userAss"][1] in taskDict):
                    taskDict[_header["userAss"][1]] = logins.userName
            elif link.groupId in rolesList:
                roles.get(link.groupId)
                taskDict[_header["userAss"][1]] = u"""Группа "%s\"""" % roles.description

        taskDict[_header["id"][1]] = task.id
        processInstanceId = task.getProcessInstanceId()
#         получаем процесс, чтобы потом получить его имя
        process = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(task.getProcessDefinitionId()).singleResult()
        docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
                              runtimeService.getVariable(processInstanceId, 'docName'))
        taskDict[_header["process"][1]] = "%s: %s" % (process.name, docName)
#         картинка, по нажатию переходим на схему

        taskDict[_header["schema"][1]] = {"link":
                                          {"@href":"./?mode=image&processId=%s" % processInstanceId,
                                           "@image":"solutions/default/resources/flowblock.png",
                                           "@text":"Схема",
                                           "@openInNewTab":"true"
                                             }
                                          }
        taskDict[_header["name"][1]] = task.name

        taskDict[_header["assign"][1]] = {"link":
                                          {"@href":"./?mode=image&processId=%s" % processInstanceId,
                                           "@image":"solutions/default/resources/imagesingrid/ok.png",
                                           "@text":"Принять",
                                           "@openInNewTab":"true"
                                             }
                                          } if taskDict[_header["userAss"][1]] != logins.userName else {"link": ""}
        taskDict[_header["finish"][1]] = {"link":
                                          {"@href":"./?mode=task&processId=%s&taskId=%s" % (processInstanceId, task.id),
                                           "@image":"solutions/default/resources/imagesingrid/finish.png",
                                           "@text":"Выполнить",
                                           "@openInNewTab":"true"
                                             }
                                          } if taskDict[_header["userAss"][1]] == logins.userName else {"link": ""}

        taskDict[_header["reassing"][1]] = {"link":
                                          {"@href":"./?mode=image&processId=%s" % processInstanceId,
                                           "@image": "solutions/default/resources/imagesingrid/user.png",
                                           "@text":"Переназначить",
                                           "@openInNewTab":"true"
                                             }
                                          } if len(identityLinks) > 1 else {"link": {}}

        if processName == '' or processName in taskDict[_header["process"][1]]:
            data["records"]["rec"].append(taskDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1100px",
                                               "@gridHeight": "500",
                                               "@totalCount": len(data["records"]["rec"]),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0],
                                                       "@width": "40px",
                                                       "@type": "LINK"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["assign"][0],
                                                       "@width": "60px",
                                                       "@type": "LINK"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["reassing"][0],
                                                       "@width": "85px",
                                                       "@type": "LINK"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["finish"][0],
                                                       "@width": "60px",
                                                       "@type": "LINK"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "215px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
                                                       "@width": "500px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["userAss"][0],
                                                       "@width": "100px"})

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)),
                     XMLJSONConverter.jsonToXml(json.dumps(settings)))

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    session = json.loads(session)['sessioncontext']
    activiti = ActivitiObject()
    styleAss = 'true'
    if 'currentRecordId' not in session['related']['gridContext']:
        style = "true"
    else:
        style = "false"
        taskId = session['related']['gridContext']['currentRecordId']
        if activiti.taskService.createTaskQuery().taskId(taskId).singleResult().getAssignee() != session["sid"]:
            styleAss = 'false'

    data = {"gridtoolbar":{"item":[]}}

#     data["gridtoolbar"]["item"].append({"@text":"Выполнить",
#                                         "@hint":"Выполнить задачу",
#                                         "@disable": style,
#                                         "action": {"@show_in": "MODAL_WINDOW",
#                                                    "#sorted":[{"main_context":"current"},
#                                                              {"modalwindow":{"@caption": "Изменение статуса",
#                                                                              "@height": "300",
#                                                                              "@width": "500"}
#                                                               },
#                                                              {"datapanel":{"@type": "current",
#                                                                            "@tab": "current",
#                                                                            "element": {"@id": "taskStatusCard"}
#                                                                            }
#                                                               }]
#                                                   }})

    data["gridtoolbar"]["item"].append({"@text":"Взять на исполнение",
                                        "@hint":"Взять на исполнение",
                                        "@disable": styleAss,
                                        "action": {"#sorted":
                                                     [{"main_context": 'current'},
                                                      {"server":
                                                       {"activity":
                                                        {"@id": "assign",
                                                         "@name": "workflow.grid.activeTasksGrid.assign.celesta",
                                                         "add_context": "current"}}},
                                                      {"datapanel":
                                                        {"@type": "current",
                                                         "@tab": "current",
                                                            "element":
                                                             {"@id": "tasksGrid",
                                                              "add_context": 'current'}}}
                                                         ]}})

#     data["gridtoolbar"]["item"].append({"@text":"Переназначить",
#                                         "@hint":"Переназначить задачу",
#                                         "@disable": 'false' if styleAss != 'false' and style == 'false' else 'true',
#                                         "action": {"@show_in": "MODAL_WINDOW",
#                                                    "#sorted":[{"main_context":"current"},
#                                                               {"modalwindow":{"@caption": "Переназначить задачу",
#                                                                               "@height": "300",
#                                                                               "@width": "500"}
#                                                               },
#                                                               {"datapanel":{"@type": "current",
#                                                                             "@tab": "current",
#                                                                             "element": {"@id": "reassign"}
#                                                                            }
#                                                               }]
#                                                   }})

    return XMLJSONConverter.jsonToXml(json.dumps(data))

def assign(context, main, add=None, filterinfo=None, session=None, elementId=None):
    session = json.loads(session)['sessioncontext']
    taskId = session['related']['gridContext']['currentRecordId']
    sid = session["sid"]
    activiti = ActivitiObject()
    activiti.taskService.claim(taskId, sid)
