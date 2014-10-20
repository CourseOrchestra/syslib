# coding: utf-8
import simplejson

from java.io import StringWriter
from javax.xml.stream import XMLOutputFactory

from ru.curs.celesta import CelestaException


class XMLJSONConverter():
    u'''Класс позволяет конвертировать JSON в XML и обратно'''

    def __init__(self, output=None, input=None, input_string=None, indent=0, isSorted=0, output_file_append=False):

        self.indent = indent
        self.isSorted = isSorted
        pretty_print = self.indent and (self.indent > -1);

        self.output_file_append = output_file_append
        #self.set_output(output)

        if input is not None: # input is given priority.
            self.input = input
        else:
            self.input = simplejson.loads(unicode(input_string).encode("utf8"))

    def sortJSONForXML(self, inputString):
        if inputString[0] == '@':
            return 0
        elif inputString == '#text':
            return 1
        elif inputString == '#sorted':
            return 2
        else:
            return 3

    def parse (self):
        return self.jsonParse(self.input)

    def jsonParse (self, curDict):
        self.stringWriter = StringWriter()
        self.xmlWriter = XMLOutputFactory.newInstance().createXMLStreamWriter(self.stringWriter)

        if isinstance(curDict, dict):
            self.dictParse(curDict)
#            rootElement = curDict.keys()[0]             
#            self.xmlWriter.writeStartElement(unicode(rootElement).encode("utf8"))
#            if isinstance(curDict[rootElement], dict):
#                self.dictParse(curDict[rootElement])
#            elif isinstance(curDict[rootElement], list):
#                self.arrParse(rootElement, curDict[rootElement])
#            else:
#                self.xmlWriter.writeCharacters(unicode(curDict[rootElement]).encode("utf8"))
#            self.xmlWriter.writeCharacters('\n' * self.indent)
#            self.xmlWriter.writeEndElement()
        else:
            raise  CelestaException(u'Неверный формат данных,  объект должен иметь тип JSON')

        self.xmlWriter.close()
        return self.stringWriter.toString().decode("utf8")

    def dictParse (self, curDict):
        for item in sorted(curDict, key=self.sortJSONForXML):
            if item[0] == '@':
                self.xmlWriter.writeAttribute(unicode(item[1:]).encode("utf8"), unicode(curDict[item]).encode("utf8") if curDict[item] is not None else u"")

            elif item == '#text':
                self.xmlWriter.writeCharacters(unicode(curDict[item]).encode("utf8"))

            elif item == '#sorted':
                if isinstance(curDict[item], list) and curDict[item]:
                    for itemArr in curDict[item]:
                        self.dictParse(itemArr)
                else:
                    raise  CelestaException(u'Неверный формат данных,  объект #sorted должен иметь тип list')

            elif isinstance(curDict[item], dict) and curDict[item]:
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeStartElement(unicode(item).encode("utf8"))
                self.dictParse(curDict[item])
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeEndElement()

            elif isinstance(curDict[item], list) and curDict[item]:
                self.arrParse(item, curDict[item])

            elif isinstance(curDict[item], (int, float)):
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeStartElement(unicode(item).encode("utf8"))
                self.xmlWriter.writeCharacters(unicode(curDict[item]).encode("utf8"))
                self.xmlWriter.writeEndElement()

            else:
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeStartElement(unicode(item).encode("utf8"))
                self.xmlWriter.writeCharacters(unicode(curDict[item] or "").encode("utf8"))
                self.xmlWriter.writeEndElement()

    def arrParse (self, elName, curArray):
        for item in curArray:
            if isinstance(item, dict) and item:
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeStartElement(unicode(elName).encode("utf8"))
                self.dictParse(item)
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeEndElement()
            elif isinstance(item, (int, float)):
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeStartElement(unicode(elName).encode("utf8"))
                self.xmlWriter.writeCharacters(unicode(item).encode("utf8"))
                self.xmlWriter.writeEndElement()
            else:
                self.xmlWriter.writeCharacters('\n' * self.indent)
                self.xmlWriter.writeStartElement(unicode(elName).encode("utf8"))
                self.xmlWriter.writeCharacters(unicode(item or "").encode("utf8"))
                self.xmlWriter.writeEndElement()

