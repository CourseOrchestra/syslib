# coding: utf-8

import simplejson as json
import base64
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security._security_orm import loginsCursor, subjectsCursor
import security.functions as func
from security.functions import Settings
import xml.dom.minidom
from common.sysfunctions import tableCursorImport, getGridHeight, getGridWidth, toHexForXml


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.security import SecurityParamsFactory
except:
    pass



def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''    
    settings=Settings()
    logins = loginsCursor(context)    
    # Определяем переменную для JSON данных    
    data = {"records":{"rec":[]}}
    isEmployees = settings.isEmployees()
    if isEmployees:
        employeesGrain=settings.getEmployeesParam("employeesGrain")
        employeesTable=settings.getEmployeesParam("employeesTable")
        employeesName=settings.getEmployeesParam("employeesName") #название поля с именем        
        employeesCursor=tableCursorImport(employeesGrain, employeesTable)
        employees=employeesCursor(context)

    if settings.isUseAuthServer() and settings.loginIsSubject(): #tt
        subjects=subjectsCursor(context)

        server=SecurityParamsFactory.getAuthServerUrl()        
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]
        logins_xml=func.getUsersFromAuthServer(server, sessionId)
        i=0
        for user in logins_xml.getElementsByTagName("user"):
            i+=1
            if i<firstrecord:
                continue
            loginsDict = {}
            loginsDict[toHexForXml('~~id')] = user.getAttribute("login")
            loginsDict["SID"] = user.getAttribute("SID")
            loginsDict[toHexForXml(u"Имя пользователя")] = user.getAttribute("login")
            if isEmployees:
                loginsDict["Сотрудник"] = ""
                if logins.tryGet(user.getAttribute("login")):
                    if subjects.tryGet(logins.subjectId):
                        if employees.tryGet(subjects.employeeId):
                            loginsDict["Сотрудник"] = getattr(employees, employeesName)                        
            loginsDict['properties'] = {"event":{"@name":"row_single_click",
                                                "action":{"#sorted":[{"main_context": 'current'},
                                                                     {"datapanel":{"@type":"current",
                                                                                   "@tab":"current"}
                                                                      }]
                                                          }
                                                }
                                       }
            data["records"]["rec"].append(loginsDict)
            if i >= firstrecord + pagesize:
                break
            #raise Exception(data)
    elif settings.isUseAuthServer(): #tf
        server=SecurityParamsFactory.getAuthServerUrl()        
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]        
        logins_xml=func.getUsersFromAuthServer(server, sessionId)        
        subjects=subjectsCursor(context)
        i=0
        for user in logins_xml.getElementsByTagName("user"):
            i+=1
            if i<firstrecord:
                continue
            loginsDict = {}
            loginsDict[toHexForXml('~~id')] = user.getAttribute("login")
            loginsDict["SID"] = user.getAttribute("SID")
            loginsDict[toHexForXml(u"Имя пользователя")] = user.getAttribute("login")
            loginsDict["Субъект"] = ""
            if logins.tryGet(user.getAttribute("login")):
                if subjects.tryGet(logins.subjectId):
                    loginsDict["Субъект"] = subjects.name
            loginsDict['properties'] = {"event":{"@name":"row_single_click",
                                                "action":{"#sorted":[{"main_context": 'current'},
                                                                     {"datapanel":{"@type":"current",
                                                                                   "@tab":"current"}
                                                                      }]
                                                          }
                                                }
                                       }
            data["records"]["rec"].append(loginsDict)
            if i >= firstrecord + pagesize:
                break
    elif not settings.isUseAuthServer() and not settings.loginIsSubject(): #ff
        subjects=subjectsCursor(context)
        columnsDict={u"Имя пользователя":"userName",
                     u"Субъект": ""}
        for column in sortColumnList:
            sortindex = '%s' % column.getSorting()
            if column.getId()<>u"Субъект":
                logins.orderBy(columnsDict[column.getId()] +' '+sortindex)
        logins.limit(firstrecord-1, pagesize)
        for logins in logins.iterate():
            loginsDict = {}
            loginsDict[toHexForXml('~~id')] = logins.userName
            loginsDict[toHexForXml(u"Имя пользователя")] = logins.userName
            if subjects.tryGet(logins.subjectId):
                loginsDict["Субъект"] = subjects.name
            else:
                loginsDict["Субъект"] = ""
            loginsDict['properties'] = {"event":{"@name":"row_single_click",
                                                "action":{"#sorted":[{"main_context": 'current'},
                                                                     {"datapanel":{"@type":"current",
                                                                                   "@tab":"current"}
                                                                      }]
                                                          }
                                                }
                                       }
            data["records"]["rec"].append(loginsDict)
    else: #ft
        columnsDict={u"Имя пользователя":"userName"}
        subjects=subjectsCursor(context)
        for column in sortColumnList:
            sortindex = '%s' % column.getSorting()
            logins.orderBy(columnsDict[column.getId()] +' '+sortindex)
        logins.limit(firstrecord-1, pagesize)
        for logins in logins.iterate():
            loginsDict = {}
            loginsDict[toHexForXml('~~id')] = logins.userName
            loginsDict[toHexForXml(u"Имя пользователя")] = logins.userName
            if isEmployees:
                loginsDict["Сотрудник"] = ""
                if subjects.tryGet(logins.subjectId):
                    if employees.tryGet(subjects.employeeId):
                        loginsDict["Сотрудник"] = getattr(employees, employeesName)  
            
                
            loginsDict['properties'] = {"event":{"@name":"row_single_click",
                                                "action":{"#sorted":[{"main_context": 'current'
                                                                      },
                                                                     {"datapanel":{"@type":"current",
                                                                                   "@tab":"current"}
                                                                      }]
                                                          }
                                                }
                                       }
            data["records"]["rec"].append(loginsDict)
            
    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)

def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''
    settings=Settings()
    totalcount=0   

    if settings.isUseAuthServer():        
        server=SecurityParamsFactory.getAuthServerUrl()        
        sessionId=json.loads(session)["sessioncontext"]["sessionid"]
        logins_xml=func.getUsersFromAuthServer(server, sessionId)
        totalcount=len(logins_xml.getElementsByTagName("user"))
    else:
        logins = loginsCursor(context)
        # Вычисляем количества записей в таблице
        totalcount = logins.count()
    # Заголовок таблицы
    header_str = "Пользователи"
    # В случае если таблица пустая
    if totalcount == 0 or totalcount is None:
        totalcount = "0"
        header_str = header_str + " ПУСТ"

    # Определяем список полей таблицы для отображения    
    columns={"Имя пользователя":320}
    if settings.loginIsSubject() and settings.isEmployees():
        columns["Сотрудник"]=640
    elif not settings.loginIsSubject():
        columns["Субъект"]=640
    if settings.isUseAuthServer():
        columns["SID"]=320
    
    gridSettings = func.generateGridSettings(columns, totalCount=totalcount, header=header_str, \
                                         gridHeight = getGridHeight(session, numberOfGrids = 1 if settings.loginIsSubject() else 2), \
                                         datapanelWidth = getGridWidth(session))
    # Добавляем поля для отображения в gridsettings
    res = XMLJSONConverter.jsonToXml(json.dumps(gridSettings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''
    settings=Settings()

    #raise Exception(session)
    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext'] and not settings.isUseAuthServer():    
        style_add = "false"
        style_edit = "true"
        style_delete = "true"
        style_roles = "true"        
    elif not settings.isUseAuthServer():
        style_add = "false"
        style_edit = "false"
        style_delete = "false"
        if settings.loginIsSubject():
            style_roles = "false"
        else:
            style_roles = "true"
    elif 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style_add = "true"
        style_edit = "true"
        style_delete = "true"
        style_roles = "true"
    else:
        style_add = "true"
        style_edit = "false"
        if settings.loginIsSubject():
            style_roles = "false"
        else:
            style_roles = "true"
        style_delete = "true"
        

    data = {"gridtoolbar":{"item":[{"@img": 'gridToolBar/addDirectory.png',
                                    "@text":"Добавить",
                                    "@hint":"Добавить пользователя",
                                    "@disable": style_add                                    
                                    },
                                   {"@img": 'gridToolBar/editDocument.png',
                                    "@text":"Редактировать",
                                    "@hint":"Редактировать пользователя",
                                    "@disable": style_edit                                    
                                    },
                                   {"@img": 'gridToolBar/deleteDocument.png',
                                    "@text":"Удалить",
                                    "@hint":"Удалить пользователя",
                                    "@disable": style_delete
                                    },
                                   {"@img": 'gridToolBar/addDirectory.png',
                                    "@text":"Добавить роли",
                                    "@hint":"Добавить роли",
                                    "@disable": style_roles
                                    }]
                           }
            }
    
    if style_add=="false":
        data["gridtoolbar"]["item"][0]["action"]=func.getActionJSON("add", "usersXform", "Добавление пользователя", "350", "500")    
    if style_edit=="false":
        data["gridtoolbar"]["item"][1]["action"]=func.getActionJSON("edit", "usersXform", "Редактирование пользователя", "350", "500")    
    if style_delete=="false":
        data["gridtoolbar"]["item"][2]["action"]=func.getActionJSON("delete", "usersXformDelete", "Удаление пользователя", "150", "450")
    if style_roles=="false":
        data["gridtoolbar"]["item"][3]["action"]=func.getActionJSON("roles", "usersRolesXform", "Добавление ролей", "350", "500")
        
    
    #raise Exception(data)    

    return XMLJSONConverter.jsonToXml(json.dumps(data))

