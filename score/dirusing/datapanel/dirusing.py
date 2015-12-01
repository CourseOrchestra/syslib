# coding: utf-8



def datapanel(context, main=None, session=None):
    u'''Продедура возвращает информационную панель для справочников'''
    
    xml = u'''<?xml version="1.0" encoding="UTF-8"?>
    <datapanel>
      <tab id="1" name="Редактирование данных">
        
        <!--
        <element id="12" type="webtext" proc="dirusing.webtext.dircontentbuttons.buttons.celesta">
          <related id="13"/>
        </element> -->
        <element id="11" type="xforms" template="dirusing/dirusing_filter.xml" proc="dirusing.xforms.dirfilter.cardData.celesta"> 
        </element>
        
        <element id="13" type="grid" subtype="JS_PAGE_GRID" plugin="pageDGrid" proc="dirusing.grids.dircontentgrid.getData.celesta">
            <proc id="proc13" name="dirusing.grids.dircontentgrid.getSettings.celesta" type="METADATA"/>
            <proc id="toolbar1" name="dirusing.grids.dircontentgrid.gridToolBar.celesta" type="TOOLBAR"/>
            <proc id="download1" name="dirusing.commonfunctions.downloadFileFromGrid.celesta" type="DOWNLOAD"/>
			<related id="11"/>
        </element>
        
        <element id="14" type="xforms" template="dirusing/directory_export_card.xml" proc="dirusing.xforms.direxportcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc14" name="dirusing.xforms.direxportcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="download14" name="dirusing.exportfunctions.exportToExcel.celesta" type="DOWNLOAD"/>
          <related id="13"/>
        </element>
        <element id="15" type="xforms" template="dirusing/directory_data_card.xml" proc="dirusing.xforms.dircontentcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc1" name="dirusing.xforms.dircontentcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="download2" name="dirusing.commonfunctions.downloadFileFromXform.celesta" type="DOWNLOAD"/>
          <proc id="upload2" name="dirusing.commonfunctions.uploadFileToXform.celesta" type="UPLOAD"/>
          <related id="13"/>
        </element>
        <element id="16" type="xforms" template="dirusing/directory_data_del_card.xml" proc="dirusing.xforms.dircontentdelcard.cardDelData.celesta" neverShowInPanel="true">
          <proc id="proc16" name="dirusing.xforms.dircontentdelcard.cardDelDataSave.celesta" type="SAVE"/>
          <related id="13"/>
        </element>
        <element id="17" type="xforms" template="dirusing/directory_data_del_all_card.xml" proc="dirusing.xforms.dircontentdelcard.cardDelData.celesta" neverShowInPanel="true">
          <proc id="proc17" name="dirusing.xforms.dircontentdelcard.cardDelAllDataSave.celesta" type="SAVE"/>
          <related id="13"/>
        </element>
        <element id="18" type="xforms" template="dirusing/directory_import_card.xml" proc="dirusing.xforms.dirimportcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc18" name="dirusing.xforms.dirimportcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="upload3" name="dirusing.exportfunctions.importXlsData.celesta" type="UPLOAD"/>
          <related id="13"/>
        </element>
        <!--<element id="19" type="xforms" template="dirusing/directory_import_card.xml" proc="dirusing.xforms.dirimportcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc18" name="dirusing.xforms.dirimportcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="upload3" name="dirusing.exportfunctions.importXlsDataOld.celesta" type="UPLOAD"/>
          <related id="13"/>
        </element>-->
    
      </tab>
      <!--<tab id="2" name="Редактирование структуры">
        
        <element id="2_11" type="xforms" proc="ssp.struct_import_filter" template="ssp_import_struct_filter.xml">
          <proc id="1" name="ssp.struct_data_upload_file" type="UPLOAD"/>
          <proc id="2" name="ssp.struct_data_save_file" type="SAVE"/>
          <proc id="3" name="ssp.struct_data_download_file" type="DOWNLOAD"/>
        </element>
        <element id="2_12" type="grid" subtype="EXT_PAGE_GRID" proc="ssp.struct_import_grid"/>
        <element id="2_13" type="webtext" proc="ssp.struct_import_webtext_row" hideOnLoad="true">
          <related id="2_12"/>
        </element>
        
      </tab>-->
    </datapanel>'''

    #raise Exception(XMLJSONConverter(input=data).parse())
    return xml

def datapanelHierarchical(context, main=None, session=None):
    u'''Продедура возвращает информационную панель для справочников'''
    
    xml = u'''<?xml version="1.0" encoding="UTF-8"?>
    <datapanel>
      <tab id="1" name="Редактирование данных">
        
        <!--
        <element id="12" type="webtext" proc="dirusing.webtext.dircontentbuttons.buttons.celesta">
          <related id="13"/>
        </element> -->
        <element id="11" type="xforms" template="dirusing/dirusing_filter.xml" proc="dirusing.xforms.dirfilter.cardData.celesta"> 
        </element>
        <element id="13" type="grid" subtype="JS_TREE_GRID" plugin="treeDGrid" proc="dirusing.grids.dircontentgrid.getTree.celesta">
            <proc id="toolbar1" name="dirusing.grids.dircontentgrid.gridToolBar.celesta" type="TOOLBAR"/>
            <proc id="download1" name="dirusing.commonfunctions.downloadFileFromGrid.celesta" type="DOWNLOAD"/>
			<related id="11"/>
        </element>
        <element id="14" type="xforms" template="dirusing/directory_export_card.xml" proc="dirusing.xforms.direxportcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc14" name="dirusing.xforms.direxportcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="download14" name="dirusing.exportfunctions.exportToExcel.celesta" type="DOWNLOAD"/>
          <related id="13"/>
        </element>
        <element id="15" type="xforms" template="dirusing/directory_data_card.xml" proc="dirusing.xforms.dircontentcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc1" name="dirusing.xforms.dircontentcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="download2" name="dirusing.commonfunctions.downloadFileFromXform.celesta" type="DOWNLOAD"/>
          <proc id="upload2" name="dirusing.commonfunctions.uploadFileToXform.celesta" type="UPLOAD"/>
          <related id="13"/>
        </element>
        <element id="16" type="xforms" template="dirusing/directory_data_del_card.xml" proc="dirusing.xforms.dircontentdelcard.cardDelData.celesta" neverShowInPanel="true">
          <proc id="proc16" name="dirusing.xforms.dircontentdelcard.cardDelDataSave.celesta" type="SAVE"/>
          <related id="13"/>
        </element>
        <element id="17" type="xforms" template="dirusing/directory_data_del_all_card.xml" proc="dirusing.xforms.dircontentdelcard.cardDelData.celesta" neverShowInPanel="true">
          <proc id="proc17" name="dirusing.xforms.dircontentdelcard.cardDelAllDataSave.celesta" type="SAVE"/>
          <related id="13"/>
        </element>
        <element id="18" type="xforms" template="dirusing/directory_import_card.xml" proc="dirusing.xforms.dirimportcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc18" name="dirusing.xforms.dirimportcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="upload3" name="dirusing.exportfunctions.importXlsData.celesta" type="UPLOAD"/>
          <related id="13"/>
        </element>
        <!--<element id="19" type="xforms" template="dirusing/directory_import_card.xml" proc="dirusing.xforms.dirimportcard.cardData.celesta" neverShowInPanel="true">
          <proc id="proc18" name="dirusing.xforms.dirimportcard.cardDataSave.celesta" type="SAVE"/>
          <proc id="upload3" name="dirusing.exportfunctions.importXlsDataOld.celesta" type="UPLOAD"/>
          <related id="13"/>
        </element>-->
    
      </tab>
      <!--<tab id="2" name="Редактирование структуры">
        <element id="2_11" type="xforms" proc="ssp.struct_import_filter" template="ssp_import_struct_filter.xml">
          <proc id="1" name="ssp.struct_data_upload_file" type="UPLOAD"/>
          <proc id="2" name="ssp.struct_data_save_file" type="SAVE"/>
          <proc id="3" name="ssp.struct_data_download_file" type="DOWNLOAD"/>
        </element>
        <element id="2_12" type="grid" subtype="EXT_PAGE_GRID" proc="ssp.struct_import_grid"/>
        <element id="2_13" type="webtext" proc="ssp.struct_import_webtext_row" hideOnLoad="true">
          <related id="2_12"/>
        </element>
      </tab>-->
    </datapanel>'''

    #raise Exception(XMLJSONConverter(input=data).parse())
    return xml
