#coding:utf-8
import initcontext

from common.navigator import navigatorsParts

from common.grainssettings import SettingsManager

from workflow.navigator import manageProcessesNav, navSettings, testNavigator

from workflow.xforms.addMatcher import matchingCircuitPreInsert

from workflow.tables.tablesInit import initTables

from . import _workflow_orm





navigatorsParts['54'] = manageProcessesNav
#navigatorsParts['55'] = testNavigator
navigatorsParts['__header__'] = navSettings


context = initcontext()
#Заполнение таблиц начальными данными, производится только в случае первого разворачивания решения
initTables(context)


#Настройка обработчиков событий activiti


try:
    
    from org.activiti.engine.delegate.event import ActivitiEventType    
    
    from ru.curs.showcase.runtime import AppInfoSingleton



    settingsManager = SettingsManager()
    
    eventsList = settingsManager.getGrainSettings('activitiEvents/event/@name','workflow')
    handlersList = settingsManager.getGrainSettings('activitiEvents/event/@script','workflow')
    
    
    for i in range(len(eventsList)):
        AppInfoSingleton.getAppInfo().\
        getActivitiEventScriptDictionary().\
        put(getattr(ActivitiEventType,eventsList[i]), handlersList[i])

except:
    pass




_workflow_orm.matchingCircuitCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.matchingCircuitCursor.onPreUpdate.append(matchingCircuitPreInsert)

_workflow_orm.groupsCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.groupsCursor.onPreUpdate.append(matchingCircuitPreInsert)