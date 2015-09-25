# coding: utf-8

import json
import base64
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml, getGridHeight, getGridWidth
from ru.curs.celesta.syscursors import PermissionsCursor
from security._security_orm import tablesPermissionsViewCursor

try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.app.api.grid import GridSaveResult
except:
    from ru.curs.celesta.showcase import JythonDTO

def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[], firstrecord=0, pagesize=50):    
    u'''Функция получения данных для грида. '''
    
    #raise Exception(firstrecord)

    # Создание экземпляра курсора разрешения
    permissions = tablesPermissionsViewCursor(context)    
    
    if 'formData' in session:        
        role = json.loads(session)["sessioncontext"]["related"]["xformsContext"]["formData"]["schema"]["roleid"]
        grain = json.loads(session)["sessioncontext"]["related"]["xformsContext"]["formData"]["schema"]["grainid"]
        table = json.loads(session)["sessioncontext"]["related"]["xformsContext"]["formData"]["schema"]["tablename"]
        if role<>"":
            permissions.setRange("roleid", role)
        if grain<>"":
            permissions.setRange("grainid", grain)
        if table<>"":
            permissions.setRange("tablename", table)
        
    permissions.orderBy('roleid','grainid','tablename')

    # Определяем переменную для JSON данных
    data = {"records":{"rec":[]}}
    columnsDict={u"Роль":"roleid",
                 u"Гранула":"grainid",
                 u"Таблица":"tablename",
                 u"Доступ на чтение":"r",
                 u"Доступ на добавление":"i",
                 u"Доступ на редактирование":"m",
                 u"Доступ на удаление":"d"}
    for column in sortColumnList:
        sortindex = '%s' % column.getSorting()        
        permissions.orderBy(columnsDict[column.getId()] +' '+sortindex)
    permissions.limit(firstrecord-1, pagesize)
    
    # Проходим по таблице и заполняем data    
    for permissions in permissions.iterate():
        permDict = {}
        permDict[toHexForXml('~~id')] = base64.b64encode(json.dumps([permissions.roleid, permissions.grainid, permissions.tablename]))
        permDict[u"Роль"] = permissions.roleid
        permDict[u"Гранула"] = permissions.grainid
        permDict[u"Таблица"] = permissions.tablename
        permDict[toHexForXml(u"Доступ на чтение")] = permissions.r if permissions.r else ''
        permDict[toHexForXml(u"Доступ на добавление")] = permissions.i if permissions.i else ''
        permDict[toHexForXml(u"Доступ на редактирование")] = permissions.m if permissions.m else ''
        permDict[toHexForXml(u"Доступ на удаление")] = permissions.d if permissions.d else ''

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

    # Курсор таблицы permissions
    permissions = tablesPermissionsViewCursor(context)
    # Вычисляем количества записей в таблице
    totalcount = permissions.count()
    # Заголовок таблицы
    header = "Разрешения"
    # В случае если таблица пустая
    if totalcount == 0 or totalcount is None:
        totalcount = "0"
        header = header + " ПУСТ"

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50",
                   "@gridWidth": getGridWidth(session),
                   "@gridHeight":getGridHeight(session, delta = 300),
                   "@totalCount": totalcount,
                   "@profile":"editableGrid.properties"},
    "labels":{"header":header}
    }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":"Роль", "@width": "80px",
                                                       "@readonly":"true"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Гранула", "@width": "80px",
                                                       "@readonly":"true"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Таблица", "@width": "80px",
                                                       "@readonly":"true"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на чтение", "@width": "80px",
                                                       "@readonly":"false",
                                                       "@editor":"{ editor: 'checkbox'}"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на добавление", "@width": "80px",
                                                       "@readonly":"false",
                                                       "@editor":"{ editor: 'checkbox'}"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на редактирование", "@width": "80px",
                                                       "@readonly":"false",
                                                       "@editor":"{ editor: 'checkbox'}"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на удаление", "@width": "80px",
                                                       "@readonly":"false",
                                                       "@editor":"{ editor: 'checkbox'}"})

    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    data = {"gridtoolbar":{"item":[]
                           }
            }
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowDown.png',
                                            "@text":"Скачать",
                                            "@hint":"Скачать разрешения в xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Скачать разрешения",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "permDownloadXform",
                                                                                           "add_context":"download"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )    
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowUp.png',
                                            "@text":"Загрузить",
                                            "@hint":"Загрузить разрешения из xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Загрузить разрешения",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "permUploadXform",
                                                                                           "add_context":"upload"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )


    return XMLJSONConverter.jsonToXml(json.dumps(data))

def gridSaveRecord(context=None, main=None, add=None, session=None, filterinfo=None, elementId=None, saveData=None):
    saveData = json.loads(saveData)["savedata"]["data"]
    permissions = PermissionsCursor(context)

    roleId = saveData["col1"]
    grainId = saveData["col2"]
    tableName = saveData["col3"]
    
    r = True if saveData["col4"] else False
    i = True if saveData["col5"] else False
    m = True if saveData["col6"] else False
    d = True if saveData["col7"] else False

    if permissions.tryGet(roleId, grainId, tableName):
        if r or i or m or d:
            permissions.r = r
            permissions.i = i
            permissions.m = m
            permissions.d = d
            if permissions.canModify():
                permissions.update()
            else:
                context.error(u"Недостаточно прав для данной операции!")
        else:
            if permissions.canDelete():
                permissions.delete()
            else:
                context.error(u"Недостаточно прав для данной операции!")
    else:
        if r or i or m or d:
            permissions.roleid = roleId
            permissions.grainid = grainId
            permissions.tablename = tableName
            permissions.r = r
            permissions.i = i
            permissions.m = m
            permissions.d = d
            if permissions.canInsert():
                permissions.insert()
            else:
                context.error(u"Недостаточно прав для данной операции!")
    res = GridSaveResult()
    res.setRefreshAfterSave(0)
    return res
