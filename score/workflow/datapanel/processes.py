# coding: utf-8

from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json

def manageProcesses(context, main=None, session=None):
    data = {"datapanel":{"tab":[{"@id":"1",
                                "@name":u"Развёрнутые процессы",
                                "element":[{"@id":"processesGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.processesGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.processesGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"},
                                                    {
                                                    "@id":2,
                                                    "@name":"workflow.grid.processesGrid.downloadProcFile.celesta",
                                                    "@type":"DOWNLOAD"}]
                                            },
                                           {"@id":"processFormsGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.processFormsGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       },
                                            "proc":[{
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
                                "@name":u"Запущенные процессы",
                                "element":[{"@id":"launchedProcessesGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.launchedProcessesGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.launchedProcessesGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}
                                                    ]
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
                                            "@proc":"workflow.grid.launchedProcessesEventsGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"launchedProcessesGrid"
                                                       },
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.launchedProcessesEventsGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}
                                                    ]
                                            }
                                           
                                           ]
                                },
                                {"@id":"finishedProcesses",
                                "@name":u"Завершённые процессы",
                                "element":[{"@id":"finishedProcessesGrid",
                                            "@type":"grid",
                                            "@proc":"workflow.grid.finishedProcessesGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "proc":[{
                                                    "@id":1,
                                                    "@name":"workflow.grid.finishedProcessesGrid.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"}
                                                    ]
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

def standardStartProcess(context,main=None, session=None):
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