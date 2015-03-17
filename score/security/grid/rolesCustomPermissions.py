# coding: utf-8

import simplejson as json
import base64
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml, getGridHeight, getGridWidth
from ru.curs.celesta.syscursors import RolesCursor
from security._security_orm import rolesCustomPermsCursor
from security.functions import Settings

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''

    # Создание экземпляра курсора разрешения
    roles = RolesCursor(context)
    rolesPermissions = rolesCustomPermsCursor(context)
    if 'currentRecordId' in session:     
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        rolesPermissions.setRange("permissionId", currId)
    rolesPermissions.orderBy("roleid")
    # Определяем переменную для JSON данных

    data = {"records":{"rec":[]}}
    columnsDict={u"Роль":"roleid",
                 u"Описание":"roleid"}
    for column in sortColumnList:
        sortindex = '%s' % column.getSorting()
        rolesPermissions.orderBy(columnsDict[column.getId()] +' '+sortindex)
    
    # Проходим по таблице и заполняем data    
    for rolesPermissions in rolesPermissions.iterate():
        roles.get(rolesPermissions.roleid)
        permDict = {}
        #permDict[toHexForXml('~~id')] = base64.b64encode(json.dumps([roles.id, rolesPermissions.permissionId]))
        permDict[toHexForXml('~~id')] = roles.id
        permDict[u"Роль"] = roles.id
        permDict[u"Описание"] = roles.description        
        permDict['properties'] = {"event":{"@name":"row_single_click",
                                           "action":{"#sorted":[{"main_context": 'current'},
                                                                {"datapanel":{'@type':"current",
                                                                              '@tab':"current"}
                                                                 }]
                                                     }
                                           }
                                  }
        data["records"]["rec"].append(permDict)


    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)

def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''

    # Курсор таблицы directories
    rolesPermissions = rolesCustomPermsCursor(context)    
    if 'currentRecordId' in session:     
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        rolesPermissions.setRange("permissionId", currId)
    # Вычисляем количества записей в таблице
    totalcount = rolesPermissions.count()
    # Заголовок таблицы
    header = "Роли"
    # В случае если таблица пустая
    if totalcount == 0 or totalcount is None:
        totalcount = "0"
        header = header + " ПУСТ"
        
    sec_settings = Settings()

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50",
                   "@gridWidth": getGridWidth(session),
                   "@gridHeight":getGridHeight(session, numberOfGrids = 1 if sec_settings.loginIsSubject() else 2, delta=250),
                   "@totalCount": totalcount,
                   "@profile":"default.properties"},
    "labels":{"header":header}
    }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":"Роль", "@width": "80px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Описание", "@width": "400px"})

    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    rolesPermissions = rolesCustomPermsCursor(context)

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext'][0]:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[]}}
    if rolesPermissions.canInsert():
        data["gridtoolbar"]["item"].append(
                                   {"@img": 'gridToolBar/addDirectory.png',
                                    "@text":"Добавить",
                                    "@hint":"Добавить",
                                    "@disable": "false",
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Добавление роли",
                                                                         "@height": "300",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "rolesCustomPermissionsXforms",
                                                                                   "add_context":"add"}
                                                                       }
                                                          }]
                                              }
                                    })
    if rolesPermissions.canModify():
        data["gridtoolbar"]["item"].append(
                                   {"@img": 'gridToolBar/editDocument.png',
                                    "@text":"Редактировать",
                                    "@hint":"Редактировать",
                                    "@disable": style,
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Редактирование роли",
                                                                         "@height": "300",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "rolesCustomPermissionsXforms",
                                                                                   "add_context":"edit"}
                                                                       }
                                                          }]
                                              }
                                    })
    if rolesPermissions.canDelete():
        data["gridtoolbar"]["item"].append(
                                   {"@img": 'gridToolBar/deleteDocument.png',
                                    "@text":"Удалить",
                                    "@hint":"Удалить",
                                    "@disable": style,
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Удаление роли",
                                                                         "@height": "300",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "rolesCustomPermissionsXformDelete",
                                                                                   "add_context":"delete"}
                                                                       }
                                                          }]
                                              }
                                    })
    
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowDown.png',
                                            "@text":"Скачать",
                                            "@hint":"Скачать роли в xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Скачать роли",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "rolesCustomPermissionsDownloadXform",
                                                                                           "add_context":"download"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )    
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowUp.png',
                                            "@text":"Загрузить",
                                            "@hint":"Загрузить роли из xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Загрузить роли",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "rolesCustomPermissionsUploadXform",
                                                                                           "add_context":"upload"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )

    return XMLJSONConverter.jsonToXml(json.dumps(data))

