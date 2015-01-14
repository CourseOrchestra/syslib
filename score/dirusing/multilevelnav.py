# coding: utf-8
'''
Created on 01.03.2014

@author: Kuzmin
'''
import simplejson as json

def getFoldersList(grainJsn,folderLevel):
    u'''Функция для получения сортированного списка папок для отрисовки определенного уровня навигатора'''
    folderList = []
    if grainJsn:
        if not folderLevel:
            for folder in sorted(grainJsn.iteritems()):
                if len(folder[0].split("."))==1:
                    folderList.append(folder)
        else:
            for folder in sorted(grainJsn.iteritems()):
                if folder[0].startswith(folderLevel) and folder[0].count(".")==(folderLevel.count(".")+1):
                    folderList.append(folder)
    return folderList

def getDirJson(context,grain,dirId,dirName):
    u'''Функция заполнения части навигатора'''
    main = u'{"grain":"%s","table":"%s"}' % (grain,dirId)
    table_jsn = json.loads(context.getCelesta().getScore().getGrain(grain).getTable(dirId).getCelestaDoc())
    isHierarchical=table_jsn['isHierarchical']
    if isHierarchical=='true':
        dirAction = {"main_context": main,
                 "datapanel":
                    {"@type": "dirusing.datapanel.dirusing.datapanelHierarchical.celesta", "@tab": "firstOrCurrent"}
                }
        dirJson = {"@id": dirId, "@name": dirName, "action": dirAction}
    else:
        dirAction = {"main_context": main,
                 "datapanel":
                    {"@type": "dirusing.datapanel.dirusing.datapanel.celesta", "@tab": "firstOrCurrent"}
                }
        dirJson = {"@id": dirId, "@name": dirName, "action": dirAction}
    return dirJson

def fillDir(context,levelJson,levelNumber,dirId,grain,dirName):
    u'''Функция добавления справочника в определенную папку ''' 
    level = "level%s"%levelNumber
    if dirId:
        try:
            dirJson = getDirJson(context,grain,dirId,dirName)
            levelJson[level].append(dirJson)
        except KeyError:
            levelJson[level]=[]
            levelJson[level].append(dirJson) 

def fillLevel(context,levelJson,levelNumber,parentLevel,grainJsn,tableList,grain,z):
    u'''Функция заполнения одного уровня навигатора '''
    level = "level%s"%levelNumber
    foldersList = getFoldersList(grainJsn,parentLevel)
    x=0
    for i,folder in enumerate(foldersList):
        folderId = folder[0]
        if folderId=="name": continue
        folderName = folder[1]
        if parentLevel == "" or (folderId.startswith(parentLevel) and folderId.count(".")==(parentLevel.count(".")+1)):
            try:
                levelJson[level].append({"@id":grain+folderId, "@name": folderName})
            except KeyError:
                levelJson[level]=[]
                levelJson[level].append({"@id":grain+folderId, "@name": folderName})
            #проверка на пустой/непустой лист для записи справочников по папкам
            if tableList:
                for sprav in tableList:
                    if sprav[1]==folderId:
                        print folderId, grain, sprav[2]
                        print levelJson[level]
                        if len(folderId)>2:
                            if folderId[:-2] in z:
                                x=z.count(folderId[:-2])
                        fillDir(context,levelJson[level][i+x],levelNumber+1,sprav[0],grain,sprav[2])
                        z.append(folderId)
            fillLevel(context,levelJson[level][i],levelNumber+1,folderId,grainJsn,tableList,grain,z)


