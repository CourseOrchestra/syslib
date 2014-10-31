# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus
'''

from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json

def archiveTasks(context, main=None, session=None):
    data = {"datapanel":{"tab":{"@id":"1",
                                "@name":u"Список задач",
                                "element":[{"@id":"tasksFilter",
                                            "@type":"xforms",
                                            "@template": "tasksFilter.xml",
                                            "@proc":"workflow.xforms.tasksFilter.archiveTasksFilter.celesta",
                                            },
                                           {"@id":"tasksGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.archiveTasksGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{"@id":"tasksFilter"}
#                                             "proc":[{
#                                                     "@id":1,
#                                                     "@name":"workflow.grid.activeTasksGrid.gridToolBar.celesta",
#                                                     "@type":"TOOLBAR"}]
                                            },
                                           {"@id":"tasksImage",
                                            "@type":"webtext",
                                            "@hideOnLoad":"true",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.webtext.tasksImage.webtextData.celesta",
                                            "related":{"@id":"tasksGrid"}
                                            }
                                           ]
                                }
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))
