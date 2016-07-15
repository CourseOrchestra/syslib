# coding: utf-8
'''
Created on 02.03.2016
HTML подсказки
@author: a.rudenko
'''
import json

from com.jayway.jsonpath import JsonPath
from common._common_orm import htmlHintsCursor, htmlHintsUsersCursor
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security.functions import userHasPermission
try:
    from org.apache.commons.lang3.StringEscapeUtils import unescapeHtml4
except:
    pass
from xml.sax import make_parser, handler, ContentHandler
import StringIO

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


def htmlHintElement(elementId):
    htmlHint = {
        '@id': elementId,
        '@type': 'xforms',
        '@proc': 'common.htmlhints.htmlHint.cardData.celesta',
        #'@template': 'common/htmlHints/htmlHint.xml',
        '@template': 'common.htmlhints.htmlHintXForm.xformTemplate.celesta',
        '@hideOnLoad': 'false',
        'proc': {
            '@id': 'save',
            '@name': 'common.htmlhints.htmlHint.cardSave.celesta',
            '@type': 'SAVE'
        }
    }
    return htmlHint


def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Карточка HTML подсказки'''
    sid = JsonPath.read(session, "$.sessioncontext.sid")
    htmlHints = htmlHintsCursor(context)
    htmlHintsUsers = htmlHintsUsersCursor(context)
    
    if htmlHints.tryGet(elementId):
        htmlText = htmlHints.htmlText
        if htmlText is not None:
            htmlText = htmlText
        else:
            htmlText = u""
            showOnLoad = 0
        showOnLoad = htmlHints.showOnLoad
        fullScreen = htmlHints.fullScreen
        if showOnLoad == 1: 
            showOnLoad='true' 
        else:
            showOnLoad='false'
        if fullScreen == 1: 
            fullScreen='true' 
        else:
            fullScreen='false'
    else:
        htmlText = u""
        fullScreen='false'
        showOnLoad = 'true'
        htmlHints.elementId = elementId
        htmlHints.htmlText = htmlText
        htmlHints.showOnLoad = 1
        htmlHints.fullScreen = 0
        htmlHints.tryInsert()
    if userHasPermission(context, sid, 'htmlHintsEdit'):
        userPerm = 1
    else:
        userPerm = 0
    
    if htmlHintsUsers.tryGet(elementId, sid):
        showHideHint = htmlHintsUsers.showOnLoad
        if showHideHint == 1: 
            showHideHint='true' 
        else:
            showHideHint='false'
    else:
        showHideHint  = showOnLoad
    xformsdata = {
        "schema": {
            "@xmlns": "",
            "elementId":elementId,
            "htmlText": unescapeHtml4(htmlText),
            "showHideHint": showHideHint,
            "showOnLoad": showOnLoad,
            "showHideEdit": 0,
            "userPerm": userPerm,
            "fullScreen": fullScreen
        }
    }

    xformssettings = {
        "properties": {
            "event": [
                {
                    "@name": "single_click",
                    "@linkId": "1",
                    "action": {
                        "@keep_user_settings": "true",
                        "main_context": "current",
                        "datapanel": {
                            "@type": "current",
                            "@tab": "current"
                        }
                    }
                }
            ]
        }
    }

    return JythonDTO((XMLJSONConverter.jsonToXml(json.dumps(xformsdata))),
                     XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardSave(context, main=None, add=None, filterinfo=None, session=None,
             elementId=None, xformsdata=None):
    u'''Сохранение HTML подсказки'''
    htmlHints = htmlHintsCursor(context)

    htmlText = json.loads(xformsdata)["schema"]["htmlText"]
    showOnLoad = json.loads(xformsdata)["schema"]["showOnLoad"]
    fullScreen = json.loads(xformsdata)["schema"]["fullScreen"]
    if showOnLoad == 'true': 
        showOnLoad=1 
    else:
        showOnLoad=0
    if fullScreen == 'true': 
        fullScreen=1 
    else:
        fullScreen=0
    if htmlHints.tryGet(elementId):
        htmlHints.htmlText = htmlText
        htmlHints.showOnLoad = showOnLoad
        htmlHints.fullScreen = fullScreen
        htmlHints.update()
    else:
        htmlHints.elementId = elementId
        htmlHints.htmlText = htmlText
        htmlHints.showOnLoad = showOnLoad
        htmlHints.fullScreen = fullScreen
        htmlHints.insert()

class parserSAXHandlerhtmlEdit(ContentHandler):
    def __init__(self):
        self.firstDiv = False

def htmlEdit(context, main, add, filterinfo, session, elementId):
    jsonData = json.loads(filterinfo)
    htmlText = jsonData['schema']['filter']['htmlText']
    data = htmlText
    try:
        parser = make_parser()
        handler = parserSAXHandlerhtmlEdit()
        parser.setContentHandler(handler)
        parser.parse(StringIO.StringIO(unescapeHtml4(data).encode('utf8')))
    except:
        data = "<div>%s</div>" % data
        pass
    settings = u'''
    <properties>
    </properties>
    '''
    
    res = JythonDTO(unescapeHtml4(data), settings)
    return res
    
def showOnLoadSave(context, main=None, add=None, filterinfo=None, session=None, xformsdata=None):
    u'''функция сабмишна для проверки СНИЛС.'''
    showHideHint = json.loads(xformsdata)["schema"]["showHideHint"]
    elementId = json.loads(xformsdata)["schema"]["elementId"]
    sid = JsonPath.read(session, "$.sessioncontext.sid")
    htmlHintsUsers = htmlHintsUsersCursor(context)
    #raise Exception (main, add, filterinfo, session, xformsdata)
    if showHideHint == 'true': 
        showHideHint=1 
    else:
        showHideHint=0
    if htmlHintsUsers.tryGet(elementId,sid):
        htmlHintsUsers.showOnLoad = showHideHint
        htmlHintsUsers.update()
    else:
        htmlHintsUsers.elementId = elementId
        htmlHintsUsers.sid = sid
        htmlHintsUsers.showOnLoad = showHideHint
        htmlHintsUsers.insert()
    return xformsdata