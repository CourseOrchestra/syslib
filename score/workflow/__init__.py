#coding : utf-8

from common.navigator import navigatorsParts
from workflow.navigator import manageProcessesNav, navSettings, testNavigator

from workflow.xforms.addMatcher import matchingCircuitPreInsert

from workflow.tables.tablesInit import initTables

from . import _workflow_orm


navigatorsParts['54'] = manageProcessesNav
#navigatorsParts['55'] = testNavigator
navigatorsParts['__header__'] = navSettings

initTables()

_workflow_orm.matchingCircuitCursor.onPreInsert.append(matchingCircuitPreInsert)
_workflow_orm.matchingCircuitCursor.onPreUpdate.append(matchingCircuitPreInsert)