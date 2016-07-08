# coding: utf-8
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

import os
from workflow.processUtils import ActivitiObject,  functionImport, parse_json, getUsersCursor, getUserName
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security._security_orm import loginsCursor
from ru.curs.celesta.syscursors import UserRolesCursor
from workflow.getUserInfo import userNameClass, groupUsersClass

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    activiti = ActivitiObject()
    taskService = activiti.taskService
    session = json.loads(session)['sessioncontext']
    
    datapanelSettings = parse_json()
    usersClass = userNameClass(context,datapanelSettings)
    groupsClass = groupUsersClass(context, datapanelSettings)
    sid = session["sid"]
    taskId = session['related']['gridContext']['currentRecordId']
    identityLinks = taskService.getIdentityLinksForTask(taskId)
    #raise Exception(identityLinks)


    xformsdata = {"schema":
                    {"data":{"newUser": "",
                             "users": {"user": []}}
                     }
                  }

    assignee = ''
    for link in identityLinks:
        if link.type == 'assignee':
            assignee = link.userId
    reassList = list()
    for link in identityLinks:
        if link.type != 'assignee':
            if link.userId is None:
                usersList = groupsClass.getGroupUsers(link.groupId)
                for userId in usersList:
                    if userId != assignee:
                        if userId not in reassList:
                            reassList.append(userId)
            else:
                if link.userId != assignee:
                    if link.userId not in reassList:
                        reassList.append(link.userId)
    for userId in reassList:
        xformsdata["schema"]["data"]["users"]["user"].append({"@name": usersClass.getUserName(userId),
                                                       "@id": userId})       
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"#sorted":[{"main_context": "current"},
                                                       {"datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"tasksGrid",
                                                                                 "add_context": ""}
                                                                     }
                                                       }]}
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
    if jsonData["newUser"] == '':
        return context.error(u'Не выбран назначенный на задачу')
    taskService.unclaim(taskId)
    taskService.claim(taskId, jsonData["newUser"])