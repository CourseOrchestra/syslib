# coding: utf-8
from datetime import date, datetime
from sys import maxint, minint
from time import clock


def filter_assembly(context, cursor, filter_id, field_name_list, table_name):
    u'''Функция для сборки в context.getData пустого фильтра
    Расшифровка передаваемых значений:
    free -- для обозначения, что данное поле не встречается в таблице грида или представлено типом, отличным от метаданных челесты
    label -- аргументом передаётся строка, которая будет показываться в гриде 
    type -- аргументом передаётся тип поля, если такого поля в таблице нет, либо отличается от  стандартного. Может быть:
        'DATETIME', 'VARCHAR', 'NUMERIC', 'TEXT', 'INT', 'FLOAT', 'DATE', 'BOOLEAN'. Описаны в карточке.
    selector -- если True, то на данное поле будет повешен селектор
    select_info -- аргументом передаётся путь к селектору, который надо передать в данный фильтр в формате 
        'гранула.модуль_с_Селектором.название_py-файла.имя_функции_селекции'
    itemset -- обозначает, что для данного поля нужен мультиселектор (выделяет искомое множество значений
    default -- передаёт значение по умолчанию. Указывается в списке в количестве 1 - 2 значений. Число значений зависит от типа фильтра
    unbound -- обозначает, что фильтрация по значению поля будет производится пользователем и описана отдельно
    view -- если True, то показывается фильтр при загрузке
    especial_conds={'id':имя_поля} - переменная для поля "Условий". Принимает словарь вида {значение_условия: надпись} Значение -- одно из: equal right left between
    required -- флаг для обозначения обязательности заполнения.
    '''
    if filter_id not in context.getData():
        context.getData()[filter_id] = []
    # Включение отсчёта времени для генерации randint значений в карточке для активации триггера xforms-value
    clock()
    # Создание словаря с ключами-именами полей
    field_name_dict = {}
    for field_map in field_name_list:
        field_name_dict[field_map['name']] = field_map
    # Вызов функции определения типов полей и стилей фильтра
    filtered_fields = create_filter_map(cursor, field_name_dict, {
        name for name, value in field_name_dict.items() if 'free' in value
    }
    )
    for field_dict in field_name_list:
        field_name = field_dict['name']
        # Добавление в context.getData шаблонов фильтров
        future_filter = {
            '@key': 'unview' if 'unview' in field_name_dict[field_name] and field_name_dict[field_name]['unview'] else 'view',
            '@id': field_name,
            '@tableName': table_name,
            '@label': field_name_dict[field_name]['label'],
            '@type': filtered_fields[field_name][0] or 'text',
            '@style': filtered_fields[field_name][1],
            '@minValue': "",
            '@maxValue': "",
            '@value': "",
            '@boolInput': "false",
            'items': {"item": []},
            'selects': {"select":
                        [
                            {'@label': label, '@name': name}
                            for name, label in field_dict['select'].items()
                        ] if 'select' in field_dict else []
                        },
            'item': {'@id': '', '@name': ''},
            '@randint': 0,
            'default': field_name_dict[field_name]['default'] if 'default' in field_name_dict[field_name] else '',
            '@selector_data': field_name_dict[field_name]['select_info'] if 'select_info' in field_name_dict[field_name] else '',
            '@current_condition': 'equal' if filtered_fields[field_name][0] != 'date' else 'between',
            '@required': 'true' if 'required' in field_name_dict[field_name] and field_name_dict[field_name]['required'] else 'false'
        }
        as_default(future_filter)
        future_filter['conditions'] = condition_constructor(
            future_filter,
            field_name_dict[field_name]['especial_conds'] if 'especial_conds' in field_name_dict[field_name] else False,
            future_filter['@style'], future_filter['@type']
        )
        context.getData()[filter_id].append(future_filter)


def create_filter_map(cursor, field_name_dict, free_variables):
    u'''Функция для приведения типов данных Челесты к типам данных фильтра'''
    # Функция для превращения стилей
    def choose_style(styles_dict):
        # Порядок важен, к сожалению
        for style in ['itemset', 'selector', 'select', 'unbound', 'free']:
            if style in styles_dict and styles_dict[style]:
                return style if style != 'free' else 'unbound'  # полукостыль для того, чтобы убрать необхоидмость дублировать unbound после free

        return ''

    def getFieldType(cursor, field_name):
        return cursor.meta().columns[field_name].celestaType
    # Проверка на тип курсора. У курсора есть метод getColumn.
#     attrSubstitution = lambda x: cursor.meta().getColumns()[x].getCelestaType()
#     keySubstitution = """field_name"""
#     fnameSubstitution = attrSubstitution
#     try:
#         getattr(cursor.meta(), 'getColumn')
#         keySubstitution = """field_name"""
#         fnameSubstitution = attrSubstitution
#     except AttributeError:
#         keySubstitution = """field_data"""
#         fnameSubstitution = lambda x: str(x)

    # Словарь соответствий получаемых типов к типам, используемым в фильтре
    return_dict = {
        'DATETIME': 'date', 'VARCHAR': 'text', 'NUMERIC': 'float',
        'TEXT': 'text', 'INT': 'float', 'FLOAT': 'float', 'DATE': 'date',
        'BOOLEAN': 'bool', 'BIT': 'bool', 'REAL': 'float'
    }
    fnd_set = set(field_name_dict.keys())
    styles_set = {'itemset', 'unbound', 'free', 'selector', 'select'}

    # Генератор для выделения стиля оформления, либо присвоения не выделяемого челестой типа данных
    not_in_table_fields = {
        field_name: [
            field_data['type']
            if 'type' in field_data
            else getFieldType(cursor, field_name),
            choose_style(field_data)
        ]
        for field_name, field_data in field_name_dict.items()
        if styles_set & set(field_data.keys()) or field_name in free_variables
    }

    in_table_fields = {
        field_name: [getFieldType(cursor, field_name), None]
        if field_name not in not_in_table_fields.keys()
        else not_in_table_fields[field_name]
        for field_name, field_data in cursor.meta().getColumns().items()
        if field_name in fnd_set
    }

    # Добавление свободных, не привязанных к существующим полям, переменных
    in_table_fields.update(not_in_table_fields)
    return {x: [return_dict[str(y[0]).upper()], y[1] or 'usuall'] for x, y in in_table_fields.items()}


def condition_constructor(filter_data, especial_conds, filter_style, filter_type):
    u'''
    Либо передаем свои собственные наименования, либо автозаполяем -- всё просто
    Поиск по маске педназначен для "особенной" обработки без обработки (?)
    '''
    if especial_conds:
        values = {'between', 'right', 'left', 'equal', 'masked'}
        if not all({x in values for x in especial_conds.keys()}):
            raise Exception(u"В подаваемых conditions все значения должны быть из {'between', 'right', 'left', 'equal', 'masked'}")

        conditions = {
            'condition': [
                {'@value': value,
                    '@label': label
                 } for value, label in especial_conds.items()
            ]
        }
        if len(conditions['condition']) == 1:
            filter_data['@current_condition'] = conditions['condition'][0]['@value']
    else:
        type_to_label = {'float': u'равно', 'date': u'равно', 'text': u'содержит', 'bool': u''
                         }
        between = {'@value': 'between',
                   '@label': u'между'}
        right = {'@value': 'right',
                 '@label': u'до'}
        left = {'@value': 'left',
                '@label': u'с'}
        equal = {'@value': 'equal',
                 '@label': type_to_label[filter_type]}
        masked = {'@value': 'masked', '@label': u'маска'}
        conditions = {'condition': [equal]}

        if filter_style in {'usuall', 'unbound'} and filter_type in {'float', 'date'}:
            conditions['condition'].append(between)
            conditions['condition'].append(right)
            conditions['condition'].append(left)
    return conditions


def filtered_function(context, filter_name, cursor):
    u'''Функция фильтрации по введённым значениям'''
    # Функция для преобразования дат и строк к виду, используемому для фильтров
    date_transform = lambda x: "'%s'" % x.replace('-', '')
    unbound_values = {}

    for filter_dict in context.getData()[filter_name]:
        if filter_dict['@key'] == 'view':
            if {'unbound', 'selector', 'select'} & {filter_dict['@style']}:
                # Добавление значений unbound-полей для использования вовне
                unbound_values[filter_dict['@id']] = unbound_dict_filler(filter_dict['@value'],
                                                                         True if filter_dict['@boolInput'] == 'true' else False, filter_dict['item'],
                                                                         filter_dict['@current_condition'], filter_dict['@minValue'], filter_dict['@maxValue']
                                                                         )
            if filter_dict['@style'] == 'usuall':
                if filter_dict['@current_condition'] == 'masked':
                    try:
                        cursor.setFilter(filter_dict['@id'], ("'%s'" if filter_dict['@value'] != "'" else "%s") % filter_dict['@value'])
                        cursor.count()
                    except:
                        context.message(
                            u"Фильтрация по полю {} не может быть произведена по причине некорректной маски.".format(filter_dict['@label']))
                elif filter_dict['@type'] == 'float':
                    # Фильтр по числовым полям. Зависит от условия.
                    if filter_dict['@current_condition'] == 'equal' and filter_dict['@value']:
                        cursor.setRange(filter_dict['@id'], int(filter_dict['@value']))
                    elif filter_dict['@current_condition'] == 'between' and (filter_dict['@maxValue'] or filter_dict['@minValue']):
                        cursor.setFilter(filter_dict['@id'], '..%s&%s..' % (filter_dict['@maxValue'] or maxint, filter_dict['@minValue'] or minint))
                    elif filter_dict['@current_condition'] == 'right' and filter_dict['@value']:
                        cursor.setFilter(
                            filter_dict['@id'], '..%s' % filter_dict['@value']
                        )
                    elif filter_dict['@current_condition'] == 'left' and filter_dict['@value']:
                        cursor.setFilter(
                            filter_dict['@id'], '%s..' % filter_dict['@value']
                        )

                elif filter_dict['@type'] == 'text':
                    # Фильтр по текстовому полю.
                    if filter_dict['@value']:
                        cursor.setFilter(filter_dict['@id'], "@%%'%s'%%" % filter_dict['@value'])

                elif filter_dict['@type'] == 'date':
                    # Фильтр по полю дат.
                    if filter_dict['@current_condition'] == 'equal' and filter_dict['@value']:
                        cursor.setRange(filter_dict['@id'], datetime.strptime(filter_dict['@value'], '%Y-%m-%d'))
                    elif filter_dict['@current_condition'] == 'between' and (filter_dict['@maxValue'] or filter_dict['@minValue']):
                        if len(filter_dict['@minValue']) == 0:
                            date_from = "'19700101'"
                        else:
                            date_from = date_transform(filter_dict['@minValue'])

                        if len(filter_dict['@maxValue']) == 0:
                            date_to = "'%s%s%s'" % (date.today().year, str(date.today().month).zfill(2), str(date.today().day).zfill(2))
                        else:
                            date_to = date_transform(filter_dict['@maxValue'])

                        cursor.setFilter(
                            filter_dict['@id'], '..%s&%s..' % (date_to, date_from)
                        )
                    elif filter_dict['@current_condition'] == 'right' and filter_dict['@value']:
                        cursor.setFilter(
                            filter_dict['@id'], '..%s' % (date_transform(filter_dict['@value']))
                        )
                    elif filter_dict['@current_condition'] == 'left' and filter_dict['@value']:
                        cursor.setFilter(
                            filter_dict['@id'], '%s..' % (date_transform(filter_dict['@value']))
                        )

                elif filter_dict['@type'] == 'bool':
                    if filter_dict['@boolInput'] == 'true':
                        cursor.setRange(filter_dict['@id'], True)
            elif filter_dict['@style'] == 'itemset':
                if len(filter_dict['items']['item']) != 0:
                    # Формирование сложного фильтра для мультиселектора по выделенным значениям
                    data_type = filter_dict['@type'].upper()
                    # Выбор способа передачи значений в сложный фильтр
                    if data_type == 'TEXT':
                        filter_schedule = "'%s'"
                    else:
                        filter_schedule = "%s"
                    # В зависимости от записанного значения -- из карточки или из сессии, выделяются значения для фильтрации
                    items_list = filter_dict['items']['item'] if isinstance(filter_dict['items']['item'], list) else [filter_dict['items']['item']]
                    if isinstance(items_list[0], dict):
                        filter_list = [filter_schedule % x['@name'] for x in items_list if x['@name']]
                    else:
                        filter_list = [filter_schedule % x for x in items_list if x not in {None, ''}]

                    filter_string = '|'.join(filter_list) if len(filter_list) > 1 else filter_list[0]
                    cursor.setFilter(filter_dict['@id'], filter_string or "''")
                else:
                    cursor.setRange(filter_dict['@id'])
    # Возвращение значения unbound-значений
    if unbound_values:
        return unbound_values
    else:
        return {}


def as_default(instance_dict):
    u'''Функция ораниченной функциональности для подстановки дефолтных значений'''
    if instance_dict['default']:
        value_type = instance_dict["@type"]
        value_style = instance_dict["@style"]
        if value_style in {'usuall', 'unbound'}:
            if value_type in {'date', 'float'} and not (instance_dict["@minValue"] and instance_dict["@maxValue"]):
                if len(instance_dict["default"]) == 2:
                    instance_dict["@minValue"] = instance_dict["default"][0]
                    instance_dict["@maxValue"] = instance_dict["default"][1]
                elif len(instance_dict["default"]) == 1:
                    instance_dict["@value"] = instance_dict["default"][0]

            elif value_type == 'text' and not instance_dict["@value"]:
                instance_dict["@value"] = instance_dict["default"][0]

            elif value_type == 'bool':
                instance_dict["@boolInput"] = instance_dict["default"][0]
        elif value_style == 'selector' and not instance_dict['item']['@id']:
            if len(instance_dict["default"]) == 2:
                instance_dict['item']['@id'] = instance_dict["default"][0]
                instance_dict['item']['@name'] = instance_dict["default"][1]
            elif len(instance_dict["default"]) == 1:
                instance_dict['item']['@id'] = instance_dict["default"][0]
                instance_dict['item']['@name'] = u''
        elif value_style == 'select':
            instance_dict["@value"] = instance_dict["default"][0]

        return True


def recovery(context, add):
    if add.find('|') != -1:
        add = add[:add.find('|')]
    default = False
    for field_dict in context.getData()[add]:
        field_dict['@key'] = "view"
        field_dict['@minValue'] = ""
        field_dict['@maxValue'] = ""
        field_dict['@value'] = ""
        field_dict['@boolInput'] = "false"
        field_dict['items']["item"] = []
        field_dict['item'] = {"@id": "", "@name": ""}
        field_dict['condition'] = 'equal' if field_dict['@type'] != 'date' else 'between'
        if as_default(field_dict):
            default = True
    # удаляем флаг id элемента, для которого была произведена очистка,
    # в случае, если не задействована фильтрация по умолчанию
    if not default:
        if add in context.getData().get('card_save', []):
            context.getData()['card_save'].remove(add)


def unbound_types():
    return ['text', 'bool', 'item', 'condition', 'minValue', 'maxValue']


def unbound_dict_filler(*tuple_of_values):
    keys = unbound_types()
    if len(tuple_of_values) == 1 and isinstance(tuple_of_values[0], list):
        tuple_of_values = tuple_of_values[0]
    return {keys[i]: tuple_of_values[i] if i <= len(tuple_of_values) - 1 else ''
            for i in range(len(keys))}
