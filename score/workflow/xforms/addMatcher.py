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

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord
    
try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory
    
from workflow._workflow_orm import matchingCircuitCursor 
    
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
    matchingCircuit = matchingCircuitCursor(context)
    currentId = json.loads(session["sessioncontext"]["related"]["gridContext"]["currentRecordId"])
    assignee = ''
    users = {"@tag":"tag"}
    groups = {"@tag":"tag"}
    #Фиктивный жлемент верхнего уровня
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
                                "@add":addContext,
                                "@assignee":assignee,
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
                                                                                {"@id":'generateProcessImage'}
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
        matchingCircuit.name = name
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
            #Параллельное согласование
            if isParallel == 'true':
                matchingCircuit.type = 'parallel'
                matchingCircuit.name = 'parallel'
            else:#Задача
                matchingCircuit.type = 'task'
                matchingCircuit.assJSON = ass
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
            matchingCircuit.assJSON = ass
            matchingCircuit.insert()
            
            
def matchingCircuitPreInsert(rec):
    rec.sort = generateSortValue(unicode(rec.number))            