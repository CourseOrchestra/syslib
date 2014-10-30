# coding: utf-8

'''
Created on 22.10.2014

@author: m.prudyvus
'''


import simplejson as json

from common.sysfunctions import toHexForXml
from workflow.processUtils import ActivitiObject
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

    session = json.loads(session)['sessioncontext']
    drawInstance = False
    drawProcess = False
    for params in session['urlparams']['urlparam']:
        if params['@name'] == 'processId':
            procInstId = params['@value'][1:-1]
            drawInstance = True
        if params['@name'] == 'processKey':
            procKey = params['@value'][1:-1]
            drawProcess = True
    if drawInstance:
        data = {"image":{"@align":"center",
                     "@src": u"data:image/png;base64," + getBase64Image(activiti.getExecutionModel(procInstId))}}
    elif drawProcess:
        data = {"image":{"@align":"center",
                     "@src": u"data:image/png;base64," + getBase64Image(activiti.getDeployedProcessModel(procKey))}}        

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)
