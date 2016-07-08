# coding: utf-8


def navigatorFileRepository(context, session):

    resultJSON = {
        "group": {
            "@id": "fileRepository",
            "@name": u"Хранилище файлов",
            "level1": []
        }
    }
    resultJSON["group"]["level1"].extend([
        {
            "@name": u"Файлы",
            "@id": "files",
            "action": {"#sorted": [{"main_context": "fileData"},
                                   {"datapanel": {
                                       "@type": "fileDatapanel.xml",
                                       "@tab": "1"
                                   }
            }]}

        }
    ])

    return resultJSON
