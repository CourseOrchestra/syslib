# coding: utf-8
'''
Created on 26.12.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json
import urlparse
import cgi


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord



from workflow._workflow_orm  import userGroupCursor



# from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка добавления и редактирования формы процесаа'''
    session = json.loads(session)
    userId = ''
    userName = ''
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "groupsGrid":
            groupId = gridContext["currentRecordId"]


    xformsdata = {"schema":{"@xmlns":'',
                        "data":{
                                "@userId":userId,
                                "@userName":userName,
                                "@groupId":groupId
                                }
                        }
              }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":[
                                                                                {"@id":'userGroupsGrid'},
                                                                                {"@id":'groupsGrid',
                                                                                 "add_context":groupId}]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)



def cardDataSave(context, main, add, filterinfo, session, elementId, data):
    u'''Добавление пользователя в группу'''
    data_dict = json.loads(data)
    groupId = data_dict["schema"]["data"]["@groupId"]
    userId = data_dict["schema"]["data"]["@userId"]
    userId = json.loads(userId)[1]
    userGroup = userGroupCursor(context)
    userGroup.setRange('groupId', groupId)
    userGroup.setRange('userId', userId)
    if userGroup.count() > 0:
        return context.error(u'Данный пользователь уже состоит в этой группе')
    else:
        userGroup.userId = userId
        userGroup.groupId = groupId
        userGroup.insert()
