# coding: utf-8

from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json
from workflow.processUtils import getLinkPermisson

def manageProcesses(context, main=None, session=None):
    data = {"datapanel":{"tab":[{"@id":"1",
                                "@name":u"Развёрнутые процессы",
                                "element":[{"@id":"processFilter",
                                            "@type":"xforms",
                                            "@template": "workflow/processFilter.xml",
                                            "@proc":"workflow.xforms.processFilter.filterData.celesta",
                                            },
                                           {"@id":"processesGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.processesGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.processesGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"},
                                                    {
                                                    "@id":2,
                                                    "@name":"workflow.grid.processesGrid.downloadProcFile.celesta",
                                                    "@type":"DOWNLOAD"},
                                                    {"@id": "processesMeta",
                                                     "@name": "workflow.grid.processesGrid.getMeta.celesta",
                                                     "@type": "METADATA"}],
                                            "related":{"@id":"processFilter"}
                                            },
                                           {"@id":"suspendAllProcessCard",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.xforms.suspendAllProcessCard.cardData.celesta",
                                            "@template":"workflow/suspendProcessCard.xml",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       },
                                            "proc":[
                                                    {
                                                    "@id":"suspendProcessCardSave",
                                                    "@name":"workflow.xforms.suspendAllProcessCard.cardSave.celesta",
                                                    "@type":"SAVE"}]

                                            },
                                           {"@id":"processFormsGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.processFormsGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       },
                                            "proc":[
                                                    {"@id": "processesMeta",
                                                     "@name": "workflow.grid.processFormsGrid.getMeta.celesta",
                                                     "@type": "METADATA"},
                                                    {
                                                    "@id":"processFormsGridToolBar",
                                                    "@name":"workflow.grid.processFormsGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}]

                                            },
                                           {"@id":"processFormCard",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.xforms.processFormCard.cardData.celesta",
                                            "@template":"workflow/processFormCard.xml",
                                            "related":[
                                                       {"@id":"processesGrid"},
                                                       {"@id":"processFormsGrid"}
                                                       ],
                                            "proc":[
                                                    {
                                                    "@id":"processFormCardSave",
                                                    "@name":"workflow.xforms.processFormCard.cardSave.celesta",
                                                    "@type":"SAVE"}]

                                            },
                                           {"@id":"processFormDeleteCard",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.xforms.processFormDeleteCard.cardData.celesta",
                                            "@template":"workflow/processFormDeleteCard.xml",
                                            "related":[
                                                       {"@id":"processesGrid"},
                                                       {"@id":"processFormsGrid"}
                                                       ],
                                            "proc":[
                                                    {
                                                    "@id":"processFormDeleteCardSave",
                                                    "@name":"workflow.xforms.processFormDeleteCard.cardSave.celesta",
                                                    "@type":"SAVE"}]

                                            },
                                           {"@id":"processesImage",
                                            "@type":"webtext",
                                            "@hideOnLoad":"true",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.webtext.processesImage.webtextData.celesta",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       }
                                            },
                                           {"@id":"processUploadCard",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.xforms.processUploadCard.cardData.celesta",
                                            "@template":"workflow/processUploadCard.xml",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       },
                                            "proc":[{
                                                    "@id":"processUpload",
                                                    "@name":"workflow.xforms.processUploadCard.processUpload.celesta",
                                                    "@type":"UPLOAD"},
                                                    {
                                                    "@id":"processUploadCardSave",
                                                    "@name":"workflow.xforms.processUploadCard.cardSave.celesta",
                                                    "@type":"SAVE"}]

                                            }
                                           ]
                                },
                                {"@id":"launchedProcesses",
                                "@name":u"Активные процессы",
                                "element":[{"@id":"launchedProcessFilter",
                                            "@type":"xforms",
                                            "@template": "workflow/processFilter.xml",
                                            "@proc":"workflow.xforms.processFilter.filterData.celesta",
                                            },
                                           {"@id":"launchedProcessesGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.launchedProcessesGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.launchedProcessesGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"},
                                                    {"@id": "processSettings",
                                                     "@name": "workflow.grid.launchedProcessesGrid.getSettings.celesta",
                                                     "@type": "METADATA"}
                                                    ],
                                            "related":{"@id":"launchedProcessFilter"}
                                            },
                                           {"@id":"launchedProcessImage",
                                            "@type":"webtext",
                                            "@hideOnLoad":"true",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.webtext.launchedProcessImage.webtextData.celesta",
                                            "related":{
                                                       "@id":"launchedProcessesGrid"
                                                       }
                                            },
                                           {"@id":"suspendProcessCard",
                                            "@type":"xforms",
                                            "@neverShowInPanel":"true",
                                            "@proc":"workflow.xforms.suspendProcessCard.cardData.celesta",
                                            "@template":"workflow/suspendProcessCard.xml",
                                            "related":{
                                                       "@id":"launchedProcessesGrid"
                                                       },
                                            "proc":[
                                                    {
                                                    "@id":"suspendProcessCardSave",
                                                    "@name":"workflow.xforms.suspendProcessCard.cardSave.celesta",
                                                    "@type":"SAVE"}]

                                            },
                                            {"@id":"launchedProcessesEventsGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.launchedProcessesEventsGrid.getData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"launchedProcessesGrid"
                                                       },
                                            "proc":[{"@id": "launchedProcessesEventsMeta",
                                                     "@name": "workflow.grid.launchedProcessesEventsGrid.getMeta.celesta",
                                                     "@type": "METADATA"},
                                                    {
                                                    "@id":1,
                                                    "@name":"workflow.grid.launchedProcessesEventsGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}
                                                    ]
                                            }

                                           ]
                                },
                                {"@id":"finishedProcesses",
                                "@name":u"Завершённые процессы",
                                "element":[{"@id":"finishedProcessFilter",
                                            "@type":"xforms",
                                            "@template": "workflow/processFilter.xml",
                                            "@proc":"workflow.xforms.processFilter.filterData.celesta",
                                            },
                                           {"@id":"finishedProcessesGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.finishedProcessesGrid.gridData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.finishedProcessesGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"},
                                                    {"@id": "finishedProcessMeta",
                                                     "@name": "workflow.grid.finishedProcessesGrid.getSettings.celesta",
                                                     "@type": "METADATA"}
                                                    ],
                                            "related":{"@id":"finishedProcessFilter"}
                                            },
                                            {"@id":"finishedProcessEventsGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.finishedProcessEventsGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"finishedProcessesGrid"
                                                       },
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.finishedProcessEventsGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}
                                                    ]
                                            }

                                           ]
                                }
                                ]
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def editingProcesses(context, main=None, session=None):
    u'''Датапанель редактирования процессов'''
    data = {"datapanel":{"tab":[ {"@id":"editProcess",
                                "@name":u"Конструктор процессов",
                                "element":[
                                           {"@id":"selectionProcess",
                                            "@type":"xforms",
                                            "@proc":"workflow.xforms.selectionProcess.cardData.celesta",
                                            "@template":"workflow/selectionProcessCard.xml",
                                            "proc":[
                                                    {
                                                    "@id":"selectionProcessSave",
                                                    "@name":"workflow.xforms.selectionProcess.cardSave.celesta",
                                                    "@type":"SAVE"}]
                                            },
                                           {"@id":"matchingCircuitGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.matchingCircuitGrid.treeGridData.celesta",
                                            "@subtype":"JS_TREE_GRID",
                                            "@plugin":"treeDGrid",
                                            "related":{
                                                       "@id":"selectionProcess"
                                                       },
                                            "proc":[
                                                    {"@id":1,
                                                    "@name":"workflow.grid.matchingCircuitGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"},
                                                    {"@id": "matchingCircuitMeta",
                                                    "@name":"workflow.grid.matchingCircuitGrid.treeGridMeta.celesta",
                                                     "@type": "METADATA"}
                                                    ]
                                            },
                                           {"@id":"generateProcessImage",
                                            "@hideOnLoad":"true",
                                            "@type":"webtext",
                                            "@proc":"workflow.webtext.generateProcessImage.webtextData.celesta",
                                            "related":{
                                                       "@id":"selectionProcess"
                                                       }
                                            },
                                           {"@id":"generateProcessDefinition",
                                            "@hideOnLoad":"true",
                                            "@type":"xforms",
                                            "@proc":"workflow.xforms.generateProcessDefinition.cardData.celesta",
                                            "@template":"workflow/generateProcessDefinition.xml",
                                            "related":{
                                                       "@id":"selectionProcess"
                                                       },
                                            "proc":[
                                                    {
                                                    "@id":"deployProcess",
                                                    "@name":"workflow.xforms.generateProcessDefinition.cardSave.celesta",
                                                    "@type":"SAVE"}]
                                            },
                                           {"@id":"addMatcher",
                                            "@neverShowInPanel":"true",
                                            "@type":"xforms",
                                            "@proc":"workflow.xforms.addMatcher.cardData.celesta",
                                            "@template":"workflow/addMatcherCard.xml",
                                            "related":{
                                                       "@id":"matchingCircuitGrid"
                                                       },
                                             "proc":[
                                                    {
                                                    "@id":"addMatcherSave",
                                                    "@name":"workflow.xforms.addMatcher.cardSave.celesta",
                                                    "@type":"SAVE"}]
                                            },
                                           {"@id":"moveRight",
                                            "@neverShowInPanel":"true",
                                            "@type":"xforms",
                                            "@proc":"workflow.xforms.moveRightCard.cardData.celesta",
                                            "@template":"workflow/moveRightCard.xml",
                                            "related":{
                                                       "@id":"matchingCircuitGrid"
                                                       },
                                             "proc":[
                                                    {
                                                    "@id":"moveRightSave",
                                                    "@name":"workflow.xforms.moveRightCard.cardSave.celesta",
                                                    "@type":"SAVE"}]
                                            },
                                           {"@id":"deleteMatcher",
                                            "@neverShowInPanel":"true",
                                            "@type":"xforms",
                                            "@proc":"workflow.xforms.deleteMatcher.cardData.celesta",
                                            "@template":"workflow/deleteMatcherCard.xml",
                                            "related":{
                                                       "@id":"matchingCircuitGrid"
                                                       },
                                             "proc":[
                                                    {
                                                    "@id":"deleteMatcherSave",
                                                    "@name":"workflow.xforms.deleteMatcher.cardSave.celesta",
                                                    "@type":"SAVE"}]
                                            }
                                           ]
                                }
                                ]
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))


def drawProcesses(context, main=None, session=None):
    u'''Датапанель отрисовки изображения запущенного процесса или определения процесса'''
    data = {"datapanel":{"tab":[ {"@id":"schemaProcess",
                                "@name":u"Схема процесса",
                                "element":[
                                           {"@id":"launchedProcessImage",
                                            "@type":"webtext",
                                            "@proc":"workflow.webtext.launchedProcessImage.webtextData.celesta"
                                            }

                                           ]
                                }
                                ]
                         }
            }

    return XMLJSONConverter.jsonToXml(json.dumps(data))


def userGroups(context, main=None, session=None):
    data = {"datapanel":{"tab":[{"@id":"1",
                                "@name":u"Группы пользователей",
                                "element":[
#                                            {"@id":"processFilter",
#                                             "@type":"xforms",
#                                             "@template": "workflow/processFilter.xml",
#                                             "@proc":"workflow.xforms.processFilter.filterData.celesta",
#                                             },
                                           {"@id":"groupsGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.groupsGrid.getData.celesta",
                                            "@subtype":"JS_TREE_GRID",
                                            "@plugin":"treeDGrid",
                                            "proc":[{
                                                    "@id":'groupsMeta',
                                                    "@name":"workflow.grid.groupsGrid.getMeta.celesta",
                                                    "@type":"METADATA"},
                                                    {
                                                    "@id":"groupsGridToolBar",
                                                    "@name":"workflow.grid.groupsGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}]
#                                             "related":{"@id":"processFilter"}
                                            },
                                            {"@id":"addGroupCard",
                                             "@type":"xforms",
                                             "@neverShowInPanel":"true",
                                             "@proc":"workflow.xforms.addGroupCard.cardData.celesta",
                                             "@template":"workflow/addGroupCard.xml",
                                             "related":{
                                                        "@id":"groupsGrid"
                                                        },
                                             "proc":[
                                                     {
                                                     "@id":"addGroupCardSave",
                                                     "@name":"workflow.xforms.addGroupCard.cardDataSave.celesta",
                                                     "@type":"SAVE"}]

                                             },
                                            {"@id":"delGroupCard",
                                             "@type":"xforms",
                                             "@neverShowInPanel":"true",
                                             "@proc":"workflow.xforms.delGroupCard.cardData.celesta",
                                             "@template":"workflow/delGroupCard.xml",
                                             "related":{
                                                        "@id":"groupsGrid"
                                                        },
                                             "proc":[
                                                     {
                                                     "@id":"delGroupCardSave",
                                                     "@name":"workflow.xforms.delGroupCard.cardDataSave.celesta",
                                                     "@type":"SAVE"}]

                                             },
                                                                                     
                                           {"@id":"userGroupsGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.userGroupsGrid.gridData.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                             "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"groupsGrid"
                                                       },
                                            "proc":[{
                                                    "@id":'userGroupsGridMeta',
                                                    "@name":"workflow.grid.userGroupsGrid.gridMeta.celesta",
                                                    "@type":"METADATA"},
                                                    {
                                                    "@id":"userGroupsGridToolBar",
                                                    "@name":"workflow.grid.userGroupsGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}]

                                            },
                                            {"@id":"addUserToGroupCard",
                                             "@type":"xforms",
                                             "@neverShowInPanel":"true",
                                             "@proc":"workflow.xforms.addUserToGroup.cardData.celesta",
                                             "@template":"workflow/addUserToGroup.xml",
                                             "related":[{
                                                        "@id":"groupsGrid"
                                                        },
                                                        {
                                                        "@id":"userGroupsGrid"
                                                        }],
                                             "proc":[
                                                     {
                                                     "@id":"addUserToGroupCardSave",
                                                     "@name":"workflow.xforms.addUserToGroup.cardDataSave.celesta",
                                                     "@type":"SAVE"}]

                                             },
                                            {"@id":"delUserFromGroupCard",
                                             "@type":"xforms",
                                             "@neverShowInPanel":"true",
                                             "@proc":"workflow.xforms.delUserFromGroupCard.cardData.celesta",
                                             "@template":"workflow/delUserFromGroupCard.xml",
                                             "related":[{
                                                        "@id":"groupsGrid"
                                                        },
                                                        {
                                                        "@id":"userGroupsGrid"
                                                        }],
                                             "proc":[
                                                     {
                                                     "@id":"delUserFromGroupCardSave",
                                                     "@name":"workflow.xforms.delUserFromGroupCard.cardDataSave.celesta",
                                                     "@type":"SAVE"}]

                                             },
                                           ]
                                }
                                ]
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))

def standardStartProcess(context, main=None, session=None):
    u'''Датапанель стандартного запуска процесса'''
    data = {"datapanel":{"tab":[ {"@id":"schemaProcess",
                                "@name":u"Старт процесса",
                                "element":[
                                           {"@id":"standardStartProcess",
                                            "@type":"xforms",
                                            "@proc":"workflow.xforms.standardStartProcessCard.cardData.celesta",
                                            "@template":"workflow/standardStartProcessCard.xml",
                                             "proc":[
                                                    {
                                                    "@id":"standardStartProcessCardSave",
                                                    "@name":"workflow.xforms.standardStartProcessCard.cardSave.celesta",
                                                    "@type":"SAVE"}]}

                                           ]
                                }
                                ]
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))
