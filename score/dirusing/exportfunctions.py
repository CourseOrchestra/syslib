# coding: utf-8

from java.io import FileOutputStream,File,ByteArrayOutputStream
import simplejson as json
import xml.etree.ElementTree as ET
from org.apache.poi.hssf.usermodel import HSSFWorkbook,HSSFDataFormat,HSSFCellStyle,DVConstraint,HSSFDataValidation
from org.apache.poi.hssf.util import HSSFColor
from org.apache.poi.ss.util import CellRangeAddressList,CellReference
from org.apache.poi.ss.usermodel import DataFormatter
try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    pass

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
#метод заполнения таблицы с одного листа excel, название листа=название таблицы
    def fillTable(currentTable,table_meta,sht):
        #поля таблицы
        fields = table_meta.getColumns()
        xlsColumns=[]
        rows=sht.getPhysicalNumberOfRows()
        fmt=DataFormatter
        #цикл по рядам на листе
        for i in range (0,rows):
            key=[]
            values=[]
            #цикл по полям таблицы
            for j in range (0,len(fields)):
                #к целым числовым значениям эксель прибавляет .0, которые мешают преобразовать в инт
                cell=sht.getRow(i).getCell(j)
                celltype=cell.getCellType()
                text = sht.getRow(i).getCell(j).toString()
                if celltype==cell.CELL_TYPE_NUMERIC and '.0' in text:
                    #text=fmt.formatCellValue(cell)
                    text=text.split('.')[0]
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
                    #находим значения primary key
                    if xlsColumns[j][1] in currentTable.meta().getPrimaryKey() and text!='' and text is not None:
                        if table_meta.getColumn(xlsColumns[j][1]).jdbcGetterName() == 'getInt':
                            text=int(text)
                        key.append(text)
                    #if xlsColumns[j][2] == '0':
                        #continue
                    if xlsColumns[j][2] == '1':
                        if text==u'Да':
                            text=True
                        else:
                            text=False
                    elif xlsColumns[j][2] == '2':
                        if text=='':
                            text=None
                        try:
                            text = datetime.datetime.strptime(unicode(text), '%d-%b-%Y')
                        except ValueError:
                            text = datetime.datetime(1998,1,1)
                    elif xlsColumns[j][2] == '3':
                        try:
                            if ',' in text:
                                text = text.replace(',','.')
                            text=float(text)
                        except: 
                            text=None
                    elif xlsColumns[j][2] in ('5','7') and table_meta.getColumn(xlsColumns[j][1]).jdbcGetterName() == 'getInt' and type(text) is unicode:
                        if text=='':
                            text=None
                        else:
                            text=int(text)                            
                    elif xlsColumns[j][2] == '6':
                        text = None
                    #заполняем массив значениями
                    values.append(text)
            if i!=0:
                # апдейт если есть поле с такими ключевыми полями
                if len(key)!=0 and currentTable.tryGet(*key):
                    currentTable.get(*key)
                    for x,field in enumerate(fields):
                        setattr(currentTable,field,values[x])
                    currentTable.update()
                #инсерт если таких нет
                else:
                    for x,field in enumerate(fields):
                        if table_meta.getColumn(field).jdbcGetterName() == 'getInt' and table_meta.getColumn(field).isIdentity()==True:
                            setattr(currentTable, field, None)
                        else:
                            setattr(currentTable,field,values[x])
                    currentTable.insert()
            currentTable.clear()
    #читаем файл             
    wb = HSSFWorkbook(file1)
    #сколько в файле листов-столько таблиц нужно заполнить
    for i in range(0,wb.getNumberOfSheets()):
        #заполняем таблицу с именем как у листа
        table_name=wb.getSheetName(i)
        currentTable = relatedTableCursorImport(grain_name,table_name)(context)
        table_meta=currentTable.meta()
        sht = wb.getSheetAt(i)
        fillTable(currentTable,table_meta,sht)

    return None
def exportToExcel(context, main=None, add=None, filterinfo=None,
                  session=None, elementId=None, xformsdata=None, columnId=None):
    # получение id grain и table из контекста
    grain_name = json.loads(main)['grain']
    table_name = json.loads(main)['table']
    #признак нужно ли экспортировать связанные
    export_ref = json.loads(xformsdata)['schema']['reftables']
    #export_parent = json.loads(xformsdata)['schema']['parenttables']
    # Курсор текущего справочника
    currentTable = relatedTableCursorImport(grain_name, table_name)(context)
    # Метаданные таблицы
    table_meta = currentTable.meta()
    #метод заполнения листа из таблицы
    def fillSheet(table_meta,sht,currentTable):
        row=sht.createRow(0)
        #стили для ячеек разных типов
        styleDates = wb.createCellStyle()
        styleDates.setDataFormat(HSSFDataFormat.getBuiltinFormat("m/d/yy"))
        styleHeader=wb.createCellStyle()
        styleHeader.setFillForegroundColor(HSSFColor.GREY_25_PERCENT.index);
        styleHeader.setFillPattern(HSSFCellStyle.SOLID_FOREGROUND);
        styleHeader.setDataFormat(HSSFDataFormat.getBuiltinFormat("@"))
        fontHeader = wb.createFont()
        fontHeader.setBoldweight(2)
        fontHeader.setFontHeightInPoints(11)
        styleHeader.setFont(fontHeader)
        styleStr = wb.createCellStyle()
        styleStr.setDataFormat(HSSFDataFormat.getBuiltinFormat("@"))
        styleDec = wb.createCellStyle()
        styleDec.setDataFormat(HSSFDataFormat.getBuiltinFormat("0.00"))
        #заполняем заголовки
        for i,column in enumerate(table_meta.getColumns()):
            cell=row.createCell(i)
            cell.setCellStyle(styleHeader)
            try:
                column_name=json.loads(table_meta.getColumn(column).getCelestaDoc())['name']
            except:
                column_name=column
            cell.setCellValue(column_name)
        #заполняем значения
        i=1
        for rec in currentTable.iterate():
            row=sht.createRow(i)
            for j,field in enumerate(table_meta.getColumns()):
                try:
                    field_type=int(json.loads(currentTable.meta().getColumn(field).getCelestaDoc())['fieldTypeId'])
                except:
                    field_type=0
                cell=row.createCell(j)
                #применяем стили
                if field_type not in (4,6,7,1):
                    if field_type==2:
                        cell.setCellStyle(styleDates)
                    if field_type==3:
                        cell.setCellStyle(styleDec)
                    if field_type in (5,8,9):
                        cell.setCellStyle(styleStr)
                    cell.setCellValue(getattr(rec,field))
                    #Обработка булевого значения
                elif field_type == 1:
                    cell.setCellStyle(styleStr)
                    if getattr(rec, field)==True:
                        cell.setCellValue(u'Да')
                    else:
                        cell.setCellValue(u'Нет')
                    #Обработка reference value
                elif field_type == 7:
                    cell.setCellStyle(styleStr)
                    cell.setCellValue(getattr(rec, field))
                    column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
                    refTableName = column_jsn["refTable"]
                    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                    for x,col in enumerate(relatedTable.meta().getColumns()):
                        if col in relatedTable.meta().getPrimaryKey():
                            refColumn=CellReference.convertNumToColString(x)
                            break
                        else:
                            refColumn='XZ'
                    #чтобы поставить dataValidation, указываю физически возможный последний ряд (больше не дает для такой формулы)
                    lastRow=60000
                    relatedTable.clear()
                    #добавляю dataValidation-для прстановки значений через селектор с другого листа
                    addressList = CellRangeAddressList(1,lastRow,cell.getColumnIndex(),cell.getColumnIndex())
                    dvConstraint = DVConstraint.createFormulaListConstraint("'%s'!$%s$2:$%s$%s"%(str(refTableName),str(refColumn),str(refColumn),str(lastRow)))
                    dataValidation = HSSFDataValidation(addressList, dvConstraint)
                    dataValidation.setSuppressDropDownArrow(False)
                    sht.addValidationData(dataValidation)
                
            #Обработка reference list
                elif field_type == 6:
                    cell.setCellStyle(styleStr)
                    column_jsn = json.loads(table_meta.getColumn(field).getCelestaDoc())
                    refTableName = column_jsn["refTable"]
                    mappingTableName = column_jsn["refMappingTable"]
                    refTableColumn = column_jsn["refTableColumn"]
                    relatedTable = relatedTableCursorImport(grain_name, refTableName)(context)
                    mappingTable = relatedTableCursorImport(grain_name, mappingTableName)(context)
                #Получаем primarykey'и для таблиц
                    currentTablePKs=[]
                    relatedTablePKs=[]
                    currentTablePKObject = currentTable.meta().getPrimaryKey()
                    for key in currentTablePKObject:
                        currentTablePKs.extend([key])
                    relatedTablePKObject = relatedTable.meta().getPrimaryKey()
                    for key in relatedTablePKObject:
                        relatedTablePKs.extend([key])
                #получаем foreignkey'и для таблицы с меппингом
                    foreignKeys = mappingTable.meta().getForeignKeys()
                    for foreignKey in foreignKeys:
                    #referencedTable = foreignKey.getReferencedTable()
                    #проверяем к какой таблице относится ключ и получаем список зависимых полей
                        if foreignKey.getReferencedTable() == currentTable.meta():
                            aForeignKeyColumns = foreignKey.getColumns()
                        else:
                            bForeignKeyColumns = foreignKey.getColumns()
                #ставим фильтр на таблицу меппинга по текущему значению primarykey'ев главной таблицы
                    for foreignKeyColumn,key in zip(aForeignKeyColumns, currentTablePKs):
                        mappingTable.setRange(foreignKeyColumn,getattr(currentTable, key))
                    refValue=""
                    #для каждого значения в отфильтрованной таблице меппинга
                    for mappingRec in mappingTable.iterate():
                        currentRecordIds=[]
                                #набиваем значения primarykey'ев для связанной таблицы, чтобы потом получить значения
                        for foreignKeyColumn in bForeignKeyColumns:
                            currentRecordIds.extend([getattr(mappingRec, foreignKeyColumn)])
                                #находим запись по primarykey'ям и получаем значение теребуемого поля и добавляем к уже найденным
                        relatedTable.get(*currentRecordIds)
                        refValue = refValue+getattr(relatedTable, refTableColumn)+"; "
                    cell.setCellValue(refValue)
                elif field_type==4:
                    cell.setCellValue(u'<Файл>')
            i+=1
            #автоматический размер колонок
            for j in range(0,len(table_meta.getColumns())):
                sht.autoSizeColumn(j)
        return sht
    
    #рекурсивная функция поиска всех связанных справочников для текущего, она же заполняет листы
    def findRefs(currentTable,table_name,grain_name,wb,context):
        global map_table_name
        for col in  currentTable.meta().getColumns():
            #ищем таблицы по полям типа reference value/list
            try:
                if int(json.loads(currentTable.meta().getColumn(col).getCelestaDoc())['fieldTypeId']) in (6,):
                    ref_table_name=json.loads(currentTable.meta().getColumn(col).getCelestaDoc())['refTable']
                    refTable=relatedTableCursorImport(grain_name, ref_table_name)(context)
                    map_table_name=json.loads(currentTable.meta().getColumn(col).getCelestaDoc())['refMappingTable']
                    if ref_table_name!=table_name:
                        wb=findRefs(refTable,ref_table_name,grain_name,wb,context)
                    #wb.setSheetOrder(u"%s"%map_table_name,wb.getNumberOfSheets()-1)
                if int(json.loads(currentTable.meta().getColumn(col).getCelestaDoc())['fieldTypeId']) in (7,):
                    ref_table_name=json.loads(currentTable.meta().getColumn(col).getCelestaDoc())['refTable']
                    refTable=relatedTableCursorImport(grain_name, ref_table_name)(context)
                    if ref_table_name!=table_name:
                        wb=findRefs(refTable,ref_table_name,grain_name,wb,context)
                else:
                    pass
            except TypeError:
                pass
        #заполняем лист если такого нет
        if wb.getSheet(u"%s"%table_name) is None:
            sht=wb.createSheet(u"%s"%table_name)
            sht=fillSheet(currentTable.meta(),sht,currentTable)
        return wb
    #создаем книгу excel
    wb=HSSFWorkbook()
    #если надо связанные
    if export_ref=='true':
        wb=findRefs(currentTable,table_name,grain_name,wb,context)
        if map_table_name:
            sht=wb.createSheet(u"%s"%map_table_name)
            mapTable=relatedTableCursorImport(grain_name, map_table_name)(context)
            sht=fillSheet(mapTable.meta(),sht,mapTable)
            #wb.setSheetOrder(u"%s"%map_table_name,wb.getNumberOfSheets()-1)
    #если не надо заполняем один лист
    else:
        sht=wb.createSheet(u"%s"%table_name)
        sht=fillSheet(table_meta,sht,currentTable)
    #создаем и пишем в файл      
    fileName=u'export.xls'
    file_out=FileOutputStream(File('export.xls'))
    wb.write(file_out)
    file_out.close()
    data=open(u"export.xls")
    if data:
        return JythonDownloadResult(data, fileName)        
    