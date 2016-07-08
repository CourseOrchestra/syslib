# coding: utf-8
'''
Created on 28.01.2016

@author: s.gavrilov

'''
import json

from fileRepository import functions
from ru.curs.celesta.showcase.utils import XMLJSONConverter


try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


def cardData(context, main, add, filterinfo=None, session=None, elementId=None):
    session = json.loads(session)["sessioncontext"]
    gridContext = session["related"]["gridContext"]
    data = {
        "schema": {
            "@xmlns": '',
            "content": {
                "fileName": ''
            },
            'enableSave': 'true',
            'message': u'Вы уверены, что хотите удалить файл и все записи о нём?',
            'bad_message': u'Нельзя удалять данный файл.'
        }
    }

    settings = {
        "properties": {
            "event": {
                "@name": "single_click",
                "@linkId": "save",
                "action": {"#sorted":[{ "main_context": "current"},
                    {"datapanel": {
                        "@type": "current",
                        "@tab": "current",
                        "element": {
                            "@id": gridContext["@id"],
                            "add_context": ""
                        }
                    }
                }]}
            }
        }
    }

    return JythonDTO(XMLJSONConverter.jsonToXml(json.dumps(data)),
                     XMLJSONConverter.jsonToXml(json.dumps(settings)))


def cardDataSave(context, main=None, add=None, filterinfo=None,
                 session=None, elementId=None, xformsdata=None):
    if add == 'del':
        session = json.loads(session)['sessioncontext']
        currId = session["related"]["gridContext"]["currentRecordId"]
        functions.deleteFile(context, currId)


def cardUpload(context, main=None, add=None, filterinfo=None, session=None,
               elementId=None, data=None, fileName=None, file=None):
    session = json.loads(session)['sessioncontext']
    currId = session["related"]["gridContext"].get("currentRecordId")

    functions.putFile(context, fileName, file, rewritten_file_id=currId)


def cardDownload(context, main=None, add=None, filterinfo=None,
                 session=None, elementId=None, data=None):
    session = json.loads(session)['sessioncontext']
    currId = session["related"]["gridContext"]["currentRecordId"]

    path_to_file = getFilePathById(context, currId)
    file_cursor = fileCursor(context)
    file_cursor.get(currId)

    out_stream = FileInputStream(path_to_file)

    return JythonDownloadResult(out_stream, file_cursor.name)
