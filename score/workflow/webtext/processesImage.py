# coding: utf-8

import json
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



def webtextData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None):

    session = json.loads(session)
    processKey = session['sessioncontext']['related']['gridContext']['currentRecordId']

    activiti = ActivitiObject()
    data = {"image":{"@src": u"data:image/png;base64," + getBase64Image(activiti.getDeployedProcessModel(processKey))}}


    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)
