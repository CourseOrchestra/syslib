# coding: utf-8
'''
Created on 03.12.2013

@author: d.bozhenko

'''
import simplejson as json
import base64
import urllib2
from java.util import ArrayList
import xml.dom.minidom
import string
import os

from ru.curs.celesta import CelestaException
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from ru.curs.celesta.syscursors import UserRolesCursor
#from ru.curs.celesta.syscursors import RolesCursor
from security._security_orm import loginsCursor
from security._security_orm import subjectsCursor
from security.functions import Settings
from security.functions import getUsersFromAuthServer
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

checkUserAuthServerPath=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'usersTypes.json')
#checkUserAuthServerPath=os.path.join(os.pardir,'usersTypes.json')

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого таблицы ролей. '''
    
    settings=Settings()

    #ru.curs.showcase.security.SecurityParamsFactory.getAuthServerUrl()
    rolesUsers = UserRolesCursor(context)
    currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    rolesUsers.setRange("roleid", currId)    
    content=[]
    if settings.isUseAuthServer() and settings.loginIsSubject():            
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]
        server=SecurityParamsFactory.getAuthServerUrl()                
        users_xml=getUsersFromAuthServer(server, sessionId)        
        if rolesUsers.tryFirst():
            while True:
                for user in users_xml.getElementsByTagName("user"):
                    if user.getAttribute("SID")==rolesUsers.userid:
                        content.append({"@sid" : rolesUsers.userid,
                                        "@userName" : user.getAttribute("name")
                                        })
                        break                                                
                if not rolesUsers.next():
                    break
    else:
        subjects = subjectsCursor(context)
        if rolesUsers.tryFirst():
            while True:
                if subjects.tryGet(rolesUsers.userid):
                    content.append({"@sid" : subjects.sid,
                                    "@userName" : subjects.name
                                    })
                if not rolesUsers.next():
                    break
                
    if content==[]:
        xformsdata = {"schema":{"users": ""
                                }
                      }
    else:
        xformsdata = {"schema":{"users": {"user": content}
                                }
                      }
    #raise Exception(xformsdata)

    #print xformsdata
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"id_roles_grid",
                                                                                 "add_context": ""}
                                                                     }
                                                       }
                                             }
                                    }
                      }

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника ролей. '''    
    rolesUsers = UserRolesCursor(context)
    #users = loginsCursor(context)
    currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']    
    #raise Exception(session, xformsdata)
    
    content = json.loads(xformsdata)["schema"]["users"]["user"]
    
    content=content if isinstance(content, list) else [content]
    
    rolesUsersOld = UserRolesCursor(context)
    rolesUsers.setRange("roleid", currId)
    rolesUsers.deleteAll()
    for user in content:
        rolesUsers.userid=user["@sid"]
        rolesUsers.roleid=currId
        if rolesUsers.canInsert() and rolesUsers.canModify():        
            if not rolesUsers.tryInsert():                
                rolesUsersOld.get(user["@sid"], currId)
                rolesUsers.recversion = rolesUsersOld.recversion  
                rolesUsers.update()
        elif rolesUsers.canInsert():
            rolesUsers.tryInsert()
        elif rolesUsers.canModify():            
            rolesUsersOld.get(user["@sid"], currId)
            rolesUsers.recversion = rolesUsersOld.recversion  
            rolesUsers.update()
        else:
            raise CelestaException(u"Недостаточно прав для данной операции!")


def usersCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None):
    #raise Exception(params)   
    settings=Settings()
    if settings.isUseAuthServer() and settings.loginIsSubject():
        server=SecurityParamsFactory.getAuthServerUrl()            
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]
        users_xml=getUsersFromAuthServer(server, sessionId)        
        count=0        
        for user in users_xml.getElementsByTagName("user"):
            if startswith and string.find(user.getAttribute("name"), curvalue)==0 or \
                    not startswith and string.find(user.getAttribute("name"), curvalue)>0:
                count+=1                
        #count=len(users_xml.getElementsByTagName("user"))
    else:        
        subject = subjectsCursor(context)
        #raise Exception(useAuthServer)
        subject.setFilter('name', "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))        
        count = subject.count()    
    return ResultSelectorData(None, count)

def usersList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    u'''Функция list селектора типа элемента. '''
    settings=Settings()      
    recordList = ArrayList()
    if settings.isUseAuthServer() and settings.loginIsSubject():        
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]
        server=SecurityParamsFactory.getAuthServerUrl()
        users_xml=getUsersFromAuthServer(server, sessionId)
        #raise Exception(recordcount)
        for user in users_xml.getElementsByTagName("user"):
            if startswith and string.find(user.getAttribute("name"), curvalue)==0 or \
                    not startswith and string.find(user.getAttribute("name"), curvalue)>0:
                rec = DataRecord()
                rec.setId(user.getAttribute("SID"))
                rec.setName(user.getAttribute("name"))
                recordList.add(rec)        
    else:
        subject = subjectsCursor(context)        
        subject.setFilter('sid', "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))        
        subject.orderBy('sid')        
        subject.limit(firstrecord, recordcount)
        for subject in subject.iterate():
            rec = DataRecord()
            rec.setId(subject.sid)
            if subject.name is not None or subject.name!='':
                rec.setName(subject.name)
            else:
                rec.setName(u'[Имя не назначено!]')
            recordList.add(rec)
    return ResultSelectorData(recordList, 0)