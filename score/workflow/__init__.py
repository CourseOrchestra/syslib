#coding:utf-8

from common.navigator import navigatorsParts

from common.grainssettings import settingsManager

from workflow.navigator import manageProcessesNav, navSettings, testNavigator

from workflow.xforms.addMatcher import matchingCircuitPreInsert

from workflow.tables.tablesInit import initTables

from . import _workflow_orm

from org.activiti.engine.delegate.event import ActivitiEventType



navigatorsParts['54'] = manageProcessesNav
#navigatorsParts['55'] = testNavigator
navigatorsParts['__header__'] = navSettings

#Заполнение таблиц начальными данными, производится только в случае первого разворачивания решения
initTables()

#Настройка обработчиков событий activiti

try:
    from ru.curs.showcase.runtime import AppInfoSingleton

    settingsManager = settingsManager()
    
    eventsList = settingsManager.getGrainSettings('workflow', 'activitiEvents/event/@name')
    handlersList = settingsManager.getGrainSettings('workflow','activitiEvents/event/@script')
    
    for i in range(len(eventsList)):
        AppInfoSingleton.getAppInfo().\
        getActivitiEventScriptDictionary().\
        put(getattr(ActivitiEventType,eventsList[i]), handlersList[i])

except:
    pass
_workflow_orm.matchingCircuitCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.matchingCircuitCursor.onPreUpdate.append(matchingCircuitPreInsert)