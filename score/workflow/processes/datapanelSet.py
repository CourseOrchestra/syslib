# coding: utf-8

'''
Created on 17.11.2014

@author: m.prudyvus
'''

import simplejson as json
from workflow import datapanel

def datapanelSet(context, main, session):
    u'''определяет нужную датапанель по urlparams'''
    session = json.loads(session)['sessioncontext']
    for params in session['urlparams']['urlparam']:
        if params['@name'] == 'formType':
            formType = params['@value'][0]
    if formType == 'approve':
        datapanelD = datapanel.tasks.approveTask(context, main=None, session=None)
    elif formType == 'complite':
        datapanelD = datapanel.tasks.standardCompleteTask(context, main=None, session=None)
    elif formType == 'startProcess':
        datapanelD = datapanel.processes.standardStartProcess(context, main=None, session=None)
    return datapanelD