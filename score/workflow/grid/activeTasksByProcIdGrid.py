# coding: utf-8

'''
Created on 10.11.2014

@author: m.prudyvus

все активные задачи выбранного процесса
'''

import simplejson as json
import os
from common.sysfunctions import toHexForXml, getGridWidth, getGridHeight
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, parse_json, functionImport
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor

def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session, 1)
    session = session["sessioncontext"]
    activiti = ActivitiObject()
    if isinstance(session['urlparams']['urlparam'], list):
        for params in session['urlparams']['urlparam']:
            if params['@name'] == 'processId':
                processInstanceId = params['@value'][0]
    roles = RolesCursor(context)
    u'''получение данных из фильтра'''
    processName = ''
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
#         processName = ' '.join(info["@process"].split())
        user = ' '.join(info["@assignee"].split())
    else:
        taskName = '%'
        processName = ''
        user = ''

#     активные задачи
    tasksList = activiti.taskService.createTaskQuery().processInstanceId(processInstanceId)\
                    .taskNameLike(taskName).list()

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
               "schema":[u"Схема"],
               "name":[u"Название задачи"],
#                "assign":[u"Принять"],
               "process": [u"Название процесса"],
               "description": [u"Описание процесса"],
#                "document": [u"Документ"],
#                "reassign": [u"Передать задачу"],
               "userAss": [u"Назначена на"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

    runtimeService = activiti.runtimeService
    taskService = activiti.taskService

    filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'datapanelSettings.json')
    datapanelSettings = parse_json(filePath)["specialFunction"]["getUserName"]
    function = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))

#     Проходим по таблице и заполняем data
    for task in tasksList:
#         смотрим связи задачи
        identityLinks = taskService.getIdentityLinksForTask(task.id)
        taskDict = {}
#         отображается немного разное в зав-ти юзер или группа
        for link in identityLinks:
            if link.userId is not None:
                if not (link.type == 'candidate' and _header["userAss"][1] in taskDict):
                    taskDict[_header["userAss"][1]] = function(context, link.userId)
            else:
                roles.get(link.groupId)
                taskDict[_header["userAss"][1]] = u"""Группа "%s\"""" % roles.description

        taskDict[_header["id"][1]] = task.id
        processInstanceId = task.getProcessInstanceId()
#         procDesc = activiti.runtimeService.getVariable(processInstanceId, 'processDescription')
#         if procDesc is not None:
#             taskDict[_header["description"][1]] = procDesc
#         else:
#             taskDict[_header["description"][1]] = ''
#         получаем процесс, чтобы потом получить его имя
        process = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(task.getProcessDefinitionId()).singleResult()
        docName = "%s. %s" % (runtimeService.getVariable(processInstanceId, 'docId'), \
                              runtimeService.getVariable(processInstanceId, 'docName'))
#         taskDict[_header["process"][1]] = "%s: %s" % (process.name, docName)
#         картинка, по нажатию переходим на схему

        taskDict[_header["schema"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": "./?userdata=%s&mode=image&processId=%s" \
                                                % (session["userdata"], processInstanceId,),
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/flowblock.png"}}}}

        taskDict[_header["name"][1]] = task.name
        taskDict[_header["properties"][1]] = {"event":
                                              []}
#         if taskDict[_header["userAss"][1]] != logins.userName:
#             taskDict[_header["assign"][1]] = {"div":
#                                                 {"@align": "center",
#                                                  "@class": "gridCellCursor",
#                                                  "img":
#                                                     {"@src": "solutions/default/resources/imagesingrid/ok.png"}}}
#             taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
#                                                                 "@column": _header["assign"][0],
#                                                                 "action":
#                                                                     {"#sorted":
#                                                                      [{"main_context": 'current'},
#                                                                       {"server":
#                                                                        {"activity":
#                                                                         {"@id": "assign",
#                                                                          "@name": "workflow.grid.activeTasksGrid.assign.celesta",
#                                                                          "add_context": task.id}}},
#                                                                       {"datapanel":
#                                                                         {'@type':"current",
#                                                                          '@tab':"current",
#                                                                          'element':
#                                                                             {'@id':'tasksGrid'}}}]}})
#         else:
#             taskDict[_header["assign"][1]] = ""
#         taskDict[_header["document"][1]] = {"div":
#                                             {"@align": "center",
#                                              "a":
#                                              {"@href": "./?mode=task&processId=%s&taskId=%s" % (processInstanceId, task.id),
#                                               "@target": "_blank",
#                                               "img":
#                                                 {"@src": "solutions/default/resources/play.png"}}}} \
#                                                     if taskDict[_header["userAss"][1]] == logins.userName else ""

#         if len(identityLinks) > 1:
#             taskDict[_header["reassign"][1]] = {"div":
#                                                 {"@align": "center",
#                                                  "@class": "gridCellCursor",
#                                                  "img":
#                                                     {"@src": "solutions/default/resources/imagesingrid/user.png"}}}
#             taskDict[_header["properties"][1]]["event"].append({"@name":"cell_single_click",
#                                                                 "@column": _header["reassign"][0],
#                                                                 "action":
#                                                                     {"@show_in": "MODAL_WINDOW",
#                                                                      "#sorted":
#                                                                      [{"main_context": 'current'},
#                                                                       {"modalwindow":
#                                                                           {"@caption": "Выбор пользователя"
#                                                                            }
#                                                                         },
#                                                                       {"datapanel":
#                                                                         {'@type':"current",
#                                                                          '@tab':"current",
#                                                                          'element':
#                                                                             {'@id':'reassign'}}}]}})
#         else:
#             taskDict[_header["reassign"][1]] = ""

        if (processName == '' or processName in taskDict[_header["process"][1]]) and user in taskDict[_header["userAss"][1]]:
            data["records"]["rec"].append(taskDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": len(data["records"]["rec"]),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0],
                                                       "@width": "40px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["assign"][0],
#                                                        "@width": "60px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["reassign"][0],
#                                                        "@width": "85px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["document"][0],
#                                                        "@width": "60px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0],
                                                       "@width": "215px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0],
#                                                        "@width": "500px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["userAss"][0],
                                                       "@width": "100px"})

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)),
                     XMLJSONConverter.jsonToXml(json.dumps(settings)))

# def assign(context, main, add=None, filterinfo=None, session=None, elementId=None):
#     sid = json.loads(session)['sessioncontext']["sid"]
#     activiti = ActivitiObject()
#     activiti.taskService.claim(add, sid)
#     context.message(u'Задача взята на исполнение')
