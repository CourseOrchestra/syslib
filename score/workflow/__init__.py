#coding : utf-8

from common.navigator import navigatorsParts
from workflow.navigator import manageProcessesNav, navSettings, testNavigator

navigatorsParts['54'] = manageProcessesNav
navigatorsParts['55'] = testNavigator
navigatorsParts['__header__'] = navSettings
