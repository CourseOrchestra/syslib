# coding: utf-8
'''
Created on 28.11.2013

@author: v.popov
'''

import os
import simplejson as json
from common.grainssettings import SettingsManager
from ru.curs.celesta.showcase.utils import XMLJSONConverter

class Settings():
    u"""Класс работы с настройками гранулы security из grainSettings.xml    
    
    """
    settings=[] # Статическая переменная класса, в которую сохраняются настройки гранулы.
                # Данная реализация нужна для того, чтобы не обращаться каждый раз к расположенному на жестком диске файлу настроек
                # rainSettings.xml 
    settingsTag = 'showGrains' # Наименование тэга настроек гранулы
    grainName = 'dirusing' # название гранулы
    
    def __init__(self):        
        self.settingsInstance = SettingsManager()
        # Создаём объект класса получения настроек свойств всех гранул.
    
    def getSettingsJSON(self):
        u""" Функция получения JSON'а всех настроек гранулы
            JSON имеет вид:
            {<Имя параметра>: <значение параметра>}
        """
        if not self.settings:
            # Если переменная настроек self.settings пуста, получаем настройки из общего файла настроек grainSettings.xml
            names=self.settingsInstance.getGrainSettings("%s/grain/@name" % self.settingsTag, self.grainName)
#             settingsJson={}
#             for i in range(len(names)):
#                 settingsJson[names[i]] = values[i]
            if names and not isinstance(names, list):
                names = [names]  
            self.settings = names or []                                                                   
        return self.settings

def showGrains(context):
    u'''Функция читает файл с кортежем, в котором указано, какие гранулы отображать. '''

#     settingsObject = SettingsManager(context)
#     result = XMLJSONConverter.xmlToJson(settingsObject.getGrainSettings())['grain']['@name']
    return Settings().getSettingsJSON()

#print hideGrains()



