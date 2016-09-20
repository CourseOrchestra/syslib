# coding: utf-8
import json

from common.api.datapanels.grids import ToolbarItem
from common.api.events.action import Action, ModalWindow
from common.api.events.activities import DatapanelElement
from common.filtertools.filter import recovery


def card_info(context, elementId):
    u'''Функция перевода данных из context.getData в xforms'''
    filters = [
        x
        for x in context.getData()[elementId]
        if x['@key'] == 'view'
    ]

    return filters


def card_save(xformsdata, context, filter_id):
    u'''Функция перевода данных из xforms в context.getData'''
    if xformsdata == 'del':
        recovery(context, filter_id)
    elif 'filter' in xformsdata["schema"]["filters"]:
        # Возможна ситуация, когда карточка будет вызвана,
        # но не будет использован фильтр. Для исключения избыточной проверки на наличие значений словаря вводим ключ-флаг.
        if not context.getData().get(u'card_save'):
            context.getData()[u'card_save'] = set([])
        context.getData()[u'card_save'].add(filter_id)
        temp_context = xformsdata["schema"]["filters"]['filter']
        if isinstance(temp_context, dict):
            temp_context = [temp_context]
        # Перенесение данных в контекст
        for temp_filter in temp_context:
            for stable_filter in context.getData()[filter_id]:
                if temp_filter['@id'] == stable_filter['@id']:
                    # Передача данных из xforms в context
                    stable_filter['@minValue'] = temp_filter['@minValue']
                    stable_filter['@value'] = temp_filter['@value']
                    stable_filter['@maxValue'] = temp_filter['@maxValue']
                    stable_filter['@boolInput'] = temp_filter['@boolInput']
                    stable_filter['item'] = temp_filter['item']
                    stable_filter['@current_condition'] = temp_filter[
                        '@current_condition']
                    # Проверка на наличие выделенных значений
                    if 'item' in temp_filter['items']:
                        stable_filter['items'][
                            'item'] = temp_filter['items']['item']
                    else:
                        stable_filter['items']['item'] = []
                    break


def add_filter_buttons(filter_id, session, height=False, width=700,
                       add_info=u"", add_context=None, is_object=False):
    u'''Функция, формирующая кнопку тулбара грида
        filter_id - id карточки в датапанели,
        height="300" - высота карточки фильтра
        в параметр height можно задавать число фильтров в *filter для гибкого отображения размеров окна
    '''
    if isinstance(session, unicode) or isinstance(session, str):
        session = json.loads(session)['sessioncontext']
    elif "sessioncontext" in session:
        session = session["sessioncontext"]
    if not height:
        height = int(0.6 * float(session['currentDatapanelHeight']))
    else:
        height *= 60

    button = ToolbarItem("deleteFileButton")\
        .setCaption(add_info or u"Параметры поиска")\
        .setHint(u"Установить фильтр")\
        .setAction(Action()
                   .add(DatapanelElement(filter_id,
                                         add_context or filter_id))
                   .showIn(ModalWindow(u"Параметры поиска",
                                       width, height)))\
        .setImage("gridToolBar/filter.png")

    if not is_object:
        button = button.toJSONDict()

    return button
