# coding: utf-8

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    pass

from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from common import navigator, sysfunctions
import sys
import os
import common
from security.xform import rolesUsers
#from ssmmd.xforms import frontpagecard
#from ssmmd import navigator



a = Celesta.getInstance()
conn = ConnectionPool.get()
context = CallContext(conn, 'admin', a)
#print context.getCelesta()
#print dirsetting.graingateway.grids_structuregrid_treeGrid(context)
#structuregrid.treeGrid(context)
#print navigator.standardNavigator(context)

def proc1(context):
    print rolesUsers.usersList(context, session='''{"sessioncontext": {
    "sid": "admin",
    "userdata": "default",
    "phone": "123-56-78",
    "username": "admin",
    "fullusername": "Администратор",
    "email": "12@yandex.ru",
    "login": "admin",
    "currentDatapanelWidth": "1283",
    "currentDatapanelHeight": "737",
    "sessionid": "C7238DDA8199CCC978E97B438651B73C",
    "related": {"gridContext": {
        "id": "id_roles_grid",
        "currentColumnId": "Роль",
        "pageInfo": {
            "number": "1",
            "size": "20"
        },
        "liveInfo": {
            "limit": "50",
            "totalCount": "0",
            "offset": "0"
        },
        "currentDatapanelWidth": "0",
        "currentDatapanelHeight": "0",
        "selectedRecordId": "1111",
        "currentRecordId": "1111"
    }},
    "ip": "0:0:0:0:0:0:0:1"
}}''')
    
proc1(context)

