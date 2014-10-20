# coding: utf-8


import simplejson as json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security._security_orm import rolesCustomPermsCursor

def cardData(context, main, add, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}}
    xformssettings = {"properties":{"event":[{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"rolesCustomPermissionsGrid",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardDelete(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    rolesPermission = rolesCustomPermsCursor(context)
    related=json.loads(session)['sessioncontext']['related']['gridContext']    
    currId={}
    for g_context in related:
        if 'currentRecordId' in g_context.keys():
            currId[g_context["@id"]]=g_context["currentRecordId"]
    rolesPermission.get(currId["rolesCustomPermissionsGrid"], currId["customPermissionsGrid"])
    rolesPermission.delete()