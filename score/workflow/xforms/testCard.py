# coding: utf-8
'''
Created on 03.12.2013

@author: v.popov

'''
import simplejson as json
from java.util import ArrayList
try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import JythonDTO, DataRecord, ResultSelectorData



from ru.curs.celesta import CelestaException
from ru.curs.celesta.showcase.utils import XMLJSONConverter
# from dirusing.commonfunctions import relatedTableCursorImport
from kurs._kurs_orm import employeesCursor, workingTimeCursor, projectsCursor

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого таблицы типоа разрешений. '''
    
    #raise Exception(session)
    
    employees = employeesCursor(context)    

    if add == 'add':
        
        sid = json.loads(session)['sessioncontext']['sid']
        employees.get(sid)
        xformsdata = {"schema":{"context":{"@nameId":sid,
                                           "@name":employees.fio,
                                           "@date":"",
                                           "@projectId":"",
                                           "@project":"",
                                           "@start":"",
                                           "@finish":"",
                                           "@time":"",
                                           "@place":"",
                                           "@typeTime":""}
                                }
                      }
    elif add == 'edit' or add == 'clone':
        workingTime = workingTimeCursor(context)
        projects = projectsCursor(context)
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        workingTime.get(currId)
        employees.get(workingTime.employeeId)
        projects.get(workingTime.projectId)
        xformsdata = {"schema":{"context":{"@nameId":workingTime.employeeId,
                                           "@name":employees.fio,
                                           "@date":workingTime.date,
                                           "@projectId":workingTime.projectId,
                                           "@project":projects.name,
                                           "@start":workingTime.start,
                                           "@finish":workingTime.finish,
                                           "@time":workingTime.time,
                                           "@place":workingTime.place,
                                           "@typeTime":""}
                                }
                      }
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"#sorted":[{"main_context": "current"},
                                                                   {"datapanel": {"@type": "current",
                                                                                 "@tab": "current",
                                                                                 "element": {"@id":"time_grid",
                                                                                             "add_context": ""}
                                                                                 }
                                                                   }]}
                                             }
                                    }
                      }
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    workingTime = workingTimeCursor(context)
    content = json.loads(xformsdata)["schema"]["context"]
    workingTime.employeeId = content['@nameId']
    workingTime.date = content['@date']
    workingTime.projectId = content['@projectId']
    workingTime.start = content['@start']
    workingTime.finish = content['@finish']
    workingTime.time = content['@time']
    workingTime.place = content['@place']

    if add in ['add', 'clone'] and workingTime.canInsert() and workingTime.canModify():
        if not workingTime.tryInsert():
            workingTime.update()
    elif add in ['add', 'clone'] and workingTime.canInsert():
        workingTime.insert()
    elif add == 'edit' and workingTime.canModify():        
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']        
        workingTime.uid = currId
        workingTime.update()                
    else:
        raise CelestaException(u"Недостаточно прав для данной операции!")
    
    
def employeesCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None):

    employees = employeesCursor(context)
    
    employees.setFilter('fio', """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    count = employees.count()
    return ResultSelectorData(None, count)

def employeesList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    
    employees = employeesCursor(context)
    employees.setFilter('fio', """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    employees.orderBy('fio')
    employees.limit(firstrecord, recordcount)

    recordList = ArrayList()
    for employees in employees.iterate():
        rec = DataRecord()
        rec.setId(unicode(employees.uid))
        rec.setName(employees.fio)
        recordList.add(rec)
    return ResultSelectorData(recordList, 0)

def projectsCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None):

    projects = projectsCursor(context)
    
    projects.setFilter('name', """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    count = projects.count()
    return ResultSelectorData(None, count)

def projectsList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue=None, startswith=None, firstrecord=None, recordcount=None):
    
    projects = projectsCursor(context)
    projects.setFilter('name', """@%s'%s'%%""" % ("%"*(not startswith), curvalue.replace("'","''")))
    projects.orderBy('name')
    projects.limit(firstrecord, recordcount)
    recordList = ArrayList()
    for projects in projects.iterate():
        rec = DataRecord()
        rec.setId(unicode(projects.uid))
        rec.setName(projects.name)
        recordList.add(rec)
    return ResultSelectorData(recordList, 0)