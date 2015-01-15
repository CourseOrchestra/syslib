# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus

все активные задачи всех пользователей и групп
'''

import simplejson as json
import os
from common.sysfunctions import toHexForXml, getGridWidth, getGridHeight
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, parse_json, functionImport
from workflow._workflow_orm import formCursor
from java.text import SimpleDateFormat
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult
import datetime
from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor

def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех развернутых процессов. '''
    a = datetime.datetime.now()
    session = json.loads(session)

    session = session["sessioncontext"]
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

#     groupTaskList = activiti.taskService.createTaskQuery()\
#                             .taskNameLike(taskName)\
#                             .taskCreatedAfter(dateFrom)\
#                             .taskCreatedBefore(dateTo)\
#                             .orderByTaskCreateTime().desc().list()
#     managementService = activiti.managementService

    groupTaskList = activiti.taskService.createNativeTaskQuery()\
                        .sql("""select *
                                    from %s 
                                    where name_ like('%%%s%%') and
                                          create_time_>'%s' and
                                          create_time_<'%s'
                                    order by create_time_ desc
                                    limit %i
                                    offset %i""" % ('act_ru_task',
                                                       taskName, dateFrom, dateTo, pagesize, firstrecord)).list()

#     if len(groupTaskList) > 50:
#         groupTaskList = groupTaskList.subList(firstrecord, firstrecord + 50)
    data = {"records":{"rec":[]}}

    _header = {"id":["~~id"],
#                "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "assignee": [u"Исполнитель"],
               "reassign": [u"Передать задачу"],
               "date": [u"Дата"],
               "description":[u"Описание процесса"],
               "document": [u"Выполнить"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    runtimeService = activiti.runtimeService
    userRoles = UserRolesCursor(context)
    roles = RolesCursor(context)
    userRoles.setRange('userid', sid)
    form = formCursor(context)
    filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'datapanelSettings.json')
    datapanelSettings = parse_json(filePath)["specialFunction"]["getUserName"]
    function = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))


    for task in groupTaskList:
        taskDict = {}
        taskDict[_header["properties"][1]] = {"event":
                                              []}
        taskDict[_header["id"][1]] = task.id
        processInstanceId = task.getProcessInstanceId()

        procDesc = task.getProcessVariables()['processDescription']
        if procDesc is not None:
            taskDict[_header["description"][1]] = procDesc
        else:
            taskDict[_header["description"][1]] = ''
        processDefinition = activiti.repositoryService.createProcessDefinitionQuery()\
             .processDefinitionId(task.getProcessDefinitionId()).singleResult()
        docName = "%s. %s" % (task.getProcessVariables()['docId'], \
                              task.getProcessVariables()['docName'])
        taskDict[_header["process"][1]] = "%s: %s" % (processDefinition.getName(), docName)
        identityLinks = activiti.taskService.getIdentityLinksForTask(task.id)
#         taskDict[_header["assignee"][1]] = 'error'
        taskDict[_header["assignee"][1]] = ''
        reassignFlag = False
        for link in identityLinks:
            if link.userId is not None and link.type == 'assignee':
                taskDict[_header["assignee"][1]] = function(context, link.userId)
            else:
                reassignFlag = True

        taskDict[_header["date"][1]] = SimpleDateFormat("HH:mm dd.MM.yyyy").format(task.getCreateTime())
        taskDict[_header["name"][1]] = task.name
        if reassignFlag:
            taskDict[_header["reassign"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/user.png"}}}
            taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
                                                                "@column": _header["reassign"][0],
                                                                "action":
                                                                    {"@show_in": "MODAL_WINDOW",
                                                                     "#sorted":
                                                                     [{"main_context": 'current'},
                                                                      {"modalwindow":
                                                                          {"@caption": "Выбор пользователя"
                                                                           }
                                                                        },
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'reassign'}}}]}})
        else:
            taskDict[_header["reassign"][1]] = ""
        if form.tryGet(processDefinition.key, task.formKey):
            link = form.link.replace('&[processId]', processInstanceId).replace('&[taskId]', task.id)
        else:
            link = "./?userdata=%s&mode=task&processId=%s&taskId=%s" % (session["userdata"], processInstanceId, task.id)
        taskDict[_header["document"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": link,
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/play.png"}}}}

        if processName in taskDict[_header["process"][1]] and assignee in taskDict[_header["assignee"][1]]:
            data["records"]["rec"].append(taskDict)
    # raise Exception(a, datetime.datetime.now())
    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))

    return JythonDTO(res1, None)

    # Определяем список полей таблицы для отображения

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session, 1, 55, 75)
    session = json.loads(session)["sessioncontext"]
    activiti = ActivitiObject()
    inputFormat = SimpleDateFormat("yyyy-MM-dd hh:mm:ss")
    dateFrom = '0001-01-01 00:00:00'
    dateTo = '9999-12-31 23:59:59'
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        if info["@dateFrom"]:
            dateFrom = info["@dateFrom"].replace('T', ' ')
        if info["@dateTo"]:
            dateTo = info["@dateTo"].replace('T', ' ')
    else:
        taskName = '%'

    dateFrom = SimpleDateFormat.parse(inputFormat, dateFrom)
    dateTo = SimpleDateFormat.parse(inputFormat, dateTo)

    groupTaskList = activiti.taskService.createTaskQuery()\
                            .taskNameLike(taskName)\
                            .taskCreatedAfter(dateFrom)\
                            .taskCreatedBefore(dateTo)

    _header = {"id":["~~id"],
#                "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "assignee": [u"Исполнитель"],
               "reassign": [u"Передать задачу"],
               "date": [u"Дата"],
               "description":[u"Описание процесса"],
               "document": [u"Выполнить"],
               "properties":[u"properties"]}
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"30",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": groupTaskList.count(),
                                               "@profile":"default.properties"}
                                }

    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["document"][0],
                                                       "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["reassign"][0],
                                                       "@width": "85px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "200px"})

    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
                                                       "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0],
                                                       "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["assignee"][0],
                                                       "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["date"][0],
                                                       "@width": "200px"})

    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(None, res2)

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
