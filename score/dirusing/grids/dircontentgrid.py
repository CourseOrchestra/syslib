# coding: utf-8
'''
Created on 12.02.2014

@author: Kuzmin
'''

import simplejson as json
import base64
from java.text import SimpleDateFormat

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


from ru.curs.celesta.showcase.utils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList, htmlDecode
from dirusing.hierarchy import isExtr
from common.hierarchy import generateSortValue, hasChildren

from dirusing.constants import DEFAULT_DATETIME_FORMAT_JAVA



def _setFilters(session, inOutCurrentTable):
    ses = json.loads(session)['sessioncontext']
    
    #простановка фильтра на текстовые поля таблицы
    if not 'xformsContext' in ses['related']:
        return
    
    if not 'formData' in ses['related']['xformsContext']:
        return
    
    columns = ses['related']['xformsContext']['formData']['schema']['columns']
    if not isinstance(columns, list):
        columns = [columns]
    
    filterCols = dict(((col['column']['@id'], col['column']['filter']) for col in columns) if columns else {})
    for textcol, filtertext in filterCols.iteritems():
        filtercol = "%'" + filtertext + "'%"
        inOutCurrentTable.setFilter(textcol, filtercol)

def getTree(context, main=None, add=None, filterinfo=None, session=None, elementId=None, sortColumnList=None, parentId=None):
    u'''Функция получения данных для tree-грида. '''
    # получение id grain и table
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)

    # Получение метаданных таблицы
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    # Заголовки полей
    _headers = getFieldsHeaders(table_meta, "grid")
    for column in table_meta.getColumns():
            #получаем названиe колонкu с кодом дьюи
        if json.loads(table_meta.getColumn(column).getCelestaDoc())['name'] in (u'deweyCode', u'deweyCod', u'deweyKod'):
            deweyColumn = column
        if json.loads(table_meta.getColumn(column).getCelestaDoc())['name'] == u'sortNumber':
            sortColumn = column
                #генерируем номера сортировки и пишем в базу
    textcolumns = []

    #простановка фильтра на текстовые поля таблицы
    _setFilters(session, currentTable)
    
    totalcount = currentTable.count()
    if totalcount != 0:
        # Определяем переменную для JSON данных
        data = {"records":{"rec":[]}}
        # Событие по клику на запись грида


        event = {
            "event": [{
                "@name": "row_single_click",
                "action": {
                    "#sorted": [{
                        "main_context": "current"
                    },
                    {
                        "datapanel": {
                            '@type': 'current',
                            '@tab': 'current',
                            "element": {
                                "@id": "12",
                                "add_context": "row_clicked"
                            }
                        }
                    }]
                }
            },
            {
                "@name": "row_double_click",
                "action": {
                    "@show_in": "MODAL_WINDOW",
                    "#sorted": [{
                        "main_context": "current"
                    },
                    {
                        "datapanel": {
                            '@type': 'current',
                            '@tab': 'current',
                            "element": {
                                "@id": "15",
                                "add_context": "edit"
                            }
                        }
                    }]
                }
            }]
        }
        
        currentTable.orderBy('%s asc' % sortColumn)
        if sortColumnList:
            for column in sortColumnList:
                sortindex = '%s' % column.getSorting()
                for field in _headers:
                    if _headers[field][0] == column.getId():
                        if field in (u'deweyCode', u'deweyCod', u'deweyKod'):
                            field = u'sortNumber'
                        currentTable.orderBy(field + ' ' + sortindex)
        if parentId is None:
            # Обработка иерархического справочника
            for rec in currentTable.iterate():
#                 rec_dict = {}
                len_dewey = len(getattr(rec, deweyColumn).split('.'))
                if len_dewey == 1:
                    rec_dict = getRecord(currentTable, context, table_meta, grain_name, rec, _headers, event)
                    rec_dict["HasChildren"] = '1' if hasChildren(context, rec, deweyColumn) else '0'
                    data["records"]["rec"].append(rec_dict)
        else:
            selectedRecordId = json.loads(base64.b64decode(str(parentId)))
            currentTable.get(*selectedRecordId)
            parent = getattr(currentTable, deweyColumn)
            len_parent = len(parent.split('.'))
            for rec in currentTable.iterate():
#                 rec_dict = {}
                len_dewey = len(getattr(rec, deweyColumn).split('.'))
                if getattr(rec, deweyColumn).startswith(parent):
                    if len_dewey == len_parent + 1:
                        rec_dict = getRecord(currentTable, context, table_meta, grain_name, rec, _headers, event)
                        rec_dict["HasChildren"] = '1' if hasChildren(context, rec, deweyColumn) else '0'
                        data["records"]["rec"].append(rec_dict)
    else:
        data = {"records":""}

    res = XMLJSONConverter.jsonToXml(json.dumps(data))

    try:
        panelWidth = str(int(json.loads(session)['sessioncontext']['currentDatapanelWidth']) - 55) + 'px'
        panelHeight = int(json.loads(session)['sessioncontext']['currentDatapanelHeight']) - 115
    except:
        panelWidth = '900px'
        panelHeight = 450

    # Заголовок таблицы
    table_name = json.loads(table_meta.getCelestaDoc())["name"]
    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50", "@gridWidth": panelWidth, "@gridHeight": panelHeight, "@totalCount":totalcount, "@profile":"hierarchy.properties"},
    "labels":{"header":table_name}
    }
    # Определяем список порядковых номеров полей для сортировки
    sort_list = getSortList(table_meta)
    sorted_list = []
    # Добавляем поля для отображения в gridsettings
    def _sortedHeaders(s_number):
        try:
            sort_number = sort_list[s_number]
            for field in _headers:
                order_grid = _headers[field][2]
                if order_grid != sort_number or order_grid in sorted_list:
                    continue
                else:
                    if field not in ('~~id') and _headers[field][1] not in (4, 6, 7, 8):
                        settings["gridsettings"]["columns"]["col"].append({"@id":htmlDecode(_headers[field][0])})
                    elif field not in ('~~id') and _headers[field][1] in (4,):
                        settings["gridsettings"]["columns"]["col"].append({"@id":htmlDecode(_headers[field][0]),
																			"@type": "DOWNLOAD",
																			"@linkId":"download1"})
                    s_number += 1
                    _sortedHeaders(s_number)
                    break
        except IndexError:
            return None
    s_number = 0
    _sortedHeaders(s_number)
    res_set = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res, res_set)

def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''

    # получение id grain и table
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)

    # Получение метаданных таблицы
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    # Заголовки полей
    _headers = getFieldsHeaders(table_meta, "grid")
    
    
    _setFilters(session, currentTable)
    

    totalcount = currentTable.count()
    if totalcount == 0:
        return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps({"records":""})), None) 
    
    # Событие по клику на запись грида
    
    event = {
        "event": [{
            "@name": "row_single_click",
            "action": {
                "#sorted": [{
                    "main_context": "current"
                },
                {
                    "datapanel": {
                        '@type': 'current',
                        '@tab': 'current',
                        "element": {
                            "@id": "12",
                            "add_context": "row_clicked"
                        }
                    }
                }]
            }
        },
        {
            "@name": "row_double_click",
            "action": {
                "@show_in": "MODAL_WINDOW",
                "#sorted": [{
                    "main_context": "current"
                },
                {
                    "datapanel": {
                        '@type': 'current',
                        '@tab': 'current',
                        "element": {
                            "@id": "15",
                            "add_context": "edit"
                        }
                    }
                }]
            }
        }]
    }


    if sortColumnList:
        for column in sortColumnList:
            sortindex = '%s' % column.getSorting()
            for field in _headers:
                if htmlDecode(_headers[field][0]) == column.getId():
                    currentTable.orderBy(field + ' ' + sortindex)
                    
    
    # Определяем переменную для JSON данных
    data = {"records":{"rec":[]}}
    
    # Проходим по таблице и заполняем data
    currentTable.limit(firstrecord - 1, pagesize)
    for rec in currentTable.iterate():
#         rec_dict = {}
        rec_dict = getRecord(currentTable, context, table_meta, grain_name, rec, _headers)
        rec_dict['properties'] = event
        
        data["records"]["rec"].append(rec_dict)
        
        

    res = XMLJSONConverter.jsonToXml(json.dumps(data))
#     print res
    return JythonDTO(res, None)


def getRecord(currentTable, context, table_meta, grain_name, rec, _headers):
    """Возвращает запись для датасета грида (dict).
    Параметры:
        - currentTable (Celesta Cursor object) - объект курсора основной 
        таблицы с данными
        - context (Celesta CallContext) - контекст челесты
        - table_meta (Celesta Metadata !TBD!) - метеданные курсора основной 
        таблицы
        - grain_name (string) - наименование гранулы курсора основной таблицы
        - rec (Celesta Cursor Object) - курсор основной таблицы с данными
        - _headers (dict) - метаданные заголовков основной таблицы
    """
    
    sdf = SimpleDateFormat(DEFAULT_DATETIME_FORMAT_JAVA)
    rec_dict = {}
    
    for field in _headers:
        if rec is None:
            rec_dict[_headers[field][0]] = ''
            continue
        
        if field not in ('~~id',) and _headers[field][1] not in (2, 4, 6, 7, 1):
            rec_dict[_headers[field][0]] = getattr(rec, field)
        # Преобразуем первичный ключ в base64
        elif field == '~~id' and _headers[field][1] not in (4, 6, 7, 1):
            rec_dict[_headers[field][0]] = base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()]))
        #Обработка булевого значения
        elif field not in ('~~id',) and _headers[field][1] == 1:
            refFieldId = getattr(rec, field)
            if getattr(rec, field) == True:
                rec_dict[_headers[field][0]] = 'Да'
            else:
                rec_dict[_headers[field][0]] = 'Нет'
        #обработка даты. По умолчанию выводится дата и время
        elif field not in ('~~id',) and _headers[field][1] == 2:
            value = getattr(rec, field) or ''
            if value:
                value = sdf.format(value)
                
            rec_dict[_headers[field][0]] = value
        #Обработка reference value    
        elif field not in ('~~id',) and _headers[field][1] == 7:
            refFieldId = getattr(rec, field)
            if refFieldId != '' and refFieldId is not None:
                column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
                refTableName = column_jsn["refTable"]
                relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                relatedTable.get(refFieldId)
                rec_dict[_headers[field][0]] = getattr(relatedTable, column_jsn["refTableColumn"])
            else:
                rec_dict[_headers[field][0]] = ''
        #Обработка reference list
        elif field not in ('~~id',) and _headers[field][1] == 6:
            column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
            refTableName = column_jsn["refTable"]
            mappingTableName = column_jsn["refMappingTable"]
            refTableColumn = column_jsn["refTableColumn"]
            relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
            mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
            #Получаем primarykey'и для таблиц
            currentTablePKs = []
            relatedTablePKs = []
            currentTablePKObject = currentTable.meta().getPrimaryKey()
            for key in currentTablePKObject:
                currentTablePKs.extend([key])
            relatedTablePKObject = relatedTable.meta().getPrimaryKey()
            for key in relatedTablePKObject:
                relatedTablePKs.extend([key])
                #получаем foreignkey'и для таблицы с меппингом
            foreignKeys = mappingTable.meta().getForeignKeys()
            aForeignKeyColumns = []
            bForeignKeyColumns = []

            for foreignKey in foreignKeys:
                #referencedTable = foreignKey.getReferencedTable()
                #проверяем к какой таблице относится ключ и получаем список зависимых полей
                if foreignKey.getReferencedTable() == currentTable.meta():
                    aForeignKeyColumns = foreignKey.getColumns()
                else:
                    bForeignKeyColumns = foreignKey.getColumns()
                #ставим фильтр на таблицу меппинга по текущему значению primarykey'ев главной таблицы
            refValue = ""
            if aForeignKeyColumns != None and aForeignKeyColumns != '':
                for foreignKeyColumn, key in zip(aForeignKeyColumns, currentTablePKs):
                    mappingTable.setRange(foreignKeyColumn, getattr(currentTable, key))

                #для каждого значения в отфильтрованной таблице меппинга
            if bForeignKeyColumns != None and bForeignKeyColumns != '':
                for mappingRec in mappingTable.iterate():
                    currentRecordIds = []
                        #набиваем значения primarykey'ев для связанной таблицы, чтобы потом получить значения
                    for foreignKeyColumn in bForeignKeyColumns:
                        currentRecordIds.extend([getattr(mappingRec, foreignKeyColumn)])
                    #находим запись по primarykey'ям и получаем значение теребуемого поля и добавляем к уже найденным
                    if len(currentRecordIds) > 0:
                        if relatedTable.tryGet(*currentRecordIds):
                            refValue = refValue + getattr(relatedTable, refTableColumn) + "; "
            rec_dict[_headers[field][0]] = refValue
    return rec_dict

def getSettings(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    try:
        panelWidth = str(int(json.loads(session)['sessioncontext']['currentDatapanelWidth']) - 55) + 'px'
        panelHeight = int(json.loads(session)['sessioncontext']['currentDatapanelHeight']) - 115
    except:
        panelWidth = '900px'
        panelHeight = 450
    # Вычисляем количества записей в таблице
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)

    _setFilters(session, currentTable)
                
    totalcount = currentTable.count()
    # Метаданные таблицы
    table_meta = currentTable.meta()
    # Заголовок таблицы
    table_name = json.loads(table_meta.getCelestaDoc())["name"]
    # Заголовки полей
    _headers = getFieldsHeaders(table_meta, "grid")
    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50", "@gridWidth": panelWidth, "@gridHeight": panelHeight, "@totalCount":totalcount, "@profile":"sprdata.properties"},
    "labels":{"header":table_name}
    }
    # Определяем список порядковых номеров полей для сортировки
    sort_list = getSortList(table_meta)
    sorted_list = []
    # Добавляем поля для отображения в gridsettings
    def _sortedHeaders(s_number):
        try:
            sort_number = sort_list[s_number]
            for field in _headers:
                order_grid = _headers[field][2]
                if order_grid != sort_number or order_grid in sorted_list:
                    continue
                else:
                    if field not in ('~~id',) and _headers[field][1] != (4):
                        settings["gridsettings"]["columns"]["col"].append({"@id":htmlDecode(_headers[field][0])})
                    elif field not in ('~~id',) and _headers[field][1] == (4):
                        settings["gridsettings"]["columns"]["col"].append({"@id":htmlDecode(_headers[field][0]),
                                                                            "@type": "DOWNLOAD",
                                                                            "@linkId":"download1"})
                    s_number += 1
                    _sortedHeaders(s_number)
                    break
        except IndexError:
            return None
    s_number = 0
    _sortedHeaders(s_number)
    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    currentTable = relatedTableCursorImport(json.loads(main)['grain'], json.loads(main)['table'])(context)
    table_meta = currentTable.meta()
    table_jsn = json.loads(table_meta.getCelestaDoc())
    #признак иерархичности
    isHierarchical = table_jsn['isHierarchical']
    if isHierarchical == 'true':
        for column in table_meta.getColumns():
            #получаем названия колонок с кодом дьюи и сортировкой
            if json.loads(table_meta.getColumn(column).getCelestaDoc())['name'] == u'deweyCode':
                deweyColumn = column
            if json.loads(table_meta.getColumn(column).getCelestaDoc())['name'] == u'sortNumber':
                sortColumn = column
    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style_edit, style_del = "true", "true"
        style_up, style_down, style_left, style_right = "true", "true", "true", "true"
        #if isHierarchical == 'true':
            #style_add="true"
    else:
        currentRecordId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        style_up, style_down, style_left, style_right = "false", "false", "false", "false"
        if isHierarchical == 'true':
            selectedRecordId = json.loads(base64.b64decode(str(currentRecordId)))
            currentTable.get(*selectedRecordId)
            currentNumber = getattr(currentTable, deweyColumn)
            if isExtr(context, currentTable, deweyColumn, sortColumn, 'first'):
                style_up = 'true'
                style_right = 'true'
            if isExtr(context, currentTable, deweyColumn, sortColumn, 'last'):
                style_down = 'true'
            if len(currentNumber.split('.')) == 1:
                style_left = 'true'

        if currentTable.canModify(): style_edit = "false"
        else: style_edit = "true"

        if currentTable.canDelete(): style_del = "false"
        else: style_del = "true"

    if currentTable.canInsert(): style_add = "false"
    else: style_add = "true"

    if currentTable.canDelete(): style_delall = "false"
    else: style_delall = "true"


    item_common = [{
        "@img": 'gridToolBar/addFolder.png',
        "@text": "Добавить",
        "@hint": "Добавить",
        "@disable": style_add,
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [{
                "main_context": "current"
            },
            {
                "modalwindow": {
                    "@width": "685",
                    "@height": "900",
                    "@caption": "Добавление"
                }
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "15",
                        "add_context": "add"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/editFolder.png',
        "@text": "Редактировать",
        "@hint": "Редактировать",
        "@disable": style_edit,
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [{
                "main_context": "current"
            },
            {
                "modalwindow": {
                    "@width": "685",
                    "@height": "900",
                    "@caption": "Редактирование"
                }
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "15",
                        "add_context": "edit"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/delFolder.png',
        "@text": "Удалить",
        "@hint": "Удалить",
        "@disable": style_del,
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [{
                "main_context": "current"
            },
            {
                "modalwindow": {
                    "@width": "350",
                    "@height": "150",
                    "@caption": "Удаление"
                }
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "16",
                        "add_context": "edit"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/delFolder.png',
        "@text": "Удалить все",
        "@hint": "Удалить все",
        "@disable": style_delall,
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [{
                "main_context": "current"
            },
            {
                "modalwindow": {
                    "@width": "350",
                    "@height": "150",
                    "@caption": "Удаление"
                }
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "17",
                        "add_context": "edit"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/importXls.png',
        "@text": "Импорт из xls",
        "@hint": "Импорт из xls",
        "@disable": style_add,
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [{
                "main_context": "current"
            },
            {
                "modalwindow": {
                    "@width": "430",
                    "@height": "160",
                    "@caption": "Импорт из xls"
                }
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "18",
                        "add_context": "import"
                    }
                }
            }]
        }
    }]
#     {
#         "@img": "",
#         "@text": "Импорт из старой системы",
#         "@hint": "Импорт из xls",
#         "@disable": style_add,
#         "action": {
#             "@show_in": "MODAL_WINDOW",
#             "#sorted": [{
#                 "main_context": "current"
#             },
#             {
#                 "modalwindow": {
#                     "@width": "430",
#                     "@height": "160",
#                     "@caption": "Импорт из xls"
#                 }
#             },
#             {
#                 "datapanel": {
#                     "@type": "current",
#                     "@tab": "current",
#                     "element": {
#                         "@id": "19",
#                         "add_context": "import"
#                     }
#                 }
#             }]
#         }
#     }]
    
    item_export = [{
        "@img": 'gridToolBar/dirusing/ExportToExcelAll.png',
        "@text": "",
        "@hint": "Экспорт в Excel всей таблицы",
        "@disable": "false",
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [{
                "main_context": "current"
            },
            {
                "modalwindow": {
                    "@width": "430",
                    "@height": "170",
                    "@caption": "Экспорт в xls"
                }
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "14",
                        "add_context": ""
                    }
                }
            }]
        }
    }]
    
    
    item_hierarchy = [{
        "@img": 'gridToolBar/dirusing/up.png',
        "@text": "",
        "@hint": "Сдвинуть элемент вверх на том же уровне",
        "@disable": style_up,
        "action": {
            "#sorted": [{
                "main_context": "current"
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "13",
                        "add_context": ""
                    }
                }
            },
            {
                "server": {
                    "activity": {
                        "@id": "1",
                        "@name": "dirusing.hierarchy.move.celesta",
                        "add_context": "up"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/dirusing/down.png',
        "@text": "",
        "@hint": "Сдвинуть элемент вниз на том же уровне",
        "@disable": style_down,
        "action": {
            "#sorted": [{
                "main_context": "current"
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "13",
                        "add_context": ""
                    }
                }
            },
            {
                "server": {
                    "activity": {
                        "@id": "2",
                        "@name": "dirusing.hierarchy.move.celesta",
                        "add_context": "down"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/dirusing/left.png',
        "@text": "",
        "@hint": "Сдвинуть элемент на уровень вверх",
        "@disable": style_left,
        "action": {
            "#sorted": [{
                "main_context": "current"
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "13",
                        "add_context": ""
                    }
                }
            },
            {
                "server": {
                    "activity": {
                        "@id": "3",
                        "@name": "dirusing.hierarchy.move.celesta",
                        "add_context": "left"
                    }
                }
            }]
        }
    },
    {
        "@img": 'gridToolBar/dirusing/right.png',
        "@text": "",
        "@hint": "Сдвинуть элемент на уровень вниз",
        "@disable": style_right,
        "action": {
            "#sorted": [{
                "main_context": "current"
            },
            {
                "datapanel": {
                    "@type": "current",
                    "@tab": "current",
                    "element": {
                        "@id": "13",
                        "add_context": ""
                    }
                }
            },
            {
                "server": {
                    "activity": {
                        "@id": "4",
                        "@name": "dirusing.hierarchy.move.celesta",
                        "add_context": "right"
                    }
                }
            }]
        }
    }]
    
    if isHierarchical == 'true':
        data = {"gridtoolbar":{"item":item_export + item_hierarchy + item_common
                           }
            }

    else:
        data = {"gridtoolbar":{"item":item_export + item_common
                           }
            }
        
    return XMLJSONConverter.jsonToXml(json.dumps(data))

