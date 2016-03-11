# coding: utf-8
'''
Created on 02.03.2016
HTML подсказки
@author: a.rudenko
'''
import hashlib
from java.text import SimpleDateFormat
import json
import re

from com.jayway.jsonpath import JsonPath
from common.numbersseries.getNextNo import getNextNoOfSeries
from common._common_orm import htmlHintsCursor
from nci.functions.persons import checkSnilsUnique, getPersonIdBySid
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security._security_orm import subjectsCursor, loginsCursor
from security.functions import userHasPermission


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def htmlHintElement(elementId):
    htmlHint = {
            '@id': elementId,
            '@type': 'xforms',
            '@proc': 'common.htmlhints.htmlHint.cardData.celesta',
            '@template':'common/htmlHints/htmlHint.xml',
            '@hideOnLoad':'false',
            'proc': {
                '@id':'save',
                '@name':'common.htmlhints.htmlHint.cardSave.celesta',
                '@type':'SAVE'
            }
        }
    return htmlHint

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка HTML подсказки'''
    sid = JsonPath.read(session, "$.sessioncontext.sid")
    htmlHints = htmlHintsCursor(context)
    if htmlHints.tryGet(elementId):
        htmlText = htmlHints.htmlText
        htmlText = htmlText.replace('&lt;', '<').replace('&gt;', '>').replace('&lt', '<').replace('&gt', '>').replace('&nbsp;', ' ')
        showOnLoad = htmlHints.showOnLoad
        if showOnLoad is None:
            showOnLoad=0
    else:
        htmlText = u""
        showOnLoad = 0
    if userHasPermission(context, sid, 'htmlHintsEdit'):
        userPerm=1
    else:
        userPerm = 0
    xformsdata = {"schema":
                      {"@xmlns":"",
                        "htmlText":htmlText,
                        "showHideHint":showOnLoad,
                        "showOnLoad":showOnLoad,
                        "showHideEdit":0,
                        "userPerm":userPerm
                        }
                  }

    xformssettings = {"properties":{"event":[{"@name":"single_click",
                                              "@linkId": "1",
                                              "action":{"@keep_user_settings": "true",
                                                        "main_context": "current",
                                                        "datapanel": {"@type": "current",
                                                                      "@tab": "current"
                                                                      }
                                                        }
                                              }]
                                    }
                      }

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)),
                     XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))

def cardSave(context, main=None, add=None, filterinfo=None, session=None,
             elementId=None, xformsdata=None):
    u'''Сохранение HTML подсказки'''
    htmlHints = htmlHintsCursor(context)
    
    htmlText = json.loads(xformsdata)["schema"]["htmlText"]
    showOnLoad = json.loads(xformsdata)["schema"]["showOnLoad"]
    if htmlHints.tryGet(elementId):
        htmlHints.htmlText = htmlText
        htmlHints.showOnLoad = showOnLoad
        htmlHints.update()
    else:
        htmlHints.elementId = elementId
        htmlHints.htmlText = htmlText
        htmlHints.showOnLoad = showOnLoad
        htmlHints.insert()

def htmlEdit(context, main, add, filterinfo, session, elementId):
    jsonData = json.loads(filterinfo)
    htmlText = jsonData['schema']['filter']['htmlText']
    data = htmlText.replace('&lt;', '<').replace('&gt;', '>').replace('&lt', '<').replace('&gt', '>').replace('&nbsp;', ' ')#.replace('&nbsp', ' ')
    settings = u'''
    <properties>
    </properties>
    '''
    #raise Exception(main, add, filterinfo, session, elementId)
    res = JythonDTO(data, settings)
    return res