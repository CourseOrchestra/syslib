# coding: utf-8
"""
Created on 27.01.2016

@author: s.gavrilov
"""

import json

from common.sysfunctions import toHexForXml, getGridHeight
from fileRepository._fileRepository_orm import fileCursor
from ru.curs.celesta.showcase.utils import XMLJSONConverter


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


def headerFun():
    return {
        "hide_id": ["~~id"],

        "id": [u"ID файла"],
        "name": [u"Имя загруженного файла"],
        "uploadVersioning": [u"Поддерживается ли сохранность предыдущих версий"],

        "properties": [u"properties"]
    }


def gridData(context, main, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u"""Функция получения данных для грида"""

    session = json.loads(session)
    file_cursor = fileCursor(context)

    _header = headerFun()
    data = {"records": {"rec": []}}

    if sortColumnList:
        sortName = sortColumnList[0].id
        sortType = unicode(sortColumnList[0].sorting).lower()
    else:
        sortName = None

    for column in _header:
        _header[column].append(toHexForXml(_header[column][0]))
        if sortName == _header[column][0]:
            file_cursor.orderBy("%s %s" % (column, sortType))

    file_cursor.limit(firstrecord - 1, pagesize)
    for files in file_cursor.iterate():
        rec = {}
        rec[_header["id"][-1]] = rec[_header["hide_id"][-1]] = files.id
        rec[_header["name"][-1]] = files.name
        rec[_header["uploadVersioning"][-1]] = files.uploadVersioning

        #  properties
        rec["properties"] = {
            "event": {
                "@name": "row_single_click",
                "action": {
                    "#sorted": [
                        {
                            "main_context": "current"
                        },
                        {
                            "datapanel":
                            {
                                "@type": "current",
                                "@tab": "current"
                            }
                        }
                    ]
                }
            }
        }
        data["records"]["rec"].append(rec)

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)), None)


def gridMeta(context, main, add=None, filterinfo=None,
             session=None, elementId=None):
    u"""Функция получения данных для грида"""

    session = json.loads(session)
    _header = headerFun()
    file_cursor = fileCursor(context)

    totalcount = file_cursor.count()
    settings = {}
    settings["gridsettings"] = {
        "columns": {"col": []},
        "properties": {
            "@gridHeight": getGridHeight(session),
            "@gridWidth": "100%",
            "@totalCount": totalcount,
            "@pagesize": "100"
        }
    }

    settings["gridsettings"]["columns"][
        "col"].append({"@id": _header["id"][0]})

    settings["gridsettings"]["columns"][
        "col"].append({"@id": _header["name"][0]})
    settings["gridsettings"]["columns"]["col"].append(
        {"@id": _header["uploadVersioning"][0]})

    return JythonDTO(None, XMLJSONConverter.jsonToXml(json.dumps(settings)))


def gridToolBar(context, main=None, add=None, filterinfo=None,
                session=None, elementId=None):
    u'''Toolbar для грида. '''
    session = json.loads(session)['sessioncontext']["related"]['gridContext']

    style = str('currentRecordId' not in session).lower()

    data = {
        "gridtoolbar": {
            "item": [
                {
                    "@img": 'gridToolBar/addDirectory.png',
                    "@text": "Добавить",
                    "@hint": "Добавить файл",
                    "@disable": "false",
                    "action": {
                        "@show_in": "MODAL_WINDOW",
                        "#sorted": [
                            {
                                "main_context": "current"
                            },
                            {
                                "modalwindow": {
                                    "@caption": "Добавление файла",
                                    "@height": "150",
                                    "@width": "500"
                                }
                            },
                            {
                                "datapanel": {
                                    "@type": "current",
                                    "@tab": "current",
                                    "element": {
                                        "@id": "addFile",
                                        "add_context": "upload"
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "@img": 'gridToolBar/addDirectory.png',
                    "@text": "Добавить новую версию файла",
                    "@hint": "Добавить новую версию файла",
                    "@disable": style,
                    "action": {
                        "@show_in": "MODAL_WINDOW",
                        "#sorted": [
                            {
                                "main_context": "current"
                            },
                            {
                                "modalwindow": {
                                    "@caption": "Добавление новой версии файла",
                                    "@height": "150",
                                    "@width": "500"
                                }
                            },
                            {
                                "datapanel": {
                                    "@type": "current",
                                    "@tab": "current",
                                    "element": {
                                        "@id": "addFile",
                                        "add_context": "replace"
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "@img": 'gridToolBar/delFolder.png',
                    "@text": "Удалить файл",
                    "@hint": "Удаление файла вместе со всеми записями о нём.",
                    "@disable": style,
                    "action": {
                        "@show_in": "MODAL_WINDOW",
                        "#sorted": [
                            {
                                "main_context": "current"
                            },
                            {
                                "modalwindow": {
                                    "@caption": "Удаление файла вместе со всеми записями о нём",
                                    "@height": "150",
                                    "@width": "500"
                                }
                            },
                            {
                                "datapanel": {
                                    "@type": "current",
                                    "@tab": "current",
                                    "element": {
                                        "@id": "fileCardDelete",
                                        "add_context": "del"
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "@img": 'gridToolBar/arrowDown.png',
                    "@text": "Скачать файл",
                    "@hint": "Скачать выбранный файл.",
                    "@disable": style,
                    "action": {
                        "@show_in": "MODAL_WINDOW",
                        "#sorted": [
                            {
                             "main_context": "current"
                            },
                            {
                                "modalwindow": {
                                    "@caption": "Скачивание файла",
                                    "@height": "150",
                                    "@width": "500"
                                }
                            },
                            {
                                "datapanel": {
                                    "@type": "current",
                                    "@tab": "current",
                                    "element": {
                                        "@id": "fileCardDownload",
                                        "add_context": "download"
                                    }
                                }
                            }
                        ]
                    }
                },
            ]
        }
    }

    return XMLJSONConverter.jsonToXml(json.dumps(data))


def takeDataForGridToolbarUpload(identifier, style="true"):
    '''
    Функция принимает идентификатор из <element id="addFile" type="xforms"...>
    Кладётся вывод в data["gridtoolbar"]["item"]
    '''
    data = {
        "@img": 'gridToolBar/addDirectory.png',
        "@text": "Добавить файл",
        "@hint": "Добавить новую версию файла",
        "@disable": style,
        "action": {
            "@show_in": "MODAL_WINDOW",
            "#sorted": [
                {
                 "main_context": "current"
                },
                {
                    "modalwindow": {
                        "@caption": "Добавление файла",
                        "@height": "150",
                        "@width": "500"
                    }
                },
                {
                    "datapanel": {
                        "@type": "current",
                        "@tab": "current",
                        "element": {
                            "@id": identifier,
                            "add_context": "upload"
                        }
                    }
                }
            ]
        }
    }
    return data
