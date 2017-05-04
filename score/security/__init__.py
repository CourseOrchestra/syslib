# coding: utf-8
from common.navigator import navigatorsParts
from common.sysfunctions import tableCursorImport
from security.functions import Settings
from security.navigator import authentificationNavigator
from security.securityInit import securityInit
from security.setForeignKeys import setForeignKeys as setConstraint
from security.xform.users import employeesSubjectsPostInsert, employeesSubjectsPostUpdate, employeesSubjectsPreDelete

isInitContext = True
try:
    import initcontext
except ImportError:
    isInitContext = False

settings = Settings()
if not settings.loginIsSubject() and settings.isEmployees():
    # Если роли привязываются к сотруднику и таблица сотрудников настроена (нужные настройки есть в grainSettings.xml),
    # привязываем к ней триггеры.
    employeesGrain = settings.getEmployeesParam("employeesGrain")
    employeesTable = settings.getEmployeesParam("employeesTable")
    employeesCursor = tableCursorImport(employeesGrain, employeesTable)

    employeesCursor.onPostInsert.append(employeesSubjectsPostInsert)
    employeesCursor.onPostUpdate.append(employeesSubjectsPostUpdate)
    employeesCursor.onPreDelete.append(employeesSubjectsPreDelete)

if not settings.isSystemInitialised():
    if isInitContext:
        context = initcontext()
        setConstraint(
            context)  # функция устанавливает внешний ключ в таблицу subjects и меняет значение параметра isSystemInitialised на True
        securityInit(context)  # добавление в базу необходимых для работы гранулы данных

navigatorsParts['securityNavigator'] = authentificationNavigator
