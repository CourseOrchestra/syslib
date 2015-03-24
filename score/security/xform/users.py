# coding: utf-8
'''
@author: d.bozhenko

'''
import simplejson as json
#import base64
from java.util import ArrayList

try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
    from ru.curs.showcase.security import SecurityParamsFactory
except:
    from ru.curs.celesta.showcase import JythonDTO
from ru.curs.celesta import CelestaException
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security.functions import id_generator
from security.functions import Settings
from security.functions import getUsersFromAuthServer, id_generator
import hashlib
from common.numbersseries.getNextNo import getNextNoOfSeries
from common.sysfunctions import tableCursorImport
from security._security_orm import loginsCursor
from security._security_orm import subjectsCursor





def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):

    settings=Settings()

    logins = loginsCursor(context)
    subjects=subjectsCursor(context)    
    isEmployees = settings.isEmployees()
    if isEmployees:
        employeesGrain=settings.getEmployeesParam("employeesGrain")
        employeesTable=settings.getEmployeesParam("employeesTable")
        employeesId=settings.getEmployeesParam("employeesId") #название поля с первичным ключом
        employeesName=settings.getEmployeesParam("employeesName") #название поля с именем
        employeesCursor=tableCursorImport(employeesGrain, employeesTable)
        employees=employeesCursor(context)
    #raise Exception(session)
    subjectId=""
    subjectName=""
    empId=""
    empName=""            
    if 'currentRecordId' in json.loads(session)['sessioncontext']['related']['gridContext']:
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']        
        if logins.tryGet(currId) and add<>'add':
            if subjects.tryGet(logins.subjectId):
                subjectId=subjects.sid
                subjectName=subjects.name
                if isEmployees:
                    if employees.tryGet(subjects.employeeId):
                        empId=getattr(employees, employeesId)
                        empName=getattr(employees, employeesName)

    if add == 'add':        
        xformsdata = {"schema":{"@xmlns":"",
                                "user":{"@sid": "",                                        
                                        "@password": id_generator(),
                                        "@userName": "",
                                        "@subjectId":"",
                                        "@subjectName":"",
                                        "@employeeId":"",
                                        "@employeeName":"",
                                        "@isAuthServer":unicode(settings.isUseAuthServer()).lower(),
                                        "@loginIsSubject":unicode(settings.loginIsSubject()).lower(),
                                        "@add":add,
                                        "@isEmployees":unicode(isEmployees).lower(),
                                        "@key":unichr(9911)}
                                }
                      }
        if settings.loginIsSubject():
            sid=getNextNoOfSeries(context, 'subjects') + id_generator()
            xformsdata["schema"]["user"]["@subjectId"]=sid
            xformsdata["schema"]["user"]["@sid"]=sid
    elif add == 'edit' and settings.isUseAuthServer():        
        server=SecurityParamsFactory.getAuthServerUrl()
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]
        users_xml=getUsersFromAuthServer(server, sessionId)
        for user_xml in users_xml.getElementsByTagName("user"):
            if user_xml.getAttribute("login")==currId:
                break
        #raise Exception(user_xml.getAttribute("password"))        
        xformsdata = {"schema":{"user":{"@sid": user_xml.getAttribute("SID"),                                        
                                        "@password": "",
                                        "@userName": user_xml.getAttribute("login"),
                                        "@subjectId":subjectId,
                                        "@subjectName":subjectName,
                                        "@employeeId":empId,
                                        "@employeeName":empName,
                                        "@isAuthServer":unicode(settings.isUseAuthServer()).lower(),
                                        "@loginIsSubject":unicode(settings.loginIsSubject()).lower(),
                                        "@add":"",
                                        "@isEmployees":unicode(isEmployees).lower(),
                                        "@key":unichr(9911)}
                                }
                      }
    elif add == 'edit':        
        #currId = json.loads(base64.b64decode(currIdEncoded))
        logins.get(currId)        
        xformsdata = {"schema":{"user":{"@sid": logins.subjectId,                                        
                                        "@password": "",
                                        "@userName": logins.userName,
                                        "@subjectId":subjectId,
                                        "@subjectName":subjectName,
                                        "@employeeId":empId,
                                        "@employeeName":empName,
                                        "@isAuthServer":unicode(settings.isUseAuthServer()).lower(),
                                        "@loginIsSubject":unicode(settings.loginIsSubject()).lower(),
                                        "@add":add,
                                        "@isEmployees":unicode(isEmployees).lower()
                                        }
                                }
                      }
        
    #print xformsdata
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",                                                       
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":{"@id":"usersGrid",
                                                                                "add_context": ""}                                                                                                                                                                
                                                                     }
                                                       }
                                             }
                                    }
                      }

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):    
    u'''Функция сохранения карточки редактирования содержимого справочника ролей. '''
    settings=Settings()     

    logins = loginsCursor(context)    
    subject = subjectsCursor(context)    
    #raise Exception(xformsdata)
    content = json.loads(xformsdata)["schema"]["user"]
    if not settings.isUseAuthServer():
        if add=='edit' and content["@password"]=='':
            #если пароль при редактировании не заполнен, сохраняем в курсоре старый пароль из базы
            loginsOld=loginsCursor(context)
            currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
            loginsOld.get(currId)
            logins.password=loginsOld.password
        else:
            #иначе зашифровываем пароль из карточки
            pass_hash=hashlib.sha1() # Объект типа hash
            pass_hash.update(content["@password"]) # Записываем в него текущий пароль из карточки
            logins.password=pass_hash.hexdigest() # Выполняем hash функцию, записываем результат в курсор.
            #raise Exception(str(pass_hash.digest()))        
        logins.userName=content["@userName"]
        if content["@subjectId"]=="":
            logins.subjectId=None
        else:
            logins.subjectId=content["@subjectId"]
        if settings.loginIsSubject():            
            subject.sid=content["@subjectId"]
            subject.name=content["@userName"]
            if content["@employeeId"]=='':
                subject.employeeId=None
            else:
                subject.employeeId=content["@employeeId"]
            if add == 'add' and subject.canInsert() and subject.canModify():
                if not subject.tryInsert():
                    subjectOld = subjectsCursor(context)
                    subjectOld.get(content["@subjectId"])
                    subject.recversion = subjectOld.recversion
                    subject.update()
            elif add == 'add' and logins.canInsert():
                subject.insert()
            elif add == 'edit' and subject.canModify():
                subjectOld = subjectsCursor(context)
                subjectOld.get(content["@subjectId"])
                subject.recversion = subjectOld.recversion
                subject.update()
            else:
                raise CelestaException(u"Недостаточно прав для данной операции!")            
        if add == 'add' and logins.canInsert() and logins.canModify():
            if not logins.tryInsert():
                logins.update()            
        elif add == 'add' and logins.canInsert():
            logins.insert()            
        elif add == 'edit' and logins.canModify():        
            #currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']        
            loginsOld = loginsCursor(context)
            loginsOld.get(content["@userName"])
            logins.recversion = loginsOld.recversion
            logins.update()                    
        else:
            raise CelestaException(u"Недостаточно прав для данной операции!")            
    else:
        if logins.tryGet(content["@userName"]):
            if settings.loginIsSubject():
                if not subject.tryGet(logins.subjectId):
                    subject.sid=content["@sid"]
                if content["@employeeId"]=='':
                    subject.employeeId=None                    
                else:
                    subject.employeeId=content["@employeeId"]                    
                subject.name=content["@userName"]
                logins.subjectId = subject.sid                    
                if subject.canInsert() and subject.canModify():
                    if not subject.tryInsert():
                        subjectOld = subjectsCursor(context)
                        subjectOld.get(content["@subjectId"])
                        subject.recversion = subjectOld.recversion
                        subject.update()
                elif subject.canModify():
                    subjectOld = subjectsCursor(context)
                    subjectOld.get(content["@subjectId"])
                    subject.recversion = subjectOld.recversion
                    subject.update()
                else:
                    raise CelestaException(u"Недостаточно прав для данной операции!")
            else:
                if content["@subjectId"]=="":
                    logins.subjectId=None
                else:
                    logins.subjectId=content["@subjectId"]
            if logins.canModify():
                logins.update()
            else:
                raise CelestaException(u"Недостаточно прав для данной операции!")
        else:
            if settings.loginIsSubject():
                if content["@employeeId"]=='':
                    logins.subjectId=None
                else:
                    subject.employeeId=content["@employeeId"]
                    subject.sid=content["@sid"]
                    subject.name=content["@userName"]
                    logins.subjectId=subject.sid
                    if subject.canInsert() and subject.canModify():
                        if not subject.tryInsert():
                            subjectOld = subjectsCursor(context)
                            subjectOld.get(content["@subjectId"])
                            subject.recversion = subjectOld.recversion
                            subject.update()
                    elif subject.canInsert():
                        subject.insert()
                    else:
                        raise CelestaException(u"Недостаточно прав для данной операции!")
            else:
                if content["@subjectId"]=="":
                    logins.subjectId=None
                else:
                    logins.subjectId=content["@subjectId"]            
            logins.userName=content["@userName"]
            logins.password=""
            if logins.canInsert():
                logins.insert()
            else:
                raise CelestaException(u"Недостаточно прав для данной операции!")
        

def subjectsCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None):
    u'''Функция count для селектора выбора ролей. '''

    subjects = subjectsCursor(context)
    subjects.setFilter('name', """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    count = subjects.count()

    return ResultSelectorData(None, count)

def subjectsList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    u'''Функция list для селектора выбора ролей. '''
    
    subjects = subjectsCursor(context)
    subjects.setFilter('name', """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    subjects.orderBy('name')
    subjects.limit(firstrecord, recordcount)

    recordList = ArrayList()
    for subjects in subjects.iterate():
        rec = DataRecord()
        rec.setId(unicode(subjects.sid))
        rec.setName(subjects.name)
        recordList.add(rec)

    return ResultSelectorData(recordList, 0)

def employeesCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=False):
    settings=Settings()

    employeesGrain=settings.getEmployeesParam("employeesGrain")
    employeesTable=settings.getEmployeesParam("employeesTable")
#    employeesId=getEmployeesParam("employeesId")
    employeesName=settings.getEmployeesParam("employeesName")
    
    employeesCursor=tableCursorImport(employeesGrain, employeesTable)
    employees=employeesCursor(context)
    employees.setFilter(employeesName, "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))
    count = employees.count()
    #raise Exception(count)
    return ResultSelectorData(None, count)

def employeesList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=False, firstrecord=0, recordcount=None):
    u'''Функция list селектора типа элемента. '''   
    settings=Settings()

    #raise Exception(curvalue)
    recordList = ArrayList()
    employeesGrain=settings.getEmployeesParam("employeesGrain")
    employeesTable=settings.getEmployeesParam("employeesTable")
    employeesId=settings.getEmployeesParam("employeesId")
    employeesName=settings.getEmployeesParam("employeesName")
    
    employeesCursor=tableCursorImport(employeesGrain, employeesTable)
    employees=employeesCursor(context)
    employees.setFilter(employeesName, "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))
    employees.orderBy(employeesName)
    employees.limit(firstrecord, recordcount)
    for employees in employees.iterate():
        rec = DataRecord()
        rec.setId(getattr(employees, employeesId))
        rec.setName(getattr(employees, employeesName))
        recordList.add(rec)
    return ResultSelectorData(recordList, 0)




def employeesSubjectsPostInsert(rec):
    # Триггер добавляется только в случае loginEqualSubject = "false"
    settings=Settings()

    context=rec.callContext()
    employeesId=settings.getEmployeesParam("employeesId")
    employeesName=settings.getEmployeesParam("employeesName")
    sid=getNextNoOfSeries(context, 'subjects') + id_generator()
    subjects = subjectsCursor(context)
    subjects.sid=sid
    subjects.name=getattr(rec, employeesName)
    subjects.employeeId=getattr(rec, employeesId)
    if subjects.canInsert() and subjects.canModify():
        if not subjects.tryInsert():
            subjects.update()
    elif subjects.canInsert():
        subjects.insert()
    
def employeesSubjectsPostUpdate(rec):
    # Триггер добавляется только в случае loginEqualSubject = "false"
    settings=Settings()

    context=rec.callContext()
    employeesId=settings.getEmployeesParam("employeesId")
    employeesName=settings.getEmployeesParam("employeesName")    
    subjects = subjectsCursor(context)
    subjects.setRange("employeeId", getattr(rec, employeesId))
    if subjects.tryFirst():# and subjects.count()==1:
        subjects.name=getattr(rec, employeesName)    
        if subjects.canModify():
            subjects.update()
    
def employeesSubjectsPreDelete(rec):
    # Триггер добавляется только в случае loginEqualSubject = "false"
    settings=Settings()

    context=rec.callContext()
    employeesId=settings.getEmployeesParam("employeesId")
    subjects = subjectsCursor(context)
    subjects.setRange("employeeId", getattr(rec, employeesId))
    if subjects.canDelete():
        subjects.deleteAll()
    
