# coding: utf-8

'''
Created on 01.03.2014

@author: Kuzmin
'''

import os
import simplejson as json
import ru.curs.celesta.Celesta as Celesta
import ru.curs.celesta.ConnectionPool as ConnectionPool
import ru.curs.celesta.CallContext as CallContext

from common.dbutils import DataBaseXMLExchange
from java.io import FileOutputStream, FileInputStream

from common.xmlutils import XMLJSONConverter
from common import navigator
from dirusing.multilevelnav import getFoldersList,getDirJson,fillLevel,fillDir
from dirusing.showgrains import showGrains
from dirusing.commonfunctions import relatedTableCursorImport




def navDirU(context, session):
    u'''Функция построения навигатора dirusing '''
    
    jsonnav = {"group":{"@id":'test2', "@name":'Гранулы и справочники', "level1":[]}}
    # Вытаскиваем гранулы
    score = context.getCelesta().getScore()
    grains = score.getGrains()
    # Проходим по гранулам и заносим их в структуру навигатора
    x=-1
    for grain in sorted(grains):
        # проверка файла showgrains.json
        try:
            # проверка нужно ли обрабатывать данную гранулу как справочник
            if grain in showGrains():
                # определение порядкового номера гранулы для вставки кусков навигатора внутрь
                x+=1
                grainMeta = score.getGrain(grain)
                try:
                    grainName = json.loads(grainMeta.getCelestaDoc())["name"]
                except:
                    grainName = grain
                jsonnav["group"]["level1"].append({"@id":'g' + grain, "@name": grainName})
                
                tables = grainMeta.getTables()
                # список таблиц для определения ID папки
                tableList = []
                coreTables = []
                for table in tables:
                    if relatedTableCursorImport(grain,table)(context).canRead():
                        try:
                            # заполнение массива элементов типа [таблица,ID,имя таблицы]
                            parentFolder = json.loads(grainMeta.getTable(table).getCelestaDoc())["folderId"]
                            tableName = json.loads(grainMeta.getTable(table).getCelestaDoc())["name"]
                            tableList.append([table, parentFolder, tableName])
                            if parentFolder =="":
                                coreTables.append([table,tableName])
                        except TypeError:
                            continue
                try:
                    grainJsn = json.loads(grainMeta.getCelestaDoc())
                    # проходим по элементам и заполняем уровни
                    z=[]
                    fillLevel(context,jsonnav["group"]["level1"][x],2,"",grainJsn,tableList,grain,z)               
                except TypeError:
                    continue
                # Проверка и заполнение справочников вне папок
                if coreTables:
                    for coreTable in coreTables:
                        fillDir(context,jsonnav["group"]["level1"][x],2,coreTable[0],grain,coreTable[1])
        except json.scanner.JSONDecodeError:
            
            jsonnav = {"group":None}
            pass
    return jsonnav

navigator.navigatorsParts['2'] = navDirU




