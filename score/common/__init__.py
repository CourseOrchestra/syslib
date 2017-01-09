from common.navigator import navigatorsParts, seriesNavigator
from common.htmlhints.htmlHintsInit import permInit
import initcontext

context = initcontext()

if not isinstance(context, (str, unicode)):
    permInit(context)
navigatorsParts['numberSeries'] = seriesNavigator
