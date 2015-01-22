#coding:utf-8

from common.navigator import navigatorsParts

from common.grainssettings import SettingsManager

from workflow.navigator import manageProcessesNav, navSettings, testNavigator

from workflow.xforms.addMatcher import matchingCircuitPreInsert

from workflow.tables.tablesInit import initTables

from . import _workflow_orm





navigatorsParts['54'] = manageProcessesNav
#navigatorsParts['55'] = testNavigator
navigatorsParts['__header__'] = navSettings
from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext

#Заполнение таблиц начальными данными, производится только в случае первого разворачивания решения
initTables()

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

except:
    pass




_workflow_orm.matchingCircuitCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.matchingCircuitCursor.onPreUpdate.append(matchingCircuitPreInsert)

_workflow_orm.groupsCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.groupsCursor.onPreUpdate.append(matchingCircuitPreInsert)