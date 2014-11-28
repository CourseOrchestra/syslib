# coding: utf-8

import simplejson as json
import base64
from common.sysfunctions import toHexForXml, getGridWidth
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult




def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех версий развернутых процессов. '''

    session = json.loads(session)
    gridWidth = getGridWidth(session, 60)
    processKey = session['sessioncontext']['related']['gridContext']['currentRecordId']

    activiti = ActivitiObject()
    processesList = activiti.getProcessVersionsByKey(processKey, sort="desc")

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Идентификатор процесса"],
             "version":[u"Версия"],
             "file":[u"Файл"],
             "properties":[u"properties"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data    
    for process in processesList:
        procDict = {}
        procDict[_header["id"][1]] = process.id
        procDict[_header["pid"][1]] = process.id
        procDict[_header["version"][1]] = process.version
        procDict[_header["file"][1]] = u'Загрузить'
        procDict[_header["properties"][1]] = {"event":{"@name":"row_single_click",
                                         "action":{"#sorted":[{"main_context": 'current'},
                                                              {"datapanel":{'@type':"current",
                                                                            '@tab':"current",
                                                                            'element':{'@id':'processesVersionsGrid'}
                                                                            }
                                                               }]
                                                   }
                                         }
                                }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": "300",
                                               "@totalCount": len(processesList),
                                               "@profile":"default.properties"},
                                "labels":{"header":"Версии развернутых процессов"}
                                }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "200px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["version"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["file"][0], "@width": "100px", "@type":"DOWNLOAD", "@linkId":"3"})

    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def downloadProcFile(context, main=None, add=None, filterinfo=None, session=None, elementId=None, recordId=None):
    u'''Процедура скачивание файла процесса.'''

    activiti = ActivitiObject()
    process = activiti.getProcessDefinitionById(recordId)
    fileName = process.resourceName
    data = activiti.getProcessXmlById(recordId)
    return JythonDownloadResult(data, fileName)
