#coding:utf-8

from java.lang import Class
from java.sql import Connection, SQLException, DriverManager
from ru.curs.showcase.runtime import ConnectionFactory,AppInfoSingleton
from com.ziclix.python.sql import zxJDBC,PyConnection
from ru.curs.showcase.core.jython import JythonProc;
from workflow.processUtils import ActivitiObject
import simplejson as json

from workflow._workflow_orm import act_ru_identitylinkCursor, act_task_linksCursor 
    
    
from workflow.processUtils import ActivitiObject

def taskCompleteHandler(context,event):
    u'''Функция обработки завершения задачи'''
    act = ActivitiObject()
#     processEngine = EngineFactory.getActivitiProcessEngine()
#     runtimeService = processEngine.getRuntimeService()
    #Получение ключа описания процесса и идентификатора экземпляра процесса из события
    processInstanceId = event.getProcessInstanceId()
    initializeFrom = act.runtimeService.getVariable(processInstanceId,'initializeFrom')
    processInstance = act.runtimeService.createProcessInstanceQuery().processInstanceId(processInstanceId).singleResult()
    processDefId = processInstance.getProcessDefinitionId()
    processDef = act.repositoryService.createProcessDefinitionQuery().processDefinitionId(processDefId).singleResult()
    processKey = processDef.getKey()
    #Версия обновляется только для процесса согласования документа
    if initializeFrom == 'order':
        pyConn = ConnectionFactory.getPyConnection();
        pyConn.autocommit = True
        docVersion = act.runtimeService.getVariable(processInstanceId,'documentVersion')
        docId = act.runtimeService.getVariable(processInstanceId,'docId')
        #createProcessInstanceQuery().processInstanceId(processInstanceId).includeProcessVariables().singleResult()    
        try:
            cur = pyConn.cursor()
            try:
#                 cur.executemany("""update "testTable"
#                                         set "orderVersion"=?
#                                             where "ordersId"=?""", [(docVersion,docId)])
                cur.executemany("""update [dbo].[orders]
                                        set orderVersion=?
                                            where ordersId=?""", [(docVersion,docId)])
                print 'qwe'
            except:     
                print 'asd'
        finally:
            cur.close()
    if initializeFrom == 'curriculum':
        pyConn = ConnectionFactory.getPyConnection();
        pyConn.autocommit = True
        docVersion = act.runtimeService.getVariable(processInstanceId,'documentVersion')
        docId = act.runtimeService.getVariable(processInstanceId,'docId')
        #createProcessInstanceQuery().processInstanceId(processInstanceId).includeProcessVariables().singleResult()    
        try:
            cur = pyConn.cursor()
            try:
#                 cur.executemany("""update "testTable"
#                                         set "orderVersion"=?
#                                             where "ordersId"=?""", [(docVersion,docId)])
                cur.executemany("""update [bup].[clCurriculum]
                                        set curriculumVersion=?
                                            where curriculumID=?""", [(docVersion,docId)])
                print 'qwe'
            except:     
                print 'asd'
        finally:
            cur.close()
            
def taskCreatedHandler(context,event):
    u'''Обработчик создания задачи, который пишет в базу кандидатов задачи'''
    entity = event.getEntity()
    taskId = entity.getId()
    identityLinks = entity.identityLinks
    print identityLinks
#     raise Exception(entity.identityLinks)
    #raise Exception(entity, type(entity))
    users = list()
    groups = list()
    act_task_links = act_task_linksCursor(context)
#     raise Exception(act_ru_identitylink.count())
    for link in identityLinks:
        if link.userId is not None:
            users.append("'" + link.userId + "'")
        elif link.groupId is not None:
            groups.append("'" + link.groupId + "'")
    act_task_links.task_id_ = taskId
    if users == []:
        act_task_links.users = None
    else:
        act_task_links.users = ','.join(users)
    if groups == []:
        act_task_links.groups = None
    else:
        act_task_links.groups = ','.join(groups)
    act_task_links.insert()

            

def variableHandler(context,event):
    act = ActivitiObject()
    name = event.getVariableName()
    processInstanceId = event.getProcessInstanceId()
    initializeFrom = act.runtimeService.getVariable(processInstanceId,'initializeFrom')
    processDefId = event.getProcessDefinitionId()
    processDef = act.repositoryService.createProcessDefinitionQuery().processDefinitionId(processDefId).singleResult()
    processKey = processDef.getKey()
    if name == 'processStatus':     
        statusDict = {'underConstruction': 1,
                      'onAgreement':3,
                      'rejected':4,
                      'agreed': 2,
                      'refinement':5
                      }
        status = event.getVariableValue()
        docId = act.runtimeService.getVariable(processInstanceId,'docId')
        pyConn = ConnectionFactory.getPyConnection();
        pyConn.autocommit = True
        cur = pyConn.cursor()
        try:
#             cur.executemany("""update "testTable"
#                                     set "orderStatus"=?
#                                         where "ordersId"=?""", [(statusDict[status],docId)])
            if initializeFrom == 'order':
                cur.executemany("""update [dbo].[orders]
                                        set orderStatus=?
                                            where [ordersId]=?""", [(statusDict[status],docId)])
            elif initializeFrom == 'curriculum':
                cur.executemany("""update [bup].[clCurriculum]
                                        set curriculumStatus=?
                                            where curriculumID=?""", [(statusDict[status],docId)])
            print 'qwe'
        except:     
            print 'asd'
        finally:
            cur.close()
            
            
