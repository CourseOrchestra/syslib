# coding: utf-8

from common.grainssettings import SettingsManager
from common.navigator import navigatorsParts
from fileRepository.navigator import navigatorFileRepository
from fileRepository.numbersSeries.tablesInit import initTables
from functions import clusterInit
import initcontext


navigatorsParts['navigatorFileRepository'] = navigatorFileRepository

context = initcontext()
try:
    grains_settings_XML = SettingsManager(context)
    clusterInit(context)
    if grains_settings_XML.getGrainSettings("frSettings/parameter[@name='isSystemInitialised']/@value", 'fileRepository')[0] == u'false':
        grains_settings_XML.setGrainSettings(
            "frSettings/parameter[@name='isSystemInitialised']/@value", 'true', 'fileRepository')
except IndexError:
    print('File repository is not initialized')

initTables(context)
