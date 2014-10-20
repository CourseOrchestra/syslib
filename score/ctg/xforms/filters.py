# coding: utf-8
'''
Created on 12.08.2014

@author: Rudenko
'''
import simplejson as json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:  
    from ru.curs.showcase.core import UserMessage
except:
    pass
from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList


def dataFilter(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''
    
    # получение id grain и table из контекста
    currentTable = relatedTableCursorImport("acrsprav", "contrag_type")(context)
    contragTypeId = json.loads(main)['contragTypeId']
    
    # Пустая структура данных, связнная с текущим справочником
    xformsdata = {"schema":{"@xmlns":"",
                            "context":{"name": None,
                            "inn": None,
                            "type":{"@id":'-1'},
                            "orgtype": str(contragTypeId)},
                            "types":{"type":[]}
                            }
                  }
    for rec in currentTable.iterate():
        recId = getattr(rec, "id")
        name = getattr(rec, "name")
        data={"@id":recId, "@name":name}
        xformsdata["schema"]["types"]["type"].append(data)
    xformsdata["schema"]["types"]["type"].append({"@id":-1, "@name":"Все"})
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": "view"
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }


    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())
    
def groupFilter(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''
    
    # Пустая структура данных, связнная с текущим справочником
    xformsdata = {"schema":{"@xmlns":"",
                            "context":{"company": {"@id":"", "@linksallow":"0", "@linkid":"0", "@type":""},
                            "ondate":{"@check":"false", "@value":""}},
                            "types":{"type":[]}
                            }
                  }
    '''for rec in currentTable.iterate():
        recId = getattr(rec, "id")
        name = getattr(rec, "name")
        data={"@id":recId, "@name":name}
        xformsdata["schema"]["types"]["type"].append(data)
    xformsdata["schema"]["types"]["type"].append({"@id":-1 "@name":"Все"})'''
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": 1,
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": "view"
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }


    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())
    