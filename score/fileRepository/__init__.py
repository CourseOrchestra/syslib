# coding: utf-8

import initcontext
from common.navigator import navigatorsParts
from fileRepository.numbersSeries.tablesInit import initTables
from fileRepository.navigator import navigatorFileRepository
from functions import clusterInit
from common.grainssettings import SettingsManager

navigatorsParts['navigatorFileRepository'] = navigatorFileRepository

context = initcontext()
try:
    grains_settings_XML = SettingsManager(context)
    clusterInit(context)
    if grains_settings_XML.getGrainSettings("frSettings/parameter[@name='isSystemInitialised']/@value", 'fileRepository')[0] == u'false':    
        from fileInit import fileInit
        fileInit(context)    
        grains_settings_XML.setGrainSettings("frSettings/parameter[@name='isSystemInitialised']/@value", 'true', 'fileRepository') 
except IndexError:
    print('File repository is not initialized')
    
initTables(context)

    
