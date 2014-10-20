# coding: utf-8

from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from common import navigator, sysfunctions
from common.xmlutils import XMLJSONConverter

#try:
#    from java.lang import String111
#except:
#    from java.lang import Integer as III


import sys, os
import common
#from security.grid import permissions

a = Celesta.getInstance()
conn = ConnectionPool.get()
context = CallContext(conn, 'admin', a)
#print context.getCelesta()
from security.xform import permissions

def proc1(context):
    print permissions.cardData(context, add='add').data

proc1(context)
#    from dirusing._dirusing_orm import filtersConditionsCursor
#    filtersConditions = filtersConditionsCursor(context)
#    filtersConditions.id = 1
#    filtersConditions.prefix = None
#
#    if not filtersConditions.tryInsert():
#        filtersConditions.update()

#ConnectionPool.putBack(conn)


