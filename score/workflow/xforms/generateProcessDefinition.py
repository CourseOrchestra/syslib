# coding: utf-8
'''
Created on 07.11.2014

@author: tr0glo)|(I╠╣
'''

import simplejson as json

from java.util import ArrayList

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord

from workflow.processUtils import ActivitiObject

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
    u'''Карточка выбора процесса'''
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "data":
                        {
                         "@processName": "",
                         "@processKey": "",
                         "@existing": "false"
                         }
                     }
                  }
    xformssettings = {"properties":
                        {"event":
                         [{"@name": "single_click",
                           "@linkId": "1",
                           "action":
                                {"main_context": "current",
                                 "datapanel":
                                    {"@type": "current",
                                     "@tab": "current",
                                     "element":
                                     [
                                        {"@id": 'matchingCircuitGrid',
                                         "add_context": 'current'
                                         },
                                      {"@id": 'generateProcessDefinition',
                                         "add_context": 'current'
                                         }
                                     ]
                                     }
                                 }
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)




