# coding: utf-8
'''
Created on 26.12.2014

@author: tr0glo)|(I╠╣.
'''



from java.util import ArrayList


from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json
from workflow._workflow_orm import userGroupCursor, view_subjectsCursor, \
    groupsCursor


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord







# from common.xmlutils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка добавления и редактирования формы процесаа'''
    session = json.loads(session)
    userId = ''
    userName = ''
    for gridContext in session["sessioncontext"]["related"]["gridContext"]:
        if gridContext["@id"] == "groupsGrid":
            groupId = gridContext["currentRecordId"]


    xformsdata = {"schema":{"@xmlns":'',
                        "data":{
                                "@userId":userId,
                                "@userName":userName,
                                "@groupId":groupId
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
                                                                                {"@id":'userGroupsGrid'},
                                                                                {"@id":'groupsGrid',
                                                                                 "add_context":groupId}]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)



def cardDataSave(context, main, add, filterinfo, session, elementId, data):
    u'''Добавление пользователя в группу'''
    data_dict = json.loads(data)
    groupId = data_dict["schema"]["data"]["@groupId"]
    userId = data_dict["schema"]["data"]["@userId"]
    userId = json.loads(userId)[1]
    userGroup = userGroupCursor(context)
    userGroup.setRange('groupId', groupId)
    userGroup.setRange('userId', userId)
    if userGroup.count() > 0:
        return context.error(u'Данный пользователь уже состоит в этой группе')
    else:
        userGroup.userId = userId
        userGroup.groupId = groupId
        userGroup.insert()

def userListAndCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=None, firstrecord=None, recordcount=None):
    u'''Селектор пользователей. '''
    view_subjects = view_subjectsCursor(context)
    userGroup = userGroupCursor(context)
    groups = groupsCursor(context)
    #Получение списка развернутых процессов
    recordList = ArrayList()
    view_subjects.limit(firstrecord,recordcount)
    filterString = curvalue
    whereClause = []
    if '~' in filterString:
        filterString = filterString.split('~')
        groupNameFilter = filterString[1]
        filterString = filterString[0]
        if not startswith:
            groupNameFilter = "@%'" + groupNameFilter + "'%"
        else:
            groupNameFilter = "@'" + groupNameFilter + "'%"
        groups.setFilter('groupName',groupNameFilter)
        userList = []
        for groups in groups.iterate():
            userGroup.setRange('groupId',groups.groupId)
            for userGroup in userGroup.iterate():
                if userGroup.userId not in userList:
                    userList.append(userGroup.userId)
        if userList != []:
            for user in userList:
                whereClause.append("""sid = '%s'"""%(user))
            whereClause = ' or '.join(whereClause)
        else:
            whereClause = '1 = 0'
#             view_subjects.setComplexFilter(whereClause)
            
    if not startswith:
        filterString = "%" + filterString + "%"
    else:
        filterString =  filterString + "%"
    if not whereClause:
        view_subjects.setComplexFilter("""name like '%s'"""% filterString)
    else:
        whereClause += """and name like '%s'"""%(filterString)
        view_subjects.setComplexFilter(whereClause)
    userGroup.clear()
    for subjects in view_subjects.iterate():
        rec = DataRecord()
        rec.setId(json.dumps(['user',subjects.sid]))
        userGroup.setRange('userId',subjects.sid)
        groupList = []
        for userGroup in userGroup.iterate():
            groups.get(userGroup.groupId)
            groupList.append(groups.groupName)
        name = subjects.name + '(' + ','.join(groupList) + ')'
        rec.setName(name)
        recordList.add(rec)
    return ResultSelectorData(recordList, view_subjects.count())
