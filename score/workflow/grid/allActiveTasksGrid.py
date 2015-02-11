# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus

все активные задачи всех пользователей и групп
'''

import simplejson as json
import os
from com.google.gson import Gson
import time
from common.sysfunctions import toHexForXml, getGridWidth, getGridHeight
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject,  functionImport, parse_json, getUsersCursor
from workflow._workflow_orm import formCursor
from workflow.getUserInfo import userNameClass

from workflow._workflow_orm import view_task_linksCursor

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
    #raise Exception(main,add,filterinfo,session,elementId,sortColumnList,firstrecord,pagesize)
    gson = Gson()
    tasks = view_task_linksCursor(context)
    timeList = list()
    start = time.time()
    session = json.loads(session)
    session = session["sessioncontext"]

    datapanelSettings = parse_json()
    usersClass = userNameClass(context,datapanelSettings)

    timeAct = str(time.time() - start)
    timeList.append('ActivitiInit ' + timeAct)
    if "formData" in session["related"]["xformsContext"]:
        dateTo = None
        dateFrom = None
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = info["@task"]
        processName = info["@process"]
        assignee = info["@assignee"]
        if info["@dateFrom"]:
            dateFrom = info["@dateFrom"]
        if info["@dateTo"]:
            dateTo = info["@dateTo"]
    else:
        taskName = '%'
        processName = '%'
        assignee = None
        dateTo = None
        dateFrom = None


    whereClause = """processName like '%%%s%%' and name_ like '%%%s%%'"""%(processName,taskName)
    if assignee is not None and assignee != '':
        whereClause += """and assignee_ like '%%%s%%'""" % (assignee)  
    if dateFrom is not None:
        whereClause += """and create_time_ > '%s'"""%(dateFrom)
    if dateTo is not None:
        whereClause += """and create_time_ < '%s'"""%(dateTo)   
    tasks.setComplexFilter(whereClause)
    tasks.orderBy('create_time_')
    tasks.limit(firstrecord-1,pagesize)
    timeTaskReceived = str(time.time() - start)
    timeList.append('Task list received: '+timeTaskReceived)                                                   
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

    form = formCursor(context)
    #datapanelSettings = parse_json(context)["specialFunction"]["getUserName"]
    #function = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))

    timeFuncImp = str(time.time() - start)
    timeList.append('FunctionImport: ' +  timeFuncImp)

    for task in tasks.iterate():
        #print task.getIdentityLinks()
        timeStartTask = time.time()
        taskDict = {}
        taskDict[_header["properties"][1]] = {"event":
                                              []}
        taskDict[_header["id"][1]] = task.id_
        timeList.append(task.id_ + ' get task id ' +  str(time.time() - timeStartTask))
        processInstanceId = task.proc_inst_id_
        procDesc = tasks.processDescription
        timeList.append(task.id_ + ' get procDesc ' + str(time.time() - timeStartTask))
        if procDesc is not None:
            taskDict[_header["description"][1]] = procDesc
        else:
            taskDict[_header["description"][1]] = ''
#         processDefinition = activiti.repositoryService.createProcessDefinitionQuery()\
#              .processDefinitionId(task.getProcessDefinitionId()).singleResult()
        timeList.append(task.id_ + ' get procDef ' + str(time.time() - timeStartTask))

#         taskDict[_header["process"][1]] = "aaa"
        taskDict[_header["process"][1]] = tasks.processName
        timeList.append(task.id_ + ' get docIddocName ' + str(time.time() - timeStartTask))
#         taskDict[_header["assignee"][1]] = 'error'
        timeList.append(task.id_ + ' get Identity Links ' + str(time.time() - timeStartTask))
        if task.assignee_ is None:
            taskDict[_header["assignee"][1]] = ''
        else:
            taskDict[_header["assignee"][1]] = usersClass.getUserName(task.assignee_)
        reassignFlag = False
        if task.users is not None:
            users = task.users.split(',')
        else:
            users = []
        if task.groups is not None:
            groups = task.groups.split(',')
        else:
            groups = []
        if len(users) + len(groups) > 0:
            reassignFlag = True
        timeList.append(task.id_ + ' get reass flag ' + str( time.time() - timeStartTask))
        taskDict[_header["date"][1]] = SimpleDateFormat("HH:mm dd.MM.yyyy").format(task.create_time_)
        taskDict[_header["name"][1]] = task.name_
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
                                                                           "@height": "175",
                                                                           "@width": "240"
                                                                           
                                                                           }
                                                                        },
                                                                      {"datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         'element':
                                                                            {'@id':'reassign'}}}]}})
        else:
            taskDict[_header["reassign"][1]] = ""
        timeList.append(task.id_ + ' get reassign ' + str(time.time() - timeStartTask))
#         link = 'a'
        if form.tryGet(task.processKey, task.form_key_):
            link = form.link.replace('&[processId]', processInstanceId).replace('&[taskId]', task.id_)
        else:
            link = "./?userdata=%s&mode=task&processId=%s&taskId=%s" % (session["userdata"], processInstanceId, task.id_)
        taskDict[_header["document"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": link,
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/play.png"}}}}

        timeList.append(task.id_+' get doc id '+ str( time.time() - timeStartTask))
        data["records"]["rec"].append(taskDict)
        timeList.append('Task ' + task.id_ + ' added: ' +  str(time.time() - start))
    data = gson.toJson(data)
    timeList.append('Prev dumps: ' + str(time.time() - start))
    res1 = XMLJSONConverter.jsonToXml(data)
    timeList.append('Finish getData: ' + str(time.time() - start))
#     print timeList
    #raise Exception(timeList)
    return JythonDTO(res1, None)

    # Определяем список полей таблицы для отображения

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    start = time.time()
    tasks = view_task_linksCursor(context)
    gson = Gson()
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session, 1, 55, 75)
    session = json.loads(session)["sessioncontext"]

    if "formData" in session["related"]["xformsContext"]:
        dateTo = None
        dateFrom = None
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = info["@task"]
        processName = info["@process"]
        assignee = info["@assignee"]
        if info["@dateFrom"]:
            dateFrom = info["@dateFrom"]
        if info["@dateTo"]:
            dateTo = info["@dateTo"]
    else:
        taskName = '%'
        processName = '%'
        assignee = None
        dateTo = None
        dateFrom = None


    whereClause = """processName like '%%%s%%' and name_ like '%%%s%%'"""%(processName,taskName)
    if assignee is not None and assignee != '':
        whereClause += """and assignee_ like '%%%s%%'""" % (assignee)
    if dateFrom is not None:
        whereClause += """and create_time_ > '%s'"""%(dateFrom)
    if dateTo is not None:
        whereClause += """and create_time_ < '%s'"""%(dateTo)

    tasks.setComplexFilter(whereClause)

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
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": tasks.count(),
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
    settings = gson.toJson(settings)
    res2 = XMLJSONConverter.jsonToXml(settings)
    #    raise Exception(time.time() - start)
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
