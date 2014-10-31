# coding: utf-8
'''
Created on 30.10.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json
import urlparse
import cgi

from workflow.processUtils import ActivitiObject
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord
    
try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory
    
from workflow._workflow_orm import formCursor 
    
from java.io import InputStream, FileInputStream
from jarray import zeros

#from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка удаления формы процесса'''
    session = json.loads(session)
    form = formCursor(context)
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "processesGrid":
            processKey = gridContext["currentRecordId"]
        if gridContext["@id"] == "processFormsGrid":
            if 'currentRecordId' in gridContext:
                formId = gridContext["currentRecordId"]
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{}                         
                        }
              }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":[
                                                                                {"@id":'processFormsGrid'},
                                                                                {"@id":'processesGrid',
                                                                                 "add_context":processKey}]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)
                 


def cardSave(context, main, add, filterinfo, session, elementId, data):
    u'''Удаление формы процесса'''
    session = json.loads(session)
    form = formCursor(context)
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "processesGrid":
            processKey = gridContext["currentRecordId"]
        if gridContext["@id"] == "processFormsGrid":
            if 'currentRecordId' in gridContext:
                formId = gridContext["currentRecordId"]
    form.get(processKey,formId)
    form.delete()
    return context.message(u'Форма удалена')