# coding:utf-8
'''
Created on 26.12.2014

@author: tr0glo)|(I╠╣ 
'''

import json
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

from java.util import ArrayList

from common.numbersseries import getNextNo

from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

import datetime

from ru.curs.celesta.showcase.utils import XMLJSONConverter

from common.hierarchy import getNewItemInLevelInHierarchy
from common.numbersseries.getNextNo import getNextNoOfSeries

from workflow._workflow_orm import groupsCursor

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    session = json.loads(session)["sessioncontext"]
    groups = groupsCursor(context)
    groupId = ''
    groupName = ''
    if add == 'edit':
        currRec = session["related"]["gridContext"]["currentRecordId"]
        groups.get(currRec)
        groupId = groups.groupId
        groupName = groups.groupName
    data = {"schema":
              {"@xmlns":'',
               "data":
                        {"@groupId":groupId,
                         "@groupName":groupName
                         }}}

    settings = {"properties":
                  {"event":
                   {"@name":"single_click",
                    "@linkId": "1",
                    "action":
                        {"#sorted":[{"main_context": "current"},
                         {"datapanel":
                            {"@type": "current",
                             "@tab": "current",
                             "element":
                                {"@id":"groupsGrid",
                                 "add_context": groupId}}}]}}}}
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)),
                     XMLJSONConverter.jsonToXml(json.dumps(settings)))



def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    session = json.loads(session)["sessioncontext"]
    data = json.loads(xformsdata)["schema"]["data"]
    groups = groupsCursor(context)
    groupId = data["@groupId"]
    groupName = data["@groupName"]
    if add == 'add':
        numbersSerie = numbersSeriesCursor(context)
        if 'currentRecordId' in session["related"]["gridContext"]:
            groups.get(session["related"]["gridContext"]["currentRecordId"])
        linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
        if not numbersSerie.tryGet('userGroups'):
            numbersSerie.id = 'userGroups'
            numbersSerie.description = u'Серия для групп пользователей'
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
        groups.groupId = getNextNo.getNextNoOfSeries(context, 'userGroups')
        groups.groupName = groupName
        groups.number = getNewItemInLevelInHierarchy(context, groups, 'number')
        groups.insert()
    else:
        groups.get(groupId)
        groups.groupName = groupName
        groups.update()

    context.message(u'Данные добавлены')

def delCardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка удаления потока работы'''
    xformsdata = {"schema":{"@xmlns":'',
                            "data":{"@reason":''},
                            }
                  }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"#sorted":[{"main_context": "current"},
                                                        {"datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":{"@id": "grid",
                                                                                "add_context": 'current'}
                                                                     }
                                                        }]}
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def delCardDataSave(context, main, add, filterinfo, session, elementId, xformsdata):
    u'''Удаление потока работы'''
    session = json.loads(session)["sessioncontext"]
    curriculumProcess = curriculumProcessCursor(context)
    currRec = json.loads(session["related"]["gridContext"]["currentRecordId"])

    curriculumProcess.get(int(currRec))
    curriculumProcess.delete()

def groupsPreInsert(rec):
    rec.sort = generateSortValue(unicode(rec.number))
