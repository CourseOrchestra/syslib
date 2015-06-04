# coding: utf-8
from ru.curs.celesta.dbutils import XMLSerializer
from java.lang import String
from java.io import ByteArrayInputStream, ByteArrayOutputStream

from lyra.basicForm import BasicForm

class CardForm(BasicForm):
    u'''Базовый класс для формы типа карточка, реализованной в Лире'''
    def findRec(self):
        c = self._getCursor()
        c.navigate('-')
        result = ByteArrayOutputStream()
        XMLSerializer.serialize(c, result)
        return result.toString("utf-8");

    def move(self, cmd, data):
        c = self._getCursor()

        dataIS = ByteArrayInputStream(data.encode("UTF-8"))
        XMLSerializer.deserialize(c, dataIS)

        c2 = self._getCursor()
        c2.copyFieldsFrom(c)
        if c2.tryGetCurrent():
            c2.copyFieldsFrom(c)
            c2.update()
        else:
            c.insert()
        c.navigate(cmd)
        result = ByteArrayOutputStream()
        XMLSerializer.serialize(c, result)
        return result.toString("utf-8");

    def newRec(self):
        c = self._getCursor()
        c.clear()
        c.setRecversion(0)
        result = ByteArrayOutputStream()
        XMLSerializer.serialize(c, result)
        return result.toString("utf-8");

    def deleteRec(self, data):
        c = self._getCursor()

        dataIS = ByteArrayInputStream(data.encode("UTF-8"))
        XMLSerializer.deserialize(c, dataIS)

        c.delete()
        if not c.navigate('>+'):
            c.clear()
            c.setRecversion(0)
        result = ByteArrayOutputStream()
        XMLSerializer.serialize(c, result)
        return result.toString("utf-8");

