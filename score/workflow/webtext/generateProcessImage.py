# coding: utf-8

'''
Created on 12.11.2014

@author: tr0glo)|(I╠╣
'''




import simplejson as json

from common.sysfunctions import toHexForXml
from workflow.processUtils import ActivitiObject
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, getBase64Image

from workflow._workflow_orm import matchingCircuitCursor

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
    
try:
    from ru.curs.showcase.runtime import AppInfoSingleton
except:
    pass

from org.xml.sax.helpers import XMLReaderFactory
from org.xml.sax.ext import DefaultHandler2
from org.xml.sax import InputSource
from  javax.xml.stream import XMLOutputFactory
from java.io import FileInputStream, StringWriter

def webtextData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None):
#     activiti = ActivitiObject()
#     taskService = activiti.taskService;
#  
#     session = json.loads(session)['sessioncontext']
#     drawInstance = False
#     drawProcess = False
#     for params in session['urlparams']['urlparam']:
#         if params['@name'] == 'processId':
#             procInstId = params['@value'][0]
#             drawInstance = True
#         if params['@name'] == 'processKey':
#             procKey = params['@value'][0]
#             drawProcess = True
#     if drawInstance:
#         data = {"image":{"@align":"center",
#                      "@src": u"data:image/png;base64," + getBase64Image(activiti.getExecutionModel(procInstId))}}
#     elif drawProcess:
#         data = {"image":{"@align":"center",
#                      "@src": u"data:image/png;base64," + getBase64Image(activiti.getDeployedProcessModel(procKey))}}        
#          
    session = json.loads(session)
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    processKey = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processKey']
    processName = session['sessioncontext']['related']['xformsContext']['formData']['schema']['data']['@processName']
    matchingCircuit.setRange('processKey',processKey)
    if matchingCircuit.count() == 0:
        data = {'div':u'В процессе не задано задач'}
    else:
        matchingCircuitClone.setRange('processKey',processKey)
        matchingCircuit.setRange('type','parallel')
        parallelFlag = True
        for matchingCircuit in matchingCircuit.iterate():
            matchingCircuitClone.setFilter('number',"'%s.'%%" % matchingCircuit.number)
            if matchingCircuitClone.count() < 2:
                parallelFlag = False
                break
        matchingCircuit.clear()
        matchingCircuitClone.clear()
        matchingCircuit.setRange('processKey',processKey)
        matchingCircuit.setFilter('number',"!%'.'%")
        matchingCircuit.orderBy('sort')
        matchingCircuitClone.setRange('processKey',processKey)
        if parallelFlag:
            processXML = getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName)
            data = {'div':processXML}
        else:
            data = {'div':u'В одном из параллельных согласований содержится меньше двух элементов'}
    
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)


def getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName):
    u'''Функция для склейки карточки с блоками правил'''
    try:
        #rootPath = AppInfoSingleton.getAppInfo().getCurUserData().getPath() + '/xforms/workflow/'
        rootPath = 'C:/jprojects/celesta/manage/general/xforms/workflow/'
    except:
        rootPath = 'C:/jprojects/celesta/manage/general/xforms/workflow/'

    startAndEndPath = rootPath + 'typicalProcessTemplate.bpmn.xml' #путь к блоку со стартом и концом описания процесса
    consecPath = rootPath + 'consecutiveTaskTemplate.bpmn.xml' #путь к блоку, описывающему последовательную задачу
    parallelMatchingPath = rootPath + 'parallelMatchingTemplate.bpmn.xml' #путь к блоку, описываюшему параллельное выполнение задач
    parallelTaskPath  = rootPath + 'parallelTaskTemplate.bpmn.xml' #путь к блоку, описываюшему параллельную задачу
    stringWriter = StringWriter()
    xmlWriter = XMLOutputFactory.newInstance().createXMLStreamWriter(stringWriter)

    parser = XMLReaderFactory.createXMLReader()
    handler = XformsProcessTemplate(startAndEndPath, consecPath, parallelMatchingPath, parallelTaskPath, matchingCircuit, matchingCircuitClone,processKey, processName, xmlWriter)
    parser.setContentHandler(handler)
    parser.setErrorHandler(handler)
    parser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
    parser.setProperty("http://xml.org/sax/properties/lexical-handler", handler)

    stream = FileInputStream(startAndEndPath)
    parser.parse(InputSource(stream))
    xmlWriter.close()
    stringWriter.close()
    stream.close()
    return unicode(stringWriter)

class XformsProcessTemplate(DefaultHandler2):
    u'''SAX-parser для описания процесса старта и конца процесса'''
    def __init__(self, startAndEndPath, consecPath, parallelMatchingPath, parallelTaskPath,matchingCircuit,matchingCircuitClone, processKey, processName,xmlWriter):
        self.startAndEndPath = startAndEndPath
        self.consecPath = consecPath
        self.parallelMatchingPath = parallelMatchingPath
        self.parallelTaskPath = parallelTaskPath
        self.xmlWriter = xmlWriter
        self.matchingCircuit = matchingCircuit
        self.matchingCircuitClone = matchingCircuitClone
        self.processKey = processKey
        self.processName = processName

    def startDocument(self):
        self.xmlWriter.writeStartDocument("UTF-8", "1.0")

    def endDocument(self):
        self.xmlWriter.writeEndDocument()
        self.xmlWriter.flush()

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != 'startDescriptionTasks' and qname != 'process':
            self.xmlWriter.writeStartElement(qname)
            for i in range(0, attrs.getLength()):
                self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
        elif qname == 'process':
            self.xmlWriter.writeStartElement(qname)
            for i in range(0, attrs.getLength()):
                if attrs.getQName(i) == 'id':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), self.processKey)
                elif attrs.getQName(i) == 'name':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), self.processName)
                else:
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
        elif qname == 'startDescriptionTasks':
            inGatewayId = 'deleteDocumentExclusivegateway'
            assignee = 'QUQU'
            self.matchingCircuitClone.setFilter('number',"!%'.'%")
            topTasksCount = self.matchingCircuitClone.count()
            self.matchingCircuitClone.setRange('number')
            counter = 0
            parallelGatewayCounter = 1
            for matchingCircuit in self.matchingCircuit.iterate():
                if matchingCircuit.type == 'task':
                    counter += 1
                    if topTasksCount == counter:
                        outGatewayId = 'finalApprovementExclusivegateway'
                    else:
                        outGatewayId = 'outGateway'+str(matchingCircuit.id)
                    consecParser = XMLReaderFactory.createXMLReader()
                    consecHandler = consecWriter(inGatewayId,str(matchingCircuit.id),matchingCircuit.name, assignee, outGatewayId,self.xmlWriter)
                    consecParser.setContentHandler(consecHandler)
                    consecParser.setErrorHandler(consecHandler)
                    consecParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
                    consecParser.setProperty("http://xml.org/sax/properties/lexical-handler", consecHandler)
                    stream = FileInputStream(self.consecPath)
                    consecParser.parse(InputSource(stream))
                    inGatewayId = outGatewayId
                else:
                    self.matchingCircuitClone.setFilter('number',"'%s.'%%" % matchingCircuit.number)
                    counter += 1
                    if topTasksCount == counter:
                        outGatewayId = 'finalApprovementExclusivegateway'
                    else:
                        outGatewayId = 'outGatewayParallel'+str(counter)
                    parallelParser = XMLReaderFactory.createXMLReader()
                    parallelGatewayIn = parallelGatewayCounter
                    parallelGatewayCounter += 1
                    parallelGatewayOut = parallelGatewayCounter
                    parallelGatewayOut += 1
                    parallelId = parallelGatewayCounter
                    parallelGatewayCounter += 1
                    parallelHandler = parallelWriter(inGatewayId, parallelGatewayIn, parallelGatewayOut, self.matchingCircuitClone, outGatewayId, parallelId,self.parallelTaskPath,self.xmlWriter)
                    parallelParser.setContentHandler(parallelHandler)
                    parallelParser.setErrorHandler(parallelHandler)
                    parallelParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
                    parallelParser.setProperty("http://xml.org/sax/properties/lexical-handler", parallelHandler)
                    stream = FileInputStream(self.parallelMatchingPath)
                    parallelParser.parse(InputSource(stream))
                    inGatewayId = outGatewayId
    

    def endElement(self, uri, lname, qname):
        if qname != 'startDescriptionTasks':
            self.xmlWriter.writeEndElement()

    def comment(self, ch, start, length):
        self.xmlWriter.writeComment(''.join(ch[start:start + length]))

    def startPrefixMapping(self, prefix, uri):
        if prefix == "":
            self.xmlWriter.setDefaultNamespace(uri)
        else:
            self.xmlWriter.setPrefix(prefix, uri)


    def characters(self, ch, start, length):
        self.xmlWriter.writeCharacters(ch, start, length)

    def processingInstruction(self, target, data):
        self.xmlWriter.writeProcessingInstruction(target, data)

    def skippedEntity(self, name):
        self.xmlWriter.writeEntityRef(name)


class consecWriter(DefaultHandler2):
    u'''SAX-parser для блока последовательной задачи'''
    def __init__(self,inGatewayId,taskId,taskName, assignee, outGatewayId,xmlWriter):
        self.inGatewayId = inGatewayId
        self.taskId = taskId
        self.taskName = taskName
        self.assignee = assignee
        self.outGatewayId = outGatewayId
        self.xmlWriter = xmlWriter

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != "specialTag":
            self.xmlWriter.writeStartElement(qname)
            if qname == 'userTask':               
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskName)
                    if attrs.getQName(i) == 'activiti:assignee':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.assignee)
            elif qname == 'sequenceFlow':
                id = attrs.getValue('id')
                if id == 'inFlow':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'inFlow'+self.taskId)
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.inGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                elif id == 'outFlow':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'outFlow'+self.taskId)
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                elif id == 'reworkFlow':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkFlow'+self.taskId)
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkDocument')                
            elif qname == 'exclusiveGateway':
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), 'ExclusiveGateway')
            else:
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))


    def endElement(self, uri, lname, qname):
        if qname != "specialTag":
            self.xmlWriter.writeEndElement()

    def characters(self, ch, start, length):
        self.xmlWriter.writeCharacters(ch, start, length)

    def comment(self, ch, start, length):
        self.xmlWriter.writeComment(''.join(ch[start:start + length]))

    def startPrefixMapping(self, prefix, uri):
        if prefix == "":
            self.xmlWriter.setDefaultNamespace(uri)
        else:
            self.xmlWriter.setPrefix(prefix, uri)

    def processingInstruction(self, target, data):
        self.xmlWriter.writeProcessingInstruction(target, data)

    def skippedEntity(self, name):
        self.xmlWriter.writeEntityRef(name)
        

class parallelWriter(DefaultHandler2):
    u'''SAX-parser для блока последовательной задачи'''
    def __init__(self,inGatewayId, parallelGatewayIn, parallelGatewayOut, matchingCircuit, outGatewayId, parallelId, parallelTaskPath,xmlWriter):
        self.inGatewayId = inGatewayId
        self.parallelGatewayIn = parallelGatewayIn
        self.parallelGatewayOut = parallelGatewayOut
        self.parallelTaskPath = parallelTaskPath
        self.matchingCircuit = matchingCircuit
        self.outGatewayId = outGatewayId
        self.parallelId = parallelId
        self.xmlWriter = xmlWriter

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != "specialTag" and qname != "parallelTasksDescription":
            self.xmlWriter.writeStartElement(qname)
            if qname == 'parallelGateway':
                id = attrs.getValue('id')
                if id == 'parallelGatewayIn':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayIn' + str(self.parallelGatewayIn))
                        if attrs.getQName(i) == 'name':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'paralleGatewayIn')                    
                elif id == 'parallelGatewayOut':              
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayOut' + str(self.parallelGatewayOut))
                        if attrs.getQName(i) == 'name':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'paralleGatewayOut')                
            elif qname == 'sequenceFlow':
                id = attrs.getValue('id')
                if id == 'inFlow':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'inFlowParallel'+str(self.parallelId))
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.inGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayIn' + str(self.parallelGatewayIn))
                elif id == 'parallelTOexclusive':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'outFlowParallel'+str(self.parallelId))
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayOut' + str(self.parallelGatewayOut))
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                elif id == 'reworkFlow':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkFlowParallel'+str(self.parallelId))
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkDocument')                
            elif qname == 'exclusiveGateway':
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), 'ExclusiveGateway')
            else:
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
        elif qname == 'parallelTasksDescription':
            assignee = 'QUQU'
            for matchingCircuit in self.matchingCircuit.iterate():
                parallelTaskParser = XMLReaderFactory.createXMLReader()
                parallelTaskHandler = parallelTaskWriter(str(matchingCircuit.id),matchingCircuit.name,assignee, 'parallelGatewayIn' + str(self.parallelGatewayIn),'parallelGatewayOut' + str(self.parallelGatewayOut),self.xmlWriter)
                parallelTaskParser.setContentHandler(parallelTaskHandler)
                parallelTaskParser.setErrorHandler(parallelTaskHandler)
                parallelTaskParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
                parallelTaskParser.setProperty("http://xml.org/sax/properties/lexical-handler", parallelTaskHandler)
                stream = FileInputStream(self.parallelTaskPath)
                parallelTaskParser.parse(InputSource(stream))             

    def endElement(self, uri, lname, qname):
        if qname != "specialTag" and qname != 'parallelTasksDescription':
            self.xmlWriter.writeEndElement()

    def characters(self, ch, start, length):
        self.xmlWriter.writeCharacters(ch, start, length)

    def comment(self, ch, start, length):
        self.xmlWriter.writeComment(''.join(ch[start:start + length]))

    def startPrefixMapping(self, prefix, uri):
        if prefix == "":
            self.xmlWriter.setDefaultNamespace(uri)
        else:
            self.xmlWriter.setPrefix(prefix, uri)

    def processingInstruction(self, target, data):
        self.xmlWriter.writeProcessingInstruction(target, data)

    def skippedEntity(self, name):
        self.xmlWriter.writeEntityRef(name)
        
class parallelTaskWriter(DefaultHandler2):
    u'''SAX-parser для блока последовательной задачи'''
    def __init__(self,taskId,taskName, assignee, flowIn,flowOut,xmlWriter):
        self.flowIn = flowIn
        self.flowOut = flowOut
        self.taskId = taskId
        self.taskName = taskName
        self.assignee = assignee
        self.xmlWriter = xmlWriter

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != "specialTag":
            self.xmlWriter.writeStartElement(qname)
            if qname == 'userTask':               
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskName)
                    if attrs.getQName(i) == 'activiti:assignee':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.assignee)
            elif qname == 'sequenceFlow':
                id = attrs.getValue('id')
                if id == 'flowIn':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowIn+self.taskId+'parallelTask')
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowIn)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                elif id == 'flowOut':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowOut+self.taskId+'parallelTask')
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowOut)               
            else:
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))


    def endElement(self, uri, lname, qname):
        if qname != "specialTag":
            self.xmlWriter.writeEndElement()

    def characters(self, ch, start, length):
        self.xmlWriter.writeCharacters(ch, start, length)

    def comment(self, ch, start, length):
        self.xmlWriter.writeComment(''.join(ch[start:start + length]))

    def startPrefixMapping(self, prefix, uri):
        if prefix == "":
            self.xmlWriter.setDefaultNamespace(uri)
        else:
            self.xmlWriter.setPrefix(prefix, uri)

    def processingInstruction(self, target, data):
        self.xmlWriter.writeProcessingInstruction(target, data)

    def skippedEntity(self, name):
        self.xmlWriter.writeEntityRef(name)