# coding: utf-8
'''
Created on 11.10.2013

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


class directoriesXformsFolder(JythonProc):
    def getRawData(self, context, elId):
        global main, add, session, filter, elementId
        main = context.getMain()
        if context.getAdditional():
            add = context.getAdditional()
        session = context.getSession()
        if context.getFilter():
            filter = context.getFilter()
        elementId = elId
        return mainproc()

def mainproc():
    doc = minidom.Document
    properties = ''
    data = u'''<schema><folder></folder><error_message/><folders></folders></schema>'''
    settings = u'''<properties>
                <event name="single_click" linkId="1">
                     <action>
                            <main_context>current</main_context>
                            <datapanel type="current" tab="current" >
                                <element id="1"/>
                            </datapanel>
                     </action>
                </event>
            </properties>'''

    return JythonDTO(data, settings)


if __name__ == "__main__":
    mainproc()
