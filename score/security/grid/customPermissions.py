# coding: utf-8

import simplejson as json
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml, getGridHeight, getGridWidth
from security._security_orm import customPermsCursor
from security.functions import Settings

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''
    # Создание экземпляра курсора разрешения
    permissions = customPermsCursor(context)
    if 'formData' in session:
        typeId = json.loads(session)['sessioncontext']['related']['xformsContext']['formData']['schema']['permission']['@type']
        if typeId<>'':
            permissions.setRange('type', typeId)
    
    permissions.limit(firstrecord-1, pagesize)
    permissions.orderBy('name')

    # Определяем переменную для JSON данных
    data = {"records":{"rec":[]}}
    # Проходим по таблице и заполняем data
    columnsDict={u"Разрешение":"name",
                 u"Описание":"description",
                 u"Тип": "type"}
    for column in sortColumnList:
        sortindex = '%s' % column.getSorting()        
        permissions.orderBy(columnsDict[column.getId()] +' '+sortindex)
    for permissions in permissions.iterate():
        permDict = {}
        permDict[toHexForXml('~~id')] = permissions.name
        permDict[u"Разрешение"] = permissions.name
        permDict[u"Описание"] = permissions.description
        permDict[u"Тип"] = permissions.type
        permDict['properties'] = {"event":{"@name":"row_single_click",
                                           "action":{"#sorted":[{"main_context": 'current'},
                                                                {"datapanel":{'@type':"current",
                                                                              '@tab':"current",
                                                                              "element":{"@id":"rolesCustomPermissionsGrid"}
                                                                              }
                                                                 }]
                                                     }
                                           }
                                  }
        data["records"]["rec"].append(permDict)


    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)

def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''

    # Курсор таблицы permissions
    permissions = customPermsCursor(context)
    # Вычисляем количества записей в таблице
    totalcount = permissions.count()
    # Заголовок таблицы
    header = "Разрешения"
    # В случае если таблица пустая
    if totalcount == 0 or totalcount is None:
        totalcount = "0"
        header = header + " ПУСТ"
    
    sec_settings = Settings()

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns":{"col":[]},
                                "properties":{"@pagesize":"50",
                                              "@gridWidth": getGridWidth(session),
                                              "@gridHeight":getGridHeight(session, numberOfGrids = 1 if sec_settings.loginIsSubject() else 2, delta=250),
                                              "@totalCount":totalcount,
                                              "@profile":"default.properties"},
                                "labels":{"header":header}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":"Разрешение", "@width": "120px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Описание", "@width": "240px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Тип", "@width": "120px"})
    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[]
                           }
            }
    # Курсор таблицы permissions
    permissions = customPermsCursor(context)

    if permissions.canInsert():
        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/addDirectory.png',
                                            "@text":"Добавить",
                                            "@hint":"Добавить",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Добавление типа разрешения",
                                                                                 "@height": "400",
                                                                                 "@width": "500"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "customPermissionsXforms",
                                                                                           "add_context":"add"}
                                                                               }
                                                                  }]
                                                      }
                                            })
    if permissions.canModify():
        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/editDocument.png',
                                            "@text":"Редактировать",
                                            "@hint":"Редактировать",
                                            "@disable": style,
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Редактирование типа разрешения",
                                                                                 "@height": "400",
                                                                                 "@width": "500"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "customPermissionsXforms",
                                                                                           "add_context":"edit"}
                                                                               }
                                                                  }]
                                                      }
                                            })
    if permissions.canDelete():
        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/deleteDocument.png',
                                            "@text":"Удалить",
                                            "@hint":"Удалить",
                                            "@disable": style,
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Удаление типа разрешения",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "customPermissionsXformDelete",
                                                                                           "add_context":"delete"}
                                                                               }
                                                                  }]
                                                      }
                                            })
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowDown.png',
                                            "@text":"Скачать",
                                            "@hint":"Скачать прочие разрешения в xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Скачать разрешения",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "customPermissionsDownloadXform",
                                                                                           "add_context":"download"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )    
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowUp.png',
                                            "@text":"Загрузить",
                                            "@hint":"Загрузить прочие разрешения из xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Загрузить разрешения",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "customPermissionsUploadXform",
                                                                                           "add_context":"upload"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )

    return XMLJSONConverter.jsonToXml(json.dumps(data))

