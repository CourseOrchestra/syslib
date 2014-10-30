# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus
'''

from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json

def allActiveTasks(context, main=None, session=None):
    data = {"datapanel":{"tab":{"@id":"1",
                                "@name":u"Список задач",
                                "element":[{"@id":"tasksFilter",
                                            "@type":"xforms",
                                            "@template": "tasksFilter.xml",
                                            "@proc":"workflow.xforms.tasksFilter.allActiveTasksFilter.celesta",
                                            },
                                           {"@id":"tasksGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.allActiveTasksGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{"@id":"tasksFilter"},
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.allActiveTasksGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}]
                                            },
                                           {"@id":"tasksImage",
                                            "@type":"webtext",
                                            "@hideOnLoad":"true",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.webtext.tasksImage.webtextData.celesta",
                                            "related":{"@id":"tasksGrid"}
                                            },
                                           {"@id":"taskStatusCard",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@template": "tasksStatus.xml",
                                            "@proc":"workflow.xforms.tasksStatus.cardData.celesta",
                                            "related":{"@id":"tasksGrid"},
                                            "proc": {"@id": "1",
                                                     "@name": "workflow.xforms.tasksStatus.cardDataSave.celesta",
                                                     "@type": "SAVE"}
                                            }
                                           ]
                                }
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))
