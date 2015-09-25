# coding: utf-8

import json
import base64
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml, getGridHeight, getGridWidth
from ru.curs.celesta.syscursors import RolesCursor
from security._security_orm import rolesCustomPermsCursor
from security.functions import Settings

try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.app.api.grid import GridSaveResult
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
    #rolesPermissions.limit(firstrecord-1, pagesize)
    #rolesPermissions.orderBy("roleid")
    roles.limit(firstrecord-1, pagesize)
    roles.orderBy("id")
    # Определяем переменную для JSON данных

    data = {"records":{"rec":[]}}
    columnsDict={"exists":[u" "],
                 "roleId":[u"Роль"],
                 "description":[u"Описание"],
                 "properties":[u"properties"],
                 "id":["~~id"]}
    for column in columnsDict:
        columnsDict[column].append(toHexForXml(columnsDict[column][0]))

    if len(sortColumnList) > 0:
        sortName = sortColumnList[0].id
        sortType = unicode(sortColumnList[0].sorting).lower()
    else:
        sortName = None
    # Проходим по таблице и заполняем data    
    if roles.tryFindSet():
        while True:
            permDict = {}
            permDict[columnsDict["id"][1]] = json.dumps({"permission":currId,
                                                         "role":roles.id})
            permDict[columnsDict["roleId"][1]] = roles.id
            permDict[columnsDict["description"][1]] = roles.description
            rolesPermissions.setRange("roleid", roles.id)
            permDict[columnsDict["exists"][1]] = rolesPermissions.count()>0 if rolesPermissions.count() else ''
            permDict[columnsDict["properties"][1]] = {"event":{"@name":"row_single_click",
                                                               "action":{"#sorted":[{"main_context": 'current'},
                                                                    {"datapanel":{'@type':"current",
                                                                                  '@tab':"current"}
                                                                     }]
                                                         }
                                               }
                                      }
            
            data["records"]["rec"].append(permDict)
            if not roles.nextInSet():
                    break
    
    data["records"]["rec"].sort(key=lambda x: (not x[columnsDict["exists"][1]],x[columnsDict["roleId"][1]],))
    for column in columnsDict:
        if sortName == columnsDict[column][0]:
            keyField = column if sortName else 'exists'
            data["records"]["rec"].sort(key=lambda x: (x[columnsDict["%s" % keyField][1]]),reverse=(sortType=='desc'))
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
    columnsDict={"exists":[u" "],
                 "roleId":[u"Роль"],
                 "description":[u"Описание"],
                 "properties":[u"properties"]}
    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50",
                   "@gridWidth": getGridWidth(session),
                   "@gridHeight":getGridHeight(session, numberOfGrids = 1 if sec_settings.loginIsSubject() else 2, delta=250),
                   "@totalCount": totalcount,
                   "@profile":"editableGrid.properties"},
    "labels":{"header":header}
    }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":columnsDict["exists"][0], "@width": "15px",
                                                       "@readonly":"false",
                                                       "@editor":"{ editor: 'checkbox'}"})
    settings["gridsettings"]["columns"]["col"].append({"@id":columnsDict["roleId"][0], "@width": "80px",
                                                       "@readonly":"true"})
    settings["gridsettings"]["columns"]["col"].append({"@id":columnsDict["description"][0], "@width": "400px",
                                                       "@readonly":"true"})
    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    data = {"gridtoolbar":{"item":[]}}
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

def gridSaveRecord(context=None, main=None, add=None, session=None, filterinfo=None, elementId=None, saveData=None):
    saveData = json.loads(saveData)["savedata"]["data"]
    rolesPermissions = rolesCustomPermsCursor(context)
    roleId = saveData["col2"]
    permissionId = json.loads(saveData["id"])["permission"]
    if rolesPermissions.tryGet(roleId, permissionId) and not saveData["col1"]:
        if not saveData["col1"]:
            if rolesPermissions.canDelete():
                rolesPermissions.delete()
            else:
                context.error(u"Недостаточно прав для данной операции!")
    else:
        if saveData["col1"]:
            rolesPermissions.roleid = roleId
            rolesPermissions.permissionId = permissionId
            if rolesPermissions.canInsert():
                rolesPermissions.insert()
            else:
                context.error(u"Недостаточно прав для данной операции!")
    res = GridSaveResult()
    res.setRefreshAfterSave(0)
    return res