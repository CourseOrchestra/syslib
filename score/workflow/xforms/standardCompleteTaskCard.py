# coding: utf-8
'''
Created on 02.10.2014

@author: A.Vasilyev.
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
    u'''Карточка стандартного завершения задачи без смены статуса'''
    if add == "added":
        xformsdata = {"schema":
                      {"@xmlns":'',
                       "data":
                        {"@type":'hide'}}}
    else:
        xformsdata = {"schema":
                      {"@xmlns":'',
                       "data":
                        {"@type":'add',
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
                                    {"@id":'completeTaskCard',
                                     "add_context":"added"}}}}]}}
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Процедура завершения задачи'''
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
    activiti.taskService.complete(taskId)
    return context.message(u'Задача выполнена')
