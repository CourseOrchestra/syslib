# coding=utf-8
import os
import logging.config
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

# Запускаем логгер
# Сначала ищем настройку в celesta.properties
log_config_file = globalCelesta.getSetupProperties().getProperty('loggingconf.path')
# Если настройки нет, ищем в корне юзердаты
if not log_config_file:
    try:
        from ru.curs.showcase.runtime import AppInfoSingleton

        log_config_file = os.path.join(AppInfoSingleton.getAppInfo().getUserdataRoot(), 'logging.ini')
    except ImportError:
        pass
if log_config_file and os.path.exists(log_config_file):
    # Если нашли настройку и файл существует
    logging.config.fileConfig(log_config_file)
    log = logging.getLogger("solution")

    log.debug('logger file config - {}'.format(log_config_file))
else:
    # Иначе формат по-умолчанию
    log_format = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    logging.basicConfig(format=log_format, level=logging.NOTSET)

    formatter = logging.Formatter(log_format)

    log = logging.getLogger("solution")

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)

    log.addHandler(streamHandler)
    log.propagate = False  # Предотвращает дублирование логов

    log.debug("logger basic config")
