# coding: utf-8
'''
Created on 12.08.2014

@author: Rudenko
'''
from common.xmlutils import XMLJSONConverter

def ctgdataDatapanel(context, main=None, session=None):
    u'''Продедура возвращает информационную панель для контрагентов'''
    data = {"datapanel":{"tab":{"@id":"01",
                                "@name":"Редактирование данных",
                                "element":[{"@id":"11",
                                           "@type":"xforms",
                                           "@template":"ctg_filter.xml",
                                           "@proc":"ctg.xforms.filters.dataFilter.celesta",
                                           "@neverShowInPanel":"false",
                                           "related":{"@id":"13"}
                                            },
    										{"@id":"13",
                                               "@type":"grid",
                                               "@subtype":"JS_LIVE_GRID",
                                               "@plugin":"liveDGrid",
                                               "@neverShowInPanel":"false",
                                               "@proc":"ctg.grid.ctgGrids.getData.celesta",
                                               "proc":[{"@id":"id_ctg_grid_meta",
                                                        "@name":"ctg.grid.ctgGrids.getMeta.celesta",
                                                        "@type":"METADATA"
                                                        },
                                                   {"@id":"toolbarCatalogWork",
                                                    "@name":"ctg.grid.ctgGrids.gridToolBar.celesta",
                                                    "@type":"TOOLBAR"
                                                    }]
                                            },
										{"@id":"15",
                                           "@type":"xforms",
                                           "@template":"ctg.xml",
                                           "@proc":"ctg.xforms.cards.cardData.celesta",
                                           "@neverShowInPanel":"true",
                                           "proc":[{"@id":"proc1",
                                                    "@name":"dirusing.xforms.dircontentcard.cardDataSave.celesta",
                                                    "@type":"SAVE"
                                                    },
                                                   {"@id":"download2",
                                                    "@name":"dirusing.commonfunctions.downloadFileFromXform.celesta",
                                                    "@type":"DOWNLOAD"
                                                    },
    												{"@id":"upload2",
                                                        "@name":"dirusing.commonfunctions.uploadFileToXform.celesta",
                                                        "@type":"UPLOAD"
                                                        }
    												],
													"related":{"@id":"13"}
                                            },
										{"@id":"16",
                                           "@type":"xforms",
                                           "@template":"directory_data_del_card.xml",
                                           "@proc":"dirusing.xforms.dircontentdelcard.cardDelData.celesta",
                                           "@neverShowInPanel":"true",
														"proc":[{"@id":"proc16",
                                                        "@name":"dirusing.xforms.dircontentdelcard.cardDelDataSave.celesta",
                                                        "@type":"SAVE"
                                                        }],
										"related":{"@id":"13"}},
    										
										{"@id":"17",
                                           "@type":"xforms",
                                           "@template":"directory_data_del_all_card.xml",
                                           "@proc":"dirusing.xforms.dircontentdelcard.cardDelData.celesta",
                                           "@neverShowInPanel":"true",
                                           "proc":[{"@id":"proc17",
                                                        "@name":"dirusing.xforms.dircontentdelcard.cardDelAllDataSave.celesta",
                                                        "@type":"SAVE"
                                                        }],
										"related":{"@id":"13"}},
										{"@id":"18",
                                           "@type":"xforms",
                                           "@template":"directory_import_card.xml",
                                           "@proc":"dirusing.xforms.dirimportcard.cardData.celesta",
                                           "@neverShowInPanel":"true",
                                           "proc":[{"@id":"proc18",
                                                        "@name":"dirusing.xforms.dirimportcard.cardDataSave.celesta",
                                                        "@type":"SAVE"
                                                        },
    												{"@id":"upload3",
                                                            "@name":"dirusing.commonfunctions.importXlsData.celesta",
                                                            "@type":"UPLOAD"
                                                            }
    												],
										"related":{"@id":"13"}}
										
										
										]
                                }
                         }
            }

    res = XMLJSONConverter(input=data).parse()
    return res

def ctgGroupsDatapanel(context, main=None, session=None):
    u'''Продедура возвращает информационную панель для групп'''
    data = {"datapanel":{"tab":{"@id":"01",
                                "@name":"Группы",
                                "element":[{"@id":"11",
                                           "@type":"xforms",
                                           "@template":"ctg_group_filter_template.xml",
                                           "@proc":"ctg.xforms.filters.groupFilter.celesta",
                                           "@neverShowInPanel":"false",
                                           "related":{"@id":"13"}
                                            },
                                            {"@id":"13",
                                               "@type":"grid",
                                               "@subtype":"JS_LIVE_GRID",
                                               "@plugin":"liveDGrid",
                                               "@hideOnLoad":"true",
                                               "@proc":"ctg.grid.ctgGrids.getGroupsData.celesta",
                                               "proc":[{"@id":"id_ctg_grid_meta",
                                                        "@name":"ctg.grid.ctgGrids.getGroupsMeta.celesta",
                                                        "@type":"METADATA"
                                                        },
                                                   {"@id":"toolbarCatalogWork",
                                                    "@name":"ctg.grid.ctgGrids.gridGroupsToolBar.celesta",
                                                    "@type":"TOOLBAR"
                                                    }]
                                            },
                                        {"@id":"15",
                                           "@type":"xforms",
                                           "@template":"ctg_group_contrag_add.xml",
                                           "@proc":"ctg.xforms.cards.cardGroupsData.celesta",
                                           "@neverShowInPanel":"true",
                                           "proc":[{"@id":"proc1",
                                                    "@name":"ctg.xforms.cards.cardGroupsDataSave.celesta",
                                                    "@type":"SAVE"
                                                    },
                                                   {"@id":"download2",
                                                    "@name":"dirusing.commonfunctions.downloadFileFromXform.celesta",
                                                    "@type":"DOWNLOAD"
                                                    },
                                                    {"@id":"upload2",
                                                        "@name":"dirusing.commonfunctions.uploadFileToXform.celesta",
                                                        "@type":"UPLOAD"
                                                        }
                                                    ],
                                                    "related":{"@id":"13"}
                                            },
                                        {"@id":"16",
                                           "@type":"xforms",
                                           "@template":"ctg_group_contrag_del.xml",
                                           "@proc":"ctg.xforms.cards.cardExcludeOrg.celesta",
                                           "@neverShowInPanel":"true",
                                                        "proc":[{"@id":"proc16",
                                                        "@name":"ctg.xforms.cards.cardExcludeOrgSave.celesta",
                                                        "@type":"SAVE"
                                                        }],
                                        "related":{"@id":"13"}},
                                            
                                        {"@id":"17",
                                           "@type":"xforms",
                                           "@template":"directory_data_del_card.xml",
                                           "@proc":"ctg.xforms.cards.cardDel.celesta",
                                           "@neverShowInPanel":"true",
                                           "proc":[{"@id":"proc17",
                                                        "@name":"ctg.xforms.cards.cardDelSave.celesta",
                                                        "@type":"SAVE"
                                                        }],
                                        "related":{"@id":"13"}},
                                        {"@id":"18",
                                           "@type":"xforms",
                                           "@template":"directory_import_card.xml",
                                           "@proc":"dirusing.xforms.dirimportcard.cardData.celesta",
                                           "@neverShowInPanel":"true",
                                           "proc":[{"@id":"proc18",
                                                        "@name":"dirusing.xforms.dirimportcard.cardDataSave.celesta",
                                                        "@type":"SAVE"
                                                        },
                                                    {"@id":"upload3",
                                                            "@name":"dirusing.commonfunctions.importXlsData.celesta",
                                                            "@type":"UPLOAD"
                                                            }
                                                    ],
                                        "related":{"@id":"13"}}
                                        
                                        
                                        ]
                                }
                         }
            }

    res = XMLJSONConverter(input=data).parse()
    return res

