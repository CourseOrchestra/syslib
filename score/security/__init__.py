# coding: utf-8
from common.navigator import navigatorsParts
from ru.curs.celesta.syscursors import RolesCursor
from security.functions import Settings
from security.navigator import authentificationNavigator
from security.setForeignKeys import setForeignKeys as setConstraint
from security.xform.users import employeesSubjectsPostInsert, employeesSubjectsPostUpdate, employeesSubjectsPreDelete
from common.sysfunctions import tableCursorImport
from security.securityInit import securityInit
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext
from ru.curs.celesta import Celesta
import initcontext

settings = Settings()
if not settings.loginIsSubject():
    employeesGrain = settings.getEmployeesParam("employeesGrain")
    employeesTable = settings.getEmployeesParam("employeesTable")
    if settings.isEmployees():
        employeesCursor = tableCursorImport(employeesGrain, employeesTable)

        employeesCursor.onPostInsert.append(employeesSubjectsPostInsert)
        employeesCursor.onPostUpdate.append(employeesSubjectsPostUpdate)
        employeesCursor.onPreDelete.append(employeesSubjectsPreDelete)

if not settings.isSystemInitialised():
    try:
        context = initcontext()
        if settings.isEmployees():
            setConstraint(context) #функция устанавливает внешний ключ в таблицу subjects и меняет значение параметра isSystemInitialised на True
        securityInit(context)
    finally:
        pass
navigatorsParts['99'] = authentificationNavigator

