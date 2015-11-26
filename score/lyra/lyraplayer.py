# coding: utf-8
try:
    from ru.curs.showcase.core.jython import JythonDTO
    from ru.curs.showcase.util import XMLJSONConverter
except:
    from ru.curs.celesta.showcase import JythonDTO
    from ru.curs.celesta.showcase.utils import XMLJSONConverter
import basicForm
import simplejson as json
        
def getFormInstance(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    if '_lyraForms' in context.data:
        lf = context.data['_lyraForms']
    else:
        lf = {}
        context.data['_lyraForms'] = lf

    if main in lf:
        result = lf[main]
    else:
        #TODO: отработка ошибки на не найденный класс формы
        c = basicForm._formclasses[main]
        result = c(context)
        lf[main] = result
        
    result.setContext(context, session, main, add, elementId)
    return result


def getTemplate(context, main, add=None, filterinfo=None, session=None, elementId=None):
    formInstance =  getFormInstance(context, main, add, filterinfo, session, elementId)
    return JythonDTO(unicode(formInstance._buildForm()))

def getInstance(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    formInstance =  getFormInstance(context, main, add, filterinfo, session, elementId)
    cardData = formInstance.findRec()
    cardSettings = formInstance.getActions()
    return JythonDTO(cardData, cardSettings)

def submissionFirst(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.move('-', XMLJSONConverter.jsonToXml(data))
    return cardData

def submissionPrev(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.move('<', XMLJSONConverter.jsonToXml(data))
    return cardData

def submissionNext(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.move('>', XMLJSONConverter.jsonToXml(data))
    return cardData

def submissionLast(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.move('+', XMLJSONConverter.jsonToXml(data))
    return cardData

def submissionNew(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.newRec()
    return cardData

def submissionDel(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.deleteRec(XMLJSONConverter.jsonToXml(data))
    return cardData

def submissionRevert(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.revert(XMLJSONConverter.jsonToXml(data))
    return cardData

def submissionSave(context, main=None, add=None, filterinfo=None, session=None, data=None):
    formId = json.loads(data)['schema']['@formId']
    formInstance =  getFormInstance(context, formId, add, filterinfo, session, None)
    cardData = formInstance.move('=', XMLJSONConverter.jsonToXml(data))
    return cardData