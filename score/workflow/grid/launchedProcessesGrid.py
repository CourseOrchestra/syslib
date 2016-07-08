# coding: utf-8

'''
Created on 27.10.2014

@author: tr0glo)|(I╠╣
'''

from com.google.gson import Gson
import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject

from workflow._workflow_orm import view_launched_processCursor

from common.sysfunctions import getGridWidth, getGridHeight

import time

try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех запущенных процессов. '''
    start = time.clock()

    # Извлечение фильтра из related-контекста
    session = json.loads(session)
    session = session['sessioncontext']
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        processName = info["@processName"]
        description = info["@processDescription"]
    else:
        processName = ''
        description = ''

    #Получения курсора активных процессов и применение к нему фильтров
    procInstance = view_launched_processCursor(context)
    procInstance.setComplexFilter("""processName like '%%%s%%' and processDescription like '%%%s%%' """%(processName,description))
    procInstance.limit(firstrecord-1,pagesize)


    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "schema":[u"Схема"],
             "stop":[u'Остановка'],
             "activeTasks":[u'Активные задачи'],
             "version":[u"Версия"],
             "properties":[u"properties"],
             "comment":[u"Комментарий"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    # raise Exception(processesList)
    for process in procInstance.iterate():
        procDict = {}
        procDict[_header["id"][1]] = process.id_
        procDict[_header["pid"][1]] = process.id_
        procDesc = process.processDescription
        if procDesc is not None:
            procDict[_header["description"][1]] = procDesc
        else:
            procDict[_header["description"][1]] = ''
        procDict[_header["name"][1]] = process.processName
        # Поле-ссылка для показа изображения процесса
        procDict[_header["schema"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": "./?userdata=%s&mode=image&processId=%s" % \
                                                            (session["userdata"], process.id_),
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/flowblock.png"}}}}
        # Поле-кнопка для остановки процесса
        procDict[_header["stop"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/stop.png"}}}
        procDict[_header["activeTasks"][1]] = {"div":
                                                {"@align": "center",
                                                 "a":
                                                 {"@href": "./?userdata=%s&mode=table&processId=%s" \
                                                            % (session["userdata"], process.id_),
                                                  "@target": "_blank",
                                                  "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/table.png"}}}}
        # procDict[_header["description"][1]] = process.description
        # procDict[_header["version"][1]] = process.version
        procDict[_header["properties"][1]] = {"event":
                                              [
                                                {"@name":"cell_single_click",
                                                "@column": _header["stop"][0],
                                                "action":
                                                     {"@show_in": "MODAL_WINDOW",
                                                      "#sorted":
                                                         [{"main_context":"current"},
                                                          {"modalwindow":
                                                             {"@caption": u"Остановка процесса",
                                                                       "@height": "250",
                                                                       "@width": "500"
                                                              }
                                                           },
                                                          {"datapanel":
                                                             {"@type": "current",
                                                              "@tab": "current",
                                                              "element":
                                                                 {"@id": "suspendProcessCard"
                                                                  }
                                                              }
                                                           }
                                                          ]
                                                      }
                                                },
                                                {"@name":"row_single_click",
                                                                 "action":
                                                                    {"#sorted":[{"main_context": "current"},
                                                                                 {"datapanel":
                                                                                    {'@type':"current",
                                                                                     '@tab':"current",
                                                                                     "element": {"@id":"launchedProcessesEventsGrid",
                                                                                                 "add_context": ''}
                                                                                     }
                                                                                }]}
                                                                 }
                                               ]
                                              }
        data["records"]["rec"].append(procDict)
    gson = Gson()
    data = gson.toJson(data)
    res1 = XMLJSONConverter.jsonToXml(data)
#     raise Exception(data)
    print time.clock() - start
    return JythonDTO(res1, None)

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    # Определяем список полей таблицы для отображения
#     gridWidth = getGridWidth(session, 60)
    gridWidth = "100%"
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
    procInstance = view_launched_processCursor(context)
    procInstance.setComplexFilter("""processName like '%%%s%%' and processDescription like '%%%s%%' """%(processName,description))
    

    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "schema":[u"Схема"],
             "stop":[u'Остановка'],
             "activeTasks":[u'Активные задачи'],
             "version":[u"Версия"],
             "properties":[u"properties"],
             "comment":[u"Комментарий"]}
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeight,
                                               "@totalCount": procInstance.count(),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0], "@width": "40px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["stop"][0], "@width": "50px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["activeTasks"][0], "@width": "50px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "300px"})
    # settings["gridsettings"]["columns"]["col"].append({"@id":_header["version"][0], "@width": "100px"})
    # settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "400px"})

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

