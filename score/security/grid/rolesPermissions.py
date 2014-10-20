# coding: utf-8

import simplejson as json
import base64
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml
from ru.curs.celesta.syscursors import PermissionsCursor

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''

    # Создание экземпляра курсора разрешения
    permissions = PermissionsCursor(context)

    # Определяем переменную для JSON данных
    data = {"records":{"rec":[]}}
    
    roleid = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    #raise Exception(session)
    #print roleid
    permissions.setRange("roleid", roleid)
    columnsDict={u"Гранула":"grainid",
                 u"Таблица":"tablename",
                 u"Доступ на чтение":"r",
                 u"Доступ на добавление":"i",
                 u"Доступ на редактирование":"m",
                 u"Доступ на удаление":"d"}
    for column in sortColumnList:
        sortindex = '%s' % column.getSorting()        
        permissions.orderBy(columnsDict[column.getId()] +' '+sortindex)
    
    if permissions.tryFirst():
        while True:
            permDict = {}
            permDict[toHexForXml('~~id')] = base64.b64encode(json.dumps([permissions.roleid, permissions.grainid, permissions.tablename]))            
            permDict[u"Гранула"] = permissions.grainid
            permDict[u"Таблица"] = permissions.tablename
            permDict[toHexForXml(u"Доступ на чтение")] = 'gridToolBar/yes.png' if permissions.r else 'gridToolBar/no.png'
            permDict[toHexForXml(u"Доступ на добавление")] = 'gridToolBar/yes.png' if permissions.i else 'gridToolBar/no.png'
            permDict[toHexForXml(u"Доступ на редактирование")] = 'gridToolBar/yes.png' if permissions.m else 'gridToolBar/no.png'
            permDict[toHexForXml(u"Доступ на удаление")] = 'gridToolBar/yes.png' if permissions.d else 'gridToolBar/no.png'

            permDict['properties'] = {"event":
                    {"@name":"row_single_click",
                     "action":
                        {"#sorted":[
                            {"main_context": 'current'},
                             {"datapanel":
                                {'@type':"current",
                                 '@tab':"current"
                                 }
                            }
                                    ]
                        }
                     }
                 }
            data["records"]["rec"].append(permDict)
            if not permissions.next():
                break


    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)

def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''

    # Курсор таблицы permissions
    permissions = PermissionsCursor(context)
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
    "properties": {"@pagesize":"50", "@gridWidth": "900px", "@totalCount": totalcount, "@profile":"default.properties"},
    "labels":{"header":header}
    }
    # Добавляем поля для отображения в gridsettings
    #settings["gridsettings"]["columns"]["col"].append({"@id":"Роль", "@width": "80px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Гранула", "@width": "80px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Таблица", "@width": "80px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на чтение", "@width": "80px", "@type":"IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на добавление", "@width": "80px", "@type":"IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на редактирование", "@width": "80px", "@type":"IMAGE"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Доступ на удаление", "@width": "80px", "@type":"IMAGE"})

    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

#def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
#    u'''Toolbar для грида. '''
#
#    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
#        style = "true"
#    else:
#        style = "false"
#
#    data = {"gridtoolbar":{"item":[]
#                           }
#            }
#    # Курсор таблицы permissions
#    permissions = PermissionsCursor(context)
#
#    if permissions.canInsert():
#        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/addDirectory.png',
#                                    "@text":"Добавить",
#                                   "@hint":"Добавить",
#                                   "@disable": "false",
#                                   "action":{"@show_in": "MODAL_WINDOW",
#                                             "#sorted":[{"main_context":"current"},
#                                             {"datapanel":{"@type": "current",
#                                                          "@tab": "current",
#                                                          "element": {"@id": "permXforms",
#                                                                      "add_context":"add"
#                                                                      }
#                                                          }
#                                             }]
#
#                                   }})
#    if permissions.canModify():
#        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/editDocument.png',
#                            "@text":"Редактировать",
#                                   "@hint":"Редактировать",
#                                   "@disable": style,
#                                   "action":{"@show_in": "MODAL_WINDOW",
#                                             "#sorted":[{"main_context":"current"},
#                                             {"datapanel":{"@type": "current",
#                                                          "@tab": "current",
#                                                          "element": {"@id": "permXforms",
#                                                                      "add_context":"edit"
#                                                                      }
#                                                          }
#                                             }]
#                                   }})
#    if permissions.canDelete():
#        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/deleteDocument.png',
#                            "@text":"Редактировать",
#                                   "@hint":"Редактировать",
#                                   "@disable": style,
#                                   "action":{"@show_in": "MODAL_WINDOW",
#                                             "#sorted":[{"main_context":"current"},
#                                             {"datapanel":{"@type": "current",
#                                                          "@tab": "current",
#                                                          "element": {"@id": "permXforms",
#                                                                      "add_context":"delete"
#                                                                      }
#                                                          }
#                                             }]
#                                   }})
#
#
#    return XMLJSONConverter(input=data).parse()

