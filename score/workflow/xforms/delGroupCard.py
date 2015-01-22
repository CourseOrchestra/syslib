# coding:utf-8
'''
Created on 26.12.2014

@author: tr0glo)|(I╠╣ 
'''

import simplejson as json
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

from java.util import ArrayList

from common.numbersseries import getNextNo

from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

import datetime

from ru.curs.celesta.showcase.utils import XMLJSONConverter


from common.numbersseries.getNextNo import getNextNoOfSeries

from workflow._workflow_orm import groupsCursor, userGroupCursor
from common.hierarchy import hasChildren


def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    session = json.loads(session)["sessioncontext"]
    groups = groupsCursor(context)
    userGroup = userGroupCursor(context)
    currRec = session["related"]["gridContext"]["currentRecordId"]
    groups.get(currRec)
    groupId = groups.groupId
    groupName = groups.groupName
    userGroup.setRange('groupId', groupId)
    if userGroup.count() > 0:
        usersFlag = 'true'
    else:
        usersFlag = 'false'
    data = {"schema":
              {"@xmlns":'',
               "data":
                        {"@groupId":groupId,
                         "@groupName":groupName,
                         "@flag":usersFlag,
                         "@hasChildren": int(hasChildren(context, groups, 'number'))
                         }}}

    settings = {"properties":
                  {"event":
                   {"@name":"single_click",
                    "@linkId": "1",
                    "action":
                        {"main_context": "current",
                         "datapanel":
                            {"@type": "current",
                             "@tab": "current",
                             "element":
                                [{"@id":"groupsGrid",
                                 "add_context": ''},
                                 {"@id":"userGroupsGrid",
                                 "add_context": 'hide'}
                                 ]}}}}}
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)),
                     XMLJSONConverter.jsonToXml(json.dumps(settings)))



def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    session = json.loads(session)["sessioncontext"]
    data = json.loads(xformsdata)["schema"]["data"]
    groups = groupsCursor(context)
    userGroup = userGroupCursor(context)
    groupId = data["@groupId"]

    userGroup.setRange('groupId', groupId)
    userGroup.deleteAll()
    groups.get(groupId)

    groups.setFilter("number", "('%s')|('%s.'%%)" % (groups.number, groups.number))
    count = groups.count()
    groups.deleteAll()
    context.message(u'Групп%s удалена' % (u'а' if count == 1 else u'ы'))