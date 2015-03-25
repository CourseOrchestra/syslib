# coding: utf-8

import simplejson as json
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml, getGridHeight, getGridWidth
from security._security_orm import subjectsCursor
from security.functions import Settings

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''

    # Создание экземпляра курсора разрешения
    subjects = subjectsCursor(context)

    # Определяем переменную для JSON данных
    data = {"records":{"rec":[]}}
    columnsDict={u"sid":"sid",
                 u"Имя":"name"}
    for column in sortColumnList:
        sortindex = '%s' % column.getSorting()        
        subjects.orderBy(columnsDict[column.getId()] +' '+sortindex)
    subjects.limit(firstrecord-1, pagesize)
    # Проходим по таблице и заполняем data
    for subjects in subjects.iterate():        
        subjectsDict = {}
        subjectsDict[toHexForXml('~~id')] = subjects.sid
        subjectsDict["sid"] = subjects.sid
        subjectsDict[u"Имя"] = subjects.name                            
        subjectsDict['properties'] = {"event":{"@name":"row_single_click",
                                                "action":{"#sorted":[{"main_context": 'current'},
                                                                     {"datapanel":{'@type':"current",
                                                                                   '@tab':"current"}
                                                                      }]
                                                          }
                                                }
                                       }
        data["records"]["rec"].append(subjectsDict)
        

    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)

def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''
    
    subjects = subjectsCursor(context)
    #currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']    
    # Вычисляем количества записей в таблице
    totalcount = subjects.count()
    # Заголовок таблицы
    header = "Субъекты"
    # В случае если таблица пустая
    if totalcount == 0 or totalcount is None:
        totalcount = "0"
        header = header + " ПУСТ"
        
    sec_settings = Settings()

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns":{"col":[]},
                                "properties":{"@pagesize":"25",
                                              "@gridWidth":getGridWidth(session),
                                              "@gridHeight":getGridHeight(session, numberOfGrids = 1 if sec_settings.loginIsSubject() else 2),
                                              "@totalCount":totalcount,
                                              "@profile":"default.properties"},
                                "labels":{"header":header}
                                }
    # Добавляем поля для отображения в gridsettings    
    settings["gridsettings"]["columns"]["col"].append({"@id":"sid", "@width": "240px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Имя", "@width": "240px"})    
    
    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    
    settings=Settings()

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"
    
    #raise Exception(session)

    data = {"gridtoolbar":{"item":[]}}
    if not settings.isEmployees():
        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/addDirectory.png',
                                            "@text":"Добавить",
                                            "@hint":"Добавить субъект",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Добавление субъекта",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "subjectsXform",
                                                                                           "add_context":"add"}
                                                                               }
                                                                  }]
                                                      }
                                            })
        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/editDocument.png',
                                            "@text":"Редактировать",
                                            "@hint":"Редактировать субъект",
                                            "@disable": style,
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Редактирование субъекта",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "subjectsXform",
                                                                                           "add_context":"edit"}
                                                                               }
                                                                  }]
                                                      }
                                            })
        data["gridtoolbar"]["item"].append({"@img": 'gridToolBar/deleteDocument.png',
                                            "@text":"Удалить",
                                            "@hint":"Удалить субъект",
                                            "@disable": style,
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Удаление субъекта",
                                                                                 "@height": "150",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "subjectsXformDelete",
                                                                                           "add_context":"delete"}
                                                                               }
                                                                  }]
                                                      }
                                            })
    data["gridtoolbar"]["item"].append(     {"@img": 'gridToolBar/addDirectory.png',
                                             "@text":"Добавить роли",
                                             "@hint":"Добавить роли",
                                             "@disable": style,
                                             "action":{"@show_in": "MODAL_WINDOW",
                                                       "#sorted":[{"main_context":"current"},
                                                                  {"modalwindow":{"@caption": "Добавление ролей",
                                                                                  "@height": "350",
                                                                                  "@width": "500"}
                                                                   },
                                                                  {"datapanel":{"@type": "current",
                                                                                "@tab": "current",
                                                                                "element": {"@id": "subjectsRolesXform",
                                                                                            "add_context":""}
                                                                                }
                                                                   }]
                                                       }
                                             })
#                                   ,{"@img": 'gridToolBar/addDirectory.png',
#                                    "@text":"Добавить сотрудника",
#                                    "@hint":"Добавить сотрудника",
#                                    "@disable": style,
#                                    "action":{"@show_in": "MODAL_WINDOW",
#                                              "#sorted":[{"main_context":"current"},
#                                                         {"modalwindow":{"@caption": "Добавление ролей",
#                                                                         "@height": "350",
#                                                                         "@width": "500"
#                                                                         }
#                                                          },
#                                                         {"datapanel":{"@type": "current",
#                                                                       "@tab": "current",
#                                                                       "element": {"@id": "subjectsEmployeesXform",
#                                                                                   "add_context":""}
#                                                                       }
#                                                          }]
#                                              }
#                                    }

    return XMLJSONConverter.jsonToXml(json.dumps(data))

