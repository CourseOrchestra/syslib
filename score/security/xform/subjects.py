# coding: utf-8
'''
@author: d.bozhenko

'''
import json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from ru.curs.celesta import CelestaException
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security._security_orm import subjectsCursor
from security.functions import id_generator
from common.numbersseries.getNextNo import getNextNoOfSeries


def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого таблицы ролей. '''
    subjects = subjectsCursor(context)    
    #base64.b64encode(json.dumps([permissions.roleId, permissions.grainId, permissions.tablename]))    
    #raise Exception(add)
    if add == 'add':        
        sid = getNextNoOfSeries(context, 'subjects') + id_generator()
        xformsdata = {"schema":{"@xmlns":"",
                                "subject":{"@name": "",
                                            "@sid": sid}
                                }
                      }
        #raise Exception(add)
    elif add == 'edit':        
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        #currId = json.loads(base64.b64decode(currIdEncoded))        
        subjects.get(currId)        
        xformsdata = {"schema":{"subject":{"@name": subjects.name,
                                           "@sid": subjects.sid}
                                }
                      }    
    #print xformsdata
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",                                                       
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"subjectsGrid",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }
    #raise Exception(xformsdata)
    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника ролей. '''
    subjects = subjectsCursor(context)
    #subjectsUsers = subjectsUsersCursor(context)
    content = json.loads(xformsdata)["schema"]["subject"]
    subjects.name = content["@name"]
    subjects.sid = content["@sid"]        

    if add == 'add' and subjects.canInsert() and subjects.canModify():        
        if not subjects.tryInsert():
            subjectsOld = subjectsCursor(context)
            subjectsOld.get(content["@sid"])
            subjects.recversion = subjectsOld.recversion
            subjects.update()
    elif add == 'add' and subjects.canInsert():
        subjects.insert()
    elif add == 'edit' and subjects.canModify():
        currId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        subjectsOld = subjectsCursor(context)
        subjectsOld.get(currId)
        subjectsOld.name = content["@name"]
        subjectsOld.sid = content["@sid"]        
        subjectsOld.update()          
    else:
        raise CelestaException(u"Недостаточно прав для данной операции!")