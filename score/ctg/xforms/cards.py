# coding: utf-8
'''
Created on 12.08.2014

@author: Rudenko
'''

import simplejson as json
import base64
import time
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:  
    from ru.curs.showcase.core import UserMessage
except:
    pass
from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList
from datetime import datetime

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''
    
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    contragTypeId = json.loads(main)['contragTypeId']
    table_id='1'
    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    ctgSetup = relatedTableCursorImport('acrsprav', 'ctg_setup')(context)
    ctgFields = relatedTableCursorImport('acrsprav', 'ctg_fields')(context)
    ctgSetup.setRange('org_type', contragTypeId)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    table_jsn = json.loads(table_meta.getCelestaDoc())
    # Заголовок таблицы
    table_name = table_jsn["name"]
    # Получение заголовков полей
    _headers = getFieldsHeaders(table_meta,"xform")
    sort_list = getSortList(table_meta)
    sorted_list = []
    # Пустая структура данных, связнная с текущим справочником
    xformsdata = {"schema":{"@xmlns":"",
                            "edit": "true",
                            "showselect": "true",
                            "error_message": "",
                            "row": "",
                            "spravs": {"sprav":{"@id": table_id,
                                                "@name": table_name,
                                                "field": []
                                                }
                                       }


                            }
                  }

    
    # Получаем словарь полей и заголовков полей справочника
    def _sortedHeaders(s_number):
        try:
            sort_number = sort_list[s_number]
            if add == 'add' or add is None or add == '':
                for field in _headers:
                    
                    order_grid = _headers[field][2]
                    if order_grid != sort_number or order_grid in sorted_list:
                        continue
                    else:
                        field_data = {}
                        if field not in ('~~id',):
                            ctgFields.setRange('dbname', field)
                            ctgFields.first()
                            ctgFieldId = getattr(ctgFields, 'id') 
                            print ctgFieldId
                            ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
                            if ctgSetup.tryFirst():
                                ctgRequired = getattr(ctgSetup, 'required') 
                                print ctgRequired
                            else:
                                ctgRequired = None
                            if ctgRequired is not None or field=='org_type' or contragTypeId=='-1':
                                # Получение meta столбца
                                column_meta = table_meta.getColumn(field)
                                column_jsn = json.loads(column_meta.getCelestaDoc())
                                # Общая часть
                                
                                field_data["order"] = column_jsn["fieldOrderInSort"]
                                if ctgRequired == True:
                                    field_data["required"] = "true"
                                else:
                                    field_data["required"] = "false"
                                if int(table_jsn["dirTypeId"]) == 1:
                                    field_data["editable"] = "true"
                                else:
                                    field_data["editable"] = "false"
                                field_data["type_id"] = column_jsn["fieldTypeId"]
                                # Для string
                                if field_data["type_id"] == '9':
                                    field_data["max_length"] = column_meta.getLength()
                                if field_data["type_id"] != 4:
                                    if field_data["required"] == 'true':
                                        field_data["title"] = column_jsn["name"] + ' *'
                                    else:
                                        field_data["title"] = column_jsn["name"]
                                field_data["dbFieldName"] = field
                                # Пустая часть для добавления
                                field_data["ref_table_prefix"] = ""
                                field_data["ref_field_prefix"] = ""
                                field_data["ref_values"] = ""
                                
                                field_data["value"] = ""
                                if field_data["type_id"] == '7'  and field=='org_type' and contragTypeId!='-1':
                                    refFieldId = contragTypeId
                                    refTableName = column_jsn["refTable"]
                                    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                                    relatedTable.get(refFieldId)
                                    refTableColumnValue = getattr(relatedTable, column_jsn["refTableColumn"])
                                    field_data["value"] = refTableColumnValue
                                    field_data["ref_values"] = refFieldId 
                                    field_data["editable"] = "false"   
                                xformsdata["schema"]["spravs"]["sprav"]["field"].append(field_data)
                    s_number +=1
                    _sortedHeaders(s_number)
                    break
           
            else:
                # Редактирование
                # Получение значения первичного ключа записи
                #return UserMessage(u"TEST3", u"%s" % (session))
                currentRecordId = json.loads(base64.b64decode(json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']))
                xformsdata["schema"]["row"] = currentRecordId
                currentTable.get(currentRecordId)
                #Получаем список ключей в таблицы, чтобы сделать их readonly
                primaryKeys=[]
                keys=currentTable.meta().getPrimaryKey()
                for item in keys:
                    primaryKeys.extend([item])
                for field in _headers:
                    order_grid = _headers[field][2]
                    if order_grid != sort_number or order_grid in sorted_list:
                        continue
                    else:
                        field_data = {}
                        if field not in ('~~id',):
                            ctgFields.setRange('dbname', field)
                            
                            ctgFields.first()
                            ctgFieldId = getattr(ctgFields, 'id') 
                            print ctgFieldId
                            ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
                            if ctgSetup.tryFirst():
                                ctgRequired = getattr(ctgSetup, 'required') 
                                print ctgRequired
                            else:
                                ctgRequired = None
                            if ctgRequired is not None or field=='org_type' or contragTypeId=='-1':
                                # Получение meta столбца
                                column_meta = table_meta.getColumn(field)
                                column_jsn = json.loads(column_meta.getCelestaDoc())
                                # Общая часть 
    
                                field_data["order"] = column_jsn["fieldOrderInSort"]
                                if column_meta.isNullable() == False:
                                    field_data["required"] = "true"
                                else:
                                    field_data["required"] = "false"
                                if int(table_jsn["dirTypeId"]) == 1 and field not in primaryKeys:
                                    field_data["editable"] = "true"
                                else:
                                    field_data["editable"] = "false"
                                field_data["type_id"] = int(column_jsn["fieldTypeId"])
                                # Для string
                                
                                
                                if field_data["type_id"] == 9:
                                    field_data["max_length"] = column_meta.getLength()
                                if field_data["type_id"] != 4:
                                    if field_data["required"] == 'true':
                                        field_data["title"] = column_jsn["name"] + ' *'
                                    else:
                                        field_data["title"] = column_jsn["name"]
                                field_data["dbFieldName"] = field
                                # Часть для редактирования
                                field_data["ref_table_prefix"] = ""
                                field_data["ref_field_prefix"] = ""
                                if field_data["type_id"] in (1, 2, 3, 5, 9, 10, 11, 12):
                                    field_data["value"] = getattr(currentTable, field)
                                elif field_data["type_id"] == 7:
                                    refFieldId = getattr(currentTable, field)
                                    if refFieldId!='':
                                        refTableName = column_jsn["refTable"]
                                        relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                                        relatedTable.get(refFieldId)
                                        refTableColumnValue = getattr(relatedTable, column_jsn["refTableColumn"])
                                    else:
                                        refTableColumnValue=''
                                    field_data["value"] = refTableColumnValue
                                    field_data["ref_values"] = refFieldId
                                    
                                
                                # временно, пока не разобрался с другими типами полей
                                elif field_data["type_id"] == 6:
                                    refTableName = column_jsn["refTable"]
                                    mappingTableName = column_jsn["refMappingTable"]
                                    refTableColumn = column_jsn["refTableColumn"]
                                    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                                    mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                                    foreignKeys = mappingTable.meta().getForeignKeys()
                                    mappingPrimaryKeys=mappingTable.meta().getPrimaryKey()
                                    for key in mappingPrimaryKeys:
                                        mappingPrimaryKey=key
                                    currentTablePKs=[]
                                    relatedTablePKs=[]
                                    currentTablePKObject = currentTable.meta().getPrimaryKey()
                                    for key in currentTablePKObject:
                                        currentTablePKs.extend([key])
                                    relatedTablePKObject = relatedTable.meta().getPrimaryKey()
                                    for key in relatedTablePKObject:
                                        relatedTablePKs.extend([key])
                                        
                                    for foreignKey in foreignKeys:
                                        #проверяем к какой таблице относится ключ и получаем список зависимых полей
                                        if foreignKey.getReferencedTable() == currentTable.meta():
                                            aForeignKeyColumns = foreignKey.getColumns()
                                        else:
                                            bForeignKeyColumns = foreignKey.getColumns()
                                    for foreignKeyColumn,key in zip(aForeignKeyColumns, currentTablePKs):
                                        mappingTable.setRange(foreignKeyColumn,getattr(currentTable, key))
                    
                                    if mappingTable.count()!=0:
                                        field_data["ref_values"]={"item":[]}
                                    else:
                                        field_data["ref_values"]=''
                                    for mappingRec in mappingTable.iterate():
                                        currentRecordIds=[]
                                        
                                        
                                        mappingId=getattr(mappingRec, mappingPrimaryKey)
                                       
                                        #набиваем значения primarykey'ев для связанной таблицы, чтобы потом получить значения
                                        for foreignKeyColumn in bForeignKeyColumns:
                                            currentRecordIds.extend([getattr(mappingRec, foreignKeyColumn)])
                                        #находим запись по primarykey'ям и получаем значение теребуемого поля и добавляем к уже найденным
                                        
                                        jsondump = json.dumps(currentRecordIds)
                                        currentRecordCoded=base64.b64encode(str(jsondump))
                        
                                        
                                        relatedTable.get(*currentRecordIds)
                                        
                                        field_items = {'id':currentRecordCoded,'value':getattr(relatedTable, refTableColumn), 'mapping_id':mappingId}
                                        
                                        field_data["ref_values"]["item"].append(field_items)
                                       
                                    
                                    
                                  
                                    
                                else:
                                    field_data["value"] = ""
                                xformsdata["schema"]["spravs"]["sprav"]["field"].append(field_data)
                    s_number +=1
                    _sortedHeaders(s_number)
                    break
        except IndexError:
            return None
    s_number = 0            
    _sortedHeaders(s_number)
    
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }

    print XMLJSONConverter(input=xformsdata).parse()
    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())
     
def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника. '''
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    contragTypeId = json.loads(main)['contragTypeId']
    # Курсор текущей таблицы
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    ctgSetup = relatedTableCursorImport('acrsprav', 'ctg_setup')(context)
    ctgFields = relatedTableCursorImport('acrsprav', 'ctg_fields')(context)
    ctgSetup.setRange('org_type', contragTypeId)
    data_dict = json.loads(xformsdata)
    if data_dict["schema"]["row"] == '':
        # Добавление новой записи
        field_list = data_dict["schema"]["spravs"]["sprav"]["field"]
        
        try:
            dictWithoutRefList = ([item for item in field_list if item["type_id"] != u'6'])
            dictWithRefList = ([item for item in field_list if item["type_id"] == u'6'])
        except TypeError:
            if field_list["type_id"] != u'6':
                dictWithoutRefList = [field_list]
                dictWithRefList = []
            elif field_list["type_id"] == u'6':
                dictWithRefList = [field_list]
                dictWithoutRefList = []
        
       
        for field in dictWithoutRefList:
            ctgFields.setRange('dbname', field)
                            
            ctgFields.first()
            ctgFieldId = getattr(ctgFields, 'id') 
            print ctgFieldId
            ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
            if ctgSetup.tryFirst():
                ctgRequired = getattr(ctgSetup, 'required') 
                print ctgRequired
            else:
                ctgRequired = None
            
            if field["type_id"] in ('1', '2','3', '5', '9', '10', '11', '12') and (ctgRequired is not None or field=='org_type'):
                setattr(currentTable, field["dbFieldName"], field["value"])
            elif field["type_id"] in ('7') and (ctgRequired is not None or field=='org_type'):
                setattr(currentTable, field["dbFieldName"], field["ref_values"])
        currentTable.insert()
        for field in dictWithRefList:
            ctgFields.setRange('dbname', field)
                            
            ctgFields.first()
            ctgFieldId = getattr(ctgFields, 'id') 
            print ctgFieldId
            ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
            if ctgSetup.tryFirst():
                ctgRequired = getattr(ctgSetup, 'required') 
                print ctgRequired
            else:
                ctgRequired = None
            if ctgRequired is not None or field=='org_type':    
                column_jsn = json.loads(currentTable.meta().getColumn(field["dbFieldName"]).getCelestaDoc())
                mappingTableName = column_jsn["refMappingTable"]
                mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                currentTablePKObject = currentTable.meta().getPrimaryKey()
                
                foreignKeys = mappingTable.meta().getForeignKeys()
                for foreignKey in foreignKeys:
                            
                            #проверяем к какой таблице относится ключ и получаем список зависимых полей
                            if foreignKey.getReferencedTable() == currentTable.meta():
                                aForeignKeyColumns = foreignKey.getColumns()
                            else:
                                bForeignKeyColumns = foreignKey.getColumns()
              
                if field["ref_values"]=='':
                    break
                if type(field["ref_values"]["item"])==list:
                    for item in field["ref_values"]["item"]:
                        
                        mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                        
                        itemDecoded= base64.b64decode(item["id"])
                        
                        bForeignKeyColumnsValues = json.loads(itemDecoded)
                        for colA, PKA in zip(aForeignKeyColumns, currentTablePKObject):
                            setattr(mappingTable, colA, getattr(currentTable, PKA))
                            
                        for colB, value in zip(bForeignKeyColumns,bForeignKeyColumnsValues):
                            setattr(mappingTable, colB, str(value))
                            
                        mappingTable.insert()   
                elif type(field["ref_values"]["item"])==dict:
                    
                    test1= base64.b64decode(field["ref_values"]["item"]["id"]) 
                    bForeignKeyColumnsValues = json.loads(test1)
                    for colA, PKA in zip(aForeignKeyColumns, currentTablePKObject):
                        setattr(mappingTable, colA, getattr(currentTable, PKA))
                        
                    for colB, value in zip(bForeignKeyColumns,bForeignKeyColumnsValues):
                        setattr(mappingTable, colB, str(value))
                        
                    mappingTable.insert()   
                
            
        
    else:
        # Редактирование уже существующей
        currentTable.get(data_dict["schema"]["row"])
        # Список полей
        field_list = data_dict["schema"]["spravs"]["sprav"]["field"]
        
        dictWithoutRefList = ([item for item in field_list if item["type_id"] != u'6'])
        dictWithRefList = ([item for item in field_list if item["type_id"] == u'6'])
        for field in dictWithoutRefList:
            ctgFields.setRange('dbname', field)
                            
            ctgFields.first()
            ctgFieldId = getattr(ctgFields, 'id') 
            print ctgFieldId
            ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
            if ctgSetup.tryFirst():
                ctgRequired = getattr(ctgSetup, 'required') 
                print ctgRequired
            else:
                ctgRequired = None
            if field["type_id"] in ('1', '2','3', '5', '9', '10', '11', '12') and (ctgRequired is not None or field=='org_type'):
                setattr(currentTable, field["dbFieldName"], field["value"])
            elif field["type_id"] in ('7') and (ctgRequired is not None or field=='org_type'):
                setattr(currentTable, field["dbFieldName"], field["ref_values"])
        currentTable.update()
        for field in dictWithRefList:
            ctgFields.setRange('dbname', field)
                            
            ctgFields.first()
            ctgFieldId = getattr(ctgFields, 'id') 
            print ctgFieldId
            ctgSetup.setFilter('ctg_field', "'"+str(ctgFieldId)+"'")
            if ctgSetup.tryFirst():
                ctgRequired = getattr(ctgSetup, 'required') 
                print ctgRequired
            else:
                ctgRequired = None
            if ctgRequired is not None or field=='org_type':  
                column_jsn = json.loads(currentTable.meta().getColumn(field["dbFieldName"]).getCelestaDoc())
                mappingTableName = column_jsn["refMappingTable"]
                mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                currentTablePKObject = currentTable.meta().getPrimaryKey()
                foreignKeys = mappingTable.meta().getForeignKeys()
                for foreignKey in foreignKeys:
                            #проверяем к какой таблице относится ключ и получаем список зависимых полей
                            if foreignKey.getReferencedTable() == currentTable.meta():
                                aForeignKeyColumns = foreignKey.getColumns()
                            else:
                                bForeignKeyColumns = foreignKey.getColumns()
                
                    
                for colA, PKA in zip(aForeignKeyColumns, currentTablePKObject):    
                    mappingTable.setRange(colA, getattr(currentTable, PKA))
                    
                mappingTable.deleteAll()
                if field["ref_values"]=='':
                    break
                if type(field["ref_values"]["item"])==list:
                    for item in field["ref_values"]["item"]:
                        
                        mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                        
                        itemDecoded= base64.b64decode(item["id"])
                        
                        bForeignKeyColumnsValues = json.loads(itemDecoded)
                        for colA, PKA in zip(aForeignKeyColumns, currentTablePKObject):
                            setattr(mappingTable, colA, getattr(currentTable, PKA))
                            
                        for colB, value in zip(bForeignKeyColumns,bForeignKeyColumnsValues):
                            setattr(mappingTable, colB, str(value))
                            
                        mappingTable.insert() 
                elif type(field["ref_values"]["item"])==dict and field["ref_values"]["item"]["id"]!='':
                   
                    mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                    itemDecoded= base64.b64decode(field["ref_values"]["item"]["id"]) 
                    bForeignKeyColumnsValues = json.loads(itemDecoded)
                    for colA, PKA in zip(aForeignKeyColumns, currentTablePKObject):
                        setattr(mappingTable, colA, getattr(currentTable, PKA))
                        
                    for colB, value in zip(bForeignKeyColumns,bForeignKeyColumnsValues):
                        setattr(mappingTable, colB, str(value))
                    mappingTable.insert()   
                
                
def cardGroupsData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''
    if add is not None and add!='':
        groupId = json.loads(add)['schema']['context']['company']['@id']
    else:
        groupId = 1    
    
    xformsdata = {"schema":{"@xmlns":"",
                            "info": {"group":{"@id":groupId, "@allowlinks":"0", "@allowgroups":"0"}},
                            "contrags":None,
                            "deflink":{"links":[]},
                            "row": ""
                            }
                  }

    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": "view"
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())

def cardGroupsDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника. '''

    group_orgs = relatedTableCursorImport("acrsprav", "group_orgs")(context)
    
    data_dict = json.loads(xformsdata)
    groupId = data_dict["schema"]["info"]["group"]["@id"]
    field_list = data_dict["schema"]["contrags"]["contrag"]
    print str(type(field_list))
    if type(field_list)==list:
        for contrag in field_list:
            setattr(group_orgs, 'id', None)
            setattr(group_orgs, 'gr_id', groupId)
            setattr(group_orgs, 'org_id', contrag["@id"])
            setattr(group_orgs, 'start_date', datetime.strptime(contrag["@startdate"], '%Y-%m-%d'))
            group_orgs.insert()
    else:
        contragId = data_dict["schema"]["contrags"]["contrag"]["@id"]
        startdate = data_dict["schema"]["contrags"]["contrag"]["@startdate"]
        setattr(group_orgs, 'gr_id', groupId)
        setattr(group_orgs, 'org_id', contragId)
        setattr(group_orgs, 'start_date', datetime.strptime(startdate, '%Y-%m-%d'))
        group_orgs.insert()
        
        
def cardExcludeOrg(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''  
    groupOrgs = relatedTableCursorImport('acrsprav', 'group_orgs')(context)
    contrags = relatedTableCursorImport('acrsprav', 'contrags')(context)
    selectedRecordsCoded=json.loads(session)['sessioncontext']['related']['gridContext']['selectedRecordId']
    groupOrgs.get(selectedRecordsCoded)
    orgId=getattr(groupOrgs, 'org_id')
    contrags.get(orgId)
    date = getattr(groupOrgs, 'start_date')
    
 
    xformsdata = {"schema":{"@xmlns":"",
                            "info": {"row":{"@id":selectedRecordsCoded}, "org":{"@name":getattr(contrags, 'name'), "@startdate":str(date)[:-11], "@enddate":""}},
                            "contrags":None
                            }
                  }
    print xformsdata
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": "view"
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())

def cardExcludeOrgSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника. '''
    groupOrgs = relatedTableCursorImport("acrsprav", "group_orgs")(context)
    data_dict = json.loads(xformsdata)
    groupId = data_dict["schema"]["info"]["row"]["@id"]
    endDate = data_dict["schema"]["info"]["org"]["@enddate"]
    groupOrgs.get(groupId)
    
    setattr(groupOrgs, 'end_date', datetime.strptime(endDate, '%Y-%m-%d'))
    groupOrgs.update()
    

def cardDel(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}}
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())


def cardDelSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    grain_name = 'acrsprav'
    table_name = 'group_orgs'
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    selectedRecordsCoded=json.loads(session)['sessioncontext']['related']['gridContext']['selectedRecordId']
    print type(selectedRecordsCoded)
    if type(selectedRecordsCoded) is list:
        for selectedRecordCoded in selectedRecordsCoded:
            currentTable.get(selectedRecordCoded)
            currentTable.delete()
    else:
        currentTable.get(selectedRecordsCoded)
        currentTable.delete()