# coding: utf-8
'''
Created on 02.10.2014

@author: A.Vasilyev.
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

from workflow.getUserInfo import userNameClass

try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory

from java.io import InputStream, FileInputStream
from jarray import zeros

from ru.curs.celesta.showcase.utils import XMLJSONConverter

from workflow.processUtils import parse_json

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка просмотра комментариев по задаче'''
    act = ActivitiObject()
    datapanelSettings = parse_json()
    usersClass = userNameClass(context, datapanelSettings)
    comments = act.taskService.getProcessInstanceComments(add)
#     for com in comments:
#         print com.getFullMessage(), com.getUserId()
#     
#     comments = act.taskService.getCommentsByType('comment')
#     for com in comments:
#         print com.getFullMessage()
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"#sorted":[{"main_context": "current"},
                                                                    {"datapanel":{"@type": "current",
                                                                                 "@tab": "current",
                                                                                 "element":{"@id":'tasksGrid',
                                                                                            "add_context":"added"}
                                                                                 }
                                                                    }]}
                                              }]
                                    }
                      }
    xformsdata = {"schema":
                      {"@xmlns":'',
                       "data":
                        []}}
    for comment in comments:
        if comment.getProcessInstanceId() == add:
            task = act.historyService.createHistoricTaskInstanceQuery().taskId(comment.getTaskId()).singleResult()

            xformsdata["schema"]["data"].append({"@comment":unicode(usersClass.getUserName(comment.getUserId())) + ': ' + comment.getFullMessage(),
                                                 "@task":task.getName()
                                                 })
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)




