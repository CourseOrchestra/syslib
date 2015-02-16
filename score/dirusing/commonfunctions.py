# coding: utf-8

import java.io.OutputStreamWriter as OutputStreamWriter
import java.io.InputStreamReader as InputStreamReader
import java.io.BufferedReader as BufferedReader
from java.io import FileOutputStream,ByteArrayOutputStream
from ru.curs.showcase.core.jython import JythonErrorResult
import base64
import simplejson as json
from common.sysfunctions import toHexForXml
try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    pass

def relatedTableCursorImport(grain_name, table_name):
    u'''Функция, выдающая класс курсора на таблицу, связанную с выбранным справочником '''

    # Модуль, откуда импортируем класс курсора
    name = '%s._%s_orm' % (grain_name, grain_name)
    # Название класса курсора
    fromlist = ['%sCursor' % table_name]
    return getattr(__import__(name, globals(), locals(), fromlist, -1), fromlist[0])

def getFieldsHeaders(table_meta, elem_type):
    u'''Функция для получения соответствия между реальными именами полей
    и заголовками в гриде. '''

    # Заносим служебные поля
    _headers = {'~~id':['~~id', 0, 0]}

    # Получаем список имён столбцов из метаданных
    col_names = table_meta.getColumns()
    # Проходим по каждому столбцу и получаем его CelestDoc
    for col_name in col_names:
        try:
            column_jsn = json.loads(table_meta.getColumn(col_name).getCelestaDoc())
            # Проверка на видимость столбца если грид
            if elem_type=="grid":
                if column_jsn["visualLength"] == '0':
                    continue
            _headers[col_name] = [column_jsn["name"], int(column_jsn["fieldTypeId"]), int(column_jsn["fieldOrderInSort"])]
        except:
            continue
    for col in _headers:
        _headers[col][0] = toHexForXml(_headers[col][0])

    return _headers

def getSortList(table_meta):
    u'''Функция для получения списка порядковых номеров полей для сортировки'''
    
    # Аналог в 1 строку без проверки на int не int
    #sort_list = map(lambda x: int(json.loads(table_meta.getColumn(x).getCelestaDoc())["fieldOrderInGrid"]), table_meta.getColumns())

    sort_list = []
    col_names = table_meta.getColumns()
    for col_name in col_names:
        try:
            column_meta = json.loads(table_meta.getColumn(col_name).getCelestaDoc())
            sort_number = int(column_meta["fieldOrderInSort"])
            if column_meta["visualLength"] == '0':
                continue
            else:
                sort_list.append(sort_number)
        except:
            continue
    return sorted(sort_list)

def findJsonValues(element, obj):
    u'''Рекурсивная функция для получения элемента внутри json '''
    results = []
    def _findJsonValues(element, obj):
        try:
            for key, value in obj.iteritems():
                if key == element:
                    results.append(value)
                elif not isinstance(value, basestring):
                    _findJsonValues(element, obj)
        except AttributeError:
            pass

        try:
            for item in obj:
                if not isinstance(item, basestring):
                    _findJsonValues(element, obj)
        except TypeError:
            pass

    if not isinstance(obj, basestring):
        _findJsonValues(element, obj)
    return results

def htmlDecode(string):
    return string.replace('_x0020_',' ').replace('_x002e_','.').replace('_x002d_','-').replace('_x0451_',u'ё').replace('_x0401_',u'Ё')

def readLongTextData(cursor, fieldname):
    u'''Функция для чтения полей типа Longtext. '''

    getattr(cursor, 'calc%s' % fieldname)()
    inr = BufferedReader(InputStreamReader(getattr(cursor, fieldname).getInStream(), 'utf-8'))
    filedata = ""
    while 1:
        onechar = inr.read()
        if onechar != -1:
            filedata += unichr(onechar)
        else:
            break
    return filedata

def insertLongTextData(cursor, fieldname, data):
    u'''Функция вставки Longtext в поле fieldname. '''

    # cursor.init() нужно ли это?
    getattr(cursor, 'calc%s' % fieldname)()
    osw = OutputStreamWriter(getattr(cursor, fieldname).getOutStream(), 'utf-8')
    try:
        osw.append(data)
    finally:
        osw.close()

    cursor.insert()

def downloadFileFromGrid(context, main=None, add=None, filterinfo=None,
                  session=None, elementId=None, recordId=None, columnId=None):
    u'''Функция для скачивания файла из грида. '''

    #raise Exception(json.loads(base64.b64decode(recordId)))
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Наводим курсор на текущую запись
    currentTable.get(json.loads(base64.b64decode(recordId)))
    # picture указана временно, пока columnId не реализован
    getattr(currentTable, 'calcattachment')()
    data = getattr(currentTable, 'attachment').getInStream()
    # Имя файла - расширение лучше указывать в отдельном поле в таблице
    fileName = '123.xml' 
    #data = open('C:\\eclipse\eclipse.ini')
    # Если в потоке что-то есть, тогда вызываем скачивание файла
    if data:
        return JythonDownloadResult(data, fileName)


def downloadFileFromXform(context, main=None, add=None, filterinfo=None,
                  session=None, elementId=None, xformsdata=None, columnId=None):
    u'''Функция для скачивания файла из карточки. '''

    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Наводим курсор на текущую запись
    currentTable.get(json.loads(xformsdata)["schema"]["row"])
    # Пока что столбец - picture, далее через columnId
    getattr(currentTable, 'calcattachment')()
    # Создаем поток
    data = getattr(currentTable, 'attachment').getInStream()
    # Имя файла - расширение лучше указывать в отдельном поле в таблице
    fileName = '%s.xml' % currentTable.text
    # Если в потоке что-то есть, тогда вызываем скачивание файла
    if data:
        return JythonDownloadResult(data, fileName)

def uploadFileToXform(context, main, add, filterinfo, session, elementId, xformsdata, fileName, file1):
    u'''Функция для загрузки файла из формы в БД. '''
    '''context, main, add, filterinfo, session, elementId, xformsdata, fileName, file1'''

    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Переводим курсор на запись
    #currentTable.get(json.loads(xformsdata)["schema"]["row"])
    currentTable.get('1234')
    getattr(currentTable, 'calcattachment')()
    # Поток для записи файла в базу
    outputstream = getattr(currentTable, 'attachment').getOutStream()
    # Промежуточный поток
    baos = ByteArrayOutputStream()
    # Побайтово читаем поток файла и пишем его в baos
    while 1:
        onebyte = file1.read()
        if onebyte != -1:
            baos.write(onebyte)
        else:
            break
    # baos пишем в outputstream       
    baos.writeTo(outputstream)
    # Обновляем курсор
    currentTable.update()
    return JythonErrorResult()


