# coding: utf-8
'''
Created on 29.10.2014

@author: m.prudyvus
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

def archiveTasksFilter(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "info":
                        {"@task": "",
                         "@process": "",
                         "@dateFrom": "",
                         "@dateTo": "",
                         "@show": "0"
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
                                        {"@id": "tasksGrid",
                                         "add_context": 'current'
                                         }
                                     }
                                 }
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def activeTasksFilter(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "info":
                        {"@task": "",
                         "@process": "",
                         "@show": "0"
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
                                        {"@id": "tasksGrid",
                                         "add_context": 'current'
                                         }
                                     }
                                 }
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def allActiveTasksFilter(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "info":
                        {"@task": "",
                         "@process": "",
                         "@dateFrom": "",
                         "@dateTo": "",
                         "@assignee": "",
                         "@show": "0"
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
                                        {"@id": "tasksGrid",
                                         "add_context": 'current'
                                         }
                                     }
                                 }
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def activeTasksByProcIdFilter(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":
                    {"@xmlns":"",
                     "info":
                        {"@task": "",
                         "@assignee": "",
                         "@show": "0"
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
                                        {"@id": "tasksGrid",
                                         "add_context": 'current'
                                         }
                                     }
                                 }
                           }]
                         }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)
