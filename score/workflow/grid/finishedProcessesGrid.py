# coding: utf-8

'''
Created on 31.10.2014

@author: tr0glo)|(I╠╣
'''


import simplejson as json
from common.sysfunctions import toHexForXml
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from workflow.processUtils import ActivitiObject
from common.sysfunctions import getGridWidth
try:
    from ru.curs.showcase.core.jython import JythonDTO, JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDTO, JythonDownloadResult




def gridDataAndMeta(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=[]):
    u'''Функция получения списка всех запущенных процессов. '''

    activiti = ActivitiObject()
    processesList = activiti.historyService.createHistoricProcessInstanceQuery().finished().orderByProcessInstanceEndTime().includeProcessVariables().asc().list()
    session = json.loads(session)
    gridWidth = getGridWidth(session, 60)
    session = session['sessioncontext']
    if "formData" in session["related"]["xformsContext"]:
        info = session["related"]["xformsContext"]["formData"]["schema"]["info"]
        processName = info["@processName"]
    else:
        processName = ''

    data = {"records":{"rec":[]}}
    _header = {"id":["~~id"],
             "pid":[u"Код процесса"],
             "name":[u"Название процесса"],
             "description":[u"Описание"],
             "schema":[u"Схема"],
             "reason":[u"Причина завершения"],
             "version":[u"Версия"],
             "properties":[u"properties"],
             "comment":[u"Комментарий"]}

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
    # Проходим по таблице и заполняем data
    #raise Exception(processesList)
    for process in processesList:
        procDict = {}
        procDict[_header["id"][1]] = process.getId()
        procDict[_header["pid"][1]] = process.getId()
        variables = process.getProcessVariables()
        if "processDescription" in variables:
            procDesc = variables["processDescription"]
        else:
            procDesc = ''
        procDict[_header["description"][1]] = procDesc
        defId = process.getProcessDefinitionId()
        procDict[_header["name"][1]] = activiti.repositoryService.createProcessDefinitionQuery().processDefinitionId(defId).singleResult().getName()        
        if processName.lower() not in procDict[_header["name"][1]].lower():
            continue        
        procDict[_header["reason"][1]] = process.getDeleteReason()
#         procDict[_header["schema"][1]] =   {"link": {  "@href":"./?mode=image&processId="+process.getId()+"",
#                                                      "@image":"solutions/default/resources/flowblock.png",
#                                                      "@text":"Схема",
#                                                      "@openInNewTab":"true"
#                                                      }
#                                            }

        #procDict[_header["description"][1]] = process.description
        #procDict[_header["version"][1]] = process.version
        procDict[_header["properties"][1]] = {"event":
                                              [
#                                                {"@name":"cell_single_click",
#                                                "@column": _header["schema"][0],
#                                                "action":
#                                                     {"@show_in": "MODAL_WINDOW",
#                                                      "#sorted":
#                                                         [{"main_context":"current"},
#                                                          {"modalwindow":
#                                                             {"@caption": "Схема процесса"
#                                                              }
#                                                           },
#                                                          {"datapanel":
#                                                             {"@type": "current",
#                                                              "@tab": "current",
#                                                              "element":
#                                                                 {"@id": "launchedProcessImage"
#                                                                  }
#                                                              }
#                                                           }
#                                                          ]
#                                                      }
#                                                },
                                                {"@name":"row_single_click",
                                                                 "action":
                                                                    {"main_context": "current",
                                                                     "datapanel":
                                                                        {'@type':"current",
                                                                         '@tab':"current",
                                                                         "element": {"@id":"finishedProcessEventsGrid",
                                                                                     "add_context": ''}
                                                                         }
                                                                    }
                                                                 }
                                               ]
                                              }
        data["records"]["rec"].append(procDict)

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
                                "properties": {"@pagesize":"50",
                                               "@gridWidth": gridWidth,
                                               "@gridHeight": "300",
                                               "@totalCount": len(processesList),
                                               "@profile":"default.properties"}
                                }
    # Добавляем поля для отображения в gridsettings
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["schema"][0], "@width": "40px", "@type": "LINK"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["pid"][0], "@width": "150px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["name"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "300px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":_header["reason"][0], "@width": "300px"})
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["version"][0], "@width": "100px"})
    #settings["gridsettings"]["columns"]["col"].append({"@id":_header["description"][0], "@width": "400px"})
    res1 = XMLJSONConverter.jsonToXml(json.dumps(data))
    res2 = XMLJSONConverter.jsonToXml(json.dumps(settings))

    return JythonDTO(res1, res2)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":{}}}


#     data["gridtoolbar"]["item"].append({ "@text":"Остановить",
#                                         "@hint":"Остановить процесс",
#                                         "@disable": style,
#                                         "action":{"@show_in": "MODAL_WINDOW",
#                                                   "#sorted":[{"main_context":"current"},
#                                                              {"modalwindow":{"@caption": "Остановка процесса"
#                                                                              }
#                                                               },
#                                                              {"datapanel":{"@type": "current",
#                                                                            "@tab": "current",
#                                                                            "element": {"@id": "suspendProcessCard"}
#                                                                            }
#                                                               }
#                                                              ]
#                                                   }
#                                         })



    return XMLJSONConverter.jsonToXml(json.dumps(data))

