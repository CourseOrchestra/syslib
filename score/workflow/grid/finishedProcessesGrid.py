# coding: utf-8

'''
Created on 31.10.2014

@author: tr0glo)|(I╠╣
'''


import json
from com.google.gson import Gson
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from common.sysfunctions import getGridWidth, getGridHeight
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

from workflow._workflow_orm import view_finished_processCursor


import time

def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех запущенных процессов. '''
    start = time.clock()
    gson = Gson()

    session = json.loads(session)

    session = session['sessioncontext']
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        processName = info["@processName"]
        description = info["@processDescription"]
    else:
        processName = ''
        description = ''

    procInstance = view_finished_processCursor(context)
    procInstance.setFilter('end_time','!null')
    procInstance.setComplexFilter("""processName like '%%%s%%' and processDescription like '%%%s%%' """%(processName,description))
    procInstance.limit(firstrecord-1,pagesize)

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "schema":[u"Схема"],
             "reason":[u"Причина завершения"],
             "version":[u"Версия"],
             "properties":[u"properties"],
             "comment":[u"Комментарий"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    #raise Exception(processesList)
    for process in procInstance.iterate():
        procDict = {}
        procDict[_header["id"][1]] = process.id_
        procDict[_header["pid"][1]] = process.id_
        procDesc = process.processDescription
        procDict[_header["description"][1]] = procDesc
        procDict[_header["name"][1]] = process.processName
        procDict[_header["reason"][1]] = process.delete_reason
#         procDict[_header["schema"][1]] =   {"link": {  "@href":"./?mode=image&processId="+process.getId()+"",
#                                                      "@image":"solutions/default/resources/flowblock.png",
#                                                      "@text":"Схема",
#                                                      "@openInNewTab":"true"
#                                                      }
#                                            }

        #procDict[_header["description"][1]] = process.description
        #procDict[_header["version"][1]] = process.version
        procDict[_header["properties"][1]] = {"event":
                                              [
                                                {"@name":"row_single_click",
                                                                 "action":
                                                                    {"#sorted":[{"main_context": "current"},
                                                                                 {"datapanel":
                                                                                    {'@type':"current",
                                                                                     '@tab':"current",
                                                                                     "element": {"@id":"finishedProcessEventsGrid",
                                                                                                 "add_context": ''}
                                                                                     }
                                                                                }]}
                                                                 }
                                               ]
                                              }
        data["records"]["rec"].append(procDict)


    # Добавляем поля для отображения в gridsettings
    data = gson.toJson(data)
    res1 = XMLJSONConverter.jsonToXml(data)

    print time.clock() - start
    return JythonDTO(res1, None)


def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    # Определяем список полей таблицы для отображения
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session, 2, 55, 80)

    session = json.loads(session)
    session = session['sessioncontext']
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        processName = info["@processName"]
        description = info["@processDescription"]
    else:
        processName = ''
        description = ''

    procInstance = view_finished_processCursor(context)
    procInstance.setFilter('end_time','!null')
    procInstance.setComplexFilter("""processName like '%%%s%%' and processDescription like '%%%s%%' """%(processName,description))
    
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "schema":[u"Схема"],
             "reason":[u"Причина завершения"],
             "version":[u"Версия"],
             "properties":[u"properties"],
             "comment":[u"Комментарий"]}   
    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))    


    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": procInstance.count(),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["reason"][0], "@width": "300px"})

    gson = Gson()
    settings = gson.toJson(settings)
    res2 = XMLJSONConverter.jsonToXml(settings)

    return JythonDTO(None, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":{}}}


#     data["gridtoolbar"]["item"].append({ "@text":"Остановить",
#                                         "@hint":"Остановить процесс",
#                                         "@disable": style,
#                                         "action":{"@show_in": "MODAL_WINDOW",
#                                                   "#sorted":[{"main_context":"current"},
#                                                              {"modalwindow":{"@caption": "Остановка процесса"
#                                                                              }
#                                                               },
#                                                              {"datapanel":{"@type": "current",
#                                                                            "@tab": "current",
#                                                                            "element": {"@id": "suspendProcessCard"}
#                                                                            }
#                                                               }
#                                                              ]
#                                                   }
#                                         })



    return XMLJSONConverter.jsonToXml(json.dumps(data))

