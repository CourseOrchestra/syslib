# coding: utf-8
'''
Created on 09.07.2014

@author: D.Bozhenko.
'''

import json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    pass

from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":'',
                            "context":{}
                            }
                  }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"#sorted":[{"main_context": "current"},
                                                        {"datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":{"@id": "test_card",
                                                                                "add_context": 'current'}
                                                                     }
                                                        }]}
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)


def cardSave(context, main, add, filterinfo, session, elementId, data):
    #здесь необходимо описать сохранение
    print 'Save xform data from Celesta Python procedure.'
    print 'User %s' % context.userId
    print 'main "%s".' % main
    print 'add "%s".' % add
    print 'filterinfo "%s".' % filterinfo
    print 'session "%s".' % session
    print 'elementId "%s".' % elementId
    print 'data "%s".' % data
