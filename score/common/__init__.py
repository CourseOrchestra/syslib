from common.navigator import navigatorsParts, seriesNavigator

globalCelesta = None

isInitContext = True
try:
    import initcontext
except ImportError:
    isInitContext = False

if isInitContext:
    from common.htmlhints.htmlHintsInit import permInit
    context = initcontext()
    global globalCelesta
    globalCelesta = context.getCelesta()
      
    if not isinstance(context, (str, unicode)):
        permInit(context)
    
navigatorsParts['numberSeries'] = seriesNavigator
