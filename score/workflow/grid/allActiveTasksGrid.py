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
from security._security_orm import loginsCursor
from java.text import SimpleDateFormat
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult
from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor

def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    activiti = ActivitiObject()
    inputFormat = SimpleDateFormat("yyyy-MM-dd hh:mm:ss")
    dateFrom = '0001-01-01 00:00:00'
    dateTo = '9999-12-31 23:59:59'
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        processName = ' '.join(info["@process"].split())
        assignee = ' '.join(info["@assignee"].split())
        if info["@dateFrom"]:
            dateFrom = info["@dateFrom"].replace('T', ' ')
        if info["@dateTo"]:
            dateTo = info["@dateTo"].replace('T', ' ')
    else:
        taskName = '%'
        processName = ''
        assignee = ''

    dateFrom = SimpleDateFormat.parse(inputFormat, dateFrom)
    dateTo = SimpleDateFormat.parse(inputFormat, dateTo)

#     userTasksList = activiti.taskService.createTaskQuery().taskAssignee(sid).taskNameLike(taskName).list()
#     groupTaskList = activiti.taskService.createTaskQuery().taskCandidateGroup(group).taskNameLike(taskName).list()
    groupTaskList = activiti.taskService.createTaskQuery()\
                            .taskNameLike(taskName)\
                            .taskCreatedAfter(dateFrom)\
                            .taskCreatedBefore(dateTo)\
                            .orderByTaskCreateTime().desc().list()

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
#                "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "assignee": [u"Исполнитель"],
               "date": [u"Дата"],
               "link": [u"Документ"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    runtimeService = activiti.runtimeService
    logins = loginsCursor(context)
    userRoles = UserRolesCursor(context)
    roles = RolesCursor(context)
    userRoles.setRange('userid', sid)

    rolesList = []
    if userRoles.tryFirst():
        while True:
            rolesList.append(userRoles.roleid)
            if not userRoles.next():
                break

    for task in groupTaskList:
        taskDict = {}
        taskDict[_header["id"][1]] = task.id
        processInstanceId = task.getProcessInstanceId()
        processInstance = runtimeService.createProcessInstanceQuery()\
            .processInstanceId(processInstanceId).singleResult()
        processDefinition = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(processInstance.getProcessDefinitionId()).singleResult()
        docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
                              runtimeService.getVariable(processInstanceId, 'docName'))
        taskDict[_header["process"][1]] = "%s: %s" % (processDefinition.getName(), docName)
        identityLinks = activiti.taskService.getIdentityLinksForTask(task.id)
#         taskDict[_header["assignee"][1]] = 'error'
        for link in identityLinks:
            if link.userId == sid:
                logins.setRange("subjectId", sid)
                logins.first()
                taskDict[_header["assignee"][1]] = logins.userName
            elif link.groupId in rolesList:
                roles.get(link.groupId)
                taskDict[_header["assignee"][1]] = u"""Группа "%s\"""" % roles.description
        taskDict[_header["date"][1]] = unicode(task.getCreateTime())
        taskDict[_header["name"][1]] = task.name

        requestReference = runtimeService.getVariable(processInstanceId, 'requestReference')
        taskDict[_header["link"][1]] = {"div":
                                             {"@align": "center",
                                              "a":{"@href": requestReference,
                                                   "@target": "_blank",
                                                   "img":
                                                        {"@src": "solutions/default/resources/imagesingrid/link.png",
                                                         "@height": "20px"}}}}

        if processName in taskDict[_header["process"][1]] and _header["assignee"][1] in taskDict:
            data["records"]["rec"].append(taskDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1300px",
                                               "@gridHeight": "500",
                                               "@totalCount": len(data["records"]["rec"]),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["link"][0],
                                                       "@width": "55px",
                                                       "type": "IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "250px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
                                                       "@width": "550px"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    session = json.loads(session)['sessioncontext']
    activiti = ActivitiObject()
    taskService = activiti.taskService
    styleAss = 'true'
    if 'currentRecordId' not in session['related']['gridContext']:
        style = "true"
    else:
        style = "false"
        taskId = session['related']['gridContext']['currentRecordId']
        if taskService.createTaskQuery().taskId(taskId).singleResult().getAssignee() != session["sid"]:
            styleAss = 'false'

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
#
#     data["gridtoolbar"]["item"].append({"@text":"Принять",
#                                         "@hint":"Принять задачу",
#                                         "@disable": styleAss,
#                                         "action": None})

    return XMLJSONConverter.jsonToXml(json.dumps(data))
