# coding: utf-8
'''
Created on 18.09.2013

@author: AleXXL
'''
from xml.dom import minidom

from ru.curs.showcase.core.jython import JythonProc
from ru.curs.showcase.core.jython import JythonDTO

from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext

from score.dirU.GeneralFunctions import GridXmlConversion, ActionToXml
from score.dirU._dirU_orm import foldersCursor
from score.dirU._dirU_orm import directoriesCursor

# init vars
main = ""
add = ""
session = '''<sessioncontext>
   <username>master</username>
   <sid/>
   <sessionid>18768836AE58C96FEBAAF6236763D2A1</sessionid>
   <email/>
   <fullusername>master</fullusername>
   <phone/>
   <ip>127.0.0.1</ip>
   <userdata>default</userdata>
   <related>
      <gridContext id="structGrid">
         <pageInfo number="1" size="2147483646"/>
         <liveInfo limit="50" offset="0" totalCount="0"/>
         <currentRecordId>gcelesta</currentRecordId>
         <currentDatapanelWidth>0</currentDatapanelWidth>
         <currentDatapanelHeight>0</currentDatapanelHeight>
         <currentColumnId>name</currentColumnId>
         <selectedRecordId>gcelesta</selectedRecordId>
      </gridContext>
   </related>
</sessioncontext>'''
filterContext = """"""



class directoriesButtons(JythonProc):
    def getGridToolBarData(self, context):
        global main, add, session, filterContext, elementId
        main = context.getMain()
        if context.getAdditional():
            add = context.getAdditional()
        session = context.getSession()
        if context.getFilter():
            filterContext = context.getFilter()
        print context
        return mainproc()

def addEditAct (actTtype, size, reloadElem):
    actTtypes = {'add':u'Карточка добавления', 'edit':u'Карточка редактирования'}
    action = ActionToXml().xmlComp('action', {'show_in': 'MODAL_WINDOW'}, [
                                        ActionToXml().actParts('main_context', None, None, 'current'),
                                        ActionToXml().actParts('modalwindow', {'caption': actTtypes[actTtype],
                                                                               'width': size[0],
                                                                               'height': size[1]}, None, None),
                                         ActionToXml().actParts('datapanel',
                                                                {'type':'current',
                                                                'tab':'current'},
                                                                [({'id': reloadElem}, actTtype), ], None)])
    return action

def mainproc():
    relatedGrid = minidom.parseString(session).getElementsByTagName('gridContext')[0]
    relatedRowArr = relatedGrid.getElementsByTagName('selectedRecordId')

    buttonsArr = []
    if not relatedRowArr:
        buttonsArr = [1, 1, 0, 0, 0, 0]
    else:
        relatedRow = relatedRowArr[0].childNodes[0].data
        if relatedRow[0] == 'g':
            buttonsArr = [1, 1, 0, 0, 0, 0]
        elif relatedRow[0] == 'f':
            buttonsArr = [1, 1, 1, 0, 1, 0]
        elif relatedRow[0] == 'd':
            buttonsArr = [1, 1, 0, 1, 1, 1]

    addFold = ActionToXml().xmlComp('item', {'img': 'gridToolBar/addFolder.png',
                                            'hint': u'Добавить папку',
                                            'text': u'Добавить папку',
                                            'disable': 'false'}, [addEditAct('add', ['505', '180'], 'structXformsFolder')])
    addDic = ActionToXml().xmlComp('item', {'img': 'gridToolBar/addDirectory.png',
                                            'hint': u'Добавить справочник',
                                            'text': u'Добавить справочник',
                                            'disable': 'false'}, [addEditAct('add', ['605', '240'], 'structXformsDirectories')])
    if buttonsArr[2]:
        editFold = ActionToXml().xmlComp('item', {'img': 'gridToolBar/editFolder.png',
                                               'hint': u'Редактировать папку',
                                               'text': u'Редактировать папку',
                                               'disable': 'false'}, [addEditAct('edit', ['505', '180'], 'structXformsFolder')])
    else:
        editFold = ActionToXml().xmlComp('item', {'img': 'gridToolBar/editFolder.png',
                                               'hint': u'Редактировать папку',
                                               'text': u'Редактировать папку',
                                               'disable': 'true'}, [])
    if buttonsArr[3]:
        editDic = ActionToXml().xmlComp('item', {'img': 'gridToolBar/editDirectory.png',
                                               'hint': u'Редактировать справочник',
                                               'text': u'Редактировать справочник',
                                               'disable': 'false'}, [addEditAct('edit', ['605', '240'], 'structXformsDirectories')])
    else:
        editDic = ActionToXml().xmlComp('item', {'img': 'gridToolBar/editDirectory.png',
                                               'hint': u'Редактировать справочник',
                                               'text': u'Редактировать справочник',
                                               'disable': 'true'}, [])



    data = ActionToXml().xmlComp('gridtoolbar', None, [
                                    ActionToXml().xmlComp('group', {'text':u'Добавить'},
                                                          [addDic, addFold]),
                                    ActionToXml().xmlComp('group', {'text':u'Редактировать'},
                                                          [editDic, editFold])
                           ])

    #print data.toxml()
    return data.toxml()

if __name__ == "__main__":
    mainproc()
