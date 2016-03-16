# coding=UTF-8
# Source grain parameters: version=0.1, len=976, crc32=6714E3BA; compiler=7.
"""
THIS MODULE IS BEING CREATED AUTOMATICALLY EVERY TIME CELESTA STARTS.
DO NOT MODIFY IT AS YOUR CHANGES WILL BE LOST.
"""
import ru.curs.celesta.dbutils.Cursor as Cursor
import ru.curs.celesta.dbutils.ViewCursor as ViewCursor
import ru.curs.celesta.dbutils.ReadOnlyTableCursor as ReadOnlyTableCursor
from java.lang import Object
from jarray import array
from java.util import Calendar, GregorianCalendar
from java.sql import Timestamp
import datetime

def _to_timestamp(d):
    if isinstance(d, datetime.datetime):
        calendar = GregorianCalendar()
        calendar.set(d.year, d.month - 1, d.day, d.hour, d.minute, d.second)
        ts = Timestamp(calendar.getTimeInMillis())
        ts.setNanos(d.microsecond * 1000)
        return ts
    else:
        return d

class fileCursor(Cursor):
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
        self.uploadVersioning = None
        self.context = context
    def _grainName(self):
        return 'fileRepository'
    def _tableName(self):
        return 'file'
    def _parseResult(self, rs):
        self.id = rs.getString('id')
        if rs.wasNull():
            self.id = None
        self.name = rs.getString('name')
        if rs.wasNull():
            self.name = None
        self.uploadVersioning = rs.getBoolean('uploadVersioning')
        if rs.wasNull():
            self.uploadVersioning = None
        self.recversion = rs.getInt('recversion')
    def _setFieldValue(self, name, value):
        setattr(self, name, value)
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.id = None
        self.name = None
        self.uploadVersioning = None
    def _currentKeyValues(self):
        return array([None if self.id == None else unicode(self.id)], Object)
    def _currentValues(self):
        return array([None if self.id == None else unicode(self.id), None if self.name == None else unicode(self.name), None if self.uploadVersioning == None else bool(self.uploadVersioning)], Object)
    def _setAutoIncrement(self, val):
        pass
    def _preDelete(self):
        for f in fileCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in fileCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in fileCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in fileCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in fileCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in fileCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self, context):
        result = fileCursor(context)
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.id = c.id
        self.name = c.name
        self.uploadVersioning = c.uploadVersioning
        self.recversion = c.recversion
    def iterate(self):
        if self.tryFindSet():
            while True:
                yield self
                if not self.nextInSet():
                    break

class fileVersionCursor(Cursor):
    onPreDelete  = []
    onPostDelete = []
    onPreInsert  = []
    onPostInsert = []
    onPreUpdate  = []
    onPostUpdate = []
    def __init__(self, context):
        Cursor.__init__(self, context)
        self.id = None
        self.fileId = None
        self.clasterId = None
        self.fileName = None
        self.versionMajor = None
        self.versionMinor = None
        self.exist = None
        self.timestamp = None
        self.context = context
    def _grainName(self):
        return 'fileRepository'
    def _tableName(self):
        return 'fileVersion'
    def _parseResult(self, rs):
        self.id = rs.getString('id')
        if rs.wasNull():
            self.id = None
        self.fileId = rs.getString('fileId')
        if rs.wasNull():
            self.fileId = None
        self.clasterId = rs.getInt('clasterId')
        if rs.wasNull():
            self.clasterId = None
        self.fileName = rs.getString('fileName')
        if rs.wasNull():
            self.fileName = None
        self.versionMajor = rs.getInt('versionMajor')
        if rs.wasNull():
            self.versionMajor = None
        self.versionMinor = rs.getInt('versionMinor')
        if rs.wasNull():
            self.versionMinor = None
        self.exist = rs.getBoolean('exist')
        if rs.wasNull():
            self.exist = None
        self.timestamp = rs.getTimestamp('timestamp')
        if rs.wasNull():
            self.timestamp = None
        self.recversion = rs.getInt('recversion')
    def _setFieldValue(self, name, value):
        setattr(self, name, value)
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.id = None
        self.fileId = None
        self.clasterId = None
        self.fileName = None
        self.versionMajor = None
        self.versionMinor = None
        self.exist = None
        self.timestamp = None
    def _currentKeyValues(self):
        return array([None if self.id == None else unicode(self.id)], Object)
    def _currentValues(self):
        return array([None if self.id == None else unicode(self.id), None if self.fileId == None else unicode(self.fileId), None if self.clasterId == None else int(self.clasterId), None if self.fileName == None else unicode(self.fileName), None if self.versionMajor == None else int(self.versionMajor), None if self.versionMinor == None else int(self.versionMinor), None if self.exist == None else bool(self.exist), _to_timestamp(self.timestamp)], Object)
    def _setAutoIncrement(self, val):
        pass
    def _preDelete(self):
        for f in fileVersionCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in fileVersionCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in fileVersionCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in fileVersionCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in fileVersionCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in fileVersionCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self, context):
        result = fileVersionCursor(context)
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.id = c.id
        self.fileId = c.fileId
        self.clasterId = c.clasterId
        self.fileName = c.fileName
        self.versionMajor = c.versionMajor
        self.versionMinor = c.versionMinor
        self.exist = c.exist
        self.timestamp = c.timestamp
        self.recversion = c.recversion
    def iterate(self):
        if self.tryFindSet():
            while True:
                yield self
                if not self.nextInSet():
                    break

class fileCounterCursor(Cursor):
    onPreDelete  = []
    onPostDelete = []
    onPreInsert  = []
    onPostInsert = []
    onPreUpdate  = []
    onPostUpdate = []
    def __init__(self, context):
        Cursor.__init__(self, context)
        self.clasterId = None
        self.latestFileName = None
        self.context = context
    def _grainName(self):
        return 'fileRepository'
    def _tableName(self):
        return 'fileCounter'
    def _parseResult(self, rs):
        self.clasterId = rs.getInt('clasterId')
        if rs.wasNull():
            self.clasterId = None
        self.latestFileName = rs.getInt('latestFileName')
        if rs.wasNull():
            self.latestFileName = None
        self.recversion = rs.getInt('recversion')
    def _setFieldValue(self, name, value):
        setattr(self, name, value)
    def _clearBuffer(self, withKeys):
        if withKeys:
            self.clasterId = None
        self.latestFileName = None
    def _currentKeyValues(self):
        return array([None if self.clasterId == None else int(self.clasterId)], Object)
    def _currentValues(self):
        return array([None if self.clasterId == None else int(self.clasterId), None if self.latestFileName == None else int(self.latestFileName)], Object)
    def _setAutoIncrement(self, val):
        pass
    def _preDelete(self):
        for f in fileCounterCursor.onPreDelete:
            f(self)
    def _postDelete(self):
        for f in fileCounterCursor.onPostDelete:
            f(self)
    def _preInsert(self):
        for f in fileCounterCursor.onPreInsert:
            f(self)
    def _postInsert(self):
        for f in fileCounterCursor.onPostInsert:
            f(self)
    def _preUpdate(self):
        for f in fileCounterCursor.onPreUpdate:
            f(self)
    def _postUpdate(self):
        for f in fileCounterCursor.onPostUpdate:
            f(self)
    def _getBufferCopy(self, context):
        result = fileCounterCursor(context)
        result.copyFieldsFrom(self)
        return result
    def copyFieldsFrom(self, c):
        self.clasterId = c.clasterId
        self.latestFileName = c.latestFileName
        self.recversion = c.recversion
    def iterate(self):
        if self.tryFindSet():
            while True:
                yield self
                if not self.nextInSet():
                    break

