#coding:utf-8

# from ru.curs.celesta import Celesta
# from ru.curs.celesta import ConnectionPool
# from ru.curs.celesta import CallContext
# from ru.curs.celesta import SessionContext
# import sys
# 
# Celesta.getDebugInstance()
# conn = ConnectionPool.get()
# sesContext = SessionContext('super', 'testsession')
# context = CallContext(conn, sesContext)

# sys.modules['initcontext'] = lambda: context
# 
# u = __import__('ru.curs.celesta.syscursors',globals(),locals(),"UserRolesCursor",-1)
# 
# userroles = u.UserRolesCursor(context)
# 
# print userroles.count()
# from workflow.tables.tablesInit import exportTables
# 
# try:
#     exportTables(context) #Тут вы вызываете то, что хотите отдладить пошагово!
# except:
#     conn.rollback()
#     raise
# finally:
#     #ВСЕГДА ЗАКРЫВАЕМ КУРСОРЫ!!
#     context.closeCursors()
#     #ВСЕГДА ВОЗВРАЩАЕМ СОЕДИНЕНИЕ В ПУЛ!!
#     ConnectionPool.putBack(conn)

# Celesta.getDebugInstance()

from ru.curs.celesta import Celesta
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext
import sys
import java.io.OutputStreamWriter as OutputStreamWriter
import java.io.InputStreamReader as InputStreamReader
import java.io.BufferedReader as BufferedReader

Celesta.getDebugInstance()
conn = ConnectionPool.get()
sesContext = SessionContext('super', 'testsession')
context = CallContext(conn, sesContext)
  
sys.modules['initcontext'] = lambda: context

# from workflow.processUtils import ActivitiObject

from workflow._workflow_orm import act_task_linksCursor, act_ru_identitylinkCursor, act_ge_bytearrayCursor


                     #например, "hello, blob field!"

# ident = act_ru_identitylinkCursor(context)
# tskLinks = act_task_linksCursor(context)
# 
# linkDict = dict()

# for link in ident.iterate():
#     if link.task_id_ is not None:
#         user = None
#         group = None
#         if link.user_id_ is not None:
#             user = link.user_id_
#         if link.group_id_ is not None:
#             group = link.group_id_
#         
#         if link.task_id_ not in linkDict:
#             linkDict[link.task_id_] = {'users':[],'groups':[]}
#         if user is None:
#             linkDict[link.task_id_]['groups'].append("'" + group + "'")
#         else:
#             linkDict[link.task_id_]['users'].append("'" + user + "'")
#          
# for link in linkDict:
#     if not tskLinks.tryGet(link):
#         tskLinks.task_id_ = link
#         tskLinks.users = ','.join(linkDict[link]['users'])
#         tskLinks.groups = ','.join(linkDict[link]['groups'])
#         tskLinks.insert()         
 
# activiti = ActivitiObject()
#  
# variableMap = {         "initializeFrom": 'fder',
#                         "initiator": 'admin',
#                         "docId":'sdfg',
#                         "processDefinitionName":u"Тестовый процесс",
#                         "processDefinitionKey":"testProcess",
#                         "processDescription": 'sdfg',
#                         "docName":{"id1": u"переход в ed"},
#                         "docRef": {"id1": "sdfg"},
#                         "statusModel": "request", 
#                         "status": "new",
#                         "cfo":u'ЦФО',
#                         "period":u'Период',
#                         "scenario":u'Сценарий',
#                         "org":u'орг',
#                         "form":u'form',
#                         "groupToFill":"groupToFill",
#                         "peo":u"admin",
#                         "groupToChech":u"grToC",}
# for i in range(10000):
#     process = activiti.runtimeService.startProcessInstanceByKey('testProcess', variableMap)
#     print process
    
context.closeCursors()
#ВСЕГДА ВОЗВРАЩАЕМ СОЕДИНЕНИЕ В ПУЛ!!
ConnectionPool.putBack(conn)

# from workflow.processUtils import ActivitiObject
# 
# activiti = ActivitiObject()
#  
# groupTaskList = activiti.taskService.createNativeTaskQuery()\
#                         .sql("""select *
#                                     from "act_ru_task"
#                                     limit 2
#                                     offset 1""" ).list()
#  
# for task in groupTaskList:
#     print task.getIdentityLinks()




# import time
#   
#   
# conn = ConnectionPool.get()
# sesContext = SessionContext('admin', 'testsession')
# context = CallContext(conn, sesContext)
#   
# from workflow.grid.allActiveTasksGrid import getData
#   
# main = u'current'
# add = None
# filterinfo = u''
# session = u'{"sessioncontext":{"sid":"admin","userdata":"default","phone":"","username":"admin","fullusername":"admin","email":"","login":"admin","currentDatapanelWidth":"1166","currentDatapanelHeight":"727","sessionid":"0DA8A8464EAAAD528CDAAC4B716EC7AC","related":{"xformsContext":{"partialUpdate":"false","@id":"tasksFilter"}},"ip":"127.0.0.1"}}'
# elementId = u'tasksGrid'
# sortColumnList = []
# firstrecord = 1
# pagesize = 30
#   
# start = time.clock()
#   
# print getData(context, main, add, filterinfo, session, elementId, sortColumnList, firstrecord, pagesize) 
#   
# finish = time.clock() - start
#   
# print 'totalTime:', finish
