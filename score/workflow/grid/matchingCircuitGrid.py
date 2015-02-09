# coding: utf-8

import simplejson as json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO



from workflow._workflow_orm import matchingCircuitCursor, statusCursor

from common.sysfunctions import toHexForXml,getGridWidth, getGridHeight

from common import  hierarchy

from ru.curs.celesta.showcase.utils import XMLJSONConverter


def treeGrid(context, main, add, filterinfo, session, elementId, sortColumnList, parentId=None):
    u'''Функция получения данных для грида. '''
    session = json.loads(session)
    gridWidth = getGridWidth(session, 60)
    gridHeight = getGridHeight(session,2)
    sid = session['sessioncontext']['sid']
    _headers = {'id': '~~id',
                'name': u'Название',
                'number': u'Номер',
                'type': u'Тип',
                'status': u'Статус',
                'isMain': u'Тип заключения/атрибута',
                'hasChildren': 'HasChildren',
                'properties': 'properties'}
    processKey = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processKey']
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    status = statusCursor(context)
    for col in _headers:
        _headers[col] = toHexForXml(_headers[col])

    _data = {"records": {"rec": []}}
    # Курсоры
    # Событие по одинарному клику по записи
    event = {}
    # Корень дерева
    if parentId is None:
        #Вывод верхнего фиктивного элемента процесс
        id_dict = dict()
        id_dict["procKey"] = processKey
        id_dict["id"] = 'top'
        row = dict()
        row[_headers['id']] = json.dumps(id_dict)
        row[_headers['name']] = u'===Процесс==='
        
        matchingCircuit.setRange('processKey',processKey)
        row[_headers['hasChildren']] = 1 if matchingCircuit.count() > 0 else False
        row[_headers['properties']] = event
        _data["records"]["rec"].append(row)
# Дочерние элементы
    else:
        #Вывод элементов верхнего уровня
        parentId = json.loads(parentId)
        if parentId['id'] == 'top':        
            matchingCircuit.setRange('processKey',processKey)
            matchingCircuitClone.setRange('processKey',processKey)
            matchingCircuit.setFilter('number',"!%'.'%")
            matchingCircuit.orderBy('sort')
            for matchingCircuit in matchingCircuit.iterate():
                id_dict = dict()
                id_dict["procKey"] = processKey
                id_dict["id"] = matchingCircuit.id
                row = dict()
                row[_headers['id']] = json.dumps(id_dict)
                if matchingCircuit.type == 'parallel':
                    row[_headers['name']] = u'Параллельное согласование'
                    
                else:
                    row[_headers['name']] = matchingCircuit.name
                row[_headers['number']] = matchingCircuit.number
                row[_headers['hasChildren']] = hasChildren(context,matchingCircuit.number,matchingCircuitClone)
                row[_headers['properties']] = event
                _data["records"]["rec"].append(row)
        else:       
            #Вывод элементов параллельного согласования
            isEmptyFlag = True
            id_dict = parentId
            matchingCircuit.get(id_dict["procKey"],id_dict["id"])
            matchingCircuitClone.setRange('processKey',processKey)
            number = matchingCircuit.number
            matchingCircuit.setRange('processKey',processKey)
            matchingCircuit.setFilter('number', "('%s.'%%)&(!'%s.'%%'.'%%)" % (number, number))
            matchingCircuit.orderBy('sort')
            for matchingCircuit in matchingCircuit.iterate():
                isEmptyFlag = False
                id_dict = dict()
                id_dict["procKey"] = processKey
                id_dict["id"] = matchingCircuit.id
                row = dict()
                row[_headers['id']] = json.dumps(id_dict)
                row[_headers['name']] = matchingCircuit.name
                row[_headers['number']] = matchingCircuit.number

                    
                row[_headers['hasChildren']] = hasChildren(context,matchingCircuit.number,matchingCircuitClone)
                row[_headers['properties']] = event   
                _data["records"]["rec"].append(row)
            if isEmptyFlag:
                _data = {"records": ''}
    resultData = XMLJSONConverter.jsonToXml(json.dumps(_data))
    settings = {"gridsettings":
                {"action":
                 {"#sorted":
                  [{"main_context": 'current'},
                   {"datapanel":
                    {"@type": "current",
                     "@tab": "current"}}]},
                 "labels":
                    {"header": u"Порядок согласования"},
                 "columns":
                    {"col":
                     [{"@id": u"Название"},
                      {"@id": u"Номер"}
                      ]},
                 "properties":
                    {"@flip": "false",
                     "@pagesize": "30",
                     "@gridWidth": gridWidth, 
                     "@gridHeight": gridHeight,
                     "@totalCount": "0"}
                 }}
    settings = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(resultData, settings)

def hasChildren(context, ident, cursor):
    u'''Функция определения, имеет ли элемент детей. '''
    filterString = "'" + unicode(ident) + ".'%"
    cursor.setFilter('number', filterString)
    if cursor.count() > 0:
        return 1
    else:
        return False

def gridToolBar(context, main, add=None, filterinfo=None, session=None, elementId=None):
    u'''Тулбар грида согласователей процесса'''
    matchingCircuit = matchingCircuitCursor(context)
    session = json.loads(session)
    sid = session['sessioncontext']['sid']
    processKey = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processKey']
    modelId =  session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@modelId']
    textAdd = u"Добавить"
    hintAdd = u"Добавление элемента"
    textEdit = u"Редактировать"
    hintEdit = u"Редактирование элемента"
    styleDelete = 'true'
    upStyle = 'true'
    downStyle = 'true'
    leftStyle = 'true'
    rightStyle = 'true'
    if ('currentRecordId' not in session['sessioncontext']['related']['gridContext']):
        styleAdd = 'true'
        styleEdit = 'true'
    else:
        styleAdd = 'true'
        currentId = json.loads(session['sessioncontext']['related']['gridContext']['currentRecordId'])
        #В фиктивный элемент верхнего уровня можно только добавлять элементы
        if currentId['id'] == 'top':
            styleAdd = 'false'
            styleEdit = 'true'
        else:
            upStyle = 'false'
            downStyle = 'false'
            matchingCircuit.get(currentId['procKey'],currentId['id'])
            #В элементы параллельного согласования можно добавлять элементы, но нельзя редактировать параллельлное согласование
            if matchingCircuit.type == 'parallel':
                styleAdd = 'false'
                styleEdit = 'true'
            #Другие элементы можно редактировать
            else:
                styleEdit = 'false'
                if '.' in matchingCircuit.number:
                    leftStyle = 'false'
                else:
                    rightStyle = 'false'
            styleDelete = 'false'
    data = {"gridtoolbar":
        {"item":
         [{"@text": textAdd,
           "@img": "gridToolBar/addDirectory.png",
           "@hint": hintAdd,
           "@disable": styleAdd,
           "action":
            {"@show_in": "MODAL_WINDOW",
             "#sorted":
             [{"main_context": 'current'},
              {"modalwindow":
                {"@caption": u"Добавление элемента",
                 "@height": "600",
                 "@width": "700"}},
              {"datapanel":
                {"@type": "current",
                 "@tab": "current",
                    "element":
                     {"@id": "addMatcher",
                      "add_context": json.dumps(['add',processKey, modelId])}}}]}},
          {"@text": textEdit,
           "@img": "gridToolBar/editDocument.png",
           "@hint": hintEdit,
           "@disable": styleEdit,
           "action":
            {"@show_in": "MODAL_WINDOW",
             "#sorted":
             [{"main_context": 'current'},
              {"modalwindow":
                {"@caption": u"Редактирование элемента",
                 "@height": "600",
                 "@width": "700"}},
              {"datapanel":
                {"@type": "current",
                 "@tab": "current",
                    "element":
                     {"@id": "addMatcher",
                      "add_context": json.dumps(['edit',processKey, modelId])}}}]}},
          {"@img": "gridToolBar/arrowUp.png",
            "@hint": u"Поднять вопрос",
            "@disable": upStyle,
            "action":{"#sorted":[{"main_context": 'current'},
                                 {"datapanel":{"@type": "current",
                                               "@tab": "current",
                                               "element":{"@id": "matchingCircuitGrid",
                                                          "add_context": '',
                                                          "@keep_user_settings": "true"}
                                               }
                                  },
                                 {"server":{"activity":{"@id": "up",
                                                        "@name": "workflow.grid.matchingCircuitGrid.changeNumber.celesta",
                                                        "add_context": "up"}
                                            }
                                  }]
                      }
            },
           {"@img": "gridToolBar/arrowDown.png",
            "@hint": u"Опустить вопрос",
            "@disable": downStyle,
            "action":{"#sorted":[{"main_context": 'current'},
                                 {"datapanel":{"@type": "current",
                                               "@tab": "current",
                                               "element":{"@id": "matchingCircuitGrid",
                                                          "add_context": '',
                                                          "@keep_user_settings": "true"}
                                               }
                                  },
                                 {"server":{"activity":{"@id": "down",
                                                        "@name": "workflow.grid.matchingCircuitGrid.changeNumber.celesta",
                                                        "add_context":"down"}
                                            }
                                  }]
                      }
            },
           {"@img": "gridToolBar/arrowLeft.png",
            "@hint": u"Сдвинуть влево",
            "@disable": leftStyle,
            "action":{"#sorted":[{"main_context": 'current'},
                                 {"datapanel":{"@type": "current",
                                               "@tab": "current",
                                               "element":{"@id": "matchingCircuitGrid",
                                                          "add_context": '',
                                                          "@keep_user_settings": "true"}
                                               }
                                  },
                                 {"server":{"activity":{"@id": "left",
                                                        "@name": "workflow.grid.matchingCircuitGrid.changeLevel.celesta",
                                                        "add_context": "left"}
                                            }
                                  }]
                      }
            },
           {"@img": "gridToolBar/arrowRight.png",
            "@hint": u"Сдвинуть вправо",
            "@disable": rightStyle,
            "action":{"@show_in": "MODAL_WINDOW",
                      "#sorted":[{"main_context": 'current'},
                                 {"modalwindow":{"@caption": u"Выбор родительского вопроса",
                                                 "@height": "300",
                                                 "@width": "450"}
                                  },
                                 {"datapanel":{"@type": "current",
                                               "@tab": "current",
                                               "element":{"@id": "moveRight",
                                                          "add_context": '',
                                                          "@keep_user_settings": "true"}
                                               }
                                  }]
                      }
            },

          {"@text": u"Удалить",
           "@img": "gridToolBar/deleteDocument.png",
           "@hint": u"Удаление элемента",
           "@disable": styleDelete,
           "action":
            {"@show_in": "MODAL_WINDOW",
             "#sorted":
             [{"main_context": 'current'},
              {"modalwindow":
                {"@caption": u"Удаление элемента",
                 "@height": "150",
                 "@width": "450"}},
              {"datapanel":
                {"@type": "current",
                 "@tab": "current",
                    "element":
                     {"@id": "deleteMatcher",
                      "add_context": json.dumps(['edit',processKey, modelId])}}}]}}]}}

    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return res

def changeNumber(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    session = json.loads(session)["sessioncontext"]
    currentRec= json.loads(session['related']['gridContext']['currentRecordId'])
    processKey = currentRec["procKey"]
    id = currentRec["id"]
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuit.get(processKey,id)
    matchingCircuit.setRange('processKey',processKey)
    #raise Exception(currentRecordId, int(main))
    
    hierarchy.changeNodePositionInLevelOfHierarchy(context, matchingCircuit, 'number', 'sort', 1 if add == 'down' else -1)


def changeLevel(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    session = json.loads(session)["sessioncontext"]
    currentRec= json.loads(session['related']['gridContext']['currentRecordId'])
    processKey = currentRec["procKey"]
    id = currentRec["id"]
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuit.get(processKey,id)
    matchingCircuit.setRange('processKey',processKey)

    hierarchy.leftShiftNodeInHierarchy(context, matchingCircuit, 'number', 'sort')