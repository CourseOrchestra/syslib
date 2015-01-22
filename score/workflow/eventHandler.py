#coding:utf-8

from java.lang import Class
from java.sql import Connection, SQLException, DriverManager
from ru.curs.showcase.runtime import ConnectionFactory,AppInfoSingleton
from com.ziclix.python.sql import zxJDBC,PyConnection
from ru.curs.showcase.core.jython import JythonProc;

    
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
            
def taskAssignedHandler(context,event):
    u'''Функция обработки события назначения ответственного на задачу'''
    entity = event.getEntity()
    act = ActivitiObject()
    #Получение идентификатора экземпляра процесса из события
    processDefId = event.getProcessDefinitionId()
    processInstanceId = event.getProcessInstanceId()
    initializeFrom = act.runtimeService.getVariable(processInstanceId,'initializeFrom')
    processDef = act.repositoryService.createProcessDefinitionQuery().processDefinitionId(processDefId).singleResult()
    processKey = processDef.getKey()
    #Версия обновляется только для процесса согласования документа
    if initializeFrom == 'order' or initializeFrom == 'curriculum':
        
        sid = entity.getAssignee()
        message = u'Назначена задача '+entity.getName()
        params = u'<params> <link href="?userdata=workflow">Управление потоками работы</link></params>'
        pyConn = ConnectionFactory.getPyConnection()
        pyConn.autocommit = True
        #createProcessInstanceQuery().processInstanceId(processInstanceId).includeProcessVariables().singleResult()    
        try:
            cur = pyConn.cursor()
            try:
#                 cur.executemany("""update "testTable"
#                                         set "orderVersion"=?
#                                             where "ordersId"=?""", [(docVersion,docId)])
                cur.executemany("""declare @NotificationId uniqueidentifier = newId();
declare @InitiatorSid uniqueidentifier  = '8E495882-569B-45FE-97C4-9D7F68CCCBA5';
declare @sid uniqueidentifier = '8E495882-569B-45FE-97C4-9D7F68CCCBA5';
declare @MessageDate datetime = getdate();

exec dbo.CreateNotification @NotificationId,?,@InitiatorSid,@MessageDate,?,0,'02C0B79F-5614-4FED-8199-C6C42AFCF836',
'CC50B89B-2EF8-40ED-976E-9309CB1162D3','workflow',?,
        '','', '';""", [(sid,message,params)])
                print 'qwe'
            except:     
                print 'asd'
        finally:
            cur.close()

            

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