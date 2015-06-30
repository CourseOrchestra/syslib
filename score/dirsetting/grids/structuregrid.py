# coding: utf-8

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


from common import sysfunctions
from dirusing._dirusing_orm import foldersCursor, directoriesCursor
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def treeGrid(context, main=None, add=None, filterinfo=None, session=None, elementId=None, sortColumnList=None, parentId=None):

    _headers = {'id': '~~id',
                'name': u'Имя гранулы/папки/справочника',
                'prefix': u'Префикс',
                'table': u'Наименование таблицы',
                'type': u'Тип',
                'hasChildren': 'HasChildren',
                'properties': 'properties'}

    for col in _headers:
        _headers[col] = sysfunctions.toHexForXml(_headers[col])

    _data = {"records": {"rec": []}}

    folders = foldersCursor(context)
    directories = directoriesCursor(context)
    event = {"event":
                {"@name":"row_single_click",
                 "action":
                    {"main_context":"current",
                     "datapanel":
                        {'@type':'current',
                         '@tab':'current',
                         "element":[{'@id':'structXformsDirectories',
                                     "add_context":"hide"},
                                    {'@id':'structXformsFolder',
                                     "add_context":"hide"}]
                         }
                    }
                 }
             }

    if parentId is None:
        grains = context.getCelesta().getScore().grains
        for grain in sorted(grains):
            row = dict()
            row[_headers['id']] = 'g%s' % grain
            row[_headers['name']] = grain
            row[_headers['prefix']] = ''
            row[_headers['table']] = ''
            row[_headers['type']] = ''
            folders.setRange('grainId', grain)
            directories.setRange('grainId', grain)
            row[_headers['hasChildren']] = 1#int(folders.tryFirst()  or directories.tryFirst())
            row[_headers['properties']] = event
            _data["records"]["rec"].append(row)
    else:
        if parentId[0] == 'g':
            folders.setRange('grainId', parentId[1:])
            directories.setRange('grainId', parentId[1:])
        elif parentId[0] == 'f':
            folders.setRange('parentId', parentId[1:])
            directories.setRange('folderId', parentId[1:])

        folders.orderBy('name')
        directories.orderBy('name')

        for folders in folders.iterate():
            folderId = folders.id
            row = dict()
            row[_headers['id']] = 'f%d' % folderId
            row[_headers['name']] = folders.name
            row[_headers['prefix']] = ''
            row[_headers['table']] = ''
            row[_headers['type']] = ''

            _tempFolders = foldersCursor(context)
            _tempFolders.setRange('parentId', folderId)
            _tempDirectories = directoriesCursor(context)
            _tempDirectories.setRange('folderId', folderId)
            row[_headers['hasChildren']] = int(_tempFolders.tryFirst()  or _tempDirectories.tryFirst())
            row[_headers['properties']] = event
            _data["records"]["rec"].append(row)

        for  directories in directories.iterate():
            directoryId = directories.id
            row = dict()
            row[_headers['id']] = 'd%d' % directoryId
            row[_headers['name']] = directories.name
            row[_headers['prefix']] = directories.prefix
            row[_headers['table']] = directories.dbTableName
            row[_headers['type']] = ''
            row[_headers['hasChildren']] = 0
            row[_headers['properties']] = event
            _data["records"]["rec"].append(row)

    resultData = XMLJSONConverter(input=_data)
    settings = u'''
        <gridsettings>
            <action>
                <main_context>current</main_context>
                    <datapanel type="current" tab="current">
                        <element id="structXformsDirectories"><add_context>hide</add_context></element>
                        <element id="structXformsFolder"><add_context>hide</add_context></element>
                    </datapanel>
            </action>
           <labels>
            <header>
            Справочники
            </header>
          </labels>
          <columns>
            <col id="name" />
          </columns>
          <properties flip="false" pagesize="30" totalCount="0"/>
       </gridsettings>'''
    print resultData.parse()
    return JythonDTO(resultData.parse(), settings)

