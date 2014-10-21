# coding: utf-8

from ru.curs.celesta.showcase.utils import XMLJSONConverter
import simplejson as json

def manageProcesses(context, main=None, session=None):
    data = {"datapanel":{"tab":{"@id":"1",
                                "@name":u"Управление процессами",
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
                                           {"@id":"processVersionsGrid",
                                            "@type":"grid",
                                            "@hideOnLoad":"true",
                                            "@proc":"workflow.grid.processVersionsGrid.gridDataAndMeta.celesta",
                                            "@subtype":"JS_LIVE_GRID",
                                            "@plugin":"liveDGrid",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       },
                                            "proc":[{
                                                    "@id":3,
                                                    "@name":"workflow.grid.processVersionsGrid.downloadProcFile.celesta",
                                                    "@type":"DOWNLOAD"}]

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
                                            "@template":"processUploadCard.xml",
                                            "related":{
                                                       "@id":"processesGrid"
                                                       },
                                            "proc":[{
                                                    "@id":3,
                                                    "@name":"workflow.grid.processVersionsGrid.downloadProcFile.celesta",
                                                    "@type":"DOWNLOAD"}]

                                            }
                                           ]
                                }
                         }
            }
    return XMLJSONConverter.jsonToXml(json.dumps(data))
