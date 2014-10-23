# coding: utf-8

'''
Created on 22.10.2014

@author: m.prudyvus
'''


import simplejson as json
import base64
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, getBase64Image
import javax.xml.stream.XMLInputFactory as XMLInputFactory
import java.io.InputStreamReader as InputStreamReader
import org.activiti.bpmn.converter.BpmnXMLConverter as BpmnXMLConverter
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory

def webtextData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None):
    processEngine = EngineFactory.getActivitiProcessEngine()
    taskService = processEngine.getTaskService();
    activiti = ActivitiObject()

    session = json.loads(session)
    taskId = session['sessioncontext']['related']['gridContext']['currentRecordId']
    task = taskService.createTaskQuery().taskId(taskId).singleResult()
    data = {"image":{"@src": u"data:image/png;base64," + getBase64Image(activiti.getExecutionModel(task.getProcessInstanceId()))}}


    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)
