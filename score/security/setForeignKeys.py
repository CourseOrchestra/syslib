# coding: utf-8

from ru.curs.celesta import Celesta
from ru.curs.celesta.score import ForeignKey, FKRule
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from security.functions import Settings
from ru.curs.celesta import SessionContext

settings=Settings()


def setForeignKeys(context):
    tableSettings=settings.getSettingsJSON()

    celesta = context.getCelesta()
    score = celesta.getScore()
    security_grain = score.getGrain('security')
    subject_table=security_grain.getTable("subjects")
    login_table=security_grain.getTable("logins")
    #subject_column=subject_table.getColumn("employeeId")
    employees_grain=score.getGrain(tableSettings["employeesGrain"])
    employees_table=employees_grain.getTable(tableSettings["employeesTable"])
    try:    
        
        logins_keys = login_table.getForeignKeys()
        loginSubjectKeyExists = False
        for logins_key in logins_keys:
            if logins_key.getReferencedTable() == subject_table:
                loginSubjectKeyExists = True
                break
        if not loginSubjectKeyExists:
            logins_key = ForeignKey(login_table, subject_table, ["subjectId"])
        subjects_keys = subject_table.getForeignKeys()
        subjectEmployeeKeyExists = False
        for subjects_key in subjects_keys:
            if subjects_key.getReferencedTable() == employees_table:
                subjectEmployeeKeyExists = True
                break
        if not subjectEmployeeKeyExists:
            subjects_key = ForeignKey(subject_table, employees_table, ["employeeId"])
        if settings.loginIsSubject():
            logins_key.setDeleteRule(FKRule.CASCADE)
            subjects_key.setDeleteRule(FKRule.SET_NULL)
        else:
            logins_key.setDeleteRule(FKRule.SET_NULL)
        score.save()
        celesta.reInitialize()
        settings.setEmployeesParam("isSystemInitialised", "true")
    finally:
        settings.settingsJSONSave()
    
#setForeignKeys()