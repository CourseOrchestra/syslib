# coding: utf-8

from common import navigator
def navDirSetting(context, session):
    resultJSON = {"group":
                     {"@id": "test",
                      "@name": "Гранула справочников",
                      "level1":
                        {"@id": "dirM",
                          "@name": "Управление справочниками",
                          "action":
                            {"main_context": "current",
                            "datapanel":
                                {"@type": "dirsettingDatapanel.xml",
                                 "@tab": "firstOrCurrent"}
                             }
                         }
                      }
                  }

    return resultJSON

navigator.navigatorsParts['1'] = navDirSetting
