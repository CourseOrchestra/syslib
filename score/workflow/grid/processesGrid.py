# coding: utf-8

import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from workflow._workflow_orm import formCursor

from common.sysfunctions import getGridWidth, getGridHeight

try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult




def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех развернутых процессов. '''
    form = formCursor(context)
    activiti = ActivitiObject()
    # Получение списка развернутых процессов
    processesList = activiti.getActualVersionOfProcesses()
    # Извлечение фильтра из related-контекста
    # raise Exception(session)
    session = json.loads(session)
    gridWidth = getGridWidth(session, 60)
    gridHeigth = getGridHeight(session, 2, 55, 80)
    session = session['sessioncontext']
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        processName = info["@processName"]
    else:
        processName = ''
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "version":[u"Версия"],
             "stop":[u'Остановка'],
             "file":[u"Файл"],
             "schema":[u"Схема"],
             "startProcess":[u"Старт процесса"],
             "properties":[u"properties"]}
    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    for process in processesList:
        procDict = {}
        if processName.lower() not in process.name.lower():
            continue
        procDict[_header["id"][1]] = process.key
        procDict[_header["pid"][1]] = process.key
        procDict[_header["name"][1]] = process.name
        procDict[_header["description"][1]] = process.description
        procDict[_header["version"][1]] = process.version
        procDict[_header["file"][1]] = u'Загрузить'
        procDict[_header["stop"][1]] = {"div":
                                                {"@align": "center",
                                                 "@class": "gridCellCursor",
                                                 "img":
                                                    {"@src": "solutions/default/resources/imagesingrid/stop.png"}}}
        # Поле-ссылка для отрисовки изображения процесса
        procDict[_header["schema"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": "./?userdata=%s&mode=image&processKey=%s" % \
                                                    (session["userdata"], process.key),
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/flowblock.png"}}}}
        # Формирование ссылки для запуска процесса
        form.setRange('processKey', process.key)
        form.setRange('isStartForm', True)
        if form.tryFirst():  # Для процесса задана форма инициализации
            link = form.link
            link = link.replace("$[processKey]", process.key)
        else:  # Стандартная форма инициализации процесса
            link = "./?userdata=%s&mode=process&processKey=%s" % (session["userdata"], process.key)
        procDict[_header["startProcess"][1]] = {"div":
                                            {"@align": "center",
                                             "a":
                                             {"@href": link,
                                              "@target": "_blank",
                                              "img":
                                                {"@src": "solutions/default/resources/imagesingrid/play.png"}}}}


        procDict[_header["properties"][1]] = {"event":[{"@name":"row_single_click",
                                         "action":{"#sorted":[{"main_context": 'current'},
                                                              {"datapanel":{'@type':"current",
                                                                            '@tab':"current",
                                                                            'element':{'@id':'processFormsGrid'}
                                                                            }
                                                               }]
                                                   }
                                         },
                                                       {"@name":"cell_single_click",
                                                "@column": _header["stop"][0],
                                                "action":
                                                     {"@show_in": "MODAL_WINDOW",
                                                      "#sorted":
                                                         [{"main_context":"current"},
                                                          {"modalwindow":
                                                             {"@caption": "Остановка процесса"
                                                              }
                                                           },
                                                          {"server":
                                                           {"activity":
                                                            {"@id": "stop",
                                                             "@name": "workflow.grid.processesGrid.stopAll.celesta",
                                                             "add_context": ""}}}
                                                          ]
                                                      }
                                                }]
                                }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}

    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": gridHeigth,

                                               "@totalCount": len(processesList),
                                               "@profile":"default.properties"}
                                }
    if add is not None:
        settings["gridsettings"]["properties"]["@autoSelectRecordUID"] = add
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0], "@width": "40px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["startProcess"][0], "@width": "40px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["stop"][0], "@width": "40px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["version"][0], "@width": "100px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["file"][0], "@width": "100px", "@type":"DOWNLOAD", "@linkId":"2"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[]}}


#     data["gridtoolbar"]["item"].append({ "@text":"Схема",
#                                         "@hint":"Схема процесса",
#                                         "@disable": style,
#                                         "action":{"@show_in": "MODAL_WINDOW",
#                                                   "#sorted":[{"main_context":"current"},
#                                                              {"modalwindow":{"@caption": "Схема процесса"
#                                                                              }
#                                                               },
#                                                              {"datapanel":{"@type": "current",
#                                                                            "@tab": "current",
#                                                                            "element": {"@id": "processesImage"}
#                                                                            }
#                                                               }
#                                                              ]
#                                                   }
#                                         })
    data["gridtoolbar"]["item"].append({"@text":"Развернуть",
                                        "@hint":"Развернуть процесс",
                                        "@disable": "false",
                                        "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Загрузить процесс",
                                                                             "@height": "300",
                                                                             "@width": "500"}
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "processUploadCard"}
                                                                           }
                                                              }]
                                                  }
                                        })

    return XMLJSONConverter.jsonToXml(json.dumps(data))

def downloadProcFile(context, main=None, add=None, filterinfo=None, session=None, elementId=None, recordId=None):
    u'''Процедура скачивание файла процесса.'''

    activiti = ActivitiObject()
    process = activiti.getProcessDefinition(recordId)
    fileName = process.resourceName
    data = activiti.getProcessXml(recordId)
    return JythonDownloadResult(data, fileName)

def stopAll(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    activiti = ActivitiObject()
    activePerocess = activiti.runtimeService.createProcessInstanceQuery().active().list()
    for activeProcess in activePerocess:
        activiti.runtimeService.stopProcess(activeProcess.getId())