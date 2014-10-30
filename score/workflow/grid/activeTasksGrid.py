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
    identityService = activiti.identityService
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

    groupTasksList = activiti.taskService.createTaskQuery().taskCandidateGroupIn(rolesList).taskNameLike(taskName).list()
    userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid).taskNameLike(taskName).list()
    taskDict = {}
    for task in userTasksList:
        taskDict[task.id] = task
    for task in groupTasksList:
        if task.id not in taskDict:
            taskDict[task.id] = task
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
               "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "link": [u"Документ"],
               "excec": [u"Назначена на"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    runtimeService = activiti.runtimeService
    taskService = activiti.taskService
    logins = loginsCursor(context)
    for task in taskDict.values():
        identityLinks = taskService.getIdentityLinksForTask(task.id)
        procDict = {}
        show = False
        for link in identityLinks:
            if link.userId == sid:
                logins.setRange("subjectId", sid)
                logins.first()
                procDict[_header["excec"][1]] = logins.userName
                show = True
                break
            elif link.groupId in rolesList:
                roles.get(link.groupId)
                procDict[_header["excec"][1]] = u"Группа %s" % roles.description
                show = True
                break
        if show:
            procDict[_header["id"][1]] = task.id
            processInstanceId = task.getProcessInstanceId()
            processInstance = runtimeService.createProcessInstanceQuery()\
                .processInstanceId(processInstanceId).singleResult()
            processDefinition = activiti.repositoryService.createProcessDefinitionQuery()\
                .processDefinitionId(processInstance.getProcessDefinitionId()).singleResult()
            docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
                                  runtimeService.getVariable(processInstanceId, 'docName'))
            procDict[_header["process"][1]] = "%s: %s" % (processDefinition.getName(), docName)

            procDict[_header["schema"][1]] = {"div":
                                               {"@align": "center",
                                                "img":
                                                {"@src": "solutions/default/resources/flowblock.png",
                                                 "@height": "20px"}}}
            procDict[_header["name"][1]] = task.name

            requestReference = runtimeService.getVariable(processInstanceId, 'requestReference')
            procDict[_header["link"][1]] = {"div":
                                                 {"@align": "center",
                                                  "a":{"@href": requestReference,
                                                       "@target": "_blank",
                                                       "img":
                                                            {"@src": "solutions/default/resources/imagesingrid/link.png",
                                                             "@height": "20px"}}}}

            procDict[_header["properties"][1]] = {"event":
                                                  {"@name":"cell_single_click",
                                                   "@column": _header["schema"][0],
                                                   "action":
                                                        {"@show_in": "MODAL_WINDOW",
                                                         "#sorted":
                                                            [{"main_context":"current"},
                                                             {"modalwindow":
                                                                {"@caption": "Схема процесса"
                                                                 }
                                                              },
                                                             {"datapanel":
                                                                {"@type": "current",
                                                                 "@tab": "current",
                                                                 "element":
                                                                    {"@id": "tasksImage"
                                                                     }
                                                                 }
                                                              }
                                                             ]
                                                         }
                                                   }
                                                  }
            if processName == '' or processName in procDict[_header["process"][1]]:
                data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1000px",
                                               "@gridHeight": "500",
                                               "@totalCount": len(data["records"]["rec"]),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0],
                                                       "@width": "40px",
                                                       "type": "IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["link"][0],
                                                       "@width": "55px",
                                                       "type": "IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "230px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
                                                       "@width": "500px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["excec"][0],
                                                       "@width": "100px"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    session = json.loads(session)['sessioncontext']
    activiti = ActivitiObject()
    if 'currentRecordId' not in session['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[]}}
#     form = formCursor(context)
#     form.get(1)

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

#     data["gridtoolbar"]["item"].append({"@text":"Принять",
#                                         "@hint":"Принять задачу",
#                                         "@disable": styleAss,
#                                         "action": None})

    return XMLJSONConverter.jsonToXml(json.dumps(data))
