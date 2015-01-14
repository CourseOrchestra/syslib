# coding: utf-8
import simplejson as json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList
from common.hierarchy import *


def move(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    
    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    
    for column in table_meta.getColumns():
            #получаем названия колонок с кодом дьюи и сортировкой
        if json.loads(table_meta.getColumn(column).getCelestaDoc())['name'] == u'deweyCode':
            deweyColumn=column
        if json.loads(table_meta.getColumn(column).getCelestaDoc())['name'] == u'sortNumber':
            sortColumn=column
    current_rec=json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    #движение вверх
    if add=="up":
        for rec in currentTable.iterate():
            if current_rec==base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                changeNodePositionInLevelOfHierarchy(context, rec, deweyColumn, sortColumn, -1)
    #движение вниз
    if add=="down":
        for rec in currentTable.iterate():
            if current_rec==base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                changeNodePositionInLevelOfHierarchy(context, rec, deweyColumn, sortColumn, 1)
    #движение влево
    if add=="left":
        for rec in currentTable.iterate():
            if current_rec==base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                leftShiftNodeInHierarchy(context, rec, deweyColumn, sortColumn)
    #движение вправо
    if add=="right":
        for rec in currentTable.iterate():
            if current_rec==base64.b64encode(json.dumps([elem for elem in rec._currentKeyValues()])):
                currentNumber=getattr(rec,deweyColumn)
                currentList=currentNumber.split('.')
                prevList=currentList
                prevList[-1]=str(int(currentList[-1])-1)
                shiftNodeToOtherLevelInHierarchy(context, rec, deweyColumn, sortColumn, '.'.join(prevList))
                