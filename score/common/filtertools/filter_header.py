#coding: utf-8
#from datetime import date, datetime, timedelta
from collections import OrderedDict
from any_functions import is_exist
from filter import unbound_types, unbound_dict_filler
from __builtin__ import len
from common.filtertools.any_functions import Something


# Class chapter
class IncorrectHeaderInput(ValueError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class HeaderDict:
    u'''
    Класс, собирающий данные для хэдера из сторонних источников. Состоит из двух чатей -- 
    функции-конструктора, получающей метаданные, описывающие каждое выводящееся поле, и 
    функции return_header, которая на основе метаданных и переданных занчений, формирует
    хэдер. Описание:
        INIT::
    В переменной labels приходит либо словарь вида {'field_id': {'Значение':'Наименование'}}, либо 
    фильтр-контекст, к которому надо добавлять context_list=True.
    
    Обозначения для словаря RETURN, который содержит метаданные вывода:
    - 'data_type' -- тип данных поля;
    - 'empty' -- то, что выводится в хэдере, если не приходят данные;
    - 'label' -- надпись, выводимая нпосредственно перед значениями фильтра;
    - 'values_to_header' -- словарь значений, которые подменяют пришедшие из фильтра;
    - 'end' -- значение, добавляющееся в конце строки хэдера;
    - 'case_sensitive' -- если True, то не происходит текстовая обработка получаемых данных.
    '''
    data_types = {'date', 'float', 'text', 'bool'}
    smth = Something()
    
    def __init__(self, labels, header=u'', context_list=False):
        # main processing
        # Переработка входных в label данных для создания фильтровых строк хэдера
        if not context_list:
            self.header_dict = OrderedDict([(i, self.preprocessor_any(j)) for i, j in unicoder(labels).items()])
        else:
            self.string_count = 0
            self.header_dict = OrderedDict([(val_dict['@id'], self.preprocessor_context(val_dict)) for val_dict in unicoder(labels)])
        self.header = header
        self.is_context = context_list
        
    # Функция переработки вручную сработанного словаря
    def preprocessor_any(self, values_dict):
        must_have_settings = {'data_type', 'empty', 'label', 'values_to_header', 
                              'end', 'case_sensitive'}

        if 'data_type' not in values_dict.keys() or values_dict['data_type'] not in self.data_types:
            raise IncorrectHeaderInput("Incorrect input: not specified field data type.")
        result = {}
        for setting in must_have_settings:
            if setting in values_dict.keys():
                result[setting] = values_dict[setting]
            elif setting == 'end':
                result[setting] = '; '
            elif setting == 'case_sensitive':
                result[setting] = False
            else:
                result[setting] = ''
        # postprocessing
        if is_exist(values_dict, u'newline'):
            result['newline'] = True
        return result
    
    # Функция переработки контекста из фильтра
    def preprocessor_context(self, context_field):
        result = {}
        result['data_type'] = context_field['@type']
        result['empty'] = u''
        result['label'] = u'%s' % context_field['@label']   
        self.string_count += len(context_field['@label'])
        if context_field['@face'] == 'select':
            result['values_to_header'] = {x['@name'] : x['@label'] for x in context_field['selects']["select"]}
        else:
            result['values_to_header'] = {}
        result['end'] = '.'
        #result['case_sensitive'] = '.'
        
        if self.string_count > 100 or context_field['@face'] == 'itemset':
            result['newline'] = True
            self.string_count = 0
            
        return result
    
    def replace_header(self, new_header):
        self.header = new_header
    
    def return_header(self, current_values, context_filter=False):
        u'''current_values = {id_field: value} for non-standard filtering and
            {id_field: {data_types : value, ...}} for STANDARTEN'''
        # New view
        # Приведение всех значений в поле, которое обрабатывается в соответствие с типом
        if context_filter is False:
            standard_header_dict = through_filler(current_values, self.header_dict)      
        else:
            for y in current_values.values():
                if is_exist(y, 'item', {'@id': self.smth}):
                    y['text'] = y['item']['@name']
                if is_exist(y, 'items'):
                    if '@name' not in y['items']:
                        y['text'] = u'; '.join([x['@name'] for x in y['items']])
                    else:
                        y['text'] = y['items']['@name']
            standard_header_dict = current_values
        header_list = [{"@class": 'header-class', "span": {"@class": 'header-header', '#text': self.header}}]
        i = 0
        next_upper = False
        # Формирование списка с подстановкой значений, либо emtpy-вариантом
        for key, values_dict in self.header_dict.items():
            datatype = get_value_through_type(
                values_dict['data_type'], 
                standard_header_dict[key] if key in standard_header_dict.keys() else unbound_dict_filler(['']))
            h_key = ''
            h_cond = ''
            h_value = ''
            if datatype in ('', ['', ''], None):
                h_value = values_dict['empty']
            else:
                if is_exist(values_dict, 'values_to_header'):
                    format_string = values_dict['values_to_header'][datatype]
                else:
                    format_string = datatype
                if isinstance(format_string, list):
                    if values_dict['data_type'] in {'date', 'float'}:
                        if filter(None, format_string):
                            first_chapter = u'с %s '
                            second_chapter = u'по %s'
                            third_chapter = format_string[2]
                            h_key = values_dict['label']
                            if standard_header_dict[key]['condition']['@value'] == 'equal':
                                h_cond = standard_header_dict[key]['condition']['@label']
                                h_value = third_chapter
                            elif standard_header_dict[key]['condition']['@value'] == 'right':
                                h_value = second_chapter % third_chapter
                            elif standard_header_dict[key]['condition']['@value'] == 'left':
                                h_value = first_chapter % third_chapter
                            else:
                                h_value = u'%s%s' % ((first_chapter  % format_string[0]) if format_string[0] != '' else '', 
                                                     (second_chapter % format_string[1]) if format_string[1] != '' else '')
                else:
                    if values_dict['data_type'] == 'bool':
                        h_key = (values_dict['label'] + '.') if format_string in {True, 'true', 'True'} else values_dict['empty']
                    else:
                        h_key = values_dict['label'] if values_dict['label'] else ''
                        if self.is_context:
                            h_cond = standard_header_dict[key]['condition']['@label']\
                                if '@label' in standard_header_dict[key]['condition'] else u''
                        h_value = format_string
                        
            if is_exist(values_dict, 'newline'):
                h_value = unicode(h_value) + u'\n'
                next_upper = True
            if h_value != values_dict['empty']:
                h_value = unicode(h_value) + values_dict['end']
                first_string = h_key or h_value or u'' 
                if next_upper and not is_exist(values_dict, 'case_sensitive', True) and first_string:
                    first_string = u' '.join([first_string.split()[0].capitalize(), u' '.join(first_string.split()[1:])])\
                                if len(first_string.split()) > 1 else first_string.capitalize()
                if first_string:
                    if h_key:
                        h_key = first_string
                    elif h_value:
                        h_value = first_string     
                    next_upper = False
            if '.' in values_dict['end']:
                next_upper = True
            i += 1
            
            header_key = {"@class": "header-key", "#text": h_key + u' '}
            header_condition = {"@class": "header-condition", "#text": (h_cond + (u': ' if ';' in h_value else u' ')) if h_cond else ''}
            header_value = {"@class": "header-value", "#text": h_value + u' '}
            header_list.append({
                "@class": "header-clause",
                "span": []})
            if h_key.strip() not in {'.', ''} and (values_dict['data_type'] == 'bool' or (values_dict['data_type'] != 'bool' and h_value)):
                header_list[-1]['span'].append(header_key)
            if h_cond.strip() not in {'.', ''}:
                header_list[-1]['span'].append(header_condition)
            if h_value.strip() not in {'.', ''}:
                header_list[-1]['span'].append(header_value)
        
        header_list = filter(lambda x: x['span'] != [], header_list)
        if len(header_list) == int(bool(self.header)):
            if len(header_list) == 1:
                header_list[0]['span']["#text"] += u' нет.'
            else:
                header_list.append({
                    "@class": "header-clause",
                    "#text": u'Не заданы параметры поиска'})
        return {'span': header_list}
    

# Filler-functions
def header_type_to_filter_type():
    return {
    #data_type: position in unbound_dict_filler
        'date' :{'from': 'minValue', 'to': 'maxValue'},
        'float': {'from': 'minValue', 'to': 'maxValue'},
        'text' : 'text',
        'bool' : 'bool'
    }


# Function chapter
def get_value_through_type(value_type, value_dict):
    format_dict = header_type_to_filter_type()
    fast_trancate = lambda x: '.'.join(x.split('-')[::-1]) if isinstance(x, (str, unicode)) else x
    if value_type not in {'date', 'float'}:
        return value_dict[format_dict[value_type]]
    else:
        return [fast_trancate(x) for x in
                [value_dict[format_dict[value_type]['from']], value_dict[format_dict[value_type]['to']], 
                 value_dict[format_dict['text']]]]


def through_filler(values_dict, types_dict):
    type_to_value = header_type_to_filter_type()
    types = unbound_types()
    type_to_lst_id = {}
    for key, j in type_to_value.items():
        if isinstance(j, dict):
            type_to_lst_id[key] = {x: list_find(types, y) for x, y in j.items()}
        else:
            type_to_lst_id[key] = list_find(types, j)
    output = {}
    for i_key, i_value in values_dict.items():
        if not isinstance(type_to_lst_id[types_dict[i_key]['data_type']], dict):
            unbound_string = [''] * type_to_lst_id[types_dict[i_key]['data_type']]
            unbound_string.append(i_value)
        else:
            # hardcoding from datetime data type
            if i_value:
                from_dt = type_to_lst_id[types_dict[i_key]['data_type']]['from']
                to_dt = type_to_lst_id[types_dict[i_key]['data_type']]['to']
                min_dt, max_dt = (from_dt, to_dt) if from_dt < to_dt else (to_dt, from_dt)
                dt_value = {
                    from_dt: i_value['from'],
                    to_dt: i_value['to']
                }
                unbound_string = [''] * min_dt
                unbound_string.append(dt_value[min_dt])
                unbound_string.extend([''] * (max_dt-min_dt-1))
                unbound_string.append(dt_value[max_dt])
            else:
                unbound_string = ['']
        
        output[i_key] =  unbound_dict_filler(unbound_string)
    return output


def list_find(find_list, find_str):
    u'''Функция, которая ищет элемент в не отсортированном списке'''
    for i, elem in enumerate(find_list):
        if elem == find_str:
            return i
    return -1


def unicoder(outer_elem):
    u'''Функция, переводящая из строк в unicode всё содержимое объекта'''
    if isinstance(outer_elem, (str, unicode)):
        return unicode(outer_elem)
    if isinstance(outer_elem, (float, int)):
        return outer_elem
    if isinstance(outer_elem, (list, tuple)):
        return [unicoder(x) for x in outer_elem]
    if isinstance(outer_elem, OrderedDict):
        return OrderedDict([(unicoder(x), unicoder(y)) for x, y in outer_elem.items()])
    if isinstance(outer_elem, dict):
        return {unicoder(x):unicoder(y) for x, y in outer_elem.items()}
    return unicode(outer_elem)
