# coding: utf-8

import java.io.OutputStreamWriter as OutputStreamWriter
import java.io.InputStreamReader as InputStreamReader
import java.io.BufferedReader as BufferedReader
from java.io import FileOutputStream, ByteArrayOutputStream, FileInputStream, File
import base64
import uuid
import json
from common.sysfunctions import toHexForXml
from importlib import import_module

try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
    from ru.curs.showcase.core.jython import JythonErrorResult
except:
    pass

g_importCache = {}

def getCursorDeweyColumns(table_meta):
    """Ищет в метаданных поля для работы с Дьюи: столбец кода и сортировки.
    
    Если такие имена столбцов не найдены, по умолчанию считается, что такими 
    являются поля курсора **deweyCode** и **deweySort** 
    
    @param table_meta метаданные курсора Celesta 
    @return (tuple of (string, string)) 0 - поле кода Дьюи, 1 - поле сортировки
    Дьюи 
    """
    deweyColumn = 'deweyCode'
    sortColumn = 'deweySort'
    
    for column in table_meta.getColumns():
        cDoc = {}
        try:
            cDoc = json.loads(table_meta.getColumn(column).getCelestaDoc())
        except:
            continue
            #получаем названиe колонкu с кодом дьюи 
        if cDoc['name'] in (u'deweyCode', u'deweyCod', u'deweyKod'):
            deweyColumn = column
        if cDoc['name'] == u'sortNumber':
            sortColumn = column
            
    return deweyColumn, sortColumn

def importcache(func):
    def wrapper(grain_name, table_name):
        try:
            return g_importCache[(grain_name, table_name)]
        except KeyError:
            res = func(grain_name, table_name)
            g_importCache[(grain_name, table_name)] = res 
            return res
        
        raise Exception('Error during import cache!')
    
    return wrapper

@importcache
def relatedTableCursorImport(grain_name, table_name):
    u'''Функция, выдающая класс курсора на таблицу, связанную с выбранным справочником 
    
    Еcли table_name в формате <grain>.<table>, то имя гранулы берётся из table_name.
    Если table_name без указания гранулы, то используется grain_name.
    '''
    tn = table_name
    gn = table_name.split('.')
    if len(gn) == 1:
        gn = grain_name  
    elif len(gn) == 2:
        tn = gn[1]
        gn = gn[0]
    else:
        raise Exception('Incorrect table name: <table> or <grain>.<table> expected but %s given.' % str(table_name))
    
    # Модуль, откуда импортируем класс курсора
    name = '%s._%s_orm' % (gn, gn)
    
    return getattr(import_module(name), tn + "Cursor")
#     # Название класса курсора
#     fromlist = ['%sCursor' % table_name]
#     return getattr(__import__(name, globals(), locals(), fromlist, -1), fromlist[0])




def getFieldsHeaders(table_meta, elem_type):
    u'''Функция для получения соответствия между реальными именами полей
    и заголовками в гриде.
    
    Возвращает словарь вида:
        {<Имя поля>: 
            [<Имя столбца для XML>,    #индекс 0 
            <ИД типа>,                 #индекс 1
            <Порядок>,                 #индекс 2
            <Имя столбца>              #индекс 3
            ]
        }
    '''

    # Заносим служебные поля
    _headers = {'~~id':['~~id', 0, 0, '~~id']}

    # Получаем список имён столбцов из метаданных
    col_names = table_meta.getColumns()
    # Проходим по каждому столбцу и получаем его CelestDoc
    for col_name in col_names:
        try:
            column_jsn = json.loads(table_meta.getColumn(col_name).getCelestaDoc())
            # Проверка на видимость столбца если грид
            if elem_type == "grid":
                if column_jsn["visualLength"] == '0':
                    continue
            _headers[col_name] = [column_jsn["name"], int(column_jsn["fieldTypeId"]), int(column_jsn["fieldOrderInSort"]), column_jsn["name"]]
        except:
            continue
    for col in _headers:
        _headers[col][0] = toHexForXml(_headers[col][0])
#         _headers[col][3] = htmlDecode(_headers[col][0])

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
    return string.replace('_x0020_', ' ').replace('_x002e_', '.').replace('_x002d_', '-').replace('_x0451_', u'ё').replace('_x0401_', u'Ё')

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
        try:
            return JythonDownloadResult(data, fileName)
        except:
            return None


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
    newfileid = ''
    #raise Exception(xformsdata,session)
    try:
        currentRecordId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        selectedRecordId = json.loads(base64.b64decode(str(currentRecordId)))
    except:
        context.warning("Error: cannot get Current record id")
    # Получение курсора на таблицу
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    fields = currentTable.meta().getColumns()
    fileid = None
    if 'currentRecordId' in json.loads(session)['sessioncontext']['related']['gridContext']:
        currentRecordId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']
        selectedRecordId = json.loads(base64.b64decode(str(currentRecordId)))
        currentTable.get(*selectedRecordId)
    for field in fields:
        column_jsn = json.loads(currentTable.meta().getColumn(field).getCelestaDoc())
        if column_jsn["fieldTypeId"] == "4":
            filecolumn = field
            if "refTable" in column_jsn:
                refTableName = column_jsn["refTable"]
                refTableColumnId = column_jsn["refTableColumnId"]
                refFileColumn = column_jsn["refFileColumn"]
                relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                fileid = getattr(currentTable, filecolumn)
                if fileid != None:
                    relatedTable.setRange(refTableColumnId, fileid)
                    relatedTable.first()
                else:
                    newfileid = uuid.uuid4()
                    setattr(relatedTable, refTableColumnId, newfileid)
                    setattr(currentTable, filecolumn, newfileid)
            break
    # Переводим курсор на запись

    try:
        if newfileid != '':
            getattr(relatedTable, 'calc' + refFileColumn)()
        else:
            getattr(currentTable, 'calc' + filecolumn)()
    except:
        context.error("Error: cannot calculate blob file. Column %s Table %s" % (refFileColumn, refTableName))
    # Поток для записи файла в базу

    try:
        if newfileid != '':
            outputstream = OutputStreamWriter(getattr(relatedTable, refFileColumn).getOutStream(), 'utf-8')
        else:
            outputstream = OutputStreamWriter(getattr(currentTable, filecolumn).getOutStream(), 'utf-8')
    except:
        context.error("Error: cannot create outputstream object")

    #outputstream = getattr(currentTable, 'attachment').getOutStream()
    # Промежуточный поток

    # Побайтово читаем поток файла и пишем его в baos
    while 1:
        #i=i+1
        try:
            onebyte = file1.read()
        except:
            context.error("Error: cannot read from file to import")
        if onebyte != -1:
            try:
                outputstream.write(onebyte)
            except:
                context.error("Error: cannot write binary data to table during import. filecolumn is %s, data %s" % (filecolumn, onebyte))
        else:
            break
    #raise Exception (str(i))
    if newfileid != '':
        relatedTable.insert()
        currentTable.update()


    else:
        currentTable.update()
    context.message("File uploaded successfully")
    #return JythonErrorResult()


