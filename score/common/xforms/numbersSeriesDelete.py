# coding: utf-8


import simplejson as json
import base64
from string import lowercase

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
#from ru.curs.celesta import CelestaException
from common.xmlutils import XMLJSONConverter
from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor

def cardData(context, main, add, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}}
    xformssettings = {"properties":{"event":[{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": [{"@id":"numbersSeriesGrid",
                                                                                 "add_context": ""},
                                                                                 {"@id":"linesNumbersSeriesGrid",
                                                                                 "add_context": "hide"}
                                                                                 ]
                                                                     }
                                                       }
                                             }]
                                    }
                      }
    jsonData = XMLJSONConverter(input=xformsdata).parse()
    jsonSettings = XMLJSONConverter(input=xformssettings).parse()
    return JythonDTO(jsonData, jsonSettings)

def cardDelete(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    currentRecordId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
    numbersSeries = numbersSeriesCursor(context)
    linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
    linesOfNumbersSeries.setRange("seriesId", currentRecordId)
    linesOfNumbersSeries.deleteAll()
    numbersSeries.get(currentRecordId)
    numbersSeries.delete()