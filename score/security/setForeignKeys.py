# coding: utf-8

from ru.curs.celesta.score import ForeignKey, FKRule, IntegerColumn
from security.functions import Settings


def setForeignKeys(context):
    settings=Settings()
    celesta = context.getCelesta()
    score = celesta.getScore()
    security_grain = score.getGrain('security')
    subject_table=security_grain.getTable("subjects")
    login_table=security_grain.getTable("logins")
    try:
        password_field = login_table.getColumn("password")
        password_field.setNullableAndDefault(settings.isUseAuthServer())
    except:
        pass
    #subject_column=subject_table.getColumn("employeeId")
    employees_grain=score.getGrain(settings.getEmployeesParam("employeesGrain"))
    employees_table=employees_grain.getTable(settings.getEmployeesParam("employeesTable"))
    employees_id = employees_table.getColumn(settings.getEmployeesParam("employeesId"))
    if isinstance(employees_id, IntegerColumn):
        subject_table.getColumn("employeeId").delete()
        IntegerColumn(subject_table, "employeeId")
    else:        
        employees_id_length = employees_id.getLength()
        subject_table.getColumn("employeeId").setLength(unicode(employees_id_length))
    try:            
        logins_keys = login_table.getForeignKeys()
        for logins_key in logins_keys:
            #if logins_key.getReferencedTable() == subject_table:
            logins_key.delete()                                
                #break
        logins_key = ForeignKey(login_table, subject_table, ["subjectId"])
        subjects_keys = subject_table.getForeignKeys()
        for subjects_key in subjects_keys:
            #if subjects_key.getReferencedTable() == employees_table:
            subjects_key.delete()
                #break
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
        settings.settingsJSONSave() #deprecated. Метод пустой.
    
#setForeignKeys()