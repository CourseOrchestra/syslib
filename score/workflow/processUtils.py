# coding: utf-8

'''
Created on 30.09.2014

@author: a.vasilev
'''
import base64
import array
import re, os
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
from java.lang import String
from java.io import ByteArrayInputStream
from org.activiti.engine.impl.util.io import InputStreamSource
from org.activiti.engine.impl.util.io import StreamSource
import simplejson as json
from ru.curs.celesta.syscursors import UserRolesCursor
from common.sysfunctions import tableCursorImport
from common.grainssettings import SettingsManager


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
        self.formService = self.processEngine.getFormService()
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
#             xif = XMLInputFactory.newInstance()
#             xin = InputStreamReader(self.getProcessXml(key, vernum))
#             xtr = xif.createXMLStreamReader(xin)
            stream = self.getProcessXml(key, vernum)
            xmlSource = InputStreamSource(stream)
            model = BpmnXMLConverter().convertToBpmnModel(xmlSource, False, False, String('UTF-8'))
#             model = BpmnXMLConverter().convertToBpmnModel(xtr)
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
#             xif = XMLInputFactory.newInstance()
#             xin = InputStreamReader(self.getProcessXml(key, vernum))
#             xtr = xif.createXMLStreamReader(xin)
#             model = BpmnXMLConverter().convertToBpmnModel(xtr)
            stream = self.getProcessXml(key, vernum)
            xmlSource = InputStreamSource(stream)
            model = BpmnXMLConverter().convertToBpmnModel(xmlSource, False, False, String('UTF-8'))
            self.repositoryService.validateProcess(model)
            BpmnAutoLayout(model).execute()
        # actuals = self.runtimeService.createExecutionQuery().processInstanceId(processInstance.getId()).singleResult()
        generator = self.conf.getProcessDiagramGenerator()
        definitionImageStream = generator.generateDiagram(model, "png", self.runtimeService.getActiveActivityIds(processInstance.getProcessInstanceId()))
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

def setVariablesInLink(activiti, processId, taskId, link):
    pattern = '\$\[\w+\]'
    params = re.compile(pattern)
    variables = activiti.runtimeService.createProcessInstanceQuery()\
                    .processInstanceId(processId).includeProcessVariables().singleResult().getProcessVariables()
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
        link = link.replace(key, unicode(replaceDict[key]))
    return link

def parse_json(context):
    settingsManager = SettingsManager()
    content = {"default":{},
               "manual":{},
               "specialFunction":{}
               }
    defaultNamesList = settingsManager.getGrainSettings('datapanelSettings/default/parameter/@name','workflow')
    defaultValuesList = settingsManager.getGrainSettings('datapanelSettings/default/parameter/@value','workflow')
    for i in range(len(defaultNamesList)):
        content["default"][defaultNamesList[i]] = defaultValuesList[i]
    manualNamesList = settingsManager.getGrainSettings('datapanelSettings/manual/parameter/@name','workflow')
    manualValuesList = settingsManager.getGrainSettings('datapanelSettings/manual/parameter/@value','workflow')
    for i in range(len(manualNamesList)):
        content["manual"][manualNamesList[i]] = manualValuesList[i]
    specNamesList = settingsManager.getGrainSettings('datapanelSettings/specialFunction/parameter/@name','workflow')
    specValuesList = settingsManager.getGrainSettings('datapanelSettings/specialFunction/parameter/@value','workflow')
    for i in range(len(specNamesList)):
        content["specialFunction"][specNamesList[i]] = specValuesList[i]
    return content

def functionImport(functionName):
    u'''импортирует функцию по ее адресу в строке'''
    mod = __import__(functionName.split('.')[0])
    components = functionName.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def listFormAccess(userId):
    u'''из userId выдает список доступных пользователю форм'''
    activiti = ActivitiObject()
    permitsList = []
    tasks = activiti.historyService.createHistoricTaskInstanceQuery().taskAssignee(userId).list()
    for task in tasks:
        if task.getFormKey() is not None:
            permitsList.append({"procId": task.getProcessInstanceId(),
                                "formId": task.getFormKey(),
                                "accessType": "write" if task.getEndTime() is None else "read"})
    return permitsList

def checkFormAccess(userId, processInstanceId, formId):
    u'''проверяет доступность формы пользователю'''
    activiti = ActivitiObject()
    tasks = activiti.historyService.createHistoricTaskInstanceQuery()\
                .taskAssignee(userId).processInstanceId(processInstanceId).list()
    result = 'deny'
    for task in tasks:
        if task.getFormKey() == formId:
            if task.getEndTime() is None:
                result = 'write'
                break
            else:
                result = 'read'
    return result

def getUserGroups(context, sid):
    u'''функция, которая возвращает список групп, в которые входит пользователь'''
    rolesList = []
    infoDictList = [{"tableName": "UserRoles",  # имя таблицы, из которой берется список групп
                     "grainName": "celesta",  # имя гранулы, из которой берется список групп
                     "userField": "userid",  # название поля, в котором находится id пользователя
                     "roleField": "roleid"  # название поля, в котором находится id группы пользователя
                     },
                    ]
#     для добавления таблицы, из которой дополнительно будут браться группы пользователя,
#     добавить в infoDictList словарь вида {"tableName": "...",
#                                           "grainName": "...",
#                                           "userField": "...",
#                                           "roleField": "..."
#                                           }
#     в котором вместо многоточий подставить соответствующие данные добавляемой таблицы
    for infoDict in infoDictList:
        if infoDict['grainName'] != 'celesta':
            userRoles = tableCursorImport(infoDict["grainName"], infoDict["tableName"])(context)
        else:
            from ru.curs.celesta.syscursors import UserRolesCursor
            userRoles = UserRolesCursor(context)
        userRoles.setRange(infoDict["userField"], sid)

        if userRoles.tryFirst():
            while True:
                rolesList.append(getattr(userRoles, infoDict["roleField"]))
                if not userRoles.next():
                    break
    return rolesList

def getUserName(context, sid):
    u'''фукнция, возвращающая имя пользователя из его логина'''
    grainName = 'security'  # имя гранулы, в которой находится таблица пользователей
    tableName = 'logins'  # имя таблицы пользователей
    sidField = 'subjectId'
    nameField = 'userName'  # поле таблицы пользователей, в котором находится имя пользователя

    users = tableCursorImport(grainName, tableName)(context)
    users.setRange(sidField, sid)
    if users.tryFirst():
        return getattr(users, nameField)
    else:
        return u'Пользователь не найден'
    
def getGroupUsers(context,groupId):
    userList = [] 
    infoDictList = [{"tableName": "UserRoles",  # имя таблицы, из которой берется список групп
                     "grainName": "celesta",  # имя гранулы, из которой берется список групп
                     "userField": "userid",  # название поля, в котором находится id пользователя
                     "roleField": "roleid"  # название поля, в котором находится id группы пользователя
                     },
                    ]
    for infoDict in infoDictList:
        if infoDict['grainName'] != 'celesta':
            userRoles = tableCursorImport(infoDict["grainName"], infoDict["tableName"])(context)
        else:
            from ru.curs.celesta.syscursors import UserRolesCursor
            userRoles = UserRolesCursor(context)
        userRoles.setRange(infoDict["roleField"], groupId)

        if userRoles.tryFirst():
            while True:
                userList.append(getattr(userRoles, infoDict["userField"]))
                if not userRoles.next():
                    break
    return userList
    
def getLinkPermisson(context,sid,mode,processKey,processId,taskId):
    userRoles = UserRolesCursor(context)
    userRoles.setRange('userid',sid)
    isUser = False
    if userRoles.tryFirst():
        while True:
            if userRoles.roleid == 'workflowDev':
                return True
            if userRoles.roleid == 'workflowUser':
                isUser = True            
            if not userRoles.next():
                break

    if isUser:
        activiti = ActivitiObject()
        if mode == 'processImage':
            return False
        elif mode == 'process':
            return False
        elif mode == 'table':
            return False
        elif mode == 'instanceImage':
            filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'datapanelSettings.json')
            datapanelSettings = parse_json(context)["specialFunction"]["getUserGroups"]
            getUserGroups = functionImport('.'.join([x for x in datapanelSettings.split('.') if x != 'celesta']))
            groupsList = getUserGroups(context,sid)
        #     задачи, у которых кандидат - группа, в которую входит текущий пользователь
            if groupsList != []:
                groupTasksList = activiti.taskService.createTaskQuery().taskCandidateGroupIn(groupsList).processInstanceId(processId).list()
            else:
                groupTasksList = []
            userTasksList = activiti.taskService.createTaskQuery().taskCandidateOrAssigned(sid).processInstanceId(processId).list()
            if len(userTasksList) == 0 and len(groupTasksList) == 0:
                return False
            else:
                return True
        elif mode == 'task':
            userTasksList = activiti.taskService.createTaskQuery().taskAssignee(sid).processInstanceId(processId).list()
            for task in userTasksList:
                if taskId == task.getId():
                    return True
            return False
            
