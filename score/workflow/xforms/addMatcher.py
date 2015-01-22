# coding: utf-8
'''
Created on 10.11.2014

@author: tr0glo)|(I╠╣.
'''


import simplejson as json
import urlparse
import cgi

from ru.curs.celesta.syscursors import UserRolesCursor

from security._security_orm import subjectsCursor

from common.hierarchy import generateSortValue, getNewItemInLevelInHierarchy, hasChildren

from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

import datetime

from common.numbersseries import getNextNo


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

from workflow._workflow_orm import matchingCircuitCursor, statusCursor, processStatusModelCursor, \
                                    groupsCursor, userGroupCursor

from workflow.processUtils import getUserName

from java.io import InputStream, FileInputStream
from jarray import zeros

# from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка добавления и редактирования элементов в грид согласователей процеса'''
    session = json.loads(session)
    add = json.loads(add)
    addContext = add[0]
    processKey = add[1]
    modelId = add[2]
    matchingCircuit = matchingCircuitCursor(context)
    groupsCur = groupsCursor(context)
    currentId = json.loads(session["sessioncontext"]["related"]["gridContext"]["currentRecordId"])
    assignee = ''
    users = {"@tag":"tag"}
    groups = {"@tag":"tag"}
    statusId = ''
    statusName = ''
    varName = ''
    assigneeName = ''
    taskKey = ''
    isDynamic = 'false'
    # Фиктивный элемент верхнего уровня
    if currentId['id'] == 'top':
        parallelAlignment = 'false'
        id = ''
        name = ''
        parentId = ''
        parentName = 'Элемент верхнего уровня'
    else:
        id = currentId['id']
        matchingCircuit.get(processKey, id)
        name = matchingCircuit.name
        # Добавление внуть параллельного согласования
        if addContext == 'add':
            parentId = id
            parentName = u'Параллельное согласование'
            parallelAlignment = 'true'
            id = ''
            name = ''
        else:
            ass = json.loads(matchingCircuit.assJSON)
            taskKey = matchingCircuit.taskKey
            # Получение ответственного лица и списка кандидатов
            subjects = subjectsCursor(context)
            assignee = ass['assignee']
            if subjects.tryGet(assignee):
                assigneeName = subjects.name
                assignee = json.dumps(['user',assignee])
            else:
                isDynamic = 'true'
            users = {'@tag':'tag', 'user':[]}
            groups = {'@tag':'tag', 'group':[]}
            for user in ass['users']:
                if user['isDynamic'] == 'false':
                    users['user'].append({'id':json.dumps(['user',user['id']]),
                                          'name':getUserName(context,user['id']),
                                          'isDynamic':user['isDynamic']})
                else:
                    users['user'].append({'id':user['id'],
                                          'name':user['id'],
                                          'isDynamic':user['isDynamic']})
            for group in ass['groups']:
                if group['isDynamic'] == 'false':
                    groupsCur.get(group['id'])
                    groups['group'].append({'id':group['id'],
                                            'name':groupsCur.groupName,
                                            'isDynamic':group['isDynamic']})
                else:
                    groups['group'].append({'id':group['id'],
                                            'name':group['id'],
                                            'isDynamic':group['isDynamic']})                    
            parentId = ''
            parentName = ''
            parallelAlignment = 'false'
    name = name.replace('{', '\{')
    name = name.replace('}', '\}')
    xformsdata = {"schema":{"@xmlns":'',
                        "data":{"@taskKey":taskKey,
                                "@isDynamic":isDynamic,
                                "@id":id,
                                "@name":name,
                                "@parentName": parentName,
                                "@parentId" : parentId,
                                "@processKey" : processKey,
                                "@parallel": parallelAlignment,
                                "@isParallel": 'false',
                                "@add":addContext,
                                "@modelId":modelId,
                                "@assignee":assignee,
                                "@assigneeName":assigneeName,
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
    # raise Exception(data)
    matchingCircuit = matchingCircuitCursor(context)
    matchingCircuitClone = matchingCircuitCursor(context)
    data_dict = json.loads(data)
    processKey = data_dict["schema"]["data"]["@processKey"]
    parentId = data_dict["schema"]["data"]["@parentId"]
    name = data_dict["schema"]["data"]["@name"]
    assignee = data_dict["schema"]["data"]["@assignee"]
    isDynamic = data_dict["schema"]["data"]["@isDynamic"]
    isParallel = data_dict["schema"]["data"]["@isParallel"]
    addContext = data_dict["schema"]["data"]["@add"]
    taskKey = data_dict["schema"]["data"]["@taskKey"]
    id = data_dict["schema"]["data"]["@id"]
    # Если добавляем не параллельное согласование, то получаем список кандидатов
    if isParallel == 'false':
        if isDynamic == 'false' and assignee != '':
            assignee = json.loads(assignee)[1]
        users = list()
        if 'user' in data_dict["schema"]["data"]["users"]:
            users = data_dict["schema"]["data"]["users"]["user"]
        if isinstance(users, dict):
            users = [users]
        usersList = list()
        for user in users:
            if user['isDynamic'] == 'false':
                usersList.append({'id':json.loads(user['id'])[1],
                                  'isDynamic': 'false'})
            else:
                usersList.append({'id':user['id'],
                                  'isDynamic': 'true'}) 
        groups = list()
        if 'group' in data_dict["schema"]["data"]["groups"]:
            groups = data_dict["schema"]["data"]["groups"]["group"]
        if isinstance(groups, dict):
            groups = [groups]
        groupsList = list()
        for group in groups:
            groupsList.append({'id':group['id'],
                              'isDynamic': group['isDynamic']})

        assJSON = {'assignee':assignee,
                   'users':usersList,
                   'groups':groupsList}
        if assignee == '' and groupsList == [] and usersList == []:
            return context.error(u"Необходимо заполнить хотя бы одно из полей: 'Ответственный','Пользователи','Группы'")
        ass = json.dumps(assJSON)
    # Редактирование элемента
    if addContext == 'edit':
        id = int(id)
        matchingCircuit.setRange('processKey', processKey)
        matchingCircuit.setRange('taskKey', taskKey)
        if matchingCircuit.count() > 0:
            matchingCircuit.first()
            if matchingCircuit.processKey == processKey and matchingCircuit.id == id:
                pass
            else:
                return context.error(u"Задача с таким ключом уже существует")
        matchingCircuit.get(processKey, id)
        matchingCircuit.name = name
        matchingCircuit.taskKey = taskKey
        matchingCircuit.assJSON = ass
        matchingCircuit.update()
        return context.message(u'Элемент изменён')
    else:
        if parentId == '':
            matchingCircuit.setRange('processKey', processKey)
            matchingCircuit.setRange('taskKey', taskKey)
            if matchingCircuit.count() > 0:
                return context.error(u"Задача с таким ключом уже существует")
            numbersSerie = numbersSeriesCursor(context)
            linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
            # Если с процессом не связаны серии номеров, то ддобавляем серию номеров
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
            matchingCircuit.id = getNextNo.getNextNoOfSeries(context, processKey)
            matchingCircuit.name = name
            matchingCircuit.taskKey = taskKey

            # Параллельное согласование
            if isParallel == 'true':
                matchingCircuit.type = 'parallel'
                matchingCircuit.name = 'parallel'
            else:  # Задача
                matchingCircuit.type = 'task'
                matchingCircuit.assJSON = ass

            matchingCircuitClone.setRange('processKey', processKey)
            matchingCircuitClone.setFilter('number', "!%'.'%")
            matchingCircuit.number = matchingCircuitClone.count() + 1
            matchingCircuit.insert()
        else:  # Добавление дочернего элемента для параллельного согласования
            parentId = int(parentId)
            matchingCircuit.setRange('processKey', processKey)
            matchingCircuit.setRange('taskKey', taskKey)
            if matchingCircuit.count() > 0:
                return context.error(u"Задача с таким ключом уже существует")
            matchingCircuit.setRange('taskKey')
            matchingCircuit.setRange('processKey', processKey)
            matchingCircuit.get(processKey, parentId)
            number = getNewItemInLevelInHierarchy(context, matchingCircuit, 'number')
            matchingCircuit.processKey = processKey
            matchingCircuit.id = getNextNo.getNextNoOfSeries(context, processKey)
            matchingCircuit.taskKey = taskKey
            matchingCircuit.name = name
            matchingCircuit.type = 'user'
            matchingCircuit.number = number

            matchingCircuit.assJSON = ass

            matchingCircuit.insert()

def usersListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Селектор пользователей, доступных для назначения на задачи. '''
    userroles = UserRolesCursor(context)
    subjects = subjectsCursor(context)
    userList = []
    userroles.setFilter('roleid', "'dev'|'user'")
    while userroles.nextInSet():
        if "'" + userroles.userid + "'" not in userList:
            userList.append("'" + userroles.userid + "'")
    if userList != []:
        filterString = "(" + '|'.join(userList) + ")"
        subjects.setFilter('sid', filterString)
    filterString = curvalue.replace("'", "''") + "'%"
    if not startswith:
        filterString = "@%'" + filterString
    else:
        filterString = "@'" + filterString
    recCount = subjects.count()
    subjects.setFilter('name', filterString)
    subjects.limit(firstrecord, recordcount)
    recordList = ArrayList()
    for subjects in subjects.iterate():
        rec = DataRecord()
        rec.setId(subjects.sid)
        rec.setName(subjects.name)
        recordList.add(rec)
    return ResultSelectorData(recordList, recCount)

def treeSelectorXML(context, main=None, add=None, filterinfo=None, session=None, params=None):
    u'''селектор пользователей из групп'''
    # raise Exception(main,add,filterinfo,session,params,context.getData()["currentSystemDiagnosesTree"])
    session = json.loads(session)
    sid = session['sessioncontext']['sid']

    userroles = UserRolesCursor(context)
    subjects = subjectsCursor(context)
    groups = groupsCursor(context)
    userGroup = userGroupCursor(context)
    userList = []
    params = json.loads(params)["params"]
    data = {"hypotheses":
            {"hypothesis": []}}
    try:
        startswith = True if params['startsWith'] == 'true' else False
        curvalue = params['curValue'].lower()
    except:
        startswith = False
        curvalue = ''
    if "id" not in params or 'group' in params["id"]:
        if "id" in params:
            parentId = json.loads(params["id"])
            groups.get(parentId[1])
            groups.setFilter("number", "('%s.'%%)&!('%s.'%%'.'%%)" % (groups.number, groups.number))
        else:
            groups.setFilter("number", "!(%'.'%)")
            data["hypotheses"]["hypothesis"].append({"@id": json.dumps(["other", 'other']),
                                                     "@name": 'Остальные',
                                                     "@leaf": "false",
                                                     "@type": "Группа"
                                                     })
        groups.orderBy('groupName')
        for groups in groups.iterate():
            userGroup.setRange('groupId', groups.groupId)
            data["hypotheses"]["hypothesis"].append({"@id": json.dumps(["group", groups.groupId]),
                                                     "@name": groups.groupName,
                                                     "@leaf": unicode(not(hasChildren(context, groups, 'number') \
                                                                          or userGroup.count() > 0)).lower(),
                                                     "@type": "Группа"
                                                     })
    if "id" in params:
        parentId = json.loads(params["id"])
    
        if parentId[0] in ('group', 'workflowDev', 'workflowUser'):
            userList = []
            if parentId[0] == 'group':
                userGroup.setRange('groupId', parentId[1])
                for userGroup in userGroup.iterate():
                    userList.append("'%s'" % userGroup.userId)
            else:
                userroles.setRange('roleid', parentId[1])
                while userroles.nextInSet():
                    userList.append("'%s'" % userroles.userid)
            if userList != []:
                userString = '|'.join(userList)
                subjects.setFilter('sid', userString)
                subjects.setFilter('name', "@%s'%s'%%" % ("%"*(not startswith), curvalue))
                subjects.orderBy('name')
                for subjects in subjects.iterate():
                    data["hypotheses"]["hypothesis"].append({"@id": json.dumps(["user", subjects.sid, parentId[1]]),
                                                             "@name": subjects.name,
                                                             "@leaf": "true",
                                                             "@checked": "false",
                                                             "@type": "Пользователь"})
        elif parentId[0] == 'other':
            userroles.setRange('roleid', 'workflowDev')
            userList = []
            subjects.setFilter('name', "@%s'%s'%%" % ("%"*(not startswith), curvalue))
            while userroles.nextInSet():
                userList.append("'%s'" % userroles.userid)
            if userList != []:
                userString = '|'.join(userList)
                subjects.setFilter('sid', userString)
        
                data["hypotheses"]["hypothesis"].append({"@id": json.dumps(["workflowDev", 'workflowDev']),
                                                         "@name": u"Разработчики",
                                                         "@leaf": unicode(subjects.count() == 0).lower(),
                                                         "@type": u"Группа"})
            userroles.setRange('roleid', "workflowUser")
            userList = []
            while userroles.nextInSet():
                userList.append("'%s'" % userroles.userid)
            if userList != []:
                userString = '|'.join(userList)
                subjects.setFilter('sid', userString)
                data["hypotheses"]["hypothesis"].append({"@id": json.dumps(["workflowUser", 'workflowUser']),
                                                         "@name": u"Сотрудники",
                                                         "@leaf": unicode(subjects.count() == 0).lower(),
                                                         "@type": u"Группа"})

    # raise Exception(data)
    if data == {"hypotheses":
            {"hypothesis": []}}:
        data = {"hypotheses":
                {"hypothesis": [{"@id": "",
                                 "@name": u"Ошибка",
                                 "@leaf": "true", }]}}

    jsonData = XMLJSONConverter.jsonToXml(json.dumps(data))
    res = JythonDTO(jsonData)
    return res


def groupsListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None):
    u'''Селектор групп пользователей. '''
    session = json.loads(session)
    sid = session['sessioncontext']['sid']

    groups = groupsCursor(context)
    userList = []
    params = json.loads(params)["params"]
    data = {"hypotheses":
            {"hypothesis": []}}
    try:
        startswith = True if params['startsWith'] == 'true' else False
        curvalue = params['curValue'].lower()
    except:
        startswith = False
        curvalue = ''
    if "id" in params:
        parentId = json.loads(params["id"])
        groups.get(parentId)
        groups.setFilter("number", "('%s.'%%)&!('%s.'%%'.'%%)" % (groups.number, groups.number))
    else:
        groups.setFilter("number", "!(%'.'%)")

    groups.orderBy('groupName')
    for groups in groups.iterate():
        data["hypotheses"]["hypothesis"].append({"@id": groups.groupId,
                                                 "@name": groups.groupName,
                                                 "@checked": "false",
                                                 "@leaf": unicode(not(hasChildren(context, groups, 'number'))).lower()
                                                 })
    if data == {"hypotheses":
            {"hypothesis": []}}:
        data = {"hypotheses":
                {"hypothesis": [{"@id": "",
                                 "@name": u"Ошибка",
                                 "@leaf": "true", }]}}

    jsonData = XMLJSONConverter.jsonToXml(json.dumps(data))
    res = JythonDTO(jsonData)
    return res


def matchingCircuitPreInsert(rec):
    rec.sort = generateSortValue(unicode(rec.number))
