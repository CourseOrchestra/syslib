# coding: utf-8
'''
Created on 03.12.2013

@author: d.bozhenko

'''
import json
from java.util import ArrayList

from ru.curs.celesta import CelestaException
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from ru.curs.celesta.syscursors import RolesCursor
from security._security_orm import rolesCustomPermsCursor


try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import JythonDTO
    #from ru.curs.celesta.showcase import ResultSelectorData
    #from ru.curs.celesta.showcase import DataRecord

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого таблицы ролей. '''    
    #roles = RolesCursor(context)
    
    related=json.loads(session)['sessioncontext']['related']['gridContext']
    #related = related if isinstance(related, list) else [related]
    currId={}
    for g_context in related:
        if 'currentRecordId' in g_context.keys():
            #raise Exception(session)
            currId[g_context["@id"]]=g_context["currentRecordId"]
                
    if add == 'add':
        xformsdata = {"schema":{"role_permission":{"@permission_id":currId["customPermissionsGrid"],
                                                   "@roleid":""}
                                }
                      }
    elif add == 'edit':        
        xformsdata = {"schema":{"role_permission":{"@permission_id":currId["customPermissionsGrid"],
                                                   "@roleid":currId["rolesCustomPermissionsGrid"]}
                                }
                      }
    #raise Exception(xformsdata)

    #print xformsdata
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"rolesCustomPermissionsGrid",
                                                                                 "add_context": ""}
                                                                     }
                                                       }
                                             }
                                    }
                      }

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника ролей. '''     
    rolesPermission = rolesCustomPermsCursor(context)
    related=json.loads(session)['sessioncontext']['related']['gridContext']
    #related = related if isinstance(related, list) else [related]
    currId={}
    for g_context in related:
        if 'currentRecordId' in g_context.keys():
            currId[g_context["@id"]]=g_context["currentRecordId"]

    content = json.loads(xformsdata)["schema"]["role_permission"]
    rolesPermission.roleid=content["@roleid"]
    rolesPermission.permissionId=content["@permission_id"]
    if rolesPermission.canInsert() and rolesPermission.canModify():        
        if add=='edit':
            rolesPermissionOld = rolesCustomPermsCursor(context)
            if rolesPermissionOld.tryGet(currId["rolesCustomPermissionsGrid"], currId["customPermissionsGrid"]):
                rolesPermission.recversion = rolesPermissionOld.recversion
                if rolesPermissionOld.canDelete():
                    rolesPermissionOld.delete()
                else:
                    raise CelestaException(u"Данная роль уже назначена для данного разрешения!")
        if not rolesPermission.tryInsert():
            rolesPermission.update()
    elif rolesPermission.canInsert():
        if add=='edit':
            rolesPermissionOld = rolesCustomPermsCursor(context)
            if rolesPermissionOld.tryGet(currId["rolesCustomPermissionsGrid"], currId["customPermissionsGrid"]):
                rolesPermission.recversion = rolesPermissionOld.recversion
                if rolesPermissionOld.canDelete():
                    rolesPermissionOld.delete()
                else:
                    raise CelestaException(u"Данная роль уже назначена для данного разрешения!")
        rolesPermission.tryInsert()
    elif rolesPermission.canModify():
        rolesPermissionOld = rolesCustomPermsCursor(context)
        rolesPermissionOld.get(currId["rolesCustomPermissionsGrid"], currId["customPermissionsGrid"])
        rolesPermission.recversion = rolesPermissionOld.recversion
        rolesPermission.update()
    else:
        raise CelestaException(u"Недостаточно прав для данной операции!")


def rolesCount(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=False):
    roles = RolesCursor(context)
    roles.setFilter('description', "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))
    count = roles.count()    
    return ResultSelectorData(None, count)

def rolesList(context, main=None, add=None, filterinfo=None, session=None, params=None,
                curvalue="", startswith=False, firstrecord=0, recordcount=None):
    u'''Функция list селектора типа элемента. '''   
    #raise Exception(curvalue)
    recordList = ArrayList()
    roles = RolesCursor(context)
    roles.setFilter('description', "@%s'%s'%%" % ("%"*(not startswith), curvalue.replace("'","''")))
    roles.orderBy('description')
    roles.limit(firstrecord, recordcount)    
    if roles.tryFindSet():
        while True:            
            rec = DataRecord()
            rec.setId(roles.id)
            rec.setName('%s - %s' % (roles.id, roles.description if roles.description else ''))
            recordList.add(rec)
            if not roles.nextInSet():
                break
    return ResultSelectorData(recordList, 0)