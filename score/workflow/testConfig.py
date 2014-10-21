# coding: utf8
'''
Created on 26.09.2014

@author: a.vasilev
'''
from org.activiti.engine import ProcessEngineConfiguration

def getActivitiProcessEngine():
    conf = ProcessEngineConfiguration.createStandaloneProcessEngineConfiguration()
    conf.setDatabaseType("postgres")
    conf.setJdbcUrl("jdbc:postgresql://localhost:5432/activiti")
    conf.setJdbcDriver("org.postgresql.Driver")
    conf.setJdbcUsername("postgres")
    conf.setJdbcPassword("F708420Dx")

    return conf.buildProcessEngine()
