# coding: utf-8
import os
import json
from ru.curs.celesta import CelestaException

def toHexForXml(s):
    '''Функция модифицирует спецсимволы в строке в формат пригодный для имен тегов xml'''
    lst = []
    for ch in s:
        numCh = ord(ch)
        if numCh not in xrange (48, 58) and\
        numCh not in xrange (65, 91) and\
        numCh not in xrange (97, 123) and \
        numCh not in xrange (1040, 1104):
            lst.append('_x%s_' % ('000%s' % hex(numCh)[2:])[-4:])
        else:
            lst.append(ch)

    return reduce(lambda x, y:x + y, lst)

def tableCursorImport(grainName, tableName):
    u'''Функция, импортирующая  класс курсора на таблицу'''

    # Bмпорт гранулы
    _grain_orm = __import__("%s._%s_orm" % (grainName, grainName),
                            globals(), locals(), "%sCursor" % tableName, -1)

    return getattr(_grain_orm, "%sCursor" % tableName)

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
        return unicode(int((int(json.loads(session)["sessioncontext"]["currentDatapanelHeight"])\
                         - gridHeaderHeight) / numberOfGrids) - delta)
    else:
        return unicode(int((int(session["sessioncontext"]["currentDatapanelHeight"])\
                         - gridHeaderHeight) / numberOfGrids) - delta)

def getSettingsPath():
    u"""Функция возвращает путь к файлу с настройками гранул."""
    try:
        from ru.curs.showcase.runtime import AppInfoSingleton
        settingsPath = r'%s\grainsSettings.xml' % os.path.dirname(AppInfoSingleton.getAppInfo().getCurUserData().getPath())
    except:
        import initcontext
        settingsPath = initcontext().celesta.setupProperties.getProperty('grainssettings.path')
    return settingsPath
