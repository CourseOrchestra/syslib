# coding: utf-8
'''
Created on 10.11.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json
import urlparse
import cgi

from common.hierarchy import generateSortValue,getNewItemInLevelInHierarchy

from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

import datetime

from common.numbersseries import getNextNo

from workflow.processUtils import ActivitiObject
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
    
from java.util import ArrayList
try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord
    
try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory
    
from workflow._workflow_orm import matchingCircuitCursor, statusCursor, processStatusModelCursor
    
from java.io import InputStream, FileInputStream
from jarray import zeros

#from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка добавления и редактирования элементов в грид согласователей процеса'''
    session = json.loads(session)
    add = json.loads(add)
    addContext = add[0]
    processKey = add[1]
    modelId = add[2]
    matchingCircuit = matchingCircuitCursor(context)
    processStatusModel = processStatusModelCursor(context)
    status = statusCursor(context)
    currentId = json.loads(session["sessioncontext"]["related"]["gridContext"]["currentRecordId"])
    assignee = ''
    users = {"@tag":"tag"}
    groups = {"@tag":"tag"}
    statusId = ''
    statusName = ''
    varName = ''
    #Фиктивный элемент верхнего уровня
    if currentId['id'] == 'top':
        parallelAlignment = 'false'
        id = ''
        name = ''
        parentId = ''
        parentName = 'Элемент верхнего уровня'
    else:
        id = currentId['id']
        matchingCircuit.get(processKey,id)
        name = matchingCircuit.name
        #Добавление внуть параллельного согласования
        if addContext == 'add':
            parentId = id
            parentName = u'Параллельное согласование'
            parallelAlignment = 'true'
            id = ''
            name = ''
        else:
            ass = json.loads(matchingCircuit.assJSON)
            statusId = matchingCircuit.statusId
            if statusId is not None:
                processStatusModel.get(processKey)
                status.get(statusId,processStatusModel.modelId)
                statusName = status.name
                varName = status.varName
            else:
                statusId = ''
            #Получение ответственного лица и списка кандидатов
            assignee = ass['assignee']
            users = {'@tag':'tag','user':[]}
            groups = {'@tag':'tag','group':[]}
            for user in ass['users']:
                users['user'].append({'name':user})
            for group in ass['groups']:
                groups['group'].append({'name':group})
            parentId = ''
            parentName = ''
            parallelAlignment = 'false'
    name = name.replace('{','\{')
    name = name.replace('}','\}')
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{
                                "@id":id,
                                "@name":name,
                                "@parentName": parentName,
                                "@parentId" : parentId,
                                "@processKey" : processKey,
                                "@parallel": parallelAlignment,
                                "@isParallel": 'false',
                                "@statusId":statusId,
                                "@statusName":statusName,
                                "@add":addContext,
                                "@modelId":modelId,
                                "@assignee":assignee,
                                "@varName":varName,
                                "users":users,
                                 "groups":groups                            
                                 }
                            }
              }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":[
                                                                                {"@id":'matchingCircuitGrid'},
                                                                                {"@id":'generateProcessImage'},
                                                                                {"@id":'generateProcessDefinition'}
                                                                                ]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)
                 


def cardSave(context, main, add, filterinfo, session, elementId, data):
    u'''Сохранение согласователя'''
    #raise Exception(data)
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    data_dict = json.loads(data)
    processKey = data_dict["schema"]["data"]["@processKey"]
    parentId = data_dict["schema"]["data"]["@parentId"]
    name = data_dict["schema"]["data"]["@name"]
    assignee = data_dict["schema"]["data"]["@assignee"]
    isParallel = data_dict["schema"]["data"]["@isParallel"]
    statusId = data_dict["schema"]["data"]["@statusId"]
    modelId = data_dict["schema"]["data"]["@modelId"]
    addContext = data_dict["schema"]["data"]["@add"]
    id = data_dict["schema"]["data"]["@id"]
    #Если добавляем не параллельное согласование, то получаем список кандидатов
    if isParallel == 'false':
        users = list()
        if 'user' in data_dict["schema"]["data"]["users"]:
            users = data_dict["schema"]["data"]["users"]["user"]
        if isinstance(users,dict):
            users = [users]
        usersList = list() 
        for user in users:
            usersList.append(user['name'])
        groups = list()
        if 'group' in data_dict["schema"]["data"]["groups"]:
            groups = data_dict["schema"]["data"]["groups"]["group"]
        if isinstance(groups,dict):
            groups = [groups]
        groupsList = list()
        for group in groups:
            groupsList.append(group['name'])
        assJSON = {'assignee':assignee,
                   'users':usersList,
                   'groups':groupsList}
        if assignee == '' and groupsList == [] and usersList == []:
            return context.error(u"Необходимо заполнить хотя бы одно из полей: 'Ответственный','Пользователи','Группы'")
        ass = json.dumps(assJSON)
    #Редактирование элемента
    if addContext == 'edit':
        id = int(id)
        matchingCircuit.get(processKey,id)
        matchingCircuit.statusId = statusId
        matchingCircuit.name = name
        matchingCircuit.modelId = modelId
        matchingCircuit.assJSON = ass
        matchingCircuit.update()
        return context.message(u'Элемент изменён')
    else:
        if parentId == '':
            numbersSerie = numbersSeriesCursor(context)
            linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
            #Если с процессом не связаны серии номеров, то ддобавляем серию номеров
            if numbersSerie.tryGet(processKey):
                pass
            else:
                numbersSerie.id = processKey
                numbersSerie.description = u'Серия для задач процесса %s' % (processKey)
                numbersSerie.insert()
                linesOfNumbersSeries.seriesId = numbersSerie.id
                linesOfNumbersSeries.numberOfLine = 1
                linesOfNumbersSeries.startingDate = datetime.datetime.now()
                linesOfNumbersSeries.startingNumber = 1
                linesOfNumbersSeries.endingNumber = 100000
                linesOfNumbersSeries.incrimentByNumber = 1
                linesOfNumbersSeries.lastUsedNumber = 0
                linesOfNumbersSeries.isOpened = True
                linesOfNumbersSeries.lastUsedDate = datetime.datetime.now()
                linesOfNumbersSeries.prefix = ''
                linesOfNumbersSeries.postfix = ''
                linesOfNumbersSeries.isFixedLength = False
                linesOfNumbersSeries.insert()
            matchingCircuit.processKey = processKey
            matchingCircuit.id = getNextNo.getNextNoOfSeries(context,processKey)
            matchingCircuit.name = name
            
            matchingCircuit.statusId = statusId
            #Параллельное согласование
            if isParallel == 'true':
                matchingCircuit.type = 'parallel'
                matchingCircuit.name = 'parallel'
            else:#Задача
                matchingCircuit.type = 'task'
                matchingCircuit.assJSON = ass
                matchingCircuit.modelId = modelId
            matchingCircuitClone.setRange('processKey',processKey)
            matchingCircuitClone.setFilter('number',"!%'.'%")
            matchingCircuit.number = matchingCircuitClone.count() + 1
            matchingCircuit.insert()	
        else:#Добавление дочернего элемента для параллельного согласования
            parentId = int(parentId)
            matchingCircuit.setRange('processKey',processKey)
            matchingCircuit.get(processKey,parentId)
            number = getNewItemInLevelInHierarchy(context, matchingCircuit, 'number')
            matchingCircuit.processKey = processKey
            matchingCircuit.id = getNextNo.getNextNoOfSeries(context,processKey)
            matchingCircuit.name = name
            matchingCircuit.type = 'user'
            matchingCircuit.number = number
            matchingCircuit.modelId = modelId
            matchingCircuit.assJSON = ass
            matchingCircuit.statusId = statusId
            matchingCircuit.insert()
            
def statusListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Селектор статусов. '''
    params = XMLJSONConverter.xmlToJson(params)
    params = json.loads(params)
    modelId = params["schema"]["filter"]["data"]["@modelId"]
    status = statusCursor(context)
    status.setRange('modelId',modelId)
    filterString = curvalue.replace("'", "''") + "'%"
    if not startswith:
        filterString = "@%'" + filterString
    else:
        filterString = "@'" + filterString
    recCount = status.count()
    status.setFilter('name',filterString)
    status.limit(firstrecord,recordcount)
    recordList = ArrayList()
    for status in status.iterate():
        rec = DataRecord()
        rec.setId(status.id)
        rec.setName(status.name)
        rec.addParameter('varName', status.varName)
        recordList.add(rec)
    return ResultSelectorData(recordList, recCount)            
            
            
            
def matchingCircuitPreInsert(rec):
    rec.sort = generateSortValue(unicode(rec.number))            