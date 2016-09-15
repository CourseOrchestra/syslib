#coding: utf-8
#from datetime import date, datetime, timedelta
from collections import OrderedDict
from any_functions import is_exist
from filter import unbound_types, unbound_dict_filler
from __builtin__ import len


# Class chapter
class IncorrectHeaderInput(ValueError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class HeaderDict:
    u'''labels = {'field_id': {'Значение':'Наименование'}}'''
    data_types = {'date', 'float', 'text', 'bool'}

    def __init__(self, labels, header=u'', special_condition=''):
        self.header_dict = OrderedDict([(i, self.preprocessor(j)) for i, j in unicoder(labels).items()])
        self.header = header

    def preprocessor(self, values_dict):
        must_have_settings = {'data_type', 'empty', 'label', 'values_to_header', 'end', 'case_sensitive'}

        if 'data_type' not in values_dict.keys() or values_dict['data_type'] not in self.data_types:
            raise IncorrectHeaderInput("Incorrect input: not specified field data type.")
        result = {}
        for setting in must_have_settings:
            if setting in values_dict.keys():
                result[setting] = values_dict[setting] if not (setting == 'end' and values_dict[setting] == '.')\
                                                       else '.'
            elif setting == 'end':
                result[setting] = '; '
            elif setting == 'case_sensitive':
                result[setting] = False
            else:
                result[setting] = ''

        return result
    
    def replace_header(self, new_header):
        self.header = new_header
    
    def return_header(self, current_values, context_filter=False):
        u'''current_values = {id_field: value} for non-standard filtering and
            {id_field: {data_types : value, ...}} for STANDARTEN'''
        if context_filter is False:
            standard_header_dict = through_filler(current_values, self.header_dict)
        else:
            for y in current_values.values():
                if y['item']:
                    y['text'] = y['item']['@name']
            standard_header_dict = current_values

        header_list = [self.header]
        unsensitive = [] if not self.header else [False]
        for key, values_dict in self.header_dict.items():
            if key not in standard_header_dict:
                continue
            datatype = get_value_through_type(values_dict['data_type'], standard_header_dict[key])

            if datatype in ('', None):
                format_string = values_dict['empty']
            elif is_exist(values_dict, 'values_to_header'):
                format_string = values_dict['values_to_header'][datatype]
            else:
                format_string = datatype

            if format_string not in ('', ['', '']):
                scheduler = u"{}{}{}".format(
                    u'%s ' % values_dict['label'] if values_dict['label'] else '',
                    u'{}',
                    values_dict['end']
                )

                if isinstance(format_string, list):
                    if values_dict['data_type'] == 'date':
                        first_chapter = (u'с %s ' % format_string[0]) if format_string[0] else u''
                        second_chapter = (u'по %s' % format_string[1]) if format_string[1] else u''
                        format_string = u'%s%s' % (first_chapter, second_chapter)
            else:
                scheduler = u'{}'
                format_string = values_dict['empty']
                
            unsensitive.append(self.header_dict[key]['case_sensitive'])
            header_list.append(scheduler.format(format_string))

        header_list[-1] = header_list[-1].rstrip().rstrip(';')
        # Проклятый костыль для того, чтобы видеть, какое поле нулевое
        new_header_list = []
        insensitive = []
        for i, head in enumerate(header_list):
            if head:
                new_header_list.append(head)
                insensitive.append(unsensitive[i])
        header_list = new_header_list
        upper_case = True
        finished_header = []
        for i, header_field in enumerate(header_list):            
            if upper_case:
                if not insensitive[i]:
                    titled_header = header_field.split()
                    if len(titled_header) > 1:
                        tempo = titled_header[0].capitalize()
                        header_field = u'{} {}'.format(unicode(tempo), ' '.join(titled_header[1:]))
                    else:
                        header_field = unicode(titled_header[0])
                upper_case = False

            if header_field.rstrip()[-1] == '.':
                upper_case = True
            finished_header.append(header_field)
        
        if len(finished_header) == 0:
            return u'Параметры фильтрации не указаны'
        elif (len(finished_header) == 1 and self.header != ''):
            return u'{}: не указаны'.format(finished_header[0]) 
        
        if self.header == '':
            finished_header = filter((lambda x: x != '.'), finished_header)
        else:
            if finished_header[1] == '.' and len(finished_header) > 2:
                return u'{} {}'.format(''.join([finished_header[0], finished_header[1]]), ' '.join(finished_header[2:]))
        
        return ' '.join(finished_header)


# Filler-functions
def header_type_to_filter_type():
    return {
    #data_type: position in unbound_dict_filler
        'date': {'from': 'minValue', 'to': 'maxValue'},
        'float' : 'text',
        'text': 'text',
        'bool': 'bool'
    }


# Function chapter
def get_value_through_type(value_type, value_dict):
    format_dict = header_type_to_filter_type()
    fast_trancate = lambda x: '.'.join(x.split('-')[::-1])
    if value_type != 'date':
        return value_dict[format_dict[value_type]]
    elif value_type == 'date':
        return [fast_trancate(x) for x in
                [value_dict[format_dict[value_type]['from']], value_dict[format_dict[value_type]['to']]]]


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
    for i, elem in enumerate(find_list):
        if elem == find_str:
            return i
    return -1


def unicoder(outer_elem):
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
