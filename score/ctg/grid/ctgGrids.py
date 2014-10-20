# coding: utf-8
'''
Created on 12.08.2014

@author: Rudenko
'''

import simplejson as json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList, htmlDecode

def getData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''
    
    # получение id grain и table
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    contragTypeId = json.loads(main)['contragTypeId']
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    ctgSetup = relatedTableCursorImport('acrsprav', 'ctg_setup')(context)
    ctgFields = relatedTableCursorImport('acrsprav', 'ctg_fields')(context)
    ctgSetup.setRange('org_type', contragTypeId)
    # Получение метаданных таблицы
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    # Заголовки полей
    _headers = getFieldsHeaders(table_meta,"grid")
    
    #table_jsn = json.loads(table_meta.getCelestaDoc())
    if str(contragTypeId)!='-1':
        currentTable.setFilter("org_type", "'"+str(contragTypeId)+"'") #Не работает с русским
    if filterinfo is not None and filterinfo!='':
        filterName = json.loads(filterinfo)['schema']['context']['name']  
        filterInn = json.loads(filterinfo)['schema']['context']['inn']
        filtercontragType = json.loads(filterinfo)['schema']['context']['type']["@id"]
        if filterName!='' and filterName is not None:
            filterText = "%'"+filterName+"'%"
            print filterText
            currentTable.setFilter("name", filterText)
        if filterInn!='':
            currentTable.setFilter("inn", "%'"+str(filterInn)+"'%")
        if filtercontragType!='' and filtercontragType!='-1':
            currentTable.setFilter("org_type", "'"+str(filtercontragType)+"'")
    totalcount = currentTable.count()
    
    if totalcount!=0:
        # Определяем переменную для JSON данных
        data = {"records":{"rec":[]}}
        # Событие по клику на запись грида


        event = {"event":
                [{"@name":"row_single_click",
                 "action":
                    {"main_context":"current",
                     "datapanel":
                        {'@type':'current',
                         '@tab':'current',
                         "element":{"@id":"12",
                                     "add_context":"row_clicked"}
                         }
                    }
                 },
                 {"@name":"row_double_click",
                 "action":
                    {"@show_in":"MODAL_WINDOW",
                     "main_context":"current",
                     "datapanel":
                        {'@type':'current',
                         '@tab':'current',
                         "element":{"@id":"15",
                                     "add_context":"edit"}
                                     }
                     }
                  }
                    ]
                 }


        if sortColumnList:
            for column in sortColumnList:
                sortindex = '%s' % column.getSorting()        
                for field in _headers:
                    if htmlDecode(_headers[field][0]) == column.getId():
                        currentTable.orderBy(field +' '+sortindex)
        # Проходим по таблице и заполняем data
        currentTable.limit(firstrecord-1,pagesize)
        for rec in currentTable.iterate():
            rec_dict = {}
            for field in _headers:
                if field not in ('~~id',):
                    if contragTypeId!='-1':
                        ctgFields.setRange('dbname', field)
                        ctgFields.first()
                        ctgFieldId = getattr(ctgFields, 'id') 
                        ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
                        if ctgSetup.tryFirst():
                            ctgRequired = getattr(ctgSetup, 'required')
                        else:
                            ctgRequired = None
                    else:
                        ctgRequired = True
                
                if field not in ('~~id',) and _headers[field][1] not in (4,6,7) and (ctgRequired is not None or contragTypeId=='-1'):
                    rec_dict[_headers[field][0]] = getattr(rec, field)
                # Преобразуем первичный ключ в base64
                if field == '~~id' and _headers[field][1] not in (4,6,7): 
                    rec_dict[_headers[field][0]] = base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()]))
                #Обработка reference value
                if field not in ('~~id',) and _headers[field][1] == 7 and (ctgRequired is not None or contragTypeId=='-1'):
                    refFieldId = getattr(rec, field)
                    if refFieldId!='' and refFieldId is not None:
                        column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
                        refTableName = column_jsn["refTable"]
                        relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                        relatedTable.get(refFieldId)
                        rec_dict[_headers[field][0]] = getattr(relatedTable, column_jsn["refTableColumn"])
                    
                #Обработка reference list
                if field not in ('~~id',) and _headers[field][1] == 6 and (ctgRequired is not None or contragTypeId=='-1'):
                    column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
                    refTableName = column_jsn["refTable"]
                    mappingTableName = column_jsn["refMappingTable"]
                    refTableColumn = column_jsn["refTableColumn"]
                    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                    mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                    #Получаем primarykey'и для таблиц
                    currentTablePKs=[]
                    relatedTablePKs=[]
                    currentTablePKObject = currentTable.meta().getPrimaryKey()
                    for key in currentTablePKObject:
                        currentTablePKs.extend([key])
                    relatedTablePKObject = relatedTable.meta().getPrimaryKey()
                    for key in relatedTablePKObject:
                        relatedTablePKs.extend([key])
                    #получаем foreignkey'и для таблицы с меппингом
                    foreignKeys = mappingTable.meta().getForeignKeys()
                    for foreignKey in foreignKeys:
                        #проверяем к какой таблице относится ключ и получаем список зависимых полей
                        if foreignKey.getReferencedTable() == currentTable.meta():
                            aForeignKeyColumns = foreignKey.getColumns()
                        else:
                            bForeignKeyColumns = foreignKey.getColumns()
                    #ставим фильтр на таблицу меппинга по текущему значению primarykey'ев главной таблицы
                    for foreignKeyColumn,key in zip(aForeignKeyColumns, currentTablePKs):
                        mappingTable.setRange(foreignKeyColumn,getattr(currentTable, key))
                    refValue=""
                    #для каждого значения в отфильтрованной таблице меппинга
                    for mappingRec in mappingTable.iterate():
                        currentRecordIds=[]
                        #набиваем значения primarykey'ев для связанной таблицы, чтобы потом получить значения
                        for foreignKeyColumn in bForeignKeyColumns:
                            currentRecordIds.extend([getattr(mappingRec, foreignKeyColumn)])
                        #находим запись по primarykey'ям и получаем значение теребуемого поля и добавляем к уже найденным
                        relatedTable.get(*currentRecordIds)
                        refValue = refValue+getattr(relatedTable, refTableColumn)+"; "
                    rec_dict[_headers[field][0]] = refValue
                       
            # Заносим событие в properties
            rec_dict['properties'] = event

            data["records"]["rec"].append(rec_dict)
    else:
        data = {"records":""}
    
    res = XMLJSONConverter(input=data).parse()
    print res
    return JythonDTO(res, None)
   

def getMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''

    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    contragTypeId = json.loads(main)['contragTypeId']
    try:
        panelWidth = str(int(json.loads(session)['sessioncontext']['currentDatapanelWidth'])-55)+'px'
        panelHeight = int(json.loads(session)['sessioncontext']['currentDatapanelHeight'])-115
    except:
        panelWidth = '900px'
        panelHeight = 450
    # Вычисляем количества записей в таблице
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    ctgSetup = relatedTableCursorImport('acrsprav', 'ctg_setup')(context)
    ctgFields = relatedTableCursorImport('acrsprav', 'ctg_fields')(context)
    ctgSetup.setRange('org_type', contragTypeId)
    totalcount = currentTable.count()
    # Метаданные таблицы
    table_meta = currentTable.meta()
    # Заголовок таблицы
    table_name = json.loads(table_meta.getCelestaDoc())["name"]
    # Заголовки полей
    _headers = getFieldsHeaders(table_meta,"grid")
    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50", "@gridWidth": panelWidth, "@gridHeight": panelHeight, "@totalCount":totalcount, "@profile":"default.properties"},
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
                if field not in ('~~id',):
                    if contragTypeId!='-1':
                        ctgFields.setRange('dbname', field)
                        ctgFields.first()
                        ctgFieldId = getattr(ctgFields, 'id')
                        ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
                        test = ctgSetup.tryFirst()
                        print test
                        if ctgSetup.tryFirst():
                            ctgRequired = getattr(ctgSetup, 'required') 
                            print ctgRequired
                        else:
                            ctgRequired = None
                    else:
                        ctgRequired = True
                else:
                    ctgRequired = None
                order_grid = _headers[field][2]
                if order_grid != sort_number or order_grid in sorted_list:
                    continue
                else:
                    if field not in ('~~id',) and _headers[field][1] not in (4,)  and ctgRequired is not None:
                        settings["gridsettings"]["columns"]["col"].append({"@id":htmlDecode(_headers[field][0])})
                    elif field not in ('~~id',) and _headers[field][1] in (4,)  and ctgRequired is not None:
                        settings["gridsettings"]["columns"]["col"].append({"@id":htmlDecode(_headers[field][0]),
                                                                            "@type": "DOWNLOAD",
                                                                            "@linkId":"download1"})
                    s_number +=1
                    _sortedHeaders(s_number)
                    break
        except IndexError:
            return None
    s_number = 0            
    _sortedHeaders(s_number)
    res = XMLJSONConverter(input=settings).parse()
    print res
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    
    currentTable = relatedTableCursorImport(grain_name,table_name)(context)
    
    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style_edit, style_del = "true","true"
    else:
        
        if currentTable.canModify(): style_edit = "false"
        else: style_edit = "true"
            
        if currentTable.canDelete(): style_del = "false"
        else: style_del = "true"
        
    if currentTable.canInsert(): style_add = "false"
    else: style_add = "true"
    
    if currentTable.canDelete(): style_delall = "false"
    else: style_delall = "true"
    
    
    data = {"gridtoolbar":{"item":[{"@img": 'gridToolBar/addFolder.png',
                                    "@text":"Добавить",
                                   "@hint":"Добавить",
                                   "@disable": style_add,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                             "main_context":"current",
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "15",
                                                                      "add_context":"add"
                                                                      }
                                                          }
                                             }
                                   },
                           {"@img": 'gridToolBar/editFolder.png',
                            "@text":"Редактировать",
                                   "@hint":"Редактировать",
                                   "@disable": style_edit,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                             "main_context":"current",
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "15",
                                                                      "add_context":"edit"
                                                                      }
                                                          }
                                             }
                                   },
                                   {"@img": 'gridToolBar/delFolder.png',
                            "@text":"Удалить",
                                   "@hint":"Удалить",
                                   "@disable": style_del,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                            "#sorted":[{"main_context":"current"}],
                                             "modalwindow":{"@width":"350","@height":"150","@caption":"Удаление"},
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "16",
                                                                      "add_context":"edit"
                                                                      }
                                                          }
                                             }
                                   },
                                    {"@img": 'gridToolBar/delFolder.png',
                            "@text":"Удалить все",
                                   "@hint":"Удалить все",
                                   "@disable": style_delall,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                             "#sorted":[{"main_context":"current"}],
                                             "modalwindow":{"@width":"350","@height":"150","@caption":"Удаление"},
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "17",
                                                                      "add_context":"edit"
                                                                      }
                                                          }
                                             }
                                   },
                                    {"@img": 'gridToolBar/importXls.png',
                            "@text":"Импорт из xls",
                                   "@hint":"Импорт из xls",
                                   "@disable": style_add,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                             "#sorted":[{"main_context":"current"}],
                                             "modalwindow":{"@width":"430","@height":"160","@caption":"Импорт из xls"},
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "18",
                                                                      "add_context":"import"
                                                                      }
                                                          }
                                             }
                                   }
                                
                                   ]
                           }
            }
    
    return XMLJSONConverter(input=data).parse()


def getGroupsData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''
    
   
    group_orgs = relatedTableCursorImport('acrsprav', 'group_orgs')(context)
    contrags = relatedTableCursorImport('acrsprav', 'contrags')(context)

    ctg_type = relatedTableCursorImport('acrsprav', 'contrag_type')(context)
    if filterinfo is not None and filterinfo!='':
        filterGroupId = json.loads(filterinfo)['schema']['context']['company']['@id'] 
        filterCheck = json.loads(filterinfo)['schema']['context']['ondate']['@check']
        filterOnDate = json.loads(filterinfo)['schema']['context']['ondate']['@value']
        if filterGroupId!='':
            group_orgs.setFilter("gr_id", "'"+str(filterGroupId)+"'")
        if filterCheck=='true':
            if filterOnDate!='':
                group_orgs.setComplexFilter("start_date<='"+'20140101'+"' and (end_date>'"+filterOnDate+"' or end_date is null)")
            
    totalcount = group_orgs.count()
    if totalcount!=0:
        data = {"records":{"rec":[]}}
        
        event = {"event":
                [{"@name":"row_single_click",
                 "action":
                    {"main_context":"current",
                     "datapanel":
                        {'@type':'current',
                         '@tab':'current',
                         "element":{"@id":"12",
                                     "add_context":"row_clicked"}
                         }
                    }
                 }
                 
                    ]
                 }
        for rec in group_orgs.iterate():
            rec_dict = {}
            
            contrags.get(getattr(rec, 'org_id'))
            orgTypeId = getattr(contrags, 'org_type')
            if orgTypeId is not None and orgTypeId != '':
                ctg_type.get(getattr(contrags, 'org_type'))
            rec_dict['_x007e__x007e_id'] = getattr(rec, 'id')
            rec_dict['Тип'] = getattr(ctg_type, 'name')
            rec_dict['Наименование'] = getattr(contrags, 'name')
            rec_dict['Идентификатор'] = getattr(contrags, 'inn')
            rec_dict['Дата_x0020_вхождения_x0020_в_x0020_группу'] = getattr(rec, 'start_date')
            rec_dict['Дата_x0020_исключения_x0020_из_x0020_группы'] = getattr(rec, 'end_date')
            rec_dict['properties'] = event
            data["records"]["rec"].append(rec_dict)
    else:
        data = {"records":""}
    res = XMLJSONConverter(input=data).parse()
    print res
    return JythonDTO(res, None)    





def getGroupsMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''

    try:
        panelWidth = str(int(json.loads(session)['sessioncontext']['currentDatapanelWidth'])-55)+'px'
        panelHeight = int(json.loads(session)['sessioncontext']['currentDatapanelHeight'])-115
    except:
        panelWidth = '900px'
        panelHeight = 450
    # Вычисляем количества записей в таблице
    currentTable = relatedTableCursorImport('acrsprav', 'group_orgs')(context)
    totalcount = currentTable.count()
    table_meta = currentTable.meta()
    _headers = getFieldsHeaders(table_meta,"grid")
    # Определяем список полей таблицы для отображения
    settings = {}
    
    settings["gridsettings"] = {"columns": {"col":[{"@id":"Тип", "@width":"150px"}, {"@id":"Наименование", "@width":"300px"},{"@id":"Идентификатор", "@width":"150px"}, {"@id":"Дата вхождения в группу", "@width":"120px"}, {"@id":"Дата исключения из группы", "@width":"120px"}]},
    "properties": {"@pagesize":"50", "@gridWidth": panelWidth, "@gridHeight": panelHeight, "@totalCount":totalcount, "@profile":"default.properties"},
    "labels":{"header":None}
    }
    
    res = XMLJSONConverter(input=settings).parse()
    print res
    return JythonDTO(None, res)       


def gridGroupsToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    currentTable = relatedTableCursorImport("acrsprav","group_orgs")(context)
    
    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style_edit, style_del = "true","true"
    else:
        
        if currentTable.canModify(): style_edit = "false"
        else: style_edit = "true"
            
        if currentTable.canDelete(): style_del = "false"
        else: style_del = "true"
        
    if currentTable.canInsert(): style_add = "false"
    else: style_add = "true"
    
    
    data = {"gridtoolbar":{"item":[{"@img": 'gridToolBar/addFolder.png',
                                    "@text":"Добавить в группу",
                                   "@hint":"Добавить в группу",
                                   "@disable": style_add,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                             "main_context":"current",
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "15",
                                                                      "add_context":filterinfo
                                                                      }
                                                          }
                                             }
                                   },
                           {"@img": 'gridToolBar/delFolder.png',
                            "@text":"Исключить из группы",
                                   "@hint":"Исключить из группы",
                                   "@disable": style_edit,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                             "main_context":"current",
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "16",
                                                                      "add_context":"edit"
                                                                      }
                                                          }
                                             }
                                   },
                                   {"@img": 'gridToolBar/delFolder.png',
                            "@text":"Удалить запись",
                                   "@hint":"Удалить запись",
                                   "@disable": style_del,
                                   "action":{"@show_in": "MODAL_WINDOW",
                                            "#sorted":[{"main_context":"current"}],
                                             "modalwindow":{"@width":"350","@height":"150","@caption":"Удаление"},
                                             "datapanel":{"@type": "current",
                                                          "@tab": "current",
                                                          "element": {"@id": "17",
                                                                      "add_context":"edit"
                                                                      }
                                                          }
                                             }
                                   }
                                    
                                
                                   ]
                           }
            }
    
    return XMLJSONConverter(input=data).parse()
 
    