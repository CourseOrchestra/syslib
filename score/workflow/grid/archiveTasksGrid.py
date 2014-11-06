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
from java.text import SimpleDateFormat
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    session = json.loads(session)["sessioncontext"]
    inputFormat = SimpleDateFormat("yyyy-MM-dd hh:mm:ss")
#     данные по умолчанию, просто, чтобы фильтр ниже не менять
    dateFrom = '0001-01-01 00:00:00'
    dateTo = '9999-12-31 23:59:59'
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = "%%%s%%" % ' '.join(info["@task"].split())
        processName = ' '.join(info["@process"].split())
        if info["@dateFrom"]:
            dateFrom = info["@dateFrom"].replace('T', ' ')
        if info["@dateTo"]:
            dateTo = info["@dateTo"].replace('T', ' ')
    else:
        taskName = '%'
        processName = ''

#     парсим дату в формат, который понимает активити
    endTimeFrom = SimpleDateFormat.parse(inputFormat, dateFrom)
    endTimeTo = SimpleDateFormat.parse(inputFormat, dateTo)

    sid = session["sid"]
    activiti = ActivitiObject()
    historyService = activiti.historyService

    tasksList = historyService.createHistoricTaskInstanceQuery()\
                                .taskAssignee(sid).finished()\
                                .taskNameLike(taskName)\
                                .taskCompletedAfter(endTimeFrom)\
                                .taskCompletedBefore(endTimeTo)\
                                .orderByHistoricTaskInstanceEndTime().desc().list()

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
#                "schema":[u"Схема"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
#                "link": [u"Документ"],
               "endTime": [u"Дата завершения"],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))


    # Проходим по таблице и заполняем data
    for task in tasksList:
        procDict = {}
        procDict[_header["id"][1]] = task.getId()
        processInstanceId = task.getProcessInstanceId()
        processInstance = activiti.runtimeService.createProcessInstanceQuery()\
            .processInstanceId(processInstanceId).singleResult()
        if processInstance is None:
            processInstance = activiti.historyService.createHistoricProcessInstanceQuery()\
                .processInstanceId(processInstanceId).singleResult()

        processDefinition = activiti.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(processInstance.getProcessDefinitionId()).singleResult()
        historicVariables = activiti.historyService.createHistoricVariableInstanceQuery()\
            .processInstanceId(processInstanceId)
        docName = "%s. %s" % (historicVariables.variableName('docId').singleResult().textValue, \
                              historicVariables.variableName('docName').singleResult().textValue)
        procDict[_header["process"][1]] = "%s: %s" % (processDefinition.getName(), docName)
        procDict[_header["name"][1]] = task.getName()
#         procDict[_header["shift"][1]] = tasks.getDeleteReason()
        procDict[_header["endTime"][1]] = SimpleDateFormat("HH:mm dd.MM.yyyy").format(task.getEndTime())

        if processName == '' or processName in procDict[_header["process"][1]]:
            data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "1300px",
                                               "@gridHeight": "500",
                                               "@totalCount": len(tasksList),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["link"][0],
#                                                        "@width": "55px",
#                                                        "type": "IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "250px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0], "@width": "600px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["endTime"][0], "@width": "150px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["type"][0], "@width": "100px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["shift"][0], "@width": "150px"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)
