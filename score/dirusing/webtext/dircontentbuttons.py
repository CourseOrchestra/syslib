# coding: utf-8
'''
Created on 03.12.2013

@author: v.popov
'''
try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

from ru.curs.celesta.showcase.utils import XMLJSONConverter


def buttons(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Р¤СѓРЅРєС†РёСЏ РґР»СЏ РєРЅРѕРїРѕРє - Р”РѕР±Р°РІРёС‚СЊ, Р РµРґР°РєС‚РёСЂРѕРІР°С‚СЊ, РЈРґР°Р»РёС‚СЊ. '''

    if add == "row_clicked":
        buttonstyle = "blue"
    else:
        buttonstyle = "disabled"

    # РљРЅРѕРїРєР° Р”РѕР±Р°РІРёС‚СЊ
    addButton = {"div":{"@class": "newbutton highbutton",
                        "span": {"@class": "blue xforms-trigger",
                                 "span": {"@class": "value",
                                          "button": {"@style": "width: 135px; text-align: center",
                                                     "@onclick": "gwtWebTextFunc('%s','1');" % elementId,
                                                     "span": {"@class": "xforms-label", "#text": "Р”РѕР±Р°РІРёС‚СЊ"
                                                              }
                                                     }

                                            }
                                 }
                        }
                 }

    # РљРЅРѕРїРєР° Р РµРґР°РєС‚РёСЂРѕРІР°С‚СЊ
    editButton = {"div":{"@class": "newbutton highbutton",
                        "span": {"@class": buttonstyle + ' xforms-trigger',
                                 "span": {"@class": "value",
                                          "button": {"@style": "width: 135px; text-align: center",
                                                     "@onclick": "gwtWebTextFunc('%s','2');" % elementId,
                                                     "span": {"@class": "xforms-label", "#text": "Р РµРґР°РєС‚РёСЂРѕРІР°С‚СЊ"
                                                              }
                                                     }

                                            }
                                 }
                        }
                 }

    # РљРЅРѕРїРєР° РЈРґР°Р»РёС‚СЊ
    delButton = {"div":{"@class": "newbutton highbutton",
                        "span": {"@class": buttonstyle + ' xforms-trigger',
                                 "span": {"@class": "value",
                                          "button": {"@style": "width: 135px; text-align: center",
                                                     "@onclick": "var answer=confirm(''Р’С‹ РґРµР№СЃС‚РІРёС‚РµР»СЊРЅРѕ С…РѕС‚РёС‚Рµ СѓРґР°Р»РёС‚СЊ РґР°РЅРЅСѓСЋ Р·Р°РїРёСЃСЊ?''); if (answer) gwtWebTextFunc('%s','3');" % elementId,
                                                     "span": {"@class": "xforms-label", "#text": "РЈРґР°Р»РёС‚СЊ"
                                                              }
                                                     }

                                            }
                                 }
                        }
                 }

    # Р”Р°РЅРЅС‹Рµ
    data = {"div": {"table": {"@cellpadding": "0px",
                              "@cellspacing": "1px",
                              "tr":{"td": [addButton,
                                    editButton,
                                    delButton
                                    ]
                                    }
                              }
                    }
            }

    # РќР°СЃС‚СЂРѕР№РєРё РєРЅРѕРїРєРё Р”РѕР±Р°РІРёС‚СЊ
    addButtonSettings = {"@name": "single_click",
                                  "@linkId": "1",
                                  "action": {"@show_in": "MODAL_WINDOW",
                                             "main_context": "current",
                                             "modalwindow": {"@caption": "Р”РѕР±Р°РІР»РµРЅРёРµ Р·Р°РїРёСЃРё"
                                                             },
                                             "datapanel": {"@type": "current",
                                                           "@tab": "current",
                                                           "element": {"@id": "15",
                                                                       "add_context": "add"
                                                                       }
                                                           }

                                             }
                                  }


    # РќР°СЃС‚СЂРѕР№РєРё РєРЅРѕРїРєРё Р РµРґР°РєС‚РёСЂРѕРІР°С‚СЊ
    editButtonSettings = {"@name": "single_click",
                                  "@linkId": "2",
                                  "action": {"@show_in": "MODAL_WINDOW",
                                             "main_context": "current",
                                             "modalwindow": {"@caption": "Р�Р·РјРµРЅРµРЅРёРµ Р·Р°РїРёСЃРё"
                                                             },
                                             "datapanel": {"@type": "current",
                                                           "@tab": "current",
                                                           "element": {"@id": "15",
                                                                       "add_context": "edit"
                                                                       }
                                                           }

                                             }
                                  }


    # РќР°СЃС‚СЂРѕР№РєРё РєРЅРѕРїРєРё РЈРґР°Р»РёС‚СЊ. РќСѓР¶РЅРѕ РґРѕРЅР°СЃС‚СЂРѕРёС‚СЊ
    delButtonSettings = {"@name": "single_click",
                                  "@linkId": "3",
                                  "action": {"@show_in": "MODAL_WINDOW",
                                             "main_context": "current",
                                             "datapanel": {"@type": "current",
                                                           "@tab": "current"
                                                           }

                                             }
                                  }


    # РќР°СЃС‚СЂРѕР№РєРё
    if add == 'row_clicked':
        settings = {"properties": {"event": [addButtonSettings, editButtonSettings, delButtonSettings]
                                   }
                    }

    else:
        settings = {"properties": {"event": addButtonSettings
                                   }
                    }

    #print XMLJSONConverter(input=data).parse().encode('cp1251'), XMLJSONConverter(input=settings).parse().encode('cp1251')
    return JythonDTO(XMLJSONConverter(input=data).parse(), XMLJSONConverter(input=settings).parse())

