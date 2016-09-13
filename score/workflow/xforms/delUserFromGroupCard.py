# coding: utf-8
'''
Created on 26.12.2014

@author: tr0glo)|(I╠╣.
'''


import json


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



from workflow._workflow_orm import userGroupCursor

from java.io import InputStream, FileInputStream
from jarray import zeros

from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка удаления пользователя из группы'''
    session = json.loads(session)
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "groupsGrid":
            groupId = gridContext["currentRecordId"]
        if gridContext["@id"] == "userGroupsGrid":
            if 'currentRecordId' in gridContext:
                userId = gridContext["currentRecordId"]
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{}
                        }
              }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"#sorted":[{"main_context": "current"},
                                                                    {"datapanel":{"@type": "current",
                                                                                 "@tab": "current",
                                                                                 "element":[
                                                                                            {"@id":'userGroupsGrid'},
                                                                                            {"@id":'groupsGrid',
                                                                                             "add_context":groupId}]
                                                                                 }
                                                                    }]}
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)



def cardDataSave(context, main, add, filterinfo, session, elementId, data):
    u'''Удаление пользователя из группы'''
    session = json.loads(session)
    userGroup = userGroupCursor(context)
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "groupsGrid":
            groupId = gridContext["currentRecordId"]
        if gridContext["@id"] == "userGroupsGrid":
            if 'currentRecordId' in gridContext:
                userId = gridContext["currentRecordId"]
    userGroup.get(userId, groupId)
    userGroup.delete()
    return context.message(u'Пользователь удален из группы')
