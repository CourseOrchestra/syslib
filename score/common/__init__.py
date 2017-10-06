# coding=utf-8
from common.navigator import navigatorsParts, seriesNavigator

globalCelesta = None

isInitContext = True
try:
    import initcontext
except ImportError:
    isInitContext = False

if isInitContext:
    context = initcontext()
    globalCelesta = context.getCelesta()

    from common.htmlhints.htmlHintsInit import permInit

    if not isinstance(context, (str, unicode)):
        permInit(context)

navigatorsParts['numberSeries'] = seriesNavigator
