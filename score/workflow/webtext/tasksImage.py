# coding: utf-8

'''
Created on 22.10.2014

@author: m.prudyvus
'''


import simplejson as json

from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, getBase64Image

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def webtextData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None):
    activiti = ActivitiObject()
    taskService = activiti.taskService;

    session = json.loads(session)
    taskId = session['sessioncontext']['related']['gridContext']['currentRecordId']
    task = taskService.createTaskQuery().taskId(taskId).singleResult()
    data = {"image":{"@src": u"data:image/png;base64," + getBase64Image(activiti.getExecutionModel(task.getProcessInstanceId()))}}


    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)
