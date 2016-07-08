# coding: utf-8
'''
Created on 06.11.2014

@author: tr0glo)|(I╠╣
'''

import simplejson as json

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

def filterData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Фильтр процессов по названию'''
    if elementId == 'processFilter':
        gridId = 'processesGrid'
        descVisible = 'false'
    elif elementId == 'launchedProcessFilter':
        gridId = 'launchedProcessesGrid'
        descVisible = 'true'
    elif elementId == 'finishedProcessFilter':
        gridId = 'finishedProcessesGrid'
        descVisible = 'true'
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "info":
                        {
                         "@processName": "",
                         "@processDescription":"",
                         "@descVisible": descVisible,
                         "@show": "0"
                         }
                     }
                  }
    xformssettings = {"properties":
                        {"event":
                         [{"@name": "single_click",
                           "@linkId": "1",
                           "action":
                                {"#sorted":[{"main_context": "current"},
                                             {"datapanel":
                                                {"@type": "current",
                                                 "@tab": "current",
                                                 "element":
                                                    {"@id": gridId,
                                                     "add_context": 'current'
                                                     }
                                                 }
                                             }]}
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

