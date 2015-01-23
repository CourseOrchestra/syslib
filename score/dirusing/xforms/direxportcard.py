# coding: utf-8
'''
Created on 16.02.2014

@author: Kuzmin
'''

import simplejson as json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
try:  
    from ru.curs.showcase.core import UserMessage
except:
    pass
from common.xmlutils import XMLJSONConverter
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders


def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''
    
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    
    table_id='1'
    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    table_jsn = json.loads(table_meta.getCelestaDoc())
    # Заголовок таблицы
    table_name = table_jsn["name"]

    # Пустая структура данных, связнная с текущим справочником
    xformsdata = {"schema":{"@xmlns":"",
                            "edit": "true",
                            "showselect": "true",
                            "error_message": "",
                            "row": "",
                            "spravs": {"sprav":{"@id": table_id,
                                                "@name": table_name,
                                                "field": []
                                                }
                                       },
                            "reftables":"false",
                            "parenttables":"false"

                            }
                  }
    
    
    xformssettings = {"properties":{"event":{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"13",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }
                                    }
                      }


    return JythonDTO(XMLJSONConverter(input=xformsdata).parse(), XMLJSONConverter(input=xformssettings).parse())

     
def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника. '''
    return None




