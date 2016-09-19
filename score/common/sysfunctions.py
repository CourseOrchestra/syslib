# coding: utf-8
import importlib
import json
import os

from ru.curs.celesta import Celesta
from ru.curs.celesta.dbutils import Cursor, ViewCursor


def toHexForXml(s):
    '''Функция модифицирует спецсимволы в строке в формат пригодный для имен тегов xml'''
    lst = []
    for ch in s:
        numCh = ord(ch)
        if numCh not in xrange (48, 58) and\
                numCh not in xrange (65, 91) and\
                numCh not in xrange (97, 123) and \
                numCh not in xrange(1040, 1104):
            lst.append('_x%s_' % ('000%s' % hex(numCh)[2:])[-4:])
        else:
            lst.append(ch)

    return reduce(lambda x, y: x + y, lst)


def tableCursorImport(grainName, tableName):
    u'''Функция, импортирующая  класс курсора на таблицу'''

    # Импорт гранулы
    if grainName == "celesta":
        from ru.curs.celesta import syscursors as _grain_orm
    else:
        _grain_orm = __import__("%s._%s_orm" % (grainName, grainName),
                                globals(), locals(), "%sCursor" % tableName, -1)

    return getattr(_grain_orm, "%sCursor" % tableName)


def objectImport(path):
    u'''Импорт объекта по пути пакет.модуль.....функция.'''

    (module_name, fun_name) = (".".join(path.split(".")[:-1]), path.split(".")[-1])

    return getattr(importlib.import_module(module_name), fun_name)


def getGridWidth(session, delta=51):
    u"""Функция получает ширину грида, в зависимости от ширины датапанели."""
    if not isinstance(session, dict):
        return unicode(int(json.loads(session)["sessioncontext"]["currentDatapanelWidth"]) - delta) + "px"
    else:
        return unicode(int(session["sessioncontext"]["currentDatapanelWidth"]) - delta) + "px"


def getGridHeight(session, numberOfGrids=1, gridHeaderHeight=55, delta=59):
    u"""Функция получает высоту грида, в зависимости от высоты датапанели."""
    # raise Exception(session)
    if not isinstance(session, dict):
        return unicode(int((int(json.loads(session)["sessioncontext"]["currentDatapanelHeight"])
                            - gridHeaderHeight) / numberOfGrids) - delta)
    else:
        return unicode(int((int(session["sessioncontext"]["currentDatapanelHeight"])
                            - gridHeaderHeight) / numberOfGrids) - delta)


def getSettingsPath():
    u"""Функция возвращает путь к файлу с настройками гранул."""

    try:
        from ru.curs.showcase.runtime import AppInfoSingleton
        settingsPath = r'%s/grainsSettings.xml' % AppInfoSingleton.getAppInfo().getUserdataRoot()
    except:
        settingsPath = Celesta.getInstance().setupProperties.getProperty('grainssettings.path')
    return settingsPath


def getFieldType(cursor, field):
    u"""Функция для получения типа поля курсора
        (хранится по разному в таблице и вьюхе)"""
    meta = cursor.meta()
    if isinstance(cursor, Cursor):
        field_type = meta.getColumn(field).celestaType
    elif isinstance(cursor, ViewCursor):
        field_type = meta.columns[field].celestaType

    return unicode(field_type)
