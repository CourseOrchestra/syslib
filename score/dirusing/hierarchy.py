# coding: utf-8
import json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList,\
    getCursorDeweyColumns
from common.hierarchy import *


def move(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']

    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()

    deweyColumn, sortColumn = getCursorDeweyColumns(currentTable.meta())
    
    current_rec = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    #движение вверх
    if add == "up":
        for rec in currentTable.iterate():
            if current_rec == base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                changeNodePositionInLevelOfHierarchy(context, rec, deweyColumn, sortColumn, -1)
    #движение вниз
    if add == "down":
        for rec in currentTable.iterate():
            if current_rec == base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                changeNodePositionInLevelOfHierarchy(context, rec, deweyColumn, sortColumn, 1)
    #движение влево
    if add == "left":
        for rec in currentTable.iterate():
            if current_rec == base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                leftShiftNodeInHierarchy(context, rec, deweyColumn, sortColumn)
    #движение вправо
    if add == "right":
        for rec in currentTable.iterate():
            if current_rec == base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                currentNumber = getattr(rec, deweyColumn)
                currentList = currentNumber.split('.')
                prevList = currentList
                prevList[-1] = str(int(currentList[-1]) - 1)
                shiftNodeToOtherLevelInHierarchy(context, rec, deweyColumn, sortColumn, '.'.join(prevList))


def getNewItemInUpperLevel(context, currentTable, numberField):
    u'''Функция возвращает номер для нового элемента в самом верхнем уровне иерархии'''
    #Создаем клон основного курсора и копируем в него фильтры    
    cursorInstanceClone = currentTable.__class__(context)
    cursorInstanceClone.limit(0, 0)
    cursorInstanceClone.setFilter(numberField, '''(!%'.'%)''')
    return str(cursorInstanceClone.count() + 1)


def isExtr(context, cursorInstance, numberField, sortField, value):
    u'''Функция определяет, является ли элемент граничным (первым или последним) на своем уровне иерархии.
    value = 'first'/'last' .'''
    currentNumber = getattr(cursorInstance, numberField)
    currentSort = getattr(cursorInstance, sortField)
    parent = '.'.join(currentNumber.split('.')[0:-1])

    #Создаем клон основного курсора и копируем в него фильтры    
    cursorInstanceClone = cursorInstance.__class__(context)
    #cursorInstanceClone.copyFiltersFrom(cursorInstance)
    cursorInstanceClone.limit(0, 0)
    if len(parent) > 0:
        cursorInstanceClone.setFilter(numberField, "'%s.'%% & ! '%s.%%.'%%" % (parent, parent))
    else:
        cursorInstanceClone.setFilter(numberField, "! %'.'%")
    if value == 'first':
        cursorInstanceClone.setFilter(sortField, "<'%s'" % currentSort)
        return False if cursorInstanceClone.count() > 0 else True
    if value == 'last':
        cursorInstanceClone.setFilter(sortField, ">'%s'" % currentSort)
        return False if cursorInstanceClone.count() > 0 else True
