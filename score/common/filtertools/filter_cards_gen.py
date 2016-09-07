# coding: utf-8
from nsi.filtertools.filter import recovery
import json

def card_info(context, elementId):
    u'''Функция переведения данных из context.getData в xforms'''
    filters = [
        x
        for x in context.getData()[elementId]
            if x['@key'] == 'view'
    ]
    
    return filters


def card_save(xformsdata, context, filter_id):
    u'''Функция переведения данных из xforms в context.getData'''
    if xformsdata == 'del':
        recovery(context, filter_id)
    elif 'filter' in xformsdata["schema"]["filters"]:
        # Возможна ситуация, когда карточка бyдет вызвана,
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
                    stable_filter['@current_condition'] = temp_filter['@current_condition']
                    # Проверка на наличие выделенных значений
                    if 'item' in temp_filter['items']:
                        stable_filter['items']['item'] = temp_filter['items']['item']
                    else:
                        stable_filter['items']['item'] = []
                    break

def add_filter_buttons(filter_id, session, height=False, width=700, add_info=u'', add_context=None):   # в параметр heigth можно задавать число фильтров в *filter для гибкого отображения размеров окна 
    u'''
    filter_id - id карточки в датапанели, 
    height="300" - высота карточки фильтра
    '''
    if isinstance(session, unicode) or isinstance(session, str):
        session = json.loads(session)['sessioncontext']
    if not height:
        height = int(0.6*float(session["sessioncontext"]['currentDatapanelHeight'] if "sessioncontext" in session else session['currentDatapanelHeight']))
    else:
        height *= 60
    button = [
        {
            "@img": 'gridToolBar/formMagnify.png',
            "@text": add_info or u"Параметры поиска",
            "@hint": u"Установить фильтр",
            "@disable": 'false',
            "action":
            {
                "@show_in": "MODAL_WINDOW",
                "#sorted":
                [
                    {"main_context":"current"},
                    {
                        "modalwindow"   :
                        {   "@caption"  : u"Параметры поиска",
                            "@height"   : height,
                            "@width"    : width
                        }
                    },
                    {
                        "datapanel":
                        {
                            "@type": "current",
                            "@tab": "current",
                            "element": 
                            {
                                "@id": filter_id,
                                "add_context": add_context or filter_id
                            }
                        }
                    }
                ]
            }
        },
    ]
    
    return button


