# coding: utf-8

from java.io import FileOutputStream,File,ByteArrayOutputStream
from java.text import SimpleDateFormat
import json
import datetime
import xml.etree.ElementTree as ET
from org.apache.poi.hssf.usermodel import HSSFWorkbook,HSSFDataFormat,HSSFCellStyle,DVConstraint,HSSFDataValidation
from org.apache.poi.hssf.util import HSSFColor
from org.apache.poi.ss.util import CellRangeAddressList,CellReference
from dirusing.commonfunctions import relatedTableCursorImport,getCursorDeweyColumns
from common.hierarchy import generateSortValue
from dirusing.hierarchy import getNewItemInUpperLevel

try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    pass
def getColumnJsns(table_meta):
    '''Метод возвращает лист json-ов всех полей таблицы с их названиями'''
    output=[]
    for col in table_meta.getColumns():
        try:
            column_jsn = json.loads(table_meta.getColumn(col).getCelestaDoc())
        except TypeError:
            column_jsn=None
        output.append({"name":col,'jsn':column_jsn})
    return output

def importXlsDataOld(context, main, add, filterinfo, session, elementId, xformsdata, fileName, file1):
    u'''Функция для загрузки файла из формы в БД. '''
    '''context, main, add, filterinfo, session, elementId, xformsdata, fileName, file1'''
    
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    currentTable = relatedTableCursorImport(grain_name,table_name)(context)
    table_meta = context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
    fields = table_meta.getColumns()
    
    xlsColumns = []
    
    baos = ByteArrayOutputStream()
    # Побайтово читаем поток файла и пишем его в baos
    while 1:
        onebyte = file1.read()
        if onebyte!=-1:
            baos.write(onebyte)
        else:
            break   
    xls = baos.toString("UTF-8")

    root = ET.fromstring(xls.encode("utf-8"))
    
    rows = root.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Row')
    for i,row in enumerate(rows):
        for j,cell in enumerate(row):
            try:
                text = cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data').text
            except AttributeError:
                text=None
                continue
            #заполнение заголовков
            if i == 0:
                for field in fields:
                    try:
                        column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
                    except TypeError:
                        xlsColumns.append([text,field,'0'])
                        continue
                    column_name = column_jsn["name"]
                    if text == column_name:
                        fieldType = column_jsn["fieldTypeId"]
                        if table_meta.getColumn(field).jdbcGetterName() == 'getInt':
                            isIdentity = table_meta.getColumn(field).isIdentity()
                        else:
                            isIdentity = 'False'
                        xlsColumns.append([text,field,fieldType,isIdentity])
            
            else:
                if xlsColumns[j][2] == '0':
                    continue
                elif xlsColumns[j][2] == '2':
                    text = datetime.datetime(1998, 1, 1)
                elif xlsColumns[j][2] == '3':
                    if ',' in text and '.' in text:
                        text = text.replace(',','')
                    if len(text)>7:
                        text = text.replace(',','')
                elif xlsColumns[j][2] == '5':
                    if xlsColumns[j][3] == True:
                        text = None
                setattr(currentTable, xlsColumns[j][1], text)
        if table_meta.getColumn('id').jdbcGetterName() == 'getInt':
            setattr(currentTable, 'id', None)
        if i!=0:
            currentTable.insert()
        row.clear()
    root.clear()   
    return None

def importXlsData(context, main, add, filterinfo, session, elementId, xformsdata, fileName, file1):
    u'''Функция для загрузки файла из формы в БД. '''
    '''context, main, add, filterinfo, session, elementId, xformsdata, fileName, file1'''
    #имя гранулы
    grain_name = json.loads(main)['grain']
    IgnoreIdentity = json.loads(xformsdata)['schema']['resetIdentity']
#метод заполнения таблицы с одного листа excel, название листа=название таблицы
    def fillTable(currentTable,table_meta,sht,table_jsn):
        #поля таблицы
        fields = table_meta.getColumns()
        columnJsns=getColumnJsns(table_meta)
    #признак иерархичности
        isHierarchical = table_jsn['isHierarchical'] == "true"
        if isHierarchical:
            deweyColumn, sortColumn = getCursorDeweyColumns(table_meta)
        xlsColumns=[]
        rows=sht.getPhysicalNumberOfRows()
        idMax=0
        #цикл по рядам на листе
        for i in range (0,rows):
            key=[]
            values=[]
            #цикл по полям таблицы
            for j in range (0,len(fields)):
                #к целым числовым значениям эксель прибавляет .0, которые мешают преобразовать в инт
                if sht.getRow(i).getCell(j)!=None:
                    try:
                        text = sht.getRow(i).getCell(j).toString()
                        if sht.getRow(i).getCell(j).getCellType()==0 and '.0' in text:
                            text=text.split('.')[0]
                    except:
                        text=''
                        context.error('Error at row %s cell %s. Cannot convert to string value %s'%(str(i),str(j),sht.getRow(i).getCell(j)))   
                else:
                    text='' 
                #заполнение заголовков
                if i == 0:
                    for field in fields:
                        try:
                            column_jsn = (item['jsn'] for item in columnJsns if item["name"] == field).next()
                            column_name = column_jsn["name"]
                            fieldType = column_jsn["fieldTypeId"]
                        except:
                            column_name=text
                            fieldType=table_meta.getColumn(field).getCelestaType()
                        if table_meta.getColumn(field).jdbcGetterName() == 'getInt':
                            isIdentity = table_meta.getColumn(field).isIdentity()
                        else:
                            isIdentity = 'False'
                        xlsColumns.append([text,field,fieldType,isIdentity])
                
                else:
                    #находим значения primary key
                    if xlsColumns[j][1] in currentTable.meta().getPrimaryKey() and text!='' and text is not None:
                        if table_meta.getColumn(xlsColumns[j][1]).jdbcGetterName() == 'getInt':
                            try:
                                text = int(text)
                            except:
                                context.error('Import error at row %s in column # %s, column name "%s". Error while converting string to integer. Expected integer number without separators, but "%s" is given' %(i,j+1,xlsColumns[j][0],text)) 
                        key.append(text)
                    if xlsColumns[j][2] in ('1','BIT'):
                        if text in (u'Да',u'да'):
                            text=True
                        else:
                            text=False
                    elif xlsColumns[j][2] in ('2','DATETIME'):
                        if text=='':
                            text=None
                        else:
                            try:
                                text=datetime.datetime.strptime(text, '%d.%m.%Y')
                            except: 
                                context.error('Import error at row %s in column # %s, column name "%s". Error while converting string to datetime. Expected date format is dd.mm.yyyy, but "%s" is given' %(i,j+1,xlsColumns[j][0],text))
                                
                    elif xlsColumns[j][2] in ('3','REAL'):
                        if text in ("",u""):
                            text=None
                        else:
                            try:
                                text = float(text.replace(',','.'))
                            except: 
                                context.error('Import error at row %s in column # %s, column name "%s". Error while converting string to real number. Expected floating point (real) number with separator (e.g. 1.0 or 1,0), but "%s" is given' %(i,j+1,xlsColumns[j][0],text))
                    
                    elif xlsColumns[j][2] in ('5','7','INT') and table_meta.getColumn(xlsColumns[j][1]).jdbcGetterName() == 'getInt':
                        if text in ("",u""):
                            text=None
                        else:
                            try:
                                text = int(text)   
                            except:
                                context.error('Import error at row %s in column # %s, column name "%s". Error while converting string to integer. Expected integer number without separators, but "%s" is given' %(i,j+1,xlsColumns[j][0],text))
                    elif xlsColumns[j][2] in ('4','6'):
                        text = None
                    #заполняем массив значениями
                    values.append(text)
            if i!=0:
                # апдейт если есть поле с такими ключевыми полями
                if len(key)!=0 and currentTable.tryGet(*key):
                    currentTable.get(*key)
                    for x,field in enumerate(fields):
                        if isHierarchical and field ==sortColumn:
                            continue
                        if isHierarchical and field ==deweyColumn:
                            setattr(currentTable,sortColumn,generateSortValue(values[x]))
                        else:
                            setattr(currentTable,field,values[x])
                    currentTable.update()
                #инсерт если таких нет
                else:
                    for x,field in enumerate(fields):
                        if isHierarchical and field ==sortColumn:
                            continue
                        if isHierarchical and field ==deweyColumn:
                            if values[x]=='' or values[x] is None:
                                newDeweyNumber=getNewItemInUpperLevel(context,currentTable,field)
                                setattr(currentTable,field, newDeweyNumber)
                                setattr(currentTable,sortColumn,generateSortValue(newDeweyNumber))
                            else:
                                setattr(currentTable,field,values[x])
                                setattr(currentTable,sortColumn,generateSortValue(values[x]))
                        elif table_meta.getColumn(field).jdbcGetterName() == 'getInt' and table_meta.getColumn(field).isIdentity()==True:
                            setattr(currentTable, field, None)
                        else:
                            setattr(currentTable,field,values[x])
                    currentTable.insert()
            currentTable.clear()
        idfound=0
        #читаем файл             
    wb = HSSFWorkbook(file1)
    #сколько в файле листов-столько таблиц нужно заполнить
    for i in range(0,wb.getNumberOfSheets()):
        #заполняем таблицу с именем как у листа
        table_name=wb.getSheetName(i)
        currentTable = relatedTableCursorImport(grain_name,table_name)(context)
        table_meta=currentTable.meta()
        try:
            table_jsn=json.loads(table_meta.getCelestaDoc())
        except TypeError:
            table_jsn={'isHierarchical':"false"}
        sht = wb.getSheetAt(i)
        fillTable(currentTable,table_meta,sht,table_jsn)
    return None

def exportToExcel(context, grain_name,table_name,export_ref):

    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    columnJsns=getColumnJsns(table_meta)
    #метод заполнения листа из таблицы
    def fillSheet(table_meta,sht,currentTable,columnJsns):
        cols=[]
        row=sht.createRow(0)
        for i,col in enumerate(table_meta.getColumns()):
            try:
                columnjsn=(item['jsn'] for item in columnJsns if item["name"] == col).next()
                field_type=int(columnjsn['fieldTypeId'])
                col_name=columnjsn["name"]
            except:
                field_type=0
                col_name=col
            cols.append((col,field_type,col_name))
            cell=row.createCell(i)
            cell.setCellValue(col_name)
        i=1
        for rec in currentTable.iterate():
            row=sht.createRow(i)
            j=0
            for col,type,name in cols:
                cell=row.createCell(j)
                if field_type == 1:
                        if getattr(rec, col):
                            cell.setCellValue(u'Да')
                        else:
                            cell.setCellValue(u'Нет')
                elif type==2:
                    sdf = SimpleDateFormat("dd.MM.YYYY")
                    if getattr(rec, col)!=None:
                       strDate = sdf.format(getattr(rec, col))
                       cell.setCellValue(strDate)
                elif type in (4,6):
                    pass
                else:
                    cell.setCellValue(getattr(rec,col))
                j+=1
            i+=1
        return sht
    
    #рекурсивная функция поиска всех связанных справочников для текущего, она же заполняет листы
    def findRefs(table_name,grain_name,context,ref_tables,map_table_names=None):
        cur_table=context.getCelesta().getScore().getGrain(grain_name).getTable(table_name)
        columnJsnsRef=getColumnJsns(cur_table)
        for col in  cur_table.getColumns():
            #ищем таблицы по полям типа reference value/list
            try:
                column_jsn=(item['jsn'] for item in columnJsnsRef if item["name"] == col).next()
                
                if int(column_jsn['fieldTypeId']) in (6,):
                    ref_table_name=column_jsn['refTable']
                    #refTable=relatedTableCursorImport(grain_name, ref_table_name)(context)
                    ref_tables.append((grain_name, ref_table_name))
                    map_table_names.append(column_jsn['refMappingTable'])
                    if ref_table_name!=table_name:
                        wb=findRefs(ref_table_name,grain_name,context,ref_tables,map_table_names)
                    #wb.setSheetOrder(u"%s"%map_table_name,wb.getNumberOfSheets()-1)
                if int(column_jsn['fieldTypeId']) in (7,):
                    ref_table_name=column_jsn['refTable']
                    #refTable=relatedTableCursorImport(grain_name, ref_table_name)(context)
                    ref_tables.append((grain_name, ref_table_name))
                    if ref_table_name!=table_name:
                        wb=findRefs(ref_table_name,grain_name,context,ref_tables,map_table_names)
                else:
                    pass
            except TypeError:
                pass
        ref_tables.append((grain_name,table_name))
        return ref_tables
    #создаем книгу excel
    wb=HSSFWorkbook()
    #если надо связанные
    map_table_names=[]
    ref_tables=[]
    if export_ref=='true':        
        ref_tables=findRefs(table_name,grain_name,context,ref_tables,map_table_names)
        for grain,table in ref_tables:
            refTable=relatedTableCursorImport(grain,table)(context)
            columnJsnsRef=getColumnJsns(refTable.meta())
            #заполняем лист если такого нет
            if wb.getSheet(u"%s"%table) is None:
                sht=wb.createSheet(u"%s"%table)
                sht=fillSheet(refTable.meta(),sht,refTable,columnJsnsRef)
        if len(map_table_names)!=0:
            for map_table_name in map_table_names:
                sht=wb.createSheet(u"%s"%map_table_name)
                mapTable=relatedTableCursorImport(grain_name, map_table_name)(context)
                columnJsnsMap=getColumnJsns(mapTable.meta())
                sht=fillSheet(mapTable.meta(),sht,mapTable,columnJsnsMap)
    #если не надо заполняем один лист
    else:
        sht=wb.createSheet(u"%s"%table_name)
        sht=fillSheet(table_meta,sht,currentTable,columnJsns)
    #создаем и пишем в файл      
    fileName=u'export.xls'
    file_out=FileOutputStream(File('export.xls'))
    wb.write(file_out)
    file_out.close()
    data=open(u"export.xls")
    if data:
        return JythonDownloadResult(data, fileName)        
