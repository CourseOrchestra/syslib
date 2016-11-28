from common.navigator import navigatorsParts, seriesNavigator
from common.htmlhints.htmlHintsInit import permInit
import initcontext

context = initcontext()
permInit(context)
navigatorsParts['numberSeries'] = seriesNavigator
