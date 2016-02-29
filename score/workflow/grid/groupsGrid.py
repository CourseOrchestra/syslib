# coding: utf-8
'''
Created on 19.12.2014

@author: tr0glo)|(I╠╣ 
'''


import json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from workflow._workflow_orm import groupsCursor
from common.sysfunctions import getGridWidth, getGridHeight
from common.hierarchy import hasChildren

try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult

def getData(context, main=None, add=None, filterinfo=None, session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None, parentId=None):
    u'''Функция получения списка всех развернутых процессов. '''
    groups = groupsCursor(context)

    session = json.loads(session)

    session = session['sessioncontext']

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "name":[u"Название"],
             "properties":[u"properties"],
             'hasChildren': [u'HasChildren'],
             }
    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    if parentId is None:
        groups.setFilter('number', "!(%'.'%)")
    else:
        groups.get(parentId)
        groups.setFilter("number", '''('%s.'%%)&!('%s.'%%'.'%%)''' % (groups.number, groups.number))
    groups.orderBy('sort')
    # Проходим по таблице и заполняем data
    for groups in groups.iterate():
        groupsDict = {}
        groupsDict[_header["id"][1]] = groups.groupId
        groupsDict[_header["name"][1]] = "%s %s" % (groups.number, groups.groupName)
        groupsDict[_header["hasChildren"][1]] = int(hasChildren(context, groups, 'number'))
        groupsDict[_header["properties"][1]] = {"event":[{"@name":"row_single_click",
                                         "action":{"#sorted":[{"main_context": 'current'},
                                                              {"datapanel":{'@type':"current",
                                                                            '@tab':"current",
                                                                            'element':{'@id':'userGroupsGrid'}
                                                                            }
                                                               }]
                                                   }
                                         } ]
                                              }
        data["records"]["rec"].append(groupsDict)

    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)
    
def getMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None): 
    u'''Функция получения списка всех развернутых процессов. '''
    groups = groupsCursor(context)
    # Получение списка развернутых процессов)
    # Извлечение фильтра из related-контекста
    # raise Exception(session)
    session = json.loads(session)
    gridWidth = getGridWidth(session, 60)
    gridHeigth = getGridHeight(session, 2, 55, 80)
    session = session['sessioncontext']
#     if "formData" in session["related"]["xformsContext"]:
#         info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
#         processName = info["@processName"]
#     else:
#         processName = ''

    _header = {"id":["~~id"],
             "name":[u"Название"],
             "properties":[u"properties"],
             'hasChildren': [u'HasChildren'],
             }
    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))

    # Определяем список полей таблицы для отображения
    settings = {}

    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": "100%",
                                               "@gridHeight": gridHeigth,
                                               "@profile":"default.properties"}
                                }
    if add is not None and add != '':
        settings["gridsettings"]["properties"]["@autoSelectRecordUID"] = add
    # Добавляем поля для отображения в gridsettings

    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    
    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":
            {"item":
             [{"@text": u"Добавить",
               "@img": "gridToolBar/addDirectory.png",
               "@hint": u"Добавить группу",
               "@disable": "false",
               "action":
                {"@show_in": "MODAL_WINDOW",
                 "#sorted":
                 [{"main_context": 'current'},
                  {"modalwindow":
                    {"@caption": u"Добавление группы",
                     "@height": "150",
                     "@width": "600"}},
                  {"datapanel":
                    {"@type": "current",
                     "@tab": "current",
                        "element":
                         {"@id": "addGroupCard",
                          "add_context": "add"}}}]}},
              {"@text": u"Редактировать",
               "@img": "gridToolBar/editDocument.png",
               "@hint": u"Редактирование группы",
               "@disable": style,
               "action":
                {"@show_in": "MODAL_WINDOW",
                 "#sorted":
                 [{"main_context": 'current'},
                  {"modalwindow":
                    {"@caption": u"Редактирование группы",
                     "@height": "150",
                     "@width": "600"}},
                  {"datapanel":
                    {"@type": "current",
                     "@tab": "current",
                        "element":
                         {"@id": "addGroupCard",
                          "add_context": "edit"}}}]}},
              {"@text": u"Удалить",
               "@img": "gridToolBar/deleteDocument.png",
               "@hint": u"Удалить группу",
               "@disable": style,
               "action":
                {"@show_in": "MODAL_WINDOW",
                 "#sorted":
                 [{"main_context": 'current'},
                  {"modalwindow":
                    {"@caption": u"Удаление группы",
                     "@height": "200",
                     "@width": "450"}},
                  {"datapanel":
                    {"@type": "current",
                     "@tab": "current",
                        "element":
                         {"@id": "delGroupCard",
                          "add_context": 'del'}}}]}}
              ]}}

    jsonData = XMLJSONConverter.jsonToXml(json.dumps(data))
    return jsonData

