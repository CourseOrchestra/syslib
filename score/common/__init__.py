from common.navigator import navigatorsParts, seriesNavigator
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext
from ru.curs.celesta import Celesta
from common.htmlhints.htmlHintsInit import permInit
import initcontext

context = initcontext()
permInit(context)
navigatorsParts['96'] = seriesNavigator