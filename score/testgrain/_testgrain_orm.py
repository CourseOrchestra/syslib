# coding=UTF-8
# Source grain parameters: version=1.0, len=5313, crc32=D4BF56D5.
"""
THIS MODULE IS BEING CREATED AUTOMATICALLY EVERY TIME CELESTA STARTS.
DO NOT MODIFY IT AS YOUR CHANGES WILL BE LOST.
"""
import ru.curs.celesta.dbutils.Cursor as Cursor
import ru.curs.celesta.dbutils.ViewCursor as ViewCursor
from java.lang import Object
from jarray import array

class employeesCursor(Cursor):
    onPreDelete  = []
    onPostDelete = []
    onPreInsert  = []
    onPostInsert = []
    onPreUpdate  = []
    onPostUpdate = []
    def __init__(self, context):
        Cursor.__init__(self, context)
        self.id = None
        self.name = None
        self.lastname = None
        self.adress_id = None
        self.adress_ids = None
        self.context = context
    def _grainName(self):
        return 'testgrain'
    def _tableName(self):
        return 'employees'
    def _parseResult(self, rs):
        self.id = rs.getInt('id')
        if rs.wasNull():
            self.id = None
        self.name = rs.getString('name')
        if rs.wasNull():
            self.name = None
        self.lastname = rs.getString('lastname')
        if rs.wasNull():
            self.lastname = None
        self.adress_id = rs.getString('adress_id')
        if rs.wasNull():
            self.adress_id = None
        self.adress_ids = rs.getString('adress_ids')
        if rs.wasNull():
            self.adress_ids = None
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.id = None
            self.name = None
        self.lastname = None
        self.adress_id = None
        self.adress_ids = None
    def _currentKeyValues(self):
        return array([None if self.id == None else int(self.id), None if self.name == None else unicode(self.name)], Object)
    def _currentValues(self):
        return array([None if self.id == None else int(self.id), None if self.name == None else unicode(self.name), None if self.lastname == None else unicode(self.lastname), None if self.adress_id == None else unicode(self.adress_id), None if self.adress_ids == None else unicode(self.adress_ids)], Object)
    def _setAutoIncrement(self, val):
        self.id = val
    def _preDelete(self):
        for f in employeesCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in employeesCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in employeesCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in employeesCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in employeesCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in employeesCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self):
        result = employeesCursor(self.callContext())
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.id = c.id
        self.name = c.name
        self.lastname = c.lastname
        self.adress_id = c.adress_id
        self.adress_ids = c.adress_ids
    def iterate(self):
        if self.tryFirst():
            while True:
                yield self
                if not self.next():
                    break

class adressesCursor(Cursor):
    onPreDelete  = []
    onPostDelete = []
    onPreInsert  = []
    onPostInsert = []
    onPreUpdate  = []
    onPostUpdate = []
    def __init__(self, context):
        Cursor.__init__(self, context)
        self.postalcode = None
        self.country = None
        self.city = None
        self.street = None
        self.building = None
        self.flat = None
        self.attachment = None
        self.context = context
    def _grainName(self):
        return 'testgrain'
    def _tableName(self):
        return 'adresses'
    def _parseResult(self, rs):
        self.postalcode = rs.getString('postalcode')
        if rs.wasNull():
            self.postalcode = None
        self.country = rs.getString('country')
        if rs.wasNull():
            self.country = None
        self.city = rs.getString('city')
        if rs.wasNull():
            self.city = None
        self.street = rs.getString('street')
        if rs.wasNull():
            self.street = None
        self.building = rs.getString('building')
        if rs.wasNull():
            self.building = None
        self.flat = rs.getString('flat')
        if rs.wasNull():
            self.flat = None
        self.attachment = None
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.postalcode = None
            self.building = None
            self.flat = None
        self.country = None
        self.city = None
        self.street = None
        self.attachment = None
    def _currentKeyValues(self):
        return array([None if self.postalcode == None else unicode(self.postalcode), None if self.building == None else unicode(self.building), None if self.flat == None else unicode(self.flat)], Object)
    def _currentValues(self):
        return array([None if self.postalcode == None else unicode(self.postalcode), None if self.country == None else unicode(self.country), None if self.city == None else unicode(self.city), None if self.street == None else unicode(self.street), None if self.building == None else unicode(self.building), None if self.flat == None else unicode(self.flat), self.attachment], Object)
    def calcattachment(self):
        self.attachment = self.calcBlob('attachment')
        self.getXRec().attachment = self.attachment.clone()
    def _setAutoIncrement(self, val):
        pass
    def _preDelete(self):
        for f in adressesCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in adressesCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in adressesCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in adressesCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in adressesCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in adressesCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self):
        result = adressesCursor(self.callContext())
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.postalcode = c.postalcode
        self.country = c.country
        self.city = c.city
        self.street = c.street
        self.building = c.building
        self.flat = c.flat
        self.attachment = c.attachment
    def iterate(self):
        if self.tryFirst():
            while True:
                yield self
                if not self.next():
                    break

class adresses_newCursor(Cursor):
    onPreDelete  = []
    onPostDelete = []
    onPreInsert  = []
    onPostInsert = []
    onPreUpdate  = []
    onPostUpdate = []
    def __init__(self, context):
        Cursor.__init__(self, context)
        self.postalcode = None
        self.country = None
        self.city = None
        self.street = None
        self.building = None
        self.flat = None
        self.attachment = None
        self.context = context
    def _grainName(self):
        return 'testgrain'
    def _tableName(self):
        return 'adresses_new'
    def _parseResult(self, rs):
        self.postalcode = rs.getString('postalcode')
        if rs.wasNull():
            self.postalcode = None
        self.country = rs.getString('country')
        if rs.wasNull():
            self.country = None
        self.city = rs.getString('city')
        if rs.wasNull():
            self.city = None
        self.street = rs.getString('street')
        if rs.wasNull():
            self.street = None
        self.building = rs.getString('building')
        if rs.wasNull():
            self.building = None
        self.flat = rs.getString('flat')
        if rs.wasNull():
            self.flat = None
        self.attachment = None
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.postalcode = None
        self.country = None
        self.city = None
        self.street = None
        self.building = None
        self.flat = None
        self.attachment = None
    def _currentKeyValues(self):
        return array([None if self.postalcode == None else unicode(self.postalcode)], Object)
    def _currentValues(self):
        return array([None if self.postalcode == None else unicode(self.postalcode), None if self.country == None else unicode(self.country), None if self.city == None else unicode(self.city), None if self.street == None else unicode(self.street), None if self.building == None else unicode(self.building), None if self.flat == None else unicode(self.flat), self.attachment], Object)
    def calcattachment(self):
        self.attachment = self.calcBlob('attachment')
        self.getXRec().attachment = self.attachment.clone()
    def _setAutoIncrement(self, val):
        pass
    def _preDelete(self):
        for f in adresses_newCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in adresses_newCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in adresses_newCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in adresses_newCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in adresses_newCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in adresses_newCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self):
        result = adresses_newCursor(self.callContext())
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.postalcode = c.postalcode
        self.country = c.country
        self.city = c.city
        self.street = c.street
        self.building = c.building
        self.flat = c.flat
        self.attachment = c.attachment
    def iterate(self):
        if self.tryFirst():
            while True:
                yield self
                if not self.next():
                    break

class mapping_testCursor(Cursor):
    onPreDelete  = []
    onPostDelete = []
    onPreInsert  = []
    onPostInsert = []
    onPreUpdate  = []
    onPostUpdate = []
    def __init__(self, context):
        Cursor.__init__(self, context)
        self.id = None
        self.ak1 = None
        self.ak2 = None
        self.bk1 = None
        self.bk2 = None
        self.bk3 = None
        self.context = context
    def _grainName(self):
        return 'testgrain'
    def _tableName(self):
        return 'mapping_test'
    def _parseResult(self, rs):
        self.id = rs.getInt('id')
        if rs.wasNull():
            self.id = None
        self.ak1 = rs.getInt('ak1')
        if rs.wasNull():
            self.ak1 = None
        self.ak2 = rs.getString('ak2')
        if rs.wasNull():
            self.ak2 = None
        self.bk1 = rs.getString('bk1')
        if rs.wasNull():
            self.bk1 = None
        self.bk2 = rs.getString('bk2')
        if rs.wasNull():
            self.bk2 = None
        self.bk3 = rs.getString('bk3')
        if rs.wasNull():
            self.bk3 = None
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.id = None
        self.ak1 = None
        self.ak2 = None
        self.bk1 = None
        self.bk2 = None
        self.bk3 = None
    def _currentKeyValues(self):
        return array([None if self.id == None else int(self.id)], Object)
    def _currentValues(self):
        return array([None if self.id == None else int(self.id), None if self.ak1 == None else int(self.ak1), None if self.ak2 == None else unicode(self.ak2), None if self.bk1 == None else unicode(self.bk1), None if self.bk2 == None else unicode(self.bk2), None if self.bk3 == None else unicode(self.bk3)], Object)
    def _setAutoIncrement(self, val):
        self.id = val
    def _preDelete(self):
        for f in mapping_testCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in mapping_testCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in mapping_testCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in mapping_testCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in mapping_testCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in mapping_testCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self):
        result = mapping_testCursor(self.callContext())
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.id = c.id
        self.ak1 = c.ak1
        self.ak2 = c.ak2
        self.bk1 = c.bk1
        self.bk2 = c.bk2
        self.bk3 = c.bk3
    def iterate(self):
        if self.tryFirst():
            while True:
                yield self
                if not self.next():
                    break

