# coding: utf-8

'''
Created on 12.11.2014

@author: tr0glo)|(I╠╣
'''



import re, os
import simplejson as json

from common.sysfunctions import toHexForXml
from workflow.processUtils import ActivitiObject
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject, getBase64Image


from workflow._workflow_orm import matchingCircuitCursor, statusCursor, statusTransitionCursor

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
from java.io import FileInputStream, StringWriter, ByteArrayInputStream
from java.lang import String
import javax.xml.stream.XMLInputFactory as XMLInputFactory
import java.io.InputStreamReader as InputStreamReader
from org.activiti.engine.impl.util.io import InputStreamSource
from org.activiti.engine.impl.util.io import StreamSource
import org.activiti.bpmn.BpmnAutoLayout as BpmnAutoLayout
import org.activiti.bpmn.converter.BpmnXMLConverter as BpmnXMLConverter

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
        taskFlag = True
        maxParallelTasks = 1
        #Проверка на то, что в каждом параллельном согласовании не менее двух задач
        for matchingCircuit in matchingCircuit.iterate():
            matchingCircuitClone.setFilter('number',"'%s.'%%" % matchingCircuit.number)
            if matchingCircuitClone.count() < 2:
                parallelFlag = False
            if matchingCircuit.statusId is None and matchingCircuit.type == 'task':
                taskFlag = False
            if matchingCircuitClone.count() > maxParallelTasks:
                maxParallelTasks = matchingCircuitClone.count()
        matchingCircuit.clear()
        matchingCircuitClone.clear()
        matchingCircuit.setRange('processKey',processKey)
        matchingCircuit.setFilter('number',"!%'.'%")
        matchingCircuit.orderBy('sort')
        matchingCircuitClone.setRange('processKey',processKey)
        if parallelFlag and taskFlag:#Схема согласования корректна
#             processXML = getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName)
#             data = {'div':processXML}
            actObj = ActivitiObject()
            #raise Exception(getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName).encode('utf-8'))
            #Получение xml-описания процесса
            processDefinition = getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName, maxParallelTasks)
            stream = ByteArrayInputStream(processDefinition.encode('utf-8'))
            #Генерация картинки процесса
            xmlSource = InputStreamSource(stream)
            model = BpmnXMLConverter().convertToBpmnModel(xmlSource, False, False, String('UTF-8'))
            actObj.repositoryService.validateProcess(model)
            #BpmnAutoLayout(model).execute()
            generator = actObj.conf.getProcessDiagramGenerator()
            imageStream = generator.generatePngDiagram(model)
            #a1,a2 = getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName,maxParallelTasks)
            #data = {'div':[a1,a2]}
            data = {"image":{"@align":"center",
                       "@src": u"data:image/png;base64," + getBase64Image(imageStream)}}        

        elif not parallelFlag:
            data = {'div':u'В одном из параллельных согласований содержится меньше двух элементов'}
        else:
            data = {'div':u'В процессе есть задачи с неназначенными статусами'}
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)


def getProcessXML(context,matchingCircuit,matchingCircuitClone, processKey, processName, maxParallelTasks):
    u'''Функция генерации XML-описания процесса'''
    try:
        #rootPath = AppInfoSingleton.getAppInfo().getCurUserData().getPath() + '/xforms/workflow/'
        
        rootPath = os.path.dirname(os.path.abspath(__file__)) + '/'
        
        #rootPath = 'C:/jprojects/celesta/manage/general/xforms/workflow/'
    except:
        rootPath = 'C:/jprojects/celesta/manage/general/xforms/workflow/'
    #raise Exception(rootPath,type(rootPath))
    #Пути к шаблонам частей описания процесса
    startAndEndPath = rootPath + 'typicalProcessTemplate.bpmn.xml' #путь к блоку со стартом и концом описания процесса
    consecPath = rootPath + 'consecutiveTaskTemplate.bpmn.xml' #путь к блоку, описывающему последовательную задачу
    parallelMatchingPath = rootPath + 'parallelMatchingTemplate.bpmn.xml' #путь к блоку, описываюшему параллельное выполнение задач
    parallelTaskPath  = rootPath + 'parallelTaskTemplate.bpmn.xml' #путь к блоку, описываюшему параллельную задачу
    #Объявление переменных
    status = statusCursor(context)
    statusTransition = statusTransitionCursor(context)
    stringWriter = StringWriter()
    diagramWriter = StringWriter()
    xmlWriter = XMLOutputFactory.newInstance().createXMLStreamWriter(stringWriter)
    xmlDiagramWriter = XMLOutputFactory.newInstance().createXMLStreamWriter(diagramWriter)
    parser = XMLReaderFactory.createXMLReader()
    handler = XformsProcessTemplate(startAndEndPath, consecPath, parallelMatchingPath,
                                    parallelTaskPath, matchingCircuit,
                                    matchingCircuitClone,processKey,
                                    processName, xmlWriter,
                                    xmlDiagramWriter, diagramWriter,
                                    maxParallelTasks, status,
                                    statusTransition)
    parser.setContentHandler(handler)
    parser.setErrorHandler(handler)
    parser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
    parser.setProperty("http://xml.org/sax/properties/lexical-handler", handler)
    #Парсинг шаблона
    stream = FileInputStream(startAndEndPath)
    parser.parse(InputSource(stream))
    xmlWriter.close()
    stringWriter.close()
    diagramWriter.close()
    xmlDiagramWriter.close()
    stream.close()
    return stringWriter.toString()

def transformToVar(exp,var):
    u'''Функция трансформации переменных в вид, понятный activiti'''
    if exp.match(var):
        var = var.replace('[','{')
        var = var.replace(']','}')
        return var
    else:
        return var
    
def extractAssigneeAndCandidates(assJSON):
    u'''Получение ответственного за задачу и кандидатов'''
    pattern = '\$\[\w+\]'
    exp = re.compile(pattern)
    assJSON = json.loads(assJSON)
    assignee = transformToVar(exp,assJSON['assignee'])
    userList = list()
    for user in assJSON['users']:
        userList.append(transformToVar(exp,user))
    groupList = list()
    for group in assJSON['groups']:
        groupList.append(transformToVar(exp,group))
    return assignee, ','.join(userList),','.join(groupList)
    
def findAndReplacePattern(ch,start,length,rep,pattern,xmlWriter):
    u'''Функция для замены паттерна на другую строку'''
    flag = True
    if len(pattern) == length:
        for i in range(length):
            if ch[start+i] != pattern[i]:
                flag = False
    else:
        flag = False
    if flag:
        xmlWriter.writeCharacters(rep, 0, len(rep))
        return True
    else:
        return False 
    
def getStatusAndTransitionVal(status,statusTransition):
    statusValue = json.dumps([status.id,status.varName])
    statusTransition.setRange('statusFrom',status.id)
    statusTransition.setRange('modelFrom',status.modelId)
    transitionValue = dict()
    for statusTransition in statusTransition.iterate():
        status.get(statusTransition.statusTo,statusTransition.modelTo)
        transitionValue[status.id] = status.varName
    transitionValue = json.dumps(transitionValue)
    return statusValue,transitionValue   
    
def addBPMNShape(id, height, width, x, y, diagramWriter):
    u'''Функция записи в xml-файл объекта процесса по id с заданной шириной, высотой и координатами'''
    diagramWriter.writeStartElement('bpmndi:BPMNShape')
    diagramWriter.writeAttribute('bpmnElement',id)
    diagramWriter.writeAttribute('id','BPNMShape_'+id)
    diagramWriter.writeStartElement('omgdc:Bounds')
    diagramWriter.writeAttribute('height',str(height))
    diagramWriter.writeAttribute('width',str(width))
    diagramWriter.writeAttribute('x',str(x))
    diagramWriter.writeAttribute('y',str(y))
    diagramWriter.writeEndElement()                                                                                       
    diagramWriter.writeEndElement()
    return y+height

def addBPMNEdge(id, points, diagramWriter):
    u'''Функция записи в xml-файл ребра по заданным точкам'''
    diagramWriter.writeStartElement('bpmndi:BPMNEdge')
    diagramWriter.writeAttribute('bpmnElement',id)
    diagramWriter.writeAttribute('id','BPMNEdge_'+id)
    for point in points:
        diagramWriter.writeStartElement('omgdi:waypoint')
        diagramWriter.writeAttribute('x',str(point[0]))
        diagramWriter.writeAttribute('y',str(point[1]))
        diagramWriter.writeEndElement()  
    diagramWriter.writeEndElement()

def addSpecialTag(writer):
    u'''Функция записи в xml-файл специального тэга'''
    writer.writeStartElement('specialTag')
    writer.writeAttribute('xmlns','http://www.omg.org/spec/BPMN/20100524/MODEL')
    writer.writeAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    writer.writeAttribute('xmlns:xsd','http://www.w3.org/2001/XMLSchema')
    writer.writeAttribute('xmlns:activiti','http://activiti.org/bpmn')
    writer.writeAttribute('xmlns:bpmndi','http://www.omg.org/spec/BPMN/20100524/DI')
    writer.writeAttribute('xmlns:omgdc','http://www.omg.org/spec/DD/20100524/DC')
    writer.writeAttribute('xmlns:omgdi','http://www.omg.org/spec/DD/20100524/DI')
    writer.writeAttribute('typeLanguage','http://www.w3.org/2001/XMLSchema')
    writer.writeAttribute('expressionLanguage','http://www.w3.org/1999/XPath')
    writer.writeAttribute('targetNamespace','http://activiti.org/bpmn20')
    writer.writeAttribute('id','specTa')
    
    
class XformsProcessTemplate(DefaultHandler2):
    u'''SAX-parser для описания процесса старта и конца процесса'''
    def __init__(self, startAndEndPath, consecPath, parallelMatchingPath,\
                 parallelTaskPath,matchingCircuit,matchingCircuitClone, processKey,\
                 processName,xmlWriter, xmlDiagramWriter,diagramWriter, maxParallelTasks,
                 status, transition):
        #Пути к шаблонам процессов
        self.startAndEndPath = startAndEndPath
        self.consecPath = consecPath
        self.parallelMatchingPath = parallelMatchingPath
        self.parallelTaskPath = parallelTaskPath
        #Xml-writerы для описания процесса и описания диаграмы
        self.xmlWriter = xmlWriter
        self.diagramWriter = diagramWriter
        self.xmlDiagramWriter = xmlDiagramWriter
        #Курсор таблицы схемы согласования
        self.matchingCircuit = matchingCircuit
        self.matchingCircuitClone = matchingCircuitClone
        self.processKey = processKey
        self.processName = processName
        self.maxParallelTasks = maxParallelTasks
        #Инициализация параметров объктов диаграммы
        self.startY = 30  #Начальная ордината
        self.defaultStartEndDiametr = 35 #Размер круга старта и конца процессов
        self.gatewayAxis = 40 #Размер шлюза
        self.defaultTaskHeight = 55 # Высота задачи
        self.defaultTaskWidth = 300 # Ширина задачи
        self.defaultFlowLength = 75 # Длина ребра
        #Начальная абсцисса
        self.startX = ((self.defaultTaskWidth)*(self.maxParallelTasks+1)+self.gatewayAxis*(self.maxParallelTasks-1))/2
        #Текущее положение абсциссы
        self.currentY = int()
        #Курсоры статусов и соединений между статусами для генерации значений сответствющих переменных
        self.status = status
        self.statusTransition = transition
        

    def startDocument(self):
        self.xmlWriter.writeStartDocument("UTF-8", "1.0")

    def endDocument(self):
        self.xmlWriter.writeEndDocument()
        self.xmlWriter.flush()

    def startElement(self, namespaceURI, lname, qname, attrs):
        #Тег не описание задач, процесса, описание диаграммы
        if qname != 'startDescriptionTasks' and qname != 'process' and qname != 'diagramDescription':#Обыные элементы просто переписываем
            self.xmlWriter.writeStartElement(qname)
            #Запись атрибутов, для корневого тэга диаграммы подменяем ключ процесса
            for i in range(0, attrs.getLength()):
                if qname == 'bpmndi:BPMNDiagram' and attrs.getQName(i) == 'id':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), 'BPMNDiagram_'+self.processKey)
                elif qname == 'bpmndi:BPMNPlane' and attrs.getQName(i) == 'bpmnElement':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), self.processKey)
                elif qname == 'bpmndi:BPMNPlane' and attrs.getQName(i) == 'id':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), 'BPMNPlane_'+self.processKey)
                else:    
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
            if qname == 'startEvent':#Добавление в диаграмму начального события
                self.currentY = addBPMNShape("startevent1",
                                      self.defaultStartEndDiametr,
                                      self.defaultStartEndDiametr,
                                      self.startX-self.defaultStartEndDiametr/2,
                                      self.startY-self.defaultStartEndDiametr/2,
                                      self.xmlDiagramWriter)
            elif qname == 'userTask':
                if attrs.getValue('id') == "createDocument":#Добавление в диаграмму Создания документа
                    self.currentY = addBPMNShape("createDocument",
                                      self.defaultTaskHeight,
                                      self.defaultTaskWidth,
                                      self.startX-self.defaultTaskWidth/2,
                                      self.startY+self.defaultStartEndDiametr/2+self.defaultFlowLength,
                                      self.xmlDiagramWriter)
                elif attrs.getValue('id') == "reworkDocument":# Добавление Доработки документа
                    self.currentY = addBPMNShape("reworkDocument",
                                      self.defaultTaskHeight,
                                      self.defaultTaskWidth,
                                      self.startX*2 - self.defaultTaskWidth/2,
                                      self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+0.5*self.defaultTaskHeight+self.gatewayAxis/2,
                                      self.xmlDiagramWriter)
            elif qname == 'endEvent':
                if attrs.getValue('id') == "endevent1":# Первый выход из процесса по удалению документа
                    self.currentY = addBPMNShape("endevent1",
                                      self.defaultStartEndDiametr,
                                      self.defaultStartEndDiametr,
                                      self.startX-self.defaultTaskWidth/2-self.defaultStartEndDiametr,
                                      self.startY+2*self.defaultFlowLength+self.defaultTaskHeight+self.defaultStartEndDiametr/2,
                                      self.xmlDiagramWriter)                              
                elif attrs.getValue('id') == "endevent2":# Второй выход из процесса по его завершению
                    self.currentY = addBPMNShape("endevent2",
                                      self.defaultStartEndDiametr,
                                      self.defaultStartEndDiametr,
                                      self.startX-self.defaultStartEndDiametr/2,
                                      self.currentY+self.defaultFlowLength,
                                      self.xmlDiagramWriter)
            elif qname == 'exclusiveGateway':# Шлюз на удаление документа
                self.currentY = addBPMNShape("deleteDocumentExclusivegateway",
                                  self.gatewayAxis,
                                  self.gatewayAxis,
                                  self.startX-self.gatewayAxis/2,
                                  self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+self.defaultTaskHeight,
                                  self.xmlDiagramWriter)
            elif qname == 'sequenceFlow':
                if attrs.getValue('id') == "fromStartToCreate":# Ребо от старта к созданию документа
                    addBPMNEdge("fromStartToCreate",
                                 [ (self.startX, self.startY+self.defaultStartEndDiametr/2),
                                   (self.startX, self.startY+self.defaultStartEndDiametr/2+self.defaultFlowLength)],
                                  self.xmlDiagramWriter)                   
                elif attrs.getValue('id') == "fromStartToDeleteGateway":# Ребро от Создания документа к щлюзу по удалению
                    addBPMNEdge("fromStartToDeleteGateway",
                                 [ (self.startX, self.startY+self.defaultStartEndDiametr/2+self.defaultFlowLength+self.defaultTaskHeight),
                                   (self.startX, self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+self.defaultTaskHeight)],
                                  self.xmlDiagramWriter)
                elif attrs.getValue('id') == "fromDeleteToEnd1":#Ребро ищ шлюза к первому выходу из процесса
                    addBPMNEdge("fromDeleteToEnd1",
                                 [ (self.startX, self.startY+self.defaultStartEndDiametr/2),
                                   (self.startX, self.startY+self.defaultStartEndDiametr/2+self.defaultFlowLength)],
                                  self.xmlDiagramWriter)                             
                elif attrs.getValue('id') == "fromReworkToDelete":# Ребро от доработки процесса к щлюзу по удалению
                    addBPMNEdge("fromReworkToDelete",
                                 [(self.startX*2 - self.defaultTaskWidth/2,
                                    self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+self.defaultTaskHeight+self.gatewayAxis/2),
#                                   (self.startX*2-self.defaultStartEndDiametr - self.defaultTaskWidth/2,
#                                    self.startY+self.defaultStartEndDiametr/2+self.defaultFlowLength+self.defaultTaskHeight/2),
#                                   (self.startX*2-self.defaultStartEndDiametr - self.defaultTaskWidth/2,
#                                     self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+self.defaultTaskHeight+self.gatewayAxis/2),
                                  (self.startX,
                                   self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+self.defaultTaskHeight+self.gatewayAxis/2),  
                                   ],
                                  self.xmlDiagramWriter)
                elif attrs.getValue('id') == "finalFlow":#Ребро из последнего согласования ко второму выходу из процесса
                    addBPMNEdge("finalFlow",
                                 [ (self.startX, self.currentY),
                                   (self.startX, self.currentY+self.defaultFlowLength)],
                                  self.xmlDiagramWriter)           
        elif qname == 'process':#Подменяем название и ключ процесса
            self.xmlWriter.writeStartElement(qname)
            addSpecialTag(self.xmlDiagramWriter)
            for i in range(0, attrs.getLength()):
                if attrs.getQName(i) == 'id':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), self.processKey)
                elif attrs.getQName(i) == 'name':
                    self.xmlWriter.writeAttribute(attrs.getQName(i), self.processName)
                else:
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
        elif qname == 'startDescriptionTasks':#Начало описания задач процесса
            inGatewayId = 'deleteDocumentExclusivegateway'
            self.matchingCircuitClone.setFilter('number',"!%'.'%")
            topTasksCount = self.matchingCircuitClone.count()
            self.matchingCircuitClone.setRange('number')
            counter = 0
            parallelGatewayCounter = 1
            self.currentY = self.startY + self.defaultFlowLength * 2 + self.defaultTaskHeight + self.gatewayAxis + self.defaultStartEndDiametr/2
            for matchingCircuit in self.matchingCircuit.iterate():
                if matchingCircuit.type == 'task':#Обработка последовательной задачи
                    counter += 1
                    #если задача последняя
                    if topTasksCount == counter:
                        outGatewayId = 'finalApprovementExclusivegateway'
                    else:
                        outGatewayId = 'outGateway'+str(matchingCircuit.id)
                    #Получение ответственных
                    assignee,candidates,groups = extractAssigneeAndCandidates(matchingCircuit.assJSON)
                    self.status.get(matchingCircuit.statusId,matchingCircuit.modelId)
                    statusVal, transitionsVal = getStatusAndTransitionVal(self.status, self.statusTransition)
                    consecParser = XMLReaderFactory.createXMLReader()
                    consecHandler = consecWriter(inGatewayId,'task' + str(matchingCircuit.id),
                                                 matchingCircuit.name, assignee,
                                                 candidates,groups,outGatewayId,
                                                 self.xmlWriter,self.xmlDiagramWriter,
                                                 self.currentY, self.startX,
                                                 statusVal,transitionsVal)
                    #Изменям текущую абсциссу, добавляя к ней высоту описания последовательной задачи
                    self.currentY = self.currentY + 2*self.defaultFlowLength + self.defaultTaskHeight + self.gatewayAxis
                    consecParser.setContentHandler(consecHandler)
                    consecParser.setErrorHandler(consecHandler)
                    consecParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
                    consecParser.setProperty("http://xml.org/sax/properties/lexical-handler", consecHandler)
                    #Парсинг шаблона описания последовательной задачи
                    stream = FileInputStream(self.consecPath)
                    consecParser.parse(InputSource(stream))
                    #id выходного шлюза есть id входного шлюза для следующего элемента
                    inGatewayId = outGatewayId
                    #raise Exception(consecHandler.char)
                else:#Обработка параллельного согласования
                    self.matchingCircuitClone.setFilter('number',"'%s.'%%" % matchingCircuit.number)
                    counter += 1
                    #если задача последняя
                    if topTasksCount == counter:
                        outGatewayId = 'finalApprovementExclusivegateway'
                    else:
                        outGatewayId = 'outGatewayParallel'+str(counter)
                    parallelParser = XMLReaderFactory.createXMLReader()
                    # счётчики для идентификаторов шлюзов
                    parallelGatewayIn = parallelGatewayCounter
                    parallelGatewayCounter += 1
                    parallelGatewayOut = parallelGatewayCounter
                    parallelGatewayOut += 1
                    parallelId = parallelGatewayCounter
                    parallelGatewayCounter += 1
                    parallelHandler = parallelWriter(inGatewayId, parallelGatewayIn,
                                                     parallelGatewayOut,
                                                     self.matchingCircuitClone, outGatewayId,
                                                     parallelId,self.parallelTaskPath,self.xmlWriter,
                                                     self.xmlDiagramWriter,
                                                     self.startX, self.currentY,
                                                     self.status, self.statusTransition)
                    #обновление  текущей абсциссы
                    self.currentY = self.currentY + 2*self.defaultFlowLength + self.defaultTaskHeight + 7*self.gatewayAxis
                    parallelParser.setContentHandler(parallelHandler)
                    parallelParser.setErrorHandler(parallelHandler)
                    parallelParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
                    parallelParser.setProperty("http://xml.org/sax/properties/lexical-handler", parallelHandler)
                    stream = FileInputStream(self.parallelMatchingPath)
                    #парсинг шаблона параллельных задач
                    parallelParser.parse(InputSource(stream))
                    inGatewayId = outGatewayId
        elif qname == 'diagramDescription':# вставка описания диаграммы
            diagramParser = XMLReaderFactory.createXMLReader()
            diagramHandler = diagramWriter(self.xmlWriter)
            diagramParser.setContentHandler(diagramHandler)
            diagramParser.setErrorHandler(diagramHandler)
            diagramParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
            diagramParser.setProperty("http://xml.org/sax/properties/lexical-handler", diagramHandler)
            stream = ByteArrayInputStream(self.diagramWriter.toString().encode('utf-8'))
            #парсим описание диаграммы и вставляем его в общий xml
            diagramParser.parse(InputSource(stream))
    

    def endElement(self, uri, lname, qname):
        #специальные теги-маркеры не пишутся в окончательный файл
        if qname != 'startDescriptionTasks' and qname != 'diagramDescription':
            if qname == 'process':#при закрытии тэга процесса закрываем writer диаграммы
                self.xmlDiagramWriter.writeEndElement()
                self.diagramWriter.close()
                self.xmlDiagramWriter.close
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
    def __init__(self,inGatewayId,taskId,taskName, assignee,\
                  candidates, groups, outGatewayId,xmlWriter,\
                  xmlDiagramWriter, currentY, startX, statusVal, transitionsVal):
        #инициализация идентификатора входного шлюза
        self.inGatewayId = inGatewayId
        #ответственные
        self.assignee = assignee
        self.candidates = candidates
        self.groups = groups
        #задача и ее названия
        self.taskId = taskId
        self.taskName = taskName
        #идентификатор выходного шлюза
        self.outGatewayId = outGatewayId
        self.xmlWriter = xmlWriter
        self.xmlDiagramWriter = xmlDiagramWriter
        #параметры диаграммы, аналогичные параметры в парсере общего шаблона
        self.currentY = currentY
        self.startX = startX
        self.startY = 30 
        self.defaultStartEndDiametr = 35
        self.gatewayAxis = 40
        self.defaultTaskHeight = 55
        self.defaultTaskWidth = 300
        self.defaultFlowLength = 75
        #Значение статуса и переходов
        self.statusVal = statusVal
        self.transitionsVal = transitionsVal

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != "specialTag":#спецтег не пишется
            self.xmlWriter.writeStartElement(qname)
            if qname == 'userTask':#Описание задачи процесса             
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskName)
                    if attrs.getQName(i) == 'activiti:assignee':
                        if self.assignee != '':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.assignee)
                    if attrs.getQName(i) == 'activiti:candidateUsers':
                        if self.candidates != '':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.candidates)
                    if attrs.getQName(i) == 'activiti:candidateGroups':
                        if self.groups != '':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.groups)
                self.currentY = addBPMNShape(self.taskId,
                              self.defaultTaskHeight,
                              self.defaultTaskWidth,
                              self.startX-self.defaultTaskWidth/2,
                              self.currentY,
                              self.xmlDiagramWriter)
            elif qname == 'sequenceFlow':#Описание рёбер
                id = attrs.getValue('id')
                if id == 'inFlow':#Входящее ребро
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'inFlow'+self.taskId)
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.inGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                    addBPMNEdge('inFlow'+self.taskId,
                                 [(self.startX, self.currentY),
                                 (self.startX, self.currentY+self.defaultFlowLength)],
                                 self.xmlDiagramWriter)
                    self.currentY = self.currentY+self.defaultFlowLength
               
                elif id == 'outFlow':#Исходящее ребро
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'outFlow'+self.taskId)
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                    addBPMNEdge('outFlow'+self.taskId,
                                 [(self.startX, self.currentY+self.defaultTaskHeight),
                                   (self.startX, self.currentY+self.defaultTaskHeight+self.defaultFlowLength)],
                                self.xmlDiagramWriter)
                    self.currentY = self.currentY+self.defaultFlowLength
                
                elif id == 'reworkFlow':#Ребро к доработк процесса
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkFlow'+self.taskId)
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkDocument')
                    addBPMNEdge('reworkFlow'+self.taskId, 
                                [(self.startX+self.gatewayAxis/2, self.currentY-self.gatewayAxis/2),
                                (self.startX*2, self.currentY-self.gatewayAxis/2),
                                (self.startX*2,self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+1.5*self.defaultTaskHeight+self.gatewayAxis/2)],
                                self.xmlDiagramWriter)            
            elif qname == 'exclusiveGateway':#выходной шлюз
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), 'ExclusiveGateway')
                self.currentY = addBPMNShape(self.outGatewayId,
                                      self.gatewayAxis,
                                      self.gatewayAxis,
                                      self.startX-self.gatewayAxis/2,
                                      self.currentY,
                                      self.xmlDiagramWriter)
            else:#Остальные элементы
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))


    def endElement(self, uri, lname, qname):
        if qname != "specialTag":
            self.xmlWriter.writeEndElement()

    def characters(self, ch, start, length):
        u'''Для первой задачи надо изменить условия выхода из шлюза'''
        if self.inGatewayId == 'deleteDocumentExclusivegateway':
            rep = '${deleteDocument == "false"}'
            pattern = list('${orderApproved == "true"}')
            flowFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
            rep = "task.setVariableLocal('status', '%s')" % self.statusId
            pattern = list('task.setVariableLocal("status", "createStatus")')
            statusFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
            rep = "task.setVariableLocal('transitions', '%s')" % self.transitionsVal
            pattern = list('task.setVariableLocal("transitions", "createTransitions")')
            transitionsFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
            if not flowFlag and not statusFlag and not transitionsFlag:
                self.xmlWriter.writeCharacters(ch, start, length)
        else:
            rep = "task.setVariableLocal('status', '%s')" % self.statusVal
            pattern = list('task.setVariableLocal("status", "createStatus")')
            statusFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
            rep = "task.setVariableLocal('transitions', '%s')" % self.transitionsVal
            pattern = list('task.setVariableLocal("transitions", "createTransitions")')
            transitionsFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
            if not statusFlag and not transitionsFlag:
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
    u'''SAX-parser для параллельного блока'''
    def __init__(self,inGatewayId, parallelGatewayIn, parallelGatewayOut,
                  matchingCircuit, outGatewayId, parallelId,
                  parallelTaskPath,xmlWriter, xmlDiagramWriter, startX, currentY,
                  status, transition):
        #идентификаторы входного шлюза, выходного шлюза, входного и выходного шлбза паралелльного согласования
        self.inGatewayId = inGatewayId
        self.parallelGatewayIn = parallelGatewayIn
        self.parallelGatewayOut = parallelGatewayOut
        self.parallelTaskPath = parallelTaskPath
        self.outGatewayId = outGatewayId
        self.parallelId = parallelId
        #курсор схемы согласовния процесса
        self.matchingCircuit = matchingCircuit
        #параметры диаграммы
        self.startX = startX
        self.startY = 30 
        self.defaultStartEndDiametr = 35
        self.gatewayAxis = 40
        self.defaultTaskHeight = 55
        self.defaultTaskWidth = 300
        self.defaultFlowLength = 75
        self.currentY = currentY
        self.xmlDiagramWriter = xmlDiagramWriter
        self.xmlWriter = xmlWriter
        #Курсоры для статусов и переходов
        self.status = status
        self.statusTransition = transition

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != "specialTag" and qname != "parallelTasksDescription":#специальные теги не пишем
            self.xmlWriter.writeStartElement(qname)
            if qname == 'parallelGateway':
                id = attrs.getValue('id')
                if id == 'parallelGatewayIn':#Входной шлюз параллельного согласования
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayIn' + str(self.parallelGatewayIn))
                        if attrs.getQName(i) == 'name':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'paralleGatewayIn')
                    self.currentY = addBPMNShape('parallelGatewayIn' + str(self.parallelGatewayIn),
                                                  self.gatewayAxis,
                                                  self.gatewayAxis,
                                                  self.startX-self.gatewayAxis/2,
                                                  self.currentY,
                                                  self.xmlDiagramWriter)                 
                elif id == 'parallelGatewayOut':#Выходной шлюз параллельного согласования              
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayOut' + str(self.parallelGatewayOut))
                        if attrs.getQName(i) == 'name':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'paralleGatewayOut')
                    self.currentY = addBPMNShape('parallelGatewayOut' + str(self.parallelGatewayOut),
                              self.gatewayAxis,
                              self.gatewayAxis,
                              self.startX-self.gatewayAxis/2,
                              self.currentY-self.gatewayAxis/2,
                              self.xmlDiagramWriter)                 
            elif qname == 'sequenceFlow':
                id = attrs.getValue('id')
                if id == 'inFlow':#входное ребро во входной паралелльный шлюз
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'inFlowParallel'+str(self.parallelId))
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.inGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayIn' + str(self.parallelGatewayIn))
                    addBPMNEdge('inFlowParallel'+str(self.parallelId),
                                 [(self.startX, self.currentY),
                                 (self.startX, self.currentY+self.defaultFlowLength)],
                                 self.xmlDiagramWriter)
                    self.currentY = self.currentY + self.defaultFlowLength              
                elif id == 'parallelTOexclusive':# ребро из выходного параллельного шлюза к выходному шлюзу
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'outFlowParallel'+str(self.parallelId))
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'parallelGatewayOut' + str(self.parallelGatewayOut))
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                    addBPMNEdge('outFlowParallel'+str(self.parallelId),
                                 [(self.startX, self.currentY),
                                 (self.startX, self.currentY+self.defaultFlowLength)],
                                 self.xmlDiagramWriter)
                    self.currentY = self.currentY + self.defaultFlowLength
                elif id == 'reworkFlow':#ребро к доработке документа
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkFlowParallel'+str(self.parallelId))
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), 'reworkDocument')                
                    addBPMNEdge('reworkFlowParallel'+str(self.parallelId), 
                                [(self.startX+self.gatewayAxis/2, self.currentY-self.gatewayAxis/2),
                                (self.startX*2, self.currentY-self.gatewayAxis/2),
                                (self.startX*2,self.startY+self.defaultStartEndDiametr/2+2*self.defaultFlowLength+1.5*self.defaultTaskHeight+self.gatewayAxis/2)],
                                self.xmlDiagramWriter)           
            elif qname == 'exclusiveGateway':# выходной шлюз
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.outGatewayId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), 'ExclusiveGateway')
                self.currentY = addBPMNShape(self.outGatewayId,
                          self.gatewayAxis,
                          self.gatewayAxis,
                          self.startX-self.gatewayAxis/2,
                          self.currentY,
                          self.xmlDiagramWriter)   
            else:
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
        elif qname == 'parallelTasksDescription':#спец тег для вставки описания параллельных задач
            parallelTaskNumber = self.matchingCircuit.count()
            counter = 0
            # левый угол задачи на диаграмме
            leftCorner = self.startX - (parallelTaskNumber*self.defaultTaskWidth + (parallelTaskNumber-1)*self.gatewayAxis)/2
            for matchingCircuit in self.matchingCircuit.iterate():# цикл по параллельным залдачам
                parallelTaskParser = XMLReaderFactory.createXMLReader()
                #ответственные
                assignee, candidates, groups = extractAssigneeAndCandidates(matchingCircuit.assJSON)
                #если задач нечётное количество, то центральную задачу необходимо обрабатывать отдельно
                if parallelTaskNumber % 2 == 1 and parallelTaskNumber/2 == counter:
                    isCentral = True
                else:
                    isCentral = False
                self.status.get(matchingCircuit.statusId,matchingCircuit.modelId)
                statusVal, transitionVal = getStatusAndTransitionVal(self.status, self.statusTransition)
                parallelTaskHandler = parallelTaskWriter('task' + str(matchingCircuit.id),
                                                         matchingCircuit.name,
                                                         assignee,
                                                         candidates,
                                                         groups,
                                                         'parallelGatewayIn' + str(self.parallelGatewayIn),
                                                         'parallelGatewayOut' + str(self.parallelGatewayOut),
                                                         self.xmlWriter,
                                                         self.xmlDiagramWriter,
                                                         self.startX,
                                                         self.currentY,
                                                         leftCorner,
                                                         isCentral,
                                                         statusVal,
                                                         transitionVal)
                leftCorner = leftCorner + self.defaultTaskWidth + self.gatewayAxis
                parallelTaskParser.setContentHandler(parallelTaskHandler)
                parallelTaskParser.setErrorHandler(parallelTaskHandler)
                parallelTaskParser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
                parallelTaskParser.setProperty("http://xml.org/sax/properties/lexical-handler", parallelTaskHandler)
                stream = FileInputStream(self.parallelTaskPath)
                # парсинг шаблона параллельной задачи
                parallelTaskParser.parse(InputSource(stream))  
                counter = counter + 1
            #обновление абсциссы    
            self.currentY = self.currentY + 3.5*self.gatewayAxis + self.defaultTaskHeight
            
    def endElement(self, uri, lname, qname):
        if qname != "specialTag" and qname != 'parallelTasksDescription':
            self.xmlWriter.writeEndElement()

    def characters(self, ch, start, length):
        #для первоц задачи надо изменить условие перехода
        if self.inGatewayId == 'deleteDocumentExclusivegateway':
            rep = '${deleteDocument == "false"}'
            pattern = list('${orderApproved == "true"}')
            flag = True
            if len(pattern) == length:
                for i in range(length):
                    if ch[start+i] != pattern[i]:
                        flag = False
            else:
                flag = False
            if flag:
                self.xmlWriter.writeCharacters(rep, 0, len(rep))
            else:
                self.xmlWriter.writeCharacters(ch, start, length)
        else:
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
    u'''SAX-parser для одной параллельной задачи'''
    def __init__(self,taskId,taskName, assignee, candidates,groups,
                 flowIn,flowOut,xmlWriter, xmlDiagramWriter,
                  startX, currentY, leftCorner, isCentral,
                  statusVal, transitionVal):
        #идентификатор входного и выходного шлюза
        self.flowIn = flowIn
        self.flowOut = flowOut
        # идентификатор и имя задачи
        self.taskId = taskId
        self.taskName = taskName
        # ответственные
        self.assignee = assignee
        self.xmlWriter = xmlWriter
        self.candidates = candidates
        self.groups = groups
        # параметры диаграммы
        self.startX = startX
        self.currentY = currentY
        self.leftCorner = leftCorner
        self.defaultStartEndDiametr = 35
        self.gatewayAxis = 40
        self.defaultTaskHeight = 55
        self.defaultTaskWidth = 300
        self.defaultFlowLength = 75
        self.isCentral = isCentral
        self.xmlDiagramWriter = xmlDiagramWriter
        #Идентификтаор статуса задачи
        self.statusVal = statusVal
        self.transtionVal = transitionVal

    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != "specialTag":#специальные тег не пишем
            self.xmlWriter.writeStartElement(qname)
            if qname == 'userTask': # задача              
                for i in range(0, attrs.getLength()):
                    if attrs.getQName(i) == 'id':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                    if attrs.getQName(i) == 'name':
                        self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskName)
                    if attrs.getQName(i) == 'activiti:assignee':
                        if self.assignee != '':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.assignee)
                    if attrs.getQName(i) == 'activiti:candidateUsers':
                        if self.candidates != '':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.candidates)
                    if attrs.getQName(i) == 'activiti:candidateGroups':
                        if self.groups != '':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.groups)
                addBPMNShape(self.taskId,
                          self.defaultTaskHeight,
                          self.defaultTaskWidth,
                          self.leftCorner,
                          self.currentY+self.gatewayAxis*1.5,
                          self.xmlDiagramWriter)
            elif qname == 'sequenceFlow':# входное ребро
                id = attrs.getValue('id')
                if id == 'flowIn':
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowIn+self.taskId+'parallelTask')
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowIn)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                    if self.isCentral:
                        addBPMNEdge(self.flowIn+self.taskId+'parallelTask',
                                     [(self.startX, self.currentY),
                                      (self.leftCorner+self.defaultTaskWidth/2,self.currentY + 2*self.gatewayAxis)],
                                     self.xmlDiagramWriter)  
                    else:
                        addBPMNEdge(self.flowIn+self.taskId+'parallelTask',
                                     [(self.startX - self.gatewayAxis/2, self.currentY - self.gatewayAxis/2),
                                     (self.leftCorner+self.defaultTaskWidth/2, self.currentY - self.gatewayAxis/2),
                                     (self.leftCorner+self.defaultTaskWidth/2,self.currentY + 2*self.gatewayAxis)],
                                     self.xmlDiagramWriter)   
                elif id == 'flowOut':# выходное ребро
                    for i in range(0, attrs.getLength()):
                        if attrs.getQName(i) == 'id':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowOut+self.taskId+'parallelTask')
                        if attrs.getQName(i) == 'sourceRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.taskId)
                        if attrs.getQName(i) == 'targetRef':
                            self.xmlWriter.writeAttribute(attrs.getQName(i), self.flowOut)
                    if self.isCentral:
                        addBPMNEdge(self.flowOut+self.taskId+'parallelTask',
                                     [(self.leftCorner+self.defaultTaskWidth/2, self.currentY + 2*self.gatewayAxis + self.defaultTaskHeight),
                    
                                      (self.startX, self.currentY + self.defaultTaskHeight + 3*self.gatewayAxis)],
                                     self.xmlDiagramWriter)                           
                    else:
                        addBPMNEdge(self.flowOut+self.taskId+'parallelTask',
                                     [(self.leftCorner+self.defaultTaskWidth/2, self.currentY + 2*self.gatewayAxis + self.defaultTaskHeight),
                                      (self.leftCorner+self.defaultTaskWidth/2, self.currentY + self.defaultTaskHeight + 3.5*self.gatewayAxis),
                                      (self.startX - self.gatewayAxis/2, self.currentY + self.defaultTaskHeight + 3.5*self.gatewayAxis)],
                                     self.xmlDiagramWriter)                                            
            else:
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))


    def endElement(self, uri, lname, qname):
        if qname != "specialTag":
            self.xmlWriter.writeEndElement()

    def characters(self, ch, start, length):
        u'''Надо подставить значение статуса'''
        rep = "task.setVariableLocal('status', '%s')" % self.statusVal
        pattern = list('task.setVariableLocal("status", "createStatus")')
        statusFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
        rep = "task.setVariableLocal('transitions', '%s')" % self.transtionVal
        pattern = list('task.setVariableLocal("transitions", "createTransitions")')
        transitionFlag = findAndReplacePattern(ch,start,length,rep,pattern,self.xmlWriter)
        if not statusFlag and not transitionFlag:
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
        
        
class diagramWriter(DefaultHandler2):
    u'''SAX-parser для описания диаграммы процесса'''
    def __init__(self,xmlWriter):
        self.xmlWriter = xmlWriter


    def startElement(self, namespaceURI, lname, qname, attrs):
        if qname != 'specialTag':# специальный тег не пишем
            self.xmlWriter.writeStartElement(qname)
            for i in range(0, attrs.getLength()):
                self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))


    def endElement(self, uri, lname, qname):
        if qname != 'specialTag':
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
