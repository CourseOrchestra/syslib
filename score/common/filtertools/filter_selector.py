# coding: utf-8
from java.util import ArrayList
import json
from time import clock
from importlib import import_module
from common.sysfunctions import tableCursorImport
from ru.curs.celesta.showcase.utils import XMLJSONConverter
try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData
    from ru.curs.celesta.showcase import DataRecord


def filtersList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    u'''Функция для получения списка доступных фильтров по полю @key'''
    recordList = ArrayList()
    for filter_dict in context.getData()[add]:
        if filter_dict['@key'] == 'unview':
            rec = DataRecord()
            rec.setId(filter_dict['@id'])
            rec.setName(filter_dict['@label'])
            rec.addParameter('type', filter_dict['@type'])
            rec.addParameter('randint', str(clock()))
            rec.addParameter('style', filter_dict['@style'])
            rec.addParameter('selector_data', filter_dict['@selector_data'])
            rec.addParameter('boolInput', filter_dict['@boolInput'])
            recordList.add(rec)
    return ResultSelectorData(recordList, 0)


def filtersCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    u'''Функция для получения числа доступных фильтров'''
    displayed_filters_list = [x for x in context.getData()[add] if x['@key'] == 'unview']
    return ResultSelectorData(None, len(displayed_filters_list))


def submissionUnview(context, main=None, add=None, filterinfo=None, session=None, data=None):
    u'''Функция для обнуления полей при вынесении их из фильтра'''
    data_py = json.loads(data)
    new_context = []
    for filter_inside in context.getData()[add]:
        if filter_inside['@id'] == data_py['filter']['@id']:
            filter_inside['@key'] = 'unview'
            filter_inside['@minValue'] = ''
            filter_inside['@value'] = ''
            filter_inside['@maxValue'] = ''
            filter_inside['item'] = {"@id": '', "@name": ''}
            filter_inside['@current_condition'] = data_py['filter']['@current_condition']
        new_context.append(filter_inside)
        
    context.getData()[add] = new_context
    return XMLJSONConverter.jsonToXml(data)
        

def submissionView(context, main=None, add=None, filterinfo=None, session=None, data=None):
    u'''Функция для изменения состояния полей'''
    # Операции для добавления постоянных нод
    data_py = json.loads(data)
    # Операции перестроки контекста
    new_context = []
    for filter_inside in context.getData()[add]:        
        if filter_inside['@id'] == data_py['filter']['@id']:
            filter_inside['@key'] = 'view'
            data_py['filter']['selects'] = filter_inside['selects']
            data_py['filter']['conditions'] = filter_inside['conditions']
            data_py['filter']['@current_condition'] = filter_inside['@current_condition']
        new_context.append(filter_inside)
 
    context.getData()[add] = new_context
    return XMLJSONConverter.jsonToXml(json.dumps(data_py))


def submissionSort(context, main=None, add=None, filterinfo=None, session=None, data=None):
    u'''Функция для изменения состояния полей'''
    # Операции для добавления постоянных нод
    data_py = json.loads(data)['filters']['filter']
    new_xforms_data = {'filters':{'filter':[]}}
    # Операции перестроки контекста
    for filter_inside in context.getData()[add]:
        new_xforms_data['filters']['filter'].extend([filter_xform for filter_xform in data_py if filter_xform['@id'] == filter_inside['@id']])
    return XMLJSONConverter.jsonToXml(json.dumps(new_xforms_data))


def itemsListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    u"""Функция для получения списка элементов в пределе одного фильтра типа itemset"""
    filter_parameters = json.loads(XMLJSONConverter.xmlToJson(params))["schema"]["filter"]["filter"]

    grain, table = context.getData()[add][0]["@tableName"].split('.')
    field_name = filter_parameters["@id"]
    cursor_instance = tableCursorImport(grain, table)
    cursor = cursor_instance(context)
    # Булевый флаг для определения, является ли поле числовым
    is_quotes = str(cursor.meta().getColumns()[field_name]) not in {'NUMERIC', 'INT', 'FLOAT'}
    
    if curvalue and curvalue != ' ':
        if not is_quotes:
            # При поиске по числовому полю введённому полю соответствует одно число
            cursor.setRange(field_name, int(curvalue))
            recordList = ArrayList()
            for i, cursor in enumerate(cursor.iterate()):
                rec = DataRecord()            
                current_name = getattr(cursor, field_name)
                rec.setId("rec%i" % i)  
                rec.setName(unicode(current_name))
                recordList.add(rec)
                j = i
            return ResultSelectorData(recordList, j)
    
    cursor.orderBy(field_name)
    recordList = ArrayList()
    # набираем список значений
    i = 0
    while cursor.tryFirst() and i < recordcount:
        current_name = getattr(cursor, field_name)
        # Сложный if потому что для числовых значений не учитывается первое, а должно
        if (is_quotes and i > firstrecord) or (not is_quotes and i >= firstrecord):
            rec = DataRecord()            
            rec.setId("rec%i" % i)  
            rec.setName(unicode(current_name))
            recordList.add(rec)
        # Определение формы выведения в setFilter для разных типов значений  
        current_filter = ">%s" % ("'%s'" % current_name if is_quotes else int(current_name))
        if curvalue and curvalue != ' ':
            current_filter = """%s&@%s'%s'%%""" % (current_filter, "%"*(not startswith), curvalue.replace("'", "''"))
        cursor.setFilter(field_name, current_filter)
        i += 1
    return ResultSelectorData(recordList, i)


def special_selector(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    u'''Функция для получения списка элементов в пределе одного фильтра типа itemset'''
    all_fields, current = (x['filter'] for x in json.loads(XMLJSONConverter.xmlToJson(params))['schema']['filter'])
    field_name = current['@id']
    
    selector_path = [
        neccessary_field['@selector_data']
        for neccessary_field in context.getData()[add] 
            if field_name == neccessary_field['@id']
    ][0].split('.')
    selector_module, selector_function_name = '.'.join(selector_path[:-1]), selector_path[-1]
    selector_module = import_module(selector_module)
    selector = getattr(selector_module, selector_function_name)
    
    return selector(context, main, add, filterinfo, session, params, curvalue, startswith, firstrecord, recordcount)