# coding: utf-8
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.grainssettings import SettingsManager
# from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor
import simplejson as json
import re
navigatorsParts = {}

def standardNavigator(context, session=None):
    u"""
Функция позволяет вернутть навигатор собранные из кусочков(групп),
приходящих в список navigatorsParts в виде функций, которые возвращают JSON объект"""
    settingsObject = SettingsManager(context)
    sessionDict = json.loads(session)
    allNavigator = False
    userdataNavigator = []
    try:
        userdataNavigator = settingsObject.getGrainSettings('common', 'navigator/userdata[@name="%s"]/group' % sessionDict["sessioncontext"]["userdata"])
    except:
        allNavigator = True
    localNavigators = navigatorsParts.copy()
    resultJSON = {"navigator":{}}

    resultNavigators = dict()
    if localNavigators:
        for setItem in localNavigators:
            if re.search('^__set_.+$', setItem) and (allNavigator or setItem in userdataNavigator):
                setOfPart = localNavigators[setItem]
                setOfPartRes = setOfPart(context, session)
                for part in setOfPartRes:
                    resultNavigators[part] = setOfPartRes[part]
            elif  (allNavigator or setItem in userdataNavigator):
                resultNavigators[setItem] = localNavigators[setItem](context, session)
        resultJSON["navigator"]["group"] = list()
        for part in (sorted(resultNavigators) if allNavigator else userdataNavigator):
            if part == "__header__":
                resultJSON["navigator"].update(resultNavigators[part])
            elif resultNavigators[part]["group"] is not None:
                resultJSON["navigator"]["group"].append(resultNavigators[part]["group"])
    print resultJSON
    resultNavigator = XMLJSONConverter.jsonToXml(json.dumps(resultJSON))
    return resultNavigator


def seriesNavigator(context, session):
    from security.functions import userHasPermission
    """Часть навигатора для ведения справочника серий номеров"""
    sid = json.loads(session)['sessioncontext']['sid']
    resultJSON = {"group":{"@id": "numbersSeries",
                           "@name": u"Серии номеров",
                           "level1":[]}
                  }
    '''Проверка разрешений на формирование навигатора'''
    if userHasPermission(context, sid, 'numbersSeriesPoint'):
        resultJSON["group"]["level1"].append({"@id": "numbersSeries",
                                              "@name": u"Серии номеров",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "common.datapanel.numbersSeries.datapanel.celesta",
                                                                     "@tab": "firstOrCurrent"
                                                                     }
                                                        }
                                              })
    else:
        resultJSON = {"group":None}
    return resultJSON
