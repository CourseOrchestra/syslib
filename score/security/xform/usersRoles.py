# coding: utf-8
'''
Created on 03.12.2013

@author: d.bozhenko

'''
import simplejson as json
import base64
from java.util import ArrayList
import string
import os

from ru.curs.celesta import CelestaException
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from ru.curs.celesta.syscursors import UserRolesCursor, RolesCursor
from security._security_orm import loginsCursor
#import security.functions as func
try:
    from ru.curs.showcase.security import SecurityParamsFactory
except:
    print 1

try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import JythonDTO
    #from ru.curs.celesta.showcase import ResultSelectorData
    #from ru.curs.celesta.showcase import DataRecord

#checkUserAuthServerPath=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'usersTypes.json')
#checkUserAuthServerPath=os.path.join(os.pardir,'usersTypes.json')

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого таблицы ролей. '''

    #ru.curs.showcase.security.SecurityParamsFactory.getAuthServerUrl()
    rolesUsers = UserRolesCursor(context)
    roles = RolesCursor(context)
    logins = loginsCursor(context)

    currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    logins.get(currId)
    rolesUsers.setRange("userid", logins.subjectId)
    content=[]
    if rolesUsers.tryFirst():
        while True:
            if roles.tryGet(rolesUsers.roleid):
                content.append({"@id" : roles.id#,
                                #"@description" : roles.description
                                })                                                            
            if not rolesUsers.next():
                break
        
    if content==[]:
        xformsdata = {"schema":{"roles":""}
                      }
    else:
        xformsdata = {"schema":{"roles": {"role": content}
                                }
                      }


    #raise Exception(xformsdata)

    #print xformsdata
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"usersGrid",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника ролей. '''    
    rolesUsers = UserRolesCursor(context)
    logins = loginsCursor(context)
    currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    logins.get(currId)
    rolesUsers.setRange("userid", logins.subjectId)
    rolesUsers.deleteAll()
    if json.loads(xformsdata)["schema"]["roles"]<>'':
        content = json.loads(xformsdata)["schema"]["roles"]["role"]    
        content = content if isinstance(content, list) else [content]
        rolesUsersOld = UserRolesCursor(context)
        for role in content:         
            rolesUsers.roleid=role["@id"]
            rolesUsers.userid=logins.subjectId
            if rolesUsers.canInsert() and rolesUsers.canModify():        
                if not rolesUsers.tryInsert():
                    rolesUsersOld.get(logins.subjectId, role["@id"])
                    rolesUsers.recversion = rolesUsersOld.recversion  
                    rolesUsers.update()
            elif rolesUsers.canInsert():
                rolesUsers.tryInsert()
            elif rolesUsers.canModify():
                rolesUsersOld.get(logins.subjectId, role["@id"])
                rolesUsers.recversion = rolesUsersOld.recversion  
                rolesUsers.update()
            else:
                raise CelestaException(u"Недостаточно прав для данной операции!")


def rolesCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=False):
    roles = RolesCursor(context)
    roles.setFilter('id', "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))
    count = roles.count()
    #raise Exception(count)
    return ResultSelectorData(None, count)

def rolesList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=False, firstrecord=0, recordcount=None):
    u'''Функция list селектора типа элемента. '''   
    #raise Exception(curvalue)
    recordList = ArrayList()
    roles = RolesCursor(context)
    roles.setFilter('id', "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))
    roles.orderBy('id')
    roles.limit(firstrecord, recordcount)
    if roles.tryFirst():
        while True:
            rec = DataRecord()
            rec.setId(roles.id)
            rec.setName('%s - %s' % (roles.id, roles.description if roles.description else ''))
            recordList.add(rec)
            if not roles.next():
                break
    return ResultSelectorData(recordList, 0)