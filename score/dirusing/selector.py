# coding=UTF-8


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from ru.beta2.extra.gwt.ui.selector.api import DataRecord
from java.util import ArrayList
try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.curs.showcase.core.jython import DataSelectorAttributes
    from ru.curs.showcase.core import UserMessage
    from ru.curs.celesta.showcase.utils.XMLJSONConverter import xmlToJson
except:
    pass
import simplejson as json
import base64
from xml.dom import minidom

import xml.etree.ElementTree as ET
from common.hierarchy import hasChildren
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders

def selector(context, main=None, add=None, filterinfo=None, session=None, params=None, curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']

    dom = minidom.parseString(params)
    for elem in dom.getElementsByTagName('dbFieldName'):
        for child in elem.childNodes:
            dbFieldName = child.nodeValue.strip()

    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    column_jsn = json.loads(currentTable.meta().getColumn(dbFieldName).getCelestaDoc())
    refTableName = column_jsn["refTable"]
    refTableColumn = column_jsn["refTableColumn"]
    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
    records = dict()
    recordList = ArrayList()
    recordcount = relatedTable.count() if (relatedTable.count() > 0) else 0
    #firstrecord=0
    relatedTable.limit(firstrecord, recordcount)
    relatedTable.setFilter(refTableColumn, """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'", "''")))
    relatedTable.orderBy(refTableColumn)
    for rec in relatedTable.iterate():
        keys = relatedTable.meta().getPrimaryKey()
        for item in keys:
            key = item

        refTableColumnId = getattr(rec, key)
        refTableColumnValue = getattr(rec, refTableColumn)
        print refTableColumnId, refTableColumnValue
        records[rec] = DataRecord()
        if str(refTableColumnId):
            refTableColumnId = str(refTableColumnId)
        records[rec].setId(refTableColumnId)
        records[rec].setName(refTableColumnValue)
        recordList.add(records[rec])


    records = recordList

    count = relatedTable.count()
    return ResultSelectorData(records, count)

def multiSelector(context, main=None, add=None, filterinfo=None, session=None, params=None, curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    dom = minidom.parseString(params)
    for elem in dom.getElementsByTagName('dbFieldName'):
        for child in elem.childNodes:
            dbFieldName = child.nodeValue.strip()

    currentTable = relatedTableCursorImport(grain_name, table_name)(context)

    column_jsn = json.loads(currentTable.meta().getColumn(dbFieldName).getCelestaDoc())
    refTableName = column_jsn["refTable"]
    records = dict()
    recordList = ArrayList()

    refTableColumn = column_jsn["refTableColumn"]
    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)

    relatedTablePKs = relatedTable.meta().getPrimaryKey()

    recordcount = relatedTable.count() if (relatedTable.count() > 0) else 0
    #firstrecord=0
    relatedTable.limit(firstrecord, recordcount)
    relatedTable.setFilter(refTableColumn, """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'", "''")))
    relatedTable.orderBy(refTableColumn)

    for rec in relatedTable.iterate():
        relatedTablePKValues = []
        for pkValue in relatedTablePKs:
            relatedTablePKValues.extend([getattr(relatedTable, pkValue)])


        jsondump = json.dumps(relatedTablePKValues)

        currentRecordCoded = base64.b64encode(str(jsondump))

        #currentRecordDecoded = base64.b64decode(currentRecordCoded)

        refTableColumnValue = getattr(relatedTable, refTableColumn)
        records[rec] = DataRecord()
        records[rec].setId(currentRecordCoded)

        records[rec].setName(refTableColumnValue)

        recordList.add(records[rec])
    records = recordList

    count = relatedTable.count()

    return ResultSelectorData(records, count)

def treeSelectorData(context, main=None, add=None, filterinfo=None, session=None, params=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    #raise Exception(main,add,filterinfo,session,params,context.getData())
    params = json.loads(params)["params"]
    curvalue = params["curValue"].lower() if 'curValue' in params else ''
    startswith = True if "startsWith" in params and params["startsWith"] == 'true' else False

    dbFieldName = params["generalFilters"]["filter"]["field"]["dbFieldName"]
    field_type = int(params["generalFilters"]["filter"]["field"]["type_id"])

    treeSelectorMulty = True if (field_type == 6) else False

    currentTable = relatedTableCursorImport(grain_name, table_name)(context)

    column_jsn = json.loads(currentTable.meta().getColumn(dbFieldName).getCelestaDoc())
    refTableName = column_jsn["refTable"]

    refTableColumn = column_jsn["refTableColumn"]
    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)

    relatedTable.setFilter(refTableColumn, u"""@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'", "''")))

    #previous code is the same as multiselector, below comes the difference
    recordcount = relatedTable.count() if (relatedTable.count() > 0) else 0
    #firstrecord=0
    relatedTable.limit(firstrecord, recordcount)
    relatedTable.orderBy('sortNumber')
    if recordcount == 0:
        data = u'''
                <items>
                    <item id="1" name="Поиск не дал результатов" leaf="true"/>
                </items>'''

        return JythonDTO(data)
    data = u'''<items>'''
    i = 1
    lvlprev = 0
    lvlcur = 0
    parentcount = 0
    keys = relatedTable.meta().getPrimaryKey()
    for rec in relatedTable.iterate():

        if treeSelectorMulty:
            relatedTablePKValues = []
            for pkValue in keys:
                relatedTablePKValues.extend([getattr(relatedTable, pkValue)])
            jsondump = json.dumps(relatedTablePKValues)
            refTableColumnId = base64.b64encode(str(jsondump))
        else:
            for item in keys:
                key = item
            refTableColumnId = getattr(relatedTable, key)
        #lvlprev - the level of previous node, if 0 then it's root node without parents, 1 - child node has 1 parent, 2 child node - has 1 parent and 1 grandparent and so on
        #lvlcur - the level of current node
        #if lvlprev==lvlcur - both nodes on same level, lvlprev<lvlcur, then lvlcur is a child of lvlprev, if lvlprev>lvlcur, then lvlcur share the same level with parents of previous node
        deweyCodeValue = getattr(relatedTable, 'deweyCode')
        if i == 1: #первый элемент в курсоре
            lvlprev = str(deweyCodeValue).count(".")
            lvlcur = str(deweyCodeValue).count(".")
        else:
            lvlprev = lvlcur
            lvlcur = str(deweyCodeValue).count(".") #if no dots level is zero (root), if one dote level of node is 1
        sortValue = getattr(relatedTable, 'sortNumber')
        refTableColumnValue = getattr(relatedTable, refTableColumn)
        #raise Exception(str(sortValue),str(deweyCodeValue),unicode(refTableColumnValue),str(lvlcur),str(lvlprev),str(parentcount),data)

        if hasChildren(context, relatedTable, 'deweyCode'):
            if parentcount == 0:
                data += u'''<item id="%s" name="%s %s" refvalue="%s" cls="folder" leaf="false" checked="false">''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
            elif lvlprev == lvlcur:
                data += u'''<item id="%s" name="%s %s" refvalue="%s" cls="folder" leaf="false" checked="false">''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
            elif lvlprev < lvlcur:
                data += u'''<children><item id="%s" name="%s %s" refvalue="%s" cls="folder" leaf="false" checked="false">''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
            elif lvlprev > lvlcur:
                if parentcount > 0:
                    for j in xrange(0, lvlprev - lvlcur):
                        parentcount -= 1 if (parentcount > 0) else 0
                        data += u'''</children></item>'''
                data += u'''<item id="%s" name="%s %s" refvalue="%s" cls="folder" leaf="false" checked="false">''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
            parentcount += 1
        else:
            if parentcount == 0:
                data += u'''<item id="%s" name="%s %s" refvalue="%s" cls="" leaf="true" checked="false"/>''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
            elif lvlprev == lvlcur:
                data += u'''<item id="%s" name="%s %s" refvalue="%s" cls="" leaf="true" checked="false"/>''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
            elif lvlprev < lvlcur:

                data += u'''<children><item id="%s" name="%s %s" refvalue="%s" cls="" leaf="true" checked="false"/>''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)
                if i == recordcount and parentcount > 0:
                    for j in xrange(0, lvlcur):
                        data += u'''</children></item>'''
                        parentcount -= 1 if (parentcount > 0) else 0
            elif lvlprev > lvlcur:
                if parentcount > 0:
                    for j in xrange(0, lvlprev - lvlcur):
                        data += u'''</children></item>'''
                        parentcount -= 1 if (parentcount > 0) else 0
                data += u'''<item id="%s" name="%s %s" refvalue="%s" cls="" leaf="true" checked="false"/>''' % (refTableColumnId, deweyCodeValue, refTableColumnValue, refTableColumnValue)

        i += 1
    data += u"</items>"
    #raise Exception(data,str(parentcount))

    return JythonDTO(data)
