# coding: utf-8
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
    session = json.loads(session)['sessioncontext']

    if isinstance(session['urlparams']['urlparam'], list):
        for params in session['urlparams']['urlparam']:
            if params['@name'] == 'taskId':
                taskId = params['@value'][0]
    xformsdata = {"schema":
                    {"data":{"@newStatus": "",
                             "@comment": "",
                             "statuses": {"status": []}}
                     }
                  }
    if add != "added":
        currentStatus = taskService.getVariable(taskId, 'status')
        model = taskService.getVariable(taskId, 'statusModel')
        status = statusCursor(context)
        statusTransition = statusTransitionCursor(context)
        statusTransition.setRange('statusFrom', currentStatus)
        statusTransition.setRange('modelFrom', model)
        xformsdata['schema']['data']['@type'] = 'add'
        for statusTransition in statusTransition.iterate():
            status.get(statusTransition.statusTo, statusTransition.modelTo)
            xformsdata["schema"]["data"]["statuses"]["status"].append({"@name": statusTransition.name,
                                                                       "@id": status.id})
    else:
        xformsdata['schema']['data']['@type'] = 'hide'


    xformssettings = {"properties":
                      {"event":
                       [{"@name": "single_click",
                         "@linkId": "1",
                         "action":
                            {"main_context": "current",
                             "datapanel":
                                {"@type": "current",
                                 "@tab": "current",
                                 "element":
                                    {"@id":'completeTaskCard',
                                     "add_context":"added"}}}}]}}
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)),
                     XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))

def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    session = json.loads(session)['sessioncontext']

    if isinstance(session['urlparams']['urlparam'], list):
        for params in session['urlparams']['urlparam']:
            if params['@name'] == 'taskId':
                taskId = params['@value'][0]
            elif params['@name'] == 'processId':
                processId = params['@value'][0]
    activiti = ActivitiObject()
    jsonData = json.loads(xformsdata)["schema"]["data"]

    if jsonData["@newStatus"] != '':
        if ' '.join(jsonData["@comment"].split(' ')) != '':
            activiti.taskService.addComment(taskId, processId, jsonData["@comment"])
        activiti.taskService.complete(taskId, {"status": jsonData["@newStatus"]})
        return context.message(u'Задача выполнена, статус изменен')
    else:
        return context.error(u'Ошибка, не выбран новый статус')
