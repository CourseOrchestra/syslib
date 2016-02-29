# coding: utf-8

import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow._workflow_orm import groupsCursor, userGroupCursor

from workflow.processUtils import getUserName, getUsersCursor, parse_json

try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

from workflow.getUserInfo import userNameClass

import time
from com.google.gson import Gson


def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения списка всех форм процесса развернутых процессов. '''
    start = time.clock()
    print firstrecord, pagesize
    gson = Gson()
    datapanelSettings = parse_json()
    usersClass = userNameClass(context, datapanelSettings)
    session = json.loads(session)
    groupId = session['sessioncontext']['related']['gridContext']['currentRecordId']
    userGroup = userGroupCursor(context)
    groups = groupsCursor(context)
    groups.get(groupId)
    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "name":[u"Имя пользователя"],
             "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
        
    userGroup.setRange('groupId',groupId)
    userGroup.limit(firstrecord-1,pagesize)
    # Проходим по таблице и заполняем data    
    for userGroup in userGroup.iterate():
        userDict = {}
        userDict[_header["id"][1]] =  userGroup.userId
#         userDict[_header["name"][1]] = userGroup.userId
        userDict[_header["name"][1]] = usersClass.getUserName(userGroup.userId)
       
        userDict[_header["properties"][1]] = {}
        data["records"]["rec"].append(userDict)

    # Определяем список полей таблицы для отображения

    # Добавляем поля для отображения в gridsettings
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    data = gson.toJson(data)
#     timeList.append('Prev dumps: ' + str(time.clock() - start))
    res1 = XMLJSONConverter.jsonToXml(data)
    print userGroup.count()
    print time.clock() - start
    print data
    return JythonDTO(res1,None)


def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    start = time.clock()
    gson = Gson()
    session = json.loads(session)
    groupId = session['sessioncontext']['related']['gridContext']['currentRecordId']
    userGroup = userGroupCursor(context)
    groups = groupsCursor(context)
    groups.get(groupId)
    userGroup.setRange('groupId',groupId)
    groupName = groups.groupName
    _header = {"id":["~~id"],
             "name":[u"Имя пользователя"],
             "properties":[u"properties"]}
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "100%",
                                               "@gridHeight": "300",
                                               "@totalCount": userGroup.count(),
                                               "@profile":"default.properties"},
                                "labels":{"header":"Пользователи группы "+groupName}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    
    settings = gson.toJson(settings)
    res2 = XMLJSONConverter.jsonToXml(settings)
#    raise Exception(time.clock() - start)
    return JythonDTO(None, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    session = json.loads(session)
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "groupsGrid":
            groupId = gridContext["currentRecordId"]
        if gridContext["@id"] == "userGroupsGrid":
            if 'currentRecordId' in gridContext:
                style = "false"
            else:
                style = "true"

    data = {"gridtoolbar":{"item":[]}}

    
    data["gridtoolbar"]["item"].append({ "@text":"Добавить",
                                        "@hint":"Добавление пользователя в группу",
                                        "@disable": "false",
                                        "action":{"@show_in": "MODAL_WINDOW",
                                                  "#sorted":[{"main_context":"current"},
                                                             {"modalwindow":{"@caption": "Добавление пользователя",
                                                                             "@height": "300",
                                                                             "@width": "500"
                                                                             }
                                                              },
                                                             {"datapanel":{"@type": "current",
                                                                           "@tab": "current",
                                                                           "element": {"@id": "addUserToGroupCard",
                                                                                       "add_context":"add"}
                                                                           }
                                                              }
                                                             ]
                                                  }
                                        })

    data["gridtoolbar"]["item"].append({"@text":"Удалить",
                                    "@hint":"Удаление пользователя из группы",
                                    "@disable": style,
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Удаление пользователя из групыы",
                                                                         "@height": "200",
                                                                         "@width": "500"}
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "delUserFromGroupCard",
                                                                                   "add_context":"del"}
                                                                       }
                                                          }]
                                              }
                                    })

    return XMLJSONConverter.jsonToXml(json.dumps(data))


