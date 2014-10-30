# coding: utf-8


#import org.junit.Assert.*

#import java.util.ArrayList
#import java.util.HashMap
#import java.util.Map
from java.io import FileInputStream
#from org.activiti.engine import HistoryService as HistoryService
#from org.activiti.engine import IdentityService as IdentityService
#from org.activiti.engine import RepositoryService as RepositoryService
#from org.activiti.engine import RuntimeService as RuntimeService
#from org.activiti.engine import TaskService as TaskService
#from org.activiti.engine.history import HistoricActivityInstance as HistoricActivityInstance
#from org.activiti.engine.repository import ProcessDefinition as ProcessDefinition
#from org.activiti.engine.runtime import ProcessInstance as ProcessInstance
#from org.activiti.engine.task import Task as Task
#from org.activiti.engine.test import ActivitiRule as ActivitiRule

import unittest
import os

from workflow.testConfig import getTestActivitiProcessEngine


class TestActivity(unittest.TestCase):
    
    filename = os.path.join(os.path.dirname(__file__), 'fp.bpmn')
    cfgPath = os.path.join(os.path.dirname(__file__), 'activiti.cfg.xml')

    def testStartProcess(self):
        self.activitiRule = getTestActivitiProcessEngine() #ActivitiRule()
        repositoryService = self.activitiRule.getRepositoryService()
        #repositoryService = RepositoryService()        
        file_instance = FileInputStream(self.filename)
        deployedService = repositoryService.createDeployment()
        deployedService.addInputStream("myProcess.bpmn20.xml", file_instance).deploy()
        runtimeService = self.activitiRule.getRuntimeService()
        #runtimeService = RuntimeService()
        variableMap={}
        variableMap["name"] = "Activiti"
        variableMap["status"] = "new"
        variableMap["docId"] = ""
        variableMap["docName"] = ""
        variableMap["initiator"] = "u1"
        variableMap["economist"] = "u3"
        variableMap["budgetHolder"] = "u2"
        
        processInstance = runtimeService.startProcessInstanceByKey("testZayavki", variableMap)
        self.assertNotEqual(processInstance.getId(), None)
        print ("id " + processInstance.getId() + " " + processInstance.getProcessDefinitionId())
        taskService = self.activitiRule.getTaskService()
        task = taskService.createTaskQuery().taskAssignee("u1").singleResult()
        self.assertEqual(task.getName(), u"Подготовить заявку")
        pD = repositoryService.createProcessDefinitionQuery().processDefinitionId(task.getProcessDefinitionId()).singleResult()
        print pD.getKey()
        
        runtimeService.setVariable(processInstance.getId(), "status", "reviewedByBudgetHolder")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u2").singleResult()
        self.assertEqual(task.getName(), u"Рассмотреть заявку")
        
        runtimeService.setVariable(processInstance.getId(), "status", "new")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u1").singleResult()
        self.assertEqual(task.getName(), u"Подготовить заявку")        
        
        runtimeService.setVariable(processInstance.getId(), "status", "reviewedByBudgetHolder")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u2").singleResult()
        self.assertEqual(task.getName(), u"Рассмотреть заявку")        

        runtimeService.setVariable(processInstance.getId(), "status", "reviewedByEconomist")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u3").singleResult()
        self.assertEqual(task.getName(), u"Определить источники финансирования")    

        runtimeService.setVariable(processInstance.getId(), "status", "reviewedByBudgetHolder")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u2").singleResult()
        self.assertEqual(task.getName(), u"Рассмотреть заявку")            

        runtimeService.setVariable(processInstance.getId(), "status", "reviewedByEconomist")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u3").singleResult()
        self.assertEqual(task.getName(), u"Определить источники финансирования")        
        
        runtimeService.setVariable(processInstance.getId(), "status", "approved")
        taskService.complete(task.getId())
        task = taskService.createTaskQuery().taskAssignee("u3").singleResult()
        self.assertEqual(task, None)
                
#        historyService = activitiRule.getHistoryService()
#        List<HistoricActivityInstance> activityList = historyService.createHistoricActivityInstanceQuery().list()
#        for (HistoricActivityInstance historicActivityInstance : activityList) {            
#            System.out.println("history activity " +
#            historicActivityInstance.getActivityName() +
#            ", type " +
#            historicActivityInstance.getActivityType() +
#            ", duration was " +
#            historicActivityInstance.getDurationInMillis())

  
if __name__ == '__main__':
    unittest.main()
        