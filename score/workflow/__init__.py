#coding:utf-8
import initcontext

from common.navigator import navigatorsParts

from common.grainssettings import SettingsManager

from workflow.navigator import manageProcessesNav, navSettings, testNavigator

from workflow.other.triggers import matchingCircuitPreInsert

from workflow.tables.tablesInit import initTables

from . import _workflow_orm





navigatorsParts['54'] = manageProcessesNav
#navigatorsParts['55'] = testNavigator
navigatorsParts['__header__'] = navSettings


context = initcontext()
#Заполнение таблиц начальными данными, производится только в случае первого разворачивания решения
initTables(context)

#Заполнение версии активити. Необходим для коррекной работы activiti
#coding:utf-8


from workflow._workflow_orm import act_ge_propertyCursor

act_property = act_ge_propertyCursor(context)

if not act_property.tryGet('schema.version'):
    if not act_property.tryGet('schema.history'):
        if not act_property.tryGet('next.dbid'):
            act_property.name_ = 'schema.version'
            act_property.value_ = '5.16' 
            act_property.rev_ = 1
            act_property.insert()
            act_property.name_ = 'schema.history'
            act_property.value_ = 'create(5.16)' 
            act_property.rev_ = 1
            act_property.insert()
            act_property.name_ = 'next.dbid'
            act_property.value_ = '1'
            act_property.rev_ = 1
            act_property.insert()



#Настройка обработчиков событий activiti


try:
    
    from org.activiti.engine.delegate.event import ActivitiEventType    
    from java.util import ArrayList
    from ru.curs.showcase.runtime import AppInfoSingleton



    settingsManager = SettingsManager()
    
    eventsList = settingsManager.getGrainSettings('activitiEvents/event/@name','workflow')
    handlersList = settingsManager.getGrainSettings('activitiEvents/event/@script','workflow')
    
    eventsDict = dict()
    for i in range(len(eventsList)):
        if eventsList[i] not in eventsDict:
            eventsDict[eventsList[i]] = ArrayList()
        eventsDict[eventsList[i]].add(handlersList[i])
        

    if 'TASK_CREATED' not in eventsDict:
        eventsDict['TASK_CREATED'] = ArrayList()
    eventsDict['TASK_CREATED'].add('workflow.eventHandler.taskCreatedHandler.cl')
    
    for eventType in eventsDict:
        AppInfoSingleton.getAppInfo().\
        getActivitiEventScriptDictionary().\
        put(getattr(ActivitiEventType,eventType), eventsDict[eventType])
       
except:
    pass




_workflow_orm.matchingCircuitCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.matchingCircuitCursor.onPreUpdate.append(matchingCircuitPreInsert)

_workflow_orm.groupsCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.groupsCursor.onPreUpdate.append(matchingCircuitPreInsert)