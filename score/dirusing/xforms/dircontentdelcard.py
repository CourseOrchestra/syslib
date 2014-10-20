# coding: utf-8
'''

@author: a.rudenko

'''
import simplejson as json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from common.xmlutils import XMLJSONConverter
try:
    from ru.curs.showcase.core import UserMessage
except:
    pass    

from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport

from common import webservicefunc
import xml.dom.minidom

def cardDelData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}}
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
    #return UserMessage(u"TEST3", u"%s" % (session))
    #print XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse()
    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())


def cardDelDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    selectedRecordsCoded=json.loads(session)['sessioncontext']['related']['gridContext']['selectedRecordId']
    print type(selectedRecordsCoded)
    if type(selectedRecordsCoded) is list:
        for selectedRecordCoded in selectedRecordsCoded:
            #print selectedRecordCoded
            #print "2"
            selectedRecordId=json.loads(base64.b64decode(selectedRecordCoded))
            currentTable.get(*selectedRecordId)
            currentTable.delete()
    else:
        #print "1"
        selectedRecordId=json.loads(base64.b64decode(selectedRecordsCoded))
        currentTable.get(*selectedRecordId)
        currentTable.delete()
        
def cardDelAllDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    #grain_name = json.loads(main)['grain']
    #table_name = json.loads(main)['table']
    #currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    #currentTable.deleteAll()
    xmlIn = u'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:show="http://showcase.curs.ru">
   <soapenv:Header>
      <show:procName>ws/GetFile.py</show:procName>
   </soapenv:Header>
   <soapenv:Body>
      <show:requestAnylang>
         <command type="select" param="">
            <context param="">
            <grain>testgrain</grain>
            <table>adresses</table>
            <records>
            <rec>
            <column name="postalcode" where="'a1'">t11</column>
            <column name="city">t22</column>
            <column name="country">t33</column>
            <column name="flat">t44</column>
            <column name="building">t55</column>
            <column name="street">t66</column>
            </rec>
            <rec>
            <column name="postalcode">a11</column>
            <column name="city" where="'t2'">a22</column>
            <column name="country">a33</column>
            <column name="flat">a44</column>
            <column name="building">a55</column>
            <column name="street">a66</column>
            </rec>
            </records>
            <sid>26d5a14e-12ce-4174-9ebe-474e0beb7ad1</sid>
            </context>
         </command>
      </show:requestAnylang>
   </soapenv:Body>
</soapenv:Envelope>'''
    dom = xml.dom.minidom.parseString(xmlIn)
    
    grain_name = dom.getElementsByTagName('grain')[0].firstChild.nodeValue
    table_name = dom.getElementsByTagName('table')[0].firstChild.nodeValue
    
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    records = dom.getElementsByTagName("rec")
    for record in records:
            for column in record.getElementsByTagName("column"):
                columnValue = column.firstChild.data
                columnName = column.getAttributeNode('name').nodeValue
                setattr(currentTable, columnName, columnValue)
                print columnName
                print columnValue
            currentTable.update()
    


