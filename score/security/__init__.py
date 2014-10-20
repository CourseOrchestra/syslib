# coding: utf-8


from common.xmlutils import XMLJSONConverter
from common.navigator import navigatorsParts
from ru.curs.celesta.syscursors import RolesCursor
from security._security_orm import customPermsCursor, customPermsTypesCursor, rolesCustomPermsCursor
from security.functions import Settings
from security.navigator import authentificationNavigator
from security.setForeignKeys import setForeignKeys as setConstraint
from security.xform.users import employeesSubjectsPostInsert, employeesSubjectsPostUpdate, employeesSubjectsPreDelete
from common.sysfunctions import tableCursorImport
from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor
from ru.curs.celesta import Celesta
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext
from java.text import SimpleDateFormat
import time, datetime

settings=Settings()
if not settings.loginIsSubject():
    employeesGrain=settings.getEmployeesParam("employeesGrain")
    employeesTable=settings.getEmployeesParam("employeesTable")
    if settings.isEmployees():
        employeesCursor=tableCursorImport(employeesGrain, employeesTable)
        
        employeesCursor.onPostInsert.append(employeesSubjectsPostInsert)
        employeesCursor.onPostUpdate.append(employeesSubjectsPostUpdate)
        employeesCursor.onPreDelete.append(employeesSubjectsPreDelete)
    
if not settings.isSystemInitialised():    
    if settings.isEmployees():
        setConstraint() #функция устанавливает внешний ключ в таблицу subjects и меняет значение параметра isSystemInitialised на True
a = Celesta.getInstance()
adminUser = settings.getEmployeesParam("admin")
conn = ConnectionPool.get()
sesContext = SessionContext(adminUser, 'initsession')
context = CallContext(conn, sesContext)
numbersSeries = numbersSeriesCursor(context)
linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
numbersSeries.id = 'subjects'
numbersSeries.description = 'subjects'
if not numbersSeries.tryInsert():
    numbersSeries.update()
if not linesOfNumbersSeries.tryGet('subjects', 1):
    sdf = SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    now = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    linesOfNumbersSeries.seriesId = 'subjects'
    linesOfNumbersSeries.numberOfLine = 1                
    linesOfNumbersSeries.startingDate = sdf.parse(now)
    linesOfNumbersSeries.startingNumber = 10
    linesOfNumbersSeries.endingNumber = 100000
    linesOfNumbersSeries.incrimentByNumber = 1
    linesOfNumbersSeries.isOpened = True
    linesOfNumbersSeries.prefix = 'subject-'
    linesOfNumbersSeries.isFixedLength = False
    linesOfNumbersSeries.insert()
customPermsTypes = customPermsTypesCursor(context)
if not customPermsTypes.tryGet('navigator'):
    customPermsTypes.name='navigator'
    customPermsTypes.description=u'Пункты меню навигатора'
    customPermsTypes.insert()
customPerms = customPermsCursor(context)
if not customPerms.tryGet('loginsSubjectsPoint'):
    customPerms.name='loginsSubjectsPoint'
    customPerms.description=u'Разрешение на отображение пункта меню Сотрудники и Пользователи'
    customPerms.type='navigator'
    customPerms.insert()
if not customPerms.tryGet('rolesPoint'):
    customPerms.name='rolesPoint'
    customPerms.description=u'Разрешение на отображение пункта меню Роли'
    customPerms.type='navigator'
    customPerms.insert()
if not customPerms.tryGet('permissionsPoint'):
    customPerms.name='permissionsPoint'
    customPerms.description=u'Разрешение на отображение пункта меню Разрешения'
    customPerms.type='navigator'
    customPerms.insert()        
if not customPerms.tryGet('numbersSeriesPoint'):
    customPerms.name='numbersSeriesPoint'
    customPerms.description=u'Разрешение на отображение пункта меню Серии номеров'
    customPerms.type='navigator'
    customPerms.insert()
rolesCustomPerms = rolesCustomPermsCursor(context)
if not rolesCustomPerms.tryGet('editor', 'loginsSubjectsPoint'):
    rolesCustomPerms.roleid='editor'
    rolesCustomPerms.permissionId='loginsSubjectsPoint'
    rolesCustomPerms.insert()
if not rolesCustomPerms.tryGet('editor', 'rolesPoint'):
    rolesCustomPerms.roleid='editor'
    rolesCustomPerms.permissionId='rolesPoint'
    rolesCustomPerms.insert()
if not rolesCustomPerms.tryGet('editor', 'permissionsPoint'):
    rolesCustomPerms.roleid='editor'
    rolesCustomPerms.permissionId='permissionsPoint'
    rolesCustomPerms.insert()
if not rolesCustomPerms.tryGet('editor', 'numbersSeriesPoint'):
    rolesCustomPerms.roleid='editor'
    rolesCustomPerms.permissionId='numbersSeriesPoint'
    rolesCustomPerms.insert()

#context.commit()
    

navigatorsParts['99'] = authentificationNavigator