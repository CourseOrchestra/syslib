# coding: utf-8

import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from workflow._workflow_orm import formCursor

try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult




def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех форм процесса развернутых процессов. '''
    session = json.loads(session)
    processKey = session['sessioncontext']['related']['gridContext']['currentRecordId']
    form = formCursor(context)
    
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "version":[u"Версия"],
             "file":[u"Файл"],
             "schema":[u"Схема"],
             "startProcess":[u"Старт процесса"],
             "properties":[u"properties"],
             "link":[u"Ссылка"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
        
    form.setRange('processKey',processKey)
    # Проходим по таблице и заполняем data    
    for form in form.iterate():
        procDict = {}
        procDict[_header["id"][1]] = form.id
        procDict[_header["name"][1]] = form.id
        procDict[_header["link"][1]] = form.link        
        procDict[_header["properties"][1]] = {}
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "800px",
                                               "@gridHeight": "300",
                                               "@totalCount": form.count(),
                                               "@profile":"default.properties"},
                                "labels":{"header":"Формы процесса"}
                                }
    # Добавляем поля для отображения в gridsettings
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["link"][0], "@width": "100px"})
    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    session = json.loads(session)
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "processesGrid":
            processKey = gridContext["currentRecordId"]
        if gridContext["@id"] == "processFormsGrid":
            if 'currentRecordId' in gridContext:
                style = "false"
            else:
                style = "true"

    data = {"gridtoolbar":{"item":[]}}

    
    data["gridtoolbar"]["item"].append({ "@text":"Добавить форму",
                                        "@hint":"Добавление формы процесса",
                                        "@disable": "false",
                                        "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Добавление формы",
                                                                             "@height": "300",
                                                                             "@width": "500"
                                                                             }
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "processFormCard",
                                                                                       "add_context":"add"}
                                                                           }
                                                              }
                                                             ]
                                                  }
                                        })
    data["gridtoolbar"]["item"].append({"@text":"Редактировать форму",
                                        "@hint":"Редактирование формы процесс",
                                        "@disable": style,
                                        "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Редактирование формы",
                                                                             "@height": "300",
                                                                             "@width": "500"}
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "processFormCard",
                                                                                       "add_context":"edit"}
                                                                           }
                                                              }]
                                                  }
                                        })

    return XMLJSONConverter.jsonToXml(json.dumps(data))


