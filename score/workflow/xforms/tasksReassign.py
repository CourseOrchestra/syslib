'''
Created on 31.10.2014

@author: m.prudyvus
'''

import simplejson as json
from java.util import ArrayList
# from org.activiti.engine.delegate.event import BaseEntityEventListener
try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import JythonDTO, DataRecord, ResultSelectorData

from workflow.processUtils import ActivitiObject
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security._security_orm import loginsCursor
from ru.curs.celesta.syscursors import UserRolesCursor

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    activiti = ActivitiObject()
    taskService = activiti.taskService
    session = json.loads(session)['sessioncontext']

    sid = session["sid"]
    taskId = session['related']['gridContext']['currentRecordId']
    identityLinks = taskService.getIdentityLinksForTask(taskId)
    logins = loginsCursor(context)
    userRoles = UserRolesCursor(context)

    xformsdata = {"schema":
                    {"data":{"newUser": "",
                             "users": {"user": []}}
                     }
                  }
    for link in identityLinks:
        if link.userId != sid:
            if link.userId is None:
                userRoles.setRange('roleid', link.groupId)
                if userRoles.tryFirst():
                    while True:
                        logins.setRange("subjectId", userRoles.userid)
                        logins.first()
                        if userRoles.userid != sid:
                            xformsdata["schema"]["data"]["users"]["user"].append({"@name": logins.userName,
                                                                                  "@id": userRoles.userid})
                        if not userRoles.next():
                            break
            else:
                logins.setRange("subjectId", link.userId)
                logins.first()
                if link.userId != sid:
                    xformsdata["schema"]["data"]["users"]["user"].append({"@name": logins.userName,
                                                                          "@id": link.userId})

    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"tasksGrid",
                                                                                 "add_context": ""}
                                                                     }
                                                       }
                                             }
                                    }
                      }
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))

def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    activiti = ActivitiObject()
    taskService = activiti.taskService
    session = json.loads(session)['sessioncontext']
    taskId = session['related']['gridContext']['currentRecordId']
    jsonData = json.loads(xformsdata)["schema"]["data"]
    taskService.delegateTask(taskId, jsonData["newUser"])