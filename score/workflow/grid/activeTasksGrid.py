# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus

задачи, на которые пользователь назначен
задачи, у которых он кандидат
задачи, у которых кандидат - его группа
'''

import simplejson as json
import os
from common.sysfunctions import toHexForXml, getGridWidth, getGridHeight
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, functionImport, setVariablesInLink, getGroupUsers, parse_json
from workflow._workflow_orm import formCursor
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor


def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)

    session = session["sessioncontext"]
    sid = session["sid"]

    activiti = ActivitiObject()
    form = formCursor(context)
    u'''получение данных из фильтра'''
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        processName = "%%%s%%" % ' '.join(info["@process"].split())
    else:
        taskName = '%'
        processName = '%'
    filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'datapanelSettings.json')
    datapanelSettings = parse_json(context)["specialFunction"]["getUserGroups"]
    
    getUserGroups = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))
    groupsList = getUserGroups(context, sid)
#     задачи, у которых кандидат - группа, в которую входит текущий пользователь
    if groupsList != []:
        groupTasksList = activiti.taskService.createTaskQuery().taskCandidateGroupIn(groupsList)\
            .taskNameLike(taskName).processDefinitionNameLike(processName).list()
        if len(groupTasksList) >= 50:
            groupTasksList = groupTasksList
    else:
        groupTasksList = []
#     задачи, у которых кандидат или исполнитель - юзер
    userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid)\
            .taskNameLike(taskName).processDefinitionNameLike(processName).list()

    if len(userTasksList) >= 50:
        userTasksList = userTasksList
    taskDict = {}
#     чтобы не дублировались задачи
    for task in userTasksList:
        if task.id not in taskDict:
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
               "document": [u"Выполнить"],
               "abandon":[u"Отказаться"],
               "description":[u'Описание процесса'],
               "reassign": [u"Передать задачу"],
               "userAss": [u"Назначена на"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

#     runtimeService = activiti.runtimeService
    taskService = activiti.taskService
    filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'datapanelSettings.json')
    datapanelSettings = parse_json(context)["specialFunction"]["getUserName"]
    taskValues = taskDict.values()[firstrecord - 1:firstrecord + 51]
    function = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))

#     Проходим по таблице и заполняем data
    for task in taskValues:
#         смотрим связи задачи
        identityLinks = taskService.getIdentityLinksForTask(task.id)
        taskDict = {}
        taskDict[_header["userAss"][1]] = ''
        reassignFlag = False
        for link in identityLinks:
            if link.userId == sid and link.type == 'assignee':
                taskDict[_header["userAss"][1]] = function(context, link.userId)
            else:
                reassignFlag = True
        taskDict[_header["id"][1]] = task.id
        processInstanceId = task.getProcessInstanceId()
#         получаем процесс, чтобы потом получить его имя
        process = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(task.getProcessDefinitionId()).singleResult()
        # Получаем описание процесса
        procDesc = activiti.runtimeService.getVariable(processInstanceId, 'processDescription')
        if procDesc is not None:
            taskDict[_header["description"][1]] = procDesc
        else:
            taskDict[_header["description"][1]] = ''
#         docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
#                               runtimeService.getVariable(processInstanceId, 'docName'))
        taskDict[_header["process"][1]] = "%s" % (process.name)
#         картинка, по нажатию переходим на схему

        taskDict[_header["schema"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": "./?userdata=%s&mode=image&processId=%s" \
                                                            % (session["userdata"], processInstanceId),
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/flowblock.png"}}}}

        taskDict[_header["name"][1]] = task.name
        taskDict[_header["properties"][1]] = {"event":
                                              []}
        if reassignFlag and taskDict[_header["userAss"][1]] == function(context, sid):
            taskDict[_header["abandon"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/stop.png"}}}
            taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
                                                                "@column": _header["abandon"][0],
                                                                "action":
                                                                    {"#sorted":
                                                                     [{"main_context": 'current'},
                                                                      {"server":
                                                                       {"activity":
                                                                        {"@id": "abandonTask",
                                                                         "@name": "workflow.grid.activeTasksGrid.abandonTask.celesta",
                                                                         "add_context": task.id}}},
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'tasksGrid'}}}]}})
        else:
            taskDict[_header["abandon"][1]] = ""
        if taskDict[_header["userAss"][1]] != function(context, sid):
            taskDict[_header["assign"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/ok.png"}}}
            taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
                                                                "@column": _header["assign"][0],
                                                                "action":
                                                                    {"#sorted":
                                                                     [{"main_context": 'current'},
                                                                      {"server":
                                                                       {"activity":
                                                                        {"@id": "assign",
                                                                         "@name": "workflow.grid.activeTasksGrid.assign.celesta",
                                                                         "add_context": task.id}}},
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'tasksGrid'}}}]}})
        else:
            taskDict[_header["assign"][1]] = ""

        if form.tryGet(process.key, task.formKey):
            link = setVariablesInLink(activiti, processInstanceId, task.id, form.link)
        else:
            link = "./?userdata=%s&mode=task&processId=%s&taskId=%s" % (session["userdata"], processInstanceId, task.id)
        taskDict[_header["document"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": link,
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/play.png"}}}} \
                                                    if taskDict[_header["userAss"][1]] == function(context, sid) else ""
#         {"link":
#                                               {"@href":"./?mode=task&processId=%s&taskId=%s" % (processInstanceId, task.id),
#                                                "@image":"solutions/default/resources/play.png",
#                                                "@text":"Выполнить",
#                                                "@openInNewTab":"true"
#                                                  }
#                                               } if taskDict[_header["userAss"][1]] == logins.userName else {"link": ""}
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

#         if processName == '' or processName in taskDict[_header["process"][1]]:
#
        data["records"]["rec"].append(taskDict)
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session, 1)
    session = json.loads(session)

    session = session["sessioncontext"]
    sid = session["sid"]
    activiti = ActivitiObject()
    u'''получение данных из фильтра'''
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        processName = "%%%s%%" % ' '.join(info["@process"].split())
    else:
        taskName = '%'
        processName = '%'
    filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'datapanelSettings.json')
    datapanelSettings = parse_json(context)["specialFunction"]["getUserGroups"]
    getUserGroups = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))
    groupsList = getUserGroups(context, sid)
#     задачи, у которых кандидат - группа, в которую входит текущий пользователь
    if groupsList != []:
        groupTasksList = activiti.taskService.createTaskQuery()\
                .taskCandidateGroupIn(groupsList).taskNameLike(taskName).processDefinitionNameLike(processName).list()
    else:
        groupTasksList = []
#     задачи, у которых кандидат или исполнитель - юзер
    userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid)\
                .taskNameLike(taskName).processDefinitionNameLike(processName).list()
    taskDict = {}
#     чтобы не дублировались задачи
    for task in userTasksList:
        if task.id not in taskDict:
            taskDict[task.id] = task
    for task in groupTasksList:
        if task.id not in taskDict:
            taskDict[task.id] = task

    _header = {"id":["~~id"],
               "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "assign":[u"Принять"],
               "process": [u"Название процесса"],
               "document": [u"Выполнить"],
               "abandon":[u"Отказаться"],
               "description":[u'Описание процесса'],
               "reassign": [u"Передать задачу"],
               "userAss": [u"Назначена на"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))


    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": len(taskDict),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0],
                                                       "@width": "40px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["assign"][0],
                                                       "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["reassign"][0],
                                                       "@width": "85px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["document"][0],
                                                       "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["abandon"][0],
                                                       "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "215px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
                                                       "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0],
                                                       "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["userAss"][0],
                                                       "@width": "100px"})

    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, jsonSettings)

def assign(context, main, add=None, filterinfo=None, session=None, elementId=None):
    sid = json.loads(session)['sessioncontext']["sid"]
    activiti = ActivitiObject()
    activiti.taskService.claim(add, sid)
    context.message(u'Задача взята на исполнение')

def abandonTask(context, main, add=None, filterinfo=None, session=None, elementId=None):
    activiti = ActivitiObject()
    activiti.taskService.unclaim(add)
    context.message(u'Вы отказались от задачи')
