# coding: utf-8
'''
Created on 16.02.2014

@author: Kuzmin
'''

import json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
import java.io.OutputStreamWriter as OutputStreamWriter
try:
    from ru.curs.celesta.showcase.utils import XMLJSONConverter
    from ru.curs.showcase.core import UserMessage
except:
    pass
from dirusing.commonfunctions import relatedTableCursorImport, getFieldsHeaders, getSortList


def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция данных для карточки редактирования содержимого справочника. '''

    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']

    table_id = '1'
    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    table_jsn = json.loads(table_meta.getCelestaDoc())
    # Заголовок таблицы
    table_name = table_jsn["name"]
    # Получение заголовков полей
    _headers = getFieldsHeaders(table_meta, "xform")

    # Пустая структура данных, связнная с текущим справочником
    xformsdata = {
        "schema": {
            "@xmlns":"",
            "edit": "true",
            "showselect": "true",
            "error_message": "",
            "row": "",
            "spravs": {
                "sprav": {
                    "@id": table_id,
                    "@name": table_name,
                    "field": []
                }
            },
			"resetIdentity":"false"
        }
    }

    xformssettings = {
        "properties": {
            "event": {
                "@name": "single_click",
                "@linkId": "1",
                "action": {
                    "#sorted": [ 
                        { "main_context": "current"},
                        { 
                            "datapanel": { 
                                "@type": "current",
                                "@tab": "current",
                                "element": {"@id":"13", "add_context": ""}
                            }
                        }]
                }
            }
        }
    }


    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(xformsdata)), XMLJSONConverter.jsonToXml(json.dumps(xformssettings)))


def cardDataSave(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    u'''Функция сохранения карточки редактирования содержимого справочника. '''
    return None




