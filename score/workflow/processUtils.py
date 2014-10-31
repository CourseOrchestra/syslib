# coding: utf-8

'''
Created on 30.09.2014

@author: a.vasilev
'''
import base64
import array
import re
try:
    from ru.curs.showcase.activiti import EngineFactory
except:
    from workflow import testConfig as EngineFactory

import javax.xml.stream.XMLInputFactory as XMLInputFactory
import java.io.InputStreamReader as InputStreamReader
import org.activiti.engine.ProcessEngineConfiguration as ProcessEngineConfiguration
import org.activiti.bpmn.BpmnAutoLayout as BpmnAutoLayout
import org.activiti.bpmn.converter.BpmnXMLConverter as BpmnXMLConverter
import org.activiti.image.ProcessDiagramGenerator as ProcessDiagramGenerator


class ActivitiObject():
    def __init__(self):
        # получение запущенного движка Activiti и необходимых сервисов
        self.processEngine = EngineFactory.getActivitiProcessEngine()
        self.conf = self.processEngine.getProcessEngineConfiguration()
        self.repositoryService = self.processEngine.getRepositoryService()
        self.historyService = self.processEngine.getHistoryService()
        self.runtimeService = self.processEngine.getRuntimeService()
        self.identityService = self.processEngine.getIdentityService()
        self.taskService = self.processEngine.getTaskService()
    def getActualVersionOfProcesses(self):
        u'''Функция получения списка всех развернутых процессов'''
        return self.repositoryService.createProcessDefinitionQuery().orderByProcessDefinitionName(). \
            asc().latestVersion().list()

    def getHistory(self):
        u'''Функция получения списка всех ранее запущенных процессов процессов'''
        processInstanceList = self.historyService.createHistoricProcessInstanceQuery().orderByProcessInstanceEndTime().asc().list()
        return processInstanceList

    def getProcessVersionsByKey(self, key, sort='asc'):
        u'''Функция получения списка всех версий определенного развернутого процесса по ключу'''
        actuals = getattr(self.repositoryService.createProcessDefinitionQuery().processDefinitionKey(key).orderByProcessDefinitionVersion(), sort)().list()
        return actuals

    def getProcessDefinition(self, key, vernum=None):
        u'''Функция выбора конкретной версии процесса по ключу'''
        actuals = self.repositoryService.createProcessDefinitionQuery().processDefinitionKey(key)
        if vernum is None:
            selectedProcess = actuals.latestVersion().singleResult()
        else:
            selectedProcess = actuals.processDefinitionVersion(vernum).singleResult()

        return selectedProcess

    def getProcessDefinitionById(self, id):
        u'''Функция выбора процесса по id'''
        actuals = self.repositoryService.createProcessDefinitionQuery().processDefinitionId(id).singleResult()

        return actuals

    def getProcessXml(self, key, vernum=None):
        selectedProcess = self.getProcessDefinition(key, vernum)
        if selectedProcess :
            return self.repositoryService.getResourceAsStream(selectedProcess.getDeploymentId(), selectedProcess.getResourceName())
        else:
            return None

    def getProcessXmlById(self, id):
        selectedProcess = self.getProcessDefinitionById(id)
        if selectedProcess :
            return self.repositoryService.getResourceAsStream(selectedProcess.getDeploymentId(), selectedProcess.getResourceName())
        else:
            return None

    def getDeployedProcessModel(self, key, vernum=None):
        u'''картинка развёрнутого процесса'''
        processDefinition = self.getProcessDefinition(key, vernum)
        if processDefinition.getDiagramResourceName():
            diagramResourceName = processDefinition.getDiagramResourceName()
            imageStream = self.repositoryService.getResourceAsStream(processDefinition.getDeploymentId(), diagramResourceName)
        else:
            xif = XMLInputFactory.newInstance()
            xin = InputStreamReader(self.getProcessXml(key, vernum))
            xtr = xif.createXMLStreamReader(xin)
            model = BpmnXMLConverter().convertToBpmnModel(xtr)
            self.repositoryService.validateProcess(model)
            BpmnAutoLayout(model).execute()
            generator = self.conf.getProcessDiagramGenerator()
            imageStream = generator.generatePngDiagram(model)
        return imageStream

    def getExecutionModel(self, processInstanceId, vernum=None):
        u'''картинка выполняющегося процесса с отмеченным таском'''
        processInstance = self.runtimeService.createProcessInstanceQuery()\
            .processInstanceId(processInstanceId).singleResult()
        processDefinition = self.repositoryService.createProcessDefinitionQuery()\
            .processDefinitionId(processInstance.getProcessDefinitionId()).singleResult()
        key = processDefinition.getKey()


        self.getProcessDefinitionById(key)
        if processDefinition.getDiagramResourceName():
            model = self.repositoryService.getBpmnModel(processDefinition.getId())
        else:
            xif = XMLInputFactory.newInstance()
            xin = InputStreamReader(self.getProcessXml(key, vernum))
            xtr = xif.createXMLStreamReader(xin)
            model = BpmnXMLConverter().convertToBpmnModel(xtr)
            self.repositoryService.validateProcess(model)
            BpmnAutoLayout(model).execute()
        actuals = self.runtimeService.createExecutionQuery().processInstanceId(processInstance.getId()).singleResult()
        generator = self.conf.getProcessDiagramGenerator()
        definitionImageStream = generator.generateDiagram(model, "png", self.runtimeService.getActiveActivityIds(actuals.getId()))
        return definitionImageStream

    def stopProcess(self, processId, reason='stopped manually'):
        self.runtimeService.deleteProcessInstance(processId, reason)

    def getUserTasks(self, username):  # all assigned, candidate and owner tasks
        u'''выбирает задачи, которые появились в identityLink, т.е. назначен на задание либо владеет им'''
        taskQuery = self.taskService.createTaskQuery().taskInvolvedUser(username).list()
        return taskQuery

    def getCandUserTasks(self, username):
        u'''выбирает только те задачи, у которых заданный пользователь является кандидатом на назначение'''
        taskQuery = self.taskService.createTaskQuery().taskCandidateUser(username).list()
        return taskQuery

    def getCandOrAssUserTasks(self, username):
        u'''выбирает только задачи, на которые назначен заданный пользователь или является кандидатом на назначение'''
        taskQuery = self.taskService.createTaskQuery().taskCandidateOrAssigned(username).list()
        return taskQuery

#     Deprecated ?
    def getUnassTasks(self):
        taskQuery = self.taskService.createTaskQuery().taskUnnassigned().list()
        return taskQuery

    def getUserAssTasks(self, username):
        u'''выбирает только те задачи, на которые назначен заданный пользователь'''
        taskQuery = self.taskService.createTaskQuery().taskAssignee(username).list()
        return taskQuery

    def getGroupCandTasks(self, candidateGroup):
        u'''выбирает только те задачи, кандидатами которых являются пользователи заданной группы'''
        taskQuery = self.taskService.createTaskQuery().taskCandidateGroup(candidateGroup).list()
        return taskQuery

def getBase64Image(imageStream):
    stringout = u''
    byteArray = [-1, -1, -1]
    while True:
        byteArray[0] = imageStream.read()
        byteArray[1] = imageStream.read()
        byteArray[2] = imageStream.read()
        if byteArray[0] == -1:
            break
        elif byteArray[1] == -1:
            stringout += base64.b64encode(array.array('B', byteArray[0:1]).tostring())
            break
        elif byteArray[2] == -1:
            stringout += base64.b64encode(array.array('B', byteArray[0:2]).tostring())
            break
        else:
            stringout += base64.b64encode(array.array('B', byteArray).tostring())
    return stringout

def setVariablesInLink(activiti,processId,taskId,link):
    pattern = '\$\[\w+\]'
    params = re.compile(pattern)
    variables = activiti.runtimeService.createProcessInstanceQuery().processInstanceId(processId).includeProcessVariables().singleResult().getProcessVariables()
    replaceDict = dict()
    for param in params.finditer(link):
        par = link[param.start():param.end()]
        if par == '$[processId]':
            replaceDict[par] = processId
        elif par == '$[taskId]':
            replaceDict[par] = taskId          
        else:
            if par[2:-1] in variables:
                replaceDict[par] = variables[par[2:-1]]
    for key in replaceDict:
        link = link.replace(key,replaceDict[key])
    return link
        
