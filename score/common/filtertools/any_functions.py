# coding: utf-8
from datetime import datetime


def is_exist(dictionary, key, *args):
    u'''Проверяет существование ключа в словаре и существование его содержимого
    Возврщает None, если передать не словарь, False, если ключа нет в словаре, либо значение этого ключа пустое, либо 
    значение не равно третьему переданному аргументу'''
    if isinstance(dictionary, dict):
        if key in dictionary:
            # Проверка на соответствие типов
            for keys in dictionary.keys():
                if dictionary[keys] == dictionary[key] and type(keys) != type(key):
                    return False
            if isinstance(dictionary[key], str):
                return dictionary[key] != '' and compare_with_shadow(dictionary[key], args)
            if dictionary[key]:
                return compare_with_shadow(dictionary[key], args)
            return False
        return False
    else:
        return None

def compare_with_shadow(source, schrodinger_cat):
    if schrodinger_cat is None:
        return True
    if len(schrodinger_cat) == 0:
        return True
    return source == schrodinger_cat[0]


def trankate(DB_time):
    u'''Привод получаемой из постгре даты к юзер-дружелюбному виду'''
    try:
        return datetime.strftime(datetime.strptime(str(DB_time), '%Y-%m-%d %H:%M:%S.%f'), '%d.%m.%Y')
    except ValueError:
        return datetime.strftime(datetime.strptime(str(DB_time), '%Y-%m-%d'), '%d.%m.%Y')