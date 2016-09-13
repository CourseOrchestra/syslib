# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus

задачи, на которые пользователь назначен
задачи, у которых он кандидат
задачи, у которых кандидат - его группа
'''

from com.google.gson import Gson
import json
import os
from common.sysfunctions import toHexForXml, getGridWidth, getGridHeight
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, functionImport, setVariablesInLink,\
                                 getGroupUsers, parse_json
                                 
from workflow.getUserInfo import userNameClass, userGroupsClass

from workflow._workflow_orm import formCursor
from workflow._workflow_orm import act_ru_taskCursor, view_task_linksCursor, act_ru_variableCursor
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor

import time


def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех развернутых процессов. '''

    variables = act_ru_variableCursor(context)
    gson = Gson()
    taskLinks = view_task_linksCursor(context)
    timeList = list()
    start = time.clock()
    datapanelSettings = parse_json()
    timeList.append("parse json:" + str(time.clock() - start))
    usersClass = userNameClass(context,datapanelSettings)
    timeList.append("userName init:" + str(time.clock() - start))
    groupsClass = userGroupsClass(context,datapanelSettings)
    timeList.append("userGroups init:" + str(time.clock() - start))
    session = json.loads(session)
    timeList.append("load session:" + str(time.clock() - start))
    session = session["sessioncontext"]
    sid = session["sid"]

    activiti = ActivitiObject()
    form = formCursor(context)
    u'''получение данных из фильтра'''
    timeList.append("act init:" + str(time.clock() - start))
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = info["@task"]
        processName =   info["@process"]
    else:
        taskName = '%'
        processName = '%'

    groupsList = groupsClass.getUserGroups(sid)


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
               "comment": [u"Комментарии"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

    whereClause = """assignee_ = '%s' or users like '%%''%s''%%' """ %(sid, sid)
    for group in groupsList:
        whereClause += """or groups like '%%''%s''%%' """ %(group)
    whereClause = '(' + whereClause +')'
    whereClause += """and processName like '%%%s%%' and name_ like '%%%s%%' """%(processName,taskName)

    taskLinks.setComplexFilter(whereClause)
    taskLinks.limit(firstrecord-1,pagesize)


    #function = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))
    timeList.append("get taskDict:" + str(time.clock() - start))
#     Проходим по таблице и заполняем data
    for task in taskLinks.iterate():
#         смотрим связи задачи
        startTask = time.clock()
        if task.users is not None:
            users = task.users.split(',')
        else:
            users = []
        if task.groups is not None:
            groups = task.groups.split(',')
        else:
            groups = []
        taskDict = {}
        taskDict[_header["userAss"][1]] = ''
        if task.assignee_ is not None:
            taskDict[_header["userAss"][1]] = usersClass.getUserName(task.assignee_)
        reassignFlag = False
        if len(users) + len(groups) > 0:
            reassignFlag = True
        timeList.append("task get identity:" + task.id_ + ' |' + str(time.clock() - startTask))
        taskDict[_header["id"][1]] = task.id_
        processInstanceId = task.proc_inst_id_

        variables.setRange('proc_inst_id_',processInstanceId)
        variables.setRange('name_','processDescription')
        variables.first()
        procDesc = variables.text_
        timeList.append("task get procdesc:" + task.id_ + '|' + str(time.clock() - startTask))
        if procDesc is not None:
            taskDict[_header["description"][1]] = procDesc
        else:
            taskDict[_header["description"][1]] = ''
#         docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
#                               runtimeService.getVariable(processInstanceId, 'docName'))
        taskDict[_header["process"][1]] = "%s" % (task.processName)
#         картинка, по нажатию переходим на схему

        taskDict[_header["schema"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": "./?userdata=%s&mode=image&processId=%s" \
                                                            % (session["userdata"], processInstanceId),
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/flowblock.png"}}}}

        taskDict[_header["name"][1]] = task.name_
        taskDict[_header["properties"][1]] = {"event":
                                              []}
        if reassignFlag and task.assignee_ == sid:
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
                                                                         "add_context": task.id_}}},
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'tasksGrid'}}}]}})
        else:
            taskDict[_header["abandon"][1]] = ""
        if task.assignee_ is None:
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
                                                                         "add_context": task.id_}}},
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'tasksGrid'}}}]}})
        else:
            taskDict[_header["assign"][1]] = ""
        timeList.append("task get buttons:" + task.id_ + '|' + str(time.clock() - startTask))    
        if form.tryGet(task.processKey, task.form_key_):
            link = setVariablesInLink(activiti, processInstanceId, task.id_, form.link)
        else:
            link = "./?userdata=%s&mode=task&processId=%s&taskId=%s" % (session["userdata"], processInstanceId, task.id_)
        timeList.append("task set links:" + task.id_ + '|' + str(time.clock() - startTask))        
        taskDict[_header["document"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": link,
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/play.png"}}}} \
                                                    if taskDict[_header["userAss"][1]] == usersClass.getUserName(sid) else ""
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
                                                                          {"@caption": u"Выбор пользователя",
                                                                            "@height": "150",
                                                                            "@width": "250"
                                                                           }
                                                                        },
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'reassign'}}}]}})
        else:
            taskDict[_header["reassign"][1]] = ""
        taskDict[_header["comment"][1]] = {"div":
                                            {"@align": "center",
                                             "@class": "gridCellCursor",
                                             "img":
                                                {"@src": "solutions/default/resources/imagesingrid/user.png"}}}
        taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
                                                            "@column": _header["comment"][0],
                                                            "action":
                                                                {"@show_in": "MODAL_WINDOW",
                                                                 "#sorted":
                                                                 [{"main_context": 'current'},
                                                                  {"modalwindow":
                                                                      {"@caption": u"Просмотр комментариев",
                                                                       "@height": "200",
                                                                       "@width": "400"
                                                                       }
                                                                    },
                                                                  {"datapanel":
                                                                    {'@type':"current",
                                                                     '@tab':"current",
                                                                     'element':
                                                                        {'@id':'viewComments',
                                                                         'add_context':processInstanceId}}}]}})
        
#         if processName == '' or processName in taskDict[_header["process"][1]]:
#
        data["records"]["rec"].append(taskDict)
        timeList.append("task added:" + task.id_ + '|' + str(time.clock() - startTask))
    timeList.append("finish:" + str(time.clock() - start))
    data = gson.toJson(data)
    res1 = XMLJSONConverter.jsonToXml(data)
#     print timeList
    #raise Exception(timeList)
    return JythonDTO(res1, None)

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    taskLinks = view_task_linksCursor(context)
    gson = Gson() 
    datapanelSettings = parse_json()
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session, 1)
    session = json.loads(session)
    groupsClass = userGroupsClass(context,datapanelSettings)
    session = session["sessioncontext"]
    sid = session["sid"]
    u'''получение данных из фильтра'''
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = info["@task"]
        processName =   info["@process"]
    else:
        taskName = '%'
        processName = '%'

#    datapanelSettings = parse_json(context)["specialFunction"]["getUserGroups"]
    #getUserGroups = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))
    groupsList = groupsClass.getUserGroups(sid)

#     
    whereClause = """assignee_ = '%s' or users like '%%''%s''%%' """ %(sid, sid)
    for group in groupsList:
        whereClause += """or groups like '%%''%s''%%' """ %(group)
    whereClause = '(' + whereClause +')'
    whereClause += """and processName like '%%%s%%' and name_ like '%%%s%%' """%(processName,taskName)

    taskLinks.setComplexFilter(whereClause)
    
#     if groupsListStr == '':
#         taskList = activiti.taskService.createNativeTaskQuery()\
#                             .sql("""select  count(*)
#                                         from act_ru_task
# 
#                                         where (assignee_ = 'admin' 
#                                         or (select count(*) 
#                                             from act_ru_identitylink 
#                                             where type_ = 'candidate' 
#                                                 and act_ru_task.id_ = act_ru_identitylink.task_id_ 
#                                                 and (user_id_ = '%s' 
#                                                     ))
#                                             > 0
#                                         )
#                                         and name_ like('%%%s%%')
# 
#                                         
#                                         """ % ( sid,sid,taskName,
#                                                              )).count()
#     else:
#         taskList = activiti.taskService.createNativeTaskQuery()\
#                             .sql("""select count(*)
#                                         from act_ru_task
#                                         where (assignee_ = '%s' 
#                                         or (select count(*) 
#                                             from act_ru_identitylink 
#                                             where type_ = 'candidate' 
#                                                 and act_ru_task.id_ = act_ru_identitylink.task_id_ 
#                                                 and (user_id_ = '%s' 
#                                                     or group_id_ in (%s)))
#                                             > 0)
#                                         and name_ like('%%%s%%')
#                                            
#                                         
#                                         """ % ( sid,sid,groupsListStr,taskName,
#                                                              )).count()
# #     задачи, у которых кандидат - группа, в которую входит текущий пользователь
#     if groupsList != []:
#         groupTasksList = activiti.taskService.createTaskQuery()\
#                 .taskCandidateGroupIn(groupsList).taskNameLike(taskName).processDefinitionNameLike(processName).list()
#     else:
#         groupTasksList = []
# #     задачи, у которых кандидат или исполнитель - юзер
#     userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid)\
#                 .taskNameLike(taskName).processDefinitionNameLike(processName).list()
#     taskDict = {}
# #     чтобы не дублировались задачи
#     for task in userTasksList:
#         if task.id not in taskDict:
#             taskDict[task.id] = task
#     for task in groupTasksList:
#         if task.id not in taskDict:
#             taskDict[task.id] = task

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
               "comment": [u"Комментарии"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

    #raise Exception(time.clock() - start)
    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": taskLinks.count(),
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
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["comment"][0],
                                                       "@width": "100px"})
    settings = gson.toJson(settings)
    res1 = XMLJSONConverter.jsonToXml(settings)
    return JythonDTO(None, res1)

def assign(context, main, add=None, filterinfo=None, session=None, elementId=None):
    sid = json.loads(session)['sessioncontext']["sid"]
    activiti = ActivitiObject()
    activiti.taskService.claim(add, sid)
    context.message(u'Задача взята на исполнение')

def abandonTask(context, main, add=None, filterinfo=None, session=None, elementId=None):
    activiti = ActivitiObject()
    activiti.taskService.unclaim(add)
    context.message(u'Вы отказались от задачи')
