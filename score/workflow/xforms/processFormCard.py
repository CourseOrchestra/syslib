# coding: utf-8
'''
Created on 30.10.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json

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
    session = json.loads(session)
    form = formCursor(context)
    link = ''
    name = ''
    processKey = ''
    formId = ''
    isStart = 'false'
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "processesGrid":
            processKey = gridContext["currentRecordId"]
        if gridContext["@id"] == "processFormsGrid":
            if 'currentRecordId' in gridContext:
                formId = gridContext["currentRecordId"]
    form.setRange('isStartForm',True)
    form.setRange('processKey',processKey)
    if form.tryFirst():
        startAdded = 'true'
    else:
        startAdded = 'false' 
    if add == "add":     
        pass
    else:
        form = formCursor(context)
        form.get(processKey,formId)
        link = form.link
        name = form.id
        isStart = 'true' if form.isStartForm else 'false'
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{"@link":link,
                                "@id":name,
                                "@name":name,
                                "@processKey":processKey,
                                "@formId":formId,
                                "@startAdded":startAdded,
                                "@isStart":isStart,
                                "@add":add},                            
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
    data_dict = json.loads(data)
    processKey = data_dict["schema"]["data"]["@processKey"]
    prevId = data_dict["schema"]["data"]["@id"]
    id = data_dict["schema"]["data"]["@name"]
    link = data_dict["schema"]["data"]["@link"]
    isStart = True if data_dict["schema"]["data"]["@isStart"] == 'true' else False
    type = data_dict["schema"]["data"]["@add"]
    form = formCursor(context)
    if type == 'add':
        form.setRange("processKey",processKey)
        form.setRange("id",id)
        if form.count() > 0:
            return context.error(u'В данном процессе уже существует форма с таким именем')
        form.id = id
        form.processKey = processKey
        form.link = link
        form.isStartForm = isStart
        form.insert()
        return context.message(u'Форма добавлена')
    else:
        form.get(processKey,prevId)
        form.delete()
        form.id = id
        form.processKey = processKey
        form.link = link
        form.isStartForm = isStart
        form.insert()
        return context.message(u'Форма изменена')