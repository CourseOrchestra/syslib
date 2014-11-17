# coding: utf-8
'''
Created on 11.11.2014

@author: m.prudyvus
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


from java.io import InputStream, FileInputStream
from jarray import zeros

# from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка стандартного запуска процесса'''
    if add == "added":
        xformsdata = {"schema":
                      {"@xmlns":'',
                       "data":
                        {"@type":'hide'}}}
    else:
        activiti = ActivitiObject()
        session = json.loads(session)['sessioncontext']
        if isinstance(session['urlparams']['urlparam'], list):
            for params in session['urlparams']['urlparam']:
                if params['@name'] == 'taskId':
                    taskId = params['@value'][0]
        xformsdata = {"schema":
                      {"@xmlns":'',
                       "data":
                        {"@type":'add',
                         "@approveValue": "",
                         "@docDescription": activiti.taskService.getVariable(taskId, 'docDescription'),
                         "docRefs": {"ref": [{"@value": ref} for ref in json.loads(activiti.taskService.getVariable(taskId, 'docRef'))]} if activiti.taskService.getVariable(taskId, 'docRef') not in ('', None) else '',
                         "approves":
                            {"approve":
                             [{"@value": "True",
                               "@label": u"Утвердить"},
                              {"@value": "False",
                               "@label": u"Отклонить"}]},
                         "@comment": ""}}}
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
                                    {"@id":'approveTaskCard',
                                     "add_context":"added"}}}}]}}
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Запуск процесса'''
    session = json.loads(session)['sessioncontext']
    if isinstance(session['urlparams']['urlparam'], list):
        for params in session['urlparams']['urlparam']:
            if params['@name'] == 'taskId':
                taskId = params['@value'][0]
            elif params['@name'] == 'processId':
                processId = params['@value'][0]
    activiti = ActivitiObject()
    jsonData = json.loads(xformsdata)["schema"]["data"]

    if ' '.join(jsonData["@comment"].split(' ')) != '':
        activiti.taskService.addComment(taskId, processId, jsonData["@comment"])
    activiti.taskService.setVariableLocal(taskId, 'approved', jsonData["@status"])
    return context.message(u'Задача %s' % (u'утверждена' if jsonData["@status"] == 'True' else u'отклонена'))
