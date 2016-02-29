# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus
'''

import simplejson as json
from common.sysfunctions import toHexForXml, getGridWidth, getGridHeight
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from java.text import SimpleDateFormat
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

import time

from com.google.gson import Gson

from workflow._workflow_orm import view_finished_tasksCursor

def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех развернутых процессов. '''
    start = time.clock()
    tasks = view_finished_tasksCursor(context)
    session = json.loads(session)
    session = session["sessioncontext"]
    activiti = ActivitiObject()
    inputFormat = SimpleDateFormat("yyyy-MM-dd hh:mm:ss")
    sid = session["sid"]
#     данные по умолчанию, просто, чтобы фильтр ниже не менять

    if "formData" in session["related"]["xformsContext"]:
        dateFrom = None
        dateTo = None
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = info["@task"]
        processName = info["@process"]
        if info["@dateFrom"]:
            dateFrom = info["@dateFrom"]
        if info["@dateTo"]:
            dateTo = info["@dateTo"]
    else:
        taskName = '%'
        processName = '%'
        dateFrom = None
        dateTo = None
#     парсим дату в формат, который понимает активити

    
    
    

    tasks.setFilter('end_time_','!null')
    tasks.setRange('assignee_',sid)
    whereClause = """processName like '%%%s%%' and name_ like '%%%s%%' """%(processName,taskName)
    if dateFrom is not None:
        whereClause += """and end_time_ > '%s'"""%(dateFrom)
    if dateTo is not None:
        whereClause += """and end_time_ < '%s'"""%(dateTo)
    tasks.setComplexFilter(whereClause)
    tasks.orderBy('end_time_')
    tasks.limit(firstrecord-1,pagesize)    

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "description":[u"Описание процесса"],
               "endTime": [u"Дата завершения"],
               "comment": [u'Комментарий'],
               "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))


    # Проходим по таблице и заполняем data
    for task in tasks.iterate():
        procDict = {}
        procDict[_header["id"][1]] = task.id_
        procDict[_header["process"][1]] = task.processName
        procDict[_header["description"][1]] = task.processDescription
        procDict[_header["name"][1]] = task.name_
        procDict[_header["endTime"][1]] = SimpleDateFormat("HH:mm dd.MM.yyyy").format(task.end_time_)
        procDict[_header["comment"][1]] = ' '.join([comment.getFullMessage() for comment in activiti.taskService.getTaskComments(task.id_)])
        data["records"]["rec"].append(procDict)
    gson = Gson()
    data = gson.toJson(data)
    res1 = XMLJSONConverter.jsonToXml(data)
    print time.clock() - start
    return JythonDTO(res1, None)

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    # Определяем список полей таблицы для отображения
    session = json.loads(session)
#     gridWidth = getGridWidth(session, 60)
    gridWidth = "100%"
    gridHeight = getGridHeight(session, 1)
    tasks = view_finished_tasksCursor(context)
    sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")
    session = session['sessioncontext']
    if "formData" in session["related"]["xformsContext"]:
        dateFrom = None
        dateTo = None
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        taskName = info["@task"]
        processName = info["@process"]
        if info["@dateFrom"]:
#             dateFrom = info["@dateFrom"].replace('T', ' ')
            dateFrom = info["@dateFrom"]
        if info["@dateTo"]:
#             dateTo = info["@dateTo"].replace('T', ' ')
            dateTo = info["@dateTo"]
    else:
        taskName = '%'
        processName = '%'
        dateFrom = None
        dateTo = None
#     raise Exception(dateTo, dateFrom)
    _header = {"id":["~~id"],
               "name":[u"Название задачи"],
               "process": [u"Название процесса"],
               "description":[u"Описание процесса"],
               "endTime": [u"Дата завершения"],
               "comment": [u'Комментарий'],
               "properties":[u"properties"]}
#     парсим дату в формат, который понимает активити


    sid = session["sid"]
    tasks.setFilter('end_time_','!null')
    tasks.setRange('assignee_',sid)
    whereClause = """processName like '%%%s%%' and name_ like '%%%s%%' """%(processName,taskName)
    if dateFrom is not None:
        whereClause += """and end_time_ > '%s'"""%(dateFrom)
    if dateTo is not None:
        whereClause += """and end_time_ < '%s'"""%(dateTo)
    
#     raise Exception(whereClause) 
    tasks.setComplexFilter(whereClause)    
    
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": tasks.count(),
                                               "@profile":"default.properties"}
                                }
    print tasks.count()
    # Добавляем поля для отображения в gridsettings
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["link"][0],
#                                                        "@width": "55px",
#                                                        "type": "IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "250px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["process"][0], "@width": "250px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["endTime"][0], "@width": "105px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["comment"][0], "@width": "250px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["type"][0], "@width": "100px"})
#     settings["gridsettings"]["columns"]["col"].append({"@id":_header["shift"][0], "@width": "150px"})

    gson = Gson()
    settings = gson.toJson(settings)
    res2 = XMLJSONConverter.jsonToXml(settings)

    return JythonDTO(None, res2)
