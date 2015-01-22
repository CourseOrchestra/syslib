# coding: utf-8

'''
Created on 21.10.2014

@author: m.prudyvus
'''

from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json
from workflow.processUtils import getLinkPermisson

def activeTasks(context, main=None, session=None):
    data = {"datapanel":{"tab":{"@id":"1",
                                "@name":u"Список задач",
                                "element":[{"@id":"tasksFilter",
                                            "@type":"xforms",
                                            "@template": "workflow/tasksFilter.xml",
                                            "@proc":"workflow.xforms.tasksFilter.activeTasksFilter.celesta",
                                            },
                                           {"@id":"tasksGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.activeTasksGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "@refreshByTimer":"false",
                                            "@refreshInterval":"20",
                                            "proc": {"@id": "tasksSettings",
                                                     "@name": "workflow.grid.activeTasksGrid.getSettings.celesta",
                                                     "@type": "METADATA"},
                                            "related":{"@id":"tasksFilter"}
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
                                            },
                                           {"@id":"reassign",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@template": "workflow/tasksReassign.xml",
                                            "@proc":"workflow.xforms.tasksReassign.cardData.celesta",
                                            "related":{"@id":"tasksGrid"},
                                            "proc": {"@id": "1",
                                                     "@name": "workflow.xforms.tasksReassign.cardDataSave.celesta",
                                                     "@type": "SAVE"}
                                            },
                                            {"@id":"viewComments",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@template": "workflow/viewComments.xml",
                                            "@proc":"workflow.xforms.viewComments.cardData.celesta",
                                            "related":{"@id":"tasksGrid"}
                                            }
                                           ]
                                }
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def allActiveTasks(context, main=None, session=None):
    data = {"datapanel":{"tab":{"@id":"1",
                                "@name":u"Список задач",
                                "element":[{"@id":"tasksFilter",
                                            "@type":"xforms",
                                            "@template": "workflow/tasksFilter.xml",
                                            "@proc":"workflow.xforms.tasksFilter.allActiveTasksFilter.celesta",
                                            },
                                           {"@id":"tasksGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.allActiveTasksGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "@refreshByTimer":"false",
                                            "@refreshInterval":"20",
                                            "related":{"@id":"tasksFilter"},
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.allActiveTasksGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"},
                                                    {"@id": "tasksSettings",
                                                     "@name": "workflow.grid.allActiveTasksGrid.getSettings.celesta",
                                                     "@type": "METADATA"}]
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
                                            },
                                           {"@id":"reassign",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@template": "workflow/tasksReassign.xml",
                                            "@proc":"workflow.xforms.tasksReassign.cardData.celesta",
                                            "related":{"@id":"tasksGrid"},
                                            "proc": {"@id": "1",
                                                     "@name": "workflow.xforms.tasksReassign.cardDataSave.celesta",
                                                     "@type": "SAVE"}
                                            }
                                           ]
                                }
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def archiveTasks(context, main=None, session=None):
    data = {"datapanel":{"tab":{"@id":"1",
                                "@name":u"Список задач",
                                "element":[{"@id":"tasksFilter",
                                            "@type":"xforms",
                                            "@template": "workflow/tasksFilter.xml",
                                            "@proc":"workflow.xforms.tasksFilter.archiveTasksFilter.celesta",
                                            },
                                           {"@id":"tasksGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.archiveTasksGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "@refreshByTimer":"false",
                                            "@refreshInterval":"20",
                                            "proc": {"@id": "tasksSettings",
                                                     "@name": "workflow.grid.activeTasksGrid.getSettings.celesta",
                                                     "@type": "METADATA"},
                                            "related":{"@id":"tasksFilter"}
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


def standardCompleteTask(context, main=None, session=None):
    u'''Датапанель стандартного завершения задачи'''
    data = {"datapanel":
            {"tab":
             {"@id":"completeTask",
              "@name":u"Завершение задачи",
              "element":
                [{"@id":"completeTaskCard",
                  "@type":"xforms",
                  "@proc":"workflow.xforms.standardCompleteTaskCard.cardData.celesta",
                  "@template":"workflow/standardCompleteTaskCard.xml",
                  "proc":
                    [{"@id":"completeTaskCardSave",
                      "@name":"workflow.xforms.standardCompleteTaskCard.cardDataSave.celesta",
                      "@type":"SAVE"}]}]}}}
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def standardCompleteTaskWithStatus(context, main=None, session=None):
    u'''Датапанель стандартного завершения задачи'''
    data = {"datapanel":
            {"tab":
             {"@id":"completeTask",
              "@name":u"Завершение задачи",
              "element":
                [{"@id":"completeTaskCard",
                  "@type":"xforms",
                  "@proc":"workflow.xforms.standardCompleteTaskStCard.cardData.celesta",
                  "@template":"workflow/standardCompleteTaskStCard.xml",
                  "proc":
                    [{"@id":"completeTaskCardSave",
                      "@name":"workflow.xforms.standardCompleteTaskStCard.cardDataSave.celesta",
                      "@type":"SAVE"}]}]}}}
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def drawTasksByProcId(context, main=None, session=None):
    u'''Датапанель отрисовки таблицы активных задач'''
    session = json.loads(session)["sessioncontext"]
    sid = session["sid"]
    if isinstance(session['urlparams']['urlparam'], list):
        for params in session['urlparams']['urlparam']:
            if params['@name'] == 'processId':
                processInstanceId = params['@value'][0]
    if not getLinkPermisson(context, sid, 'table', None, processInstanceId, None):
        return context.error(u'У Вас нет разрешения на просмотр данной страницы')
    data = {"datapanel":
            {"tab":
             [{"@id":"activeTasks",
               "@name":u"Активные задачи",
               "element":
                [{"@id":"tasksFilter",
                "@type":"xforms",
                "@template": "workflow/tasksFilter.xml",
                "@proc":"workflow.xforms.tasksFilter.activeTasksByProcIdFilter.celesta",
                },
               {"@id":"tasksGrid",
                "@type":"grid",
                "@proc":"workflow.grid.activeTasksByProcIdGrid.gridDataAndMeta.celesta",
                "@subtype":"JS_LIVE_GRID",
                "@plugin":"liveDGrid",
                "related":{"@id":"tasksFilter"},
#                 "proc":[{
#                         "@id":1,
#                         "@name":"workflow.grid.activeTasksByProcIdGrid.gridToolBar.celesta",
#                         "@type":"TOOLBAR"}]
                }]}]}}
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def approveTask(context, main=None, session=None):
    u'''Датапанель утверждения задачи'''
    data = {"datapanel":
            {"tab":
             {"@id":"completeTask",
              "@name":u"Утверждение задачи",
              "element":
                [{"@id":"approveTaskCard",
                  "@type":"xforms",
                  "@proc":"workflow.xforms.approveTaskCard.cardData.celesta",
                  "@template":"workflow/approveTaskCard.xml",
                  "proc":
                    [{"@id":"approveTaskCardSave",
                      "@name":"workflow.xforms.approveTaskCard.cardDataSave.celesta",
                      "@type":"SAVE"}]}]}}}
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def reworkDoc(context, main=None, session=None):
    u'''Датапанель утверждения задачи'''
    data = {"datapanel":
            {"tab":
             {"@id":"reworkDoc",
              "@name":u"Отправка на согласование",
              "element":
                [{"@id":"reworkDocCard",
                  "@type":"xforms",
                  "@proc":"workflow.xforms.reworkDocCard.cardData.celesta",
                  "@template":"workflow/reworkDocCard.xml",
                  "proc":
                    [{"@id":"reworkDocCardSave",
                      "@name":"workflow.xforms.reworkDocCard.cardDataSave.celesta",
                      "@type":"SAVE"}]}]}}}
    return XMLJSONConverter.jsonToXml(json.dumps(data))