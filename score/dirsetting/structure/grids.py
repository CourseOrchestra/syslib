# coding: utf-8

from xml.dom import minidom

from ru.curs.showcase.core.jython import JythonProc
from ru.curs.showcase.core.jython import JythonDTO

from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext

from dirU.GeneralFunctions import GridXmlConversion, ActionToXml
from dirU._dirU_orm import foldersCursor
from dirU._dirU_orm import directoriesCursor
from system.XMLJSONConverter import JSONToXML
# init vars
main = ""
add = ""
session = ""
filterContext = ""
elementId = ""
sortcols = None #объект типа java.util.List<ru.curs.gwt.datagrid.model.Column>
parentId = None

print 1
#
#class directoriesGrid(JythonProc):
#    def getRawData(self, context, elId, scols):
#        global main, add, session, filterContext, elementId, sortcols, parentId
#        main = context.getMain()
#        if context.getAdditional():
#            add = context.getAdditional()
#        session = context.getSession()
#        if context.getFilter():
#            filterContext = context.getFilter()
#        elementId = elId
#        sortcols = scols
#        parentId = context.getParentId()
#        return mainproc()
#
#
#def mainproc():
#
#    celestaInst = Celesta.getInstance()
#    conn = ConnectionPool.get()
#    context = CallContext(conn, 'master')
#
#    _headers = (('id', '~~id'), ('name', u'Имя гранулы/папки/справочника'), ('prefix', u'Префикс'),
#                ('table', u'Наименование таблицы'), ('type', u'Тип'), ('hasChildren', 'HasChildren'),
#                ('properties', 'properties'))
#    _data = list()
#
#    _folders = foldersCursor(context)
#    _directories = directoriesCursor(context)
#
#    event = minidom.Element('event')
#    event.setAttribute('name', 'row_single_click')
#    event.appendChild(ActionToXml().xmlComp('action', None, [
#                            ActionToXml().actParts('main_context', None, None, 'current'),
#                            ActionToXml().actParts('datapanel',
#                                                    {'type':'current',
#                                                        'tab':'current'},
#                                                    [({'id':'structXformsDirectories'}, 'hide'),
#                                                        ({'id':'structXformsFolder'}, 'hide')] ,
#                                                    None)
#                                                  ]))
#
#
#
#
#    if not parentId:
#        grains = celestaInst.getScore().grains
#        for grain in sorted(grains):
#            row = dict()
#            row['id'] = 'g%s' % grain
#            row['name'] = grain
#            row['prefix'] = ''
#            row['table'] = ''
#            row['type'] = ''
#
#            _folders.setRange('grainId', grain)
#            _directories.setRange('grainId', grain)
#            row['hasChildren'] = int(_folders.tryFirst()  or _directories.tryFirst())
#
#            row['properties'] = event
#            _data.append(row)
#    else:
#        if parentId[0] == 'g':
#            _folders.setRange('grainId', parentId[1:])
#            _directories.setRange('grainId', parentId[1:])
#        elif parentId[0] == 'f':
#            _folders.setRange('parentId', parentId[1:])
#            _directories.setRange('folderId', parentId[1:])
#        else:
#            pass
#
#        _folders.orderBy('name')
#        _directories.orderBy('name')
#
#        while _folders.next():
#            folderId = _folders.id
#            row = dict()
#            row['id'] = 'f%d' % folderId
#            row['name'] = _folders.name
#            row['prefix'] = ''
#            row['table'] = ''
#            row['type'] = ''
#
#            _tempFolders = foldersCursor(context)
#            _tempFolders.setRange('parentId', folderId)
#            _tempDirectories = directoriesCursor(context)
#            _tempDirectories.setRange('folderId', folderId)
#            row['hasChildren'] = int(_tempFolders.tryFirst()  or _tempDirectories.tryFirst())
#
#
#            row['properties'] = event
#            _data.append(row)
#
#        while _directories.next():
#            directoryId = _directories.id
#            row = dict()
#            row['id'] = 'd%d' % directoryId
#            row['name'] = _directories.name
#            row['prefix'] = _directories.prefix
#            row['table'] = _directories.dbTableName
#            row['type'] = ''
#            row['hasChildren'] = 0
#
#            row['properties'] = event
#            _data.append(row)
#
#
#
#
#    resultData = GridXmlConversion().getGridData(_headers, _data)
#    settings = u'''
#    <gridsettings>
#        <action>
#            <main_context>current</main_context>
#                <datapanel type="current" tab="current">
#                    <element id="structXformsDirectories"><add_context>hide</add_context></element>
#                    <element id="structXformsFolder"><add_context>hide</add_context></element>
#                </datapanel>
#        </action>
#       <labels>
#        <header>
#        Справочники
#        </header>
#      </labels>
#      <columns>
#        <col id="name" />
#      </columns>
#      <properties flip="false" pagesize="30" totalCount="0"/>
#   </gridsettings>'''
#    res = JythonDTO(resultData.toxml(), settings)
#
#    ConnectionPool.putBack(conn)
#    #print resultData.toprettyxml()
#    return res
#
#
#if __name__ == "__main__":
#    mainproc();
