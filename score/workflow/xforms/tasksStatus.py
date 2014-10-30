'''
Created on 23.10.2014

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
from workflow._workflow_orm import statusCursor, statusTransitionCursor

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    activiti = ActivitiObject()
    taskService = activiti.taskService
    session = json.loads(session)

    taskId = session['sessioncontext']['related']['gridContext']['currentRecordId']
    currentStatus = taskService.getVariable(taskId, 'status')
    docName = "%s. %s" % (taskService.getVariable(taskId, 'docId'), taskService.getVariable(taskId, 'docName'))
    model = taskService.getVariable(taskId, 'statusModel')
    requestReference = taskService.getVariable(taskId, 'requestReference')
    status = statusCursor(context)
    statusTransition = statusTransitionCursor(context)
    statusTransition.setRange('statusFrom', currentStatus)
    statusTransition.setRange('modelFrom', model)
    xformsdata = {"schema":
                    {"data":{"newStatus": "",
                             "docName": docName,
                             "requestReference": requestReference,
                             "statuses": {"status": []}}
                     }
                  }
    for statusTransition in statusTransition.iterate():
        status.get(statusTransition.statusTo, statusTransition.modelTo)
        xformsdata["schema"]["data"]["statuses"]["status"].append({"@name": statusTransition.name,
                                                                   "@id": status.id})

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
#     raise Exception(session)
    session = json.loads(session)
#     activiti.runtimeService.addEventListener(BaseEntityEventListener())
    taskId = session['sessioncontext']['related']['gridContext']['currentRecordId']
    jsonData = json.loads(xformsdata)["schema"]["data"]
    newStatus = jsonData["newStatus"]
    taskService.complete(taskId, {"status": newStatus})
