# coding: utf-8
'''
Created on 02.03.2016
HTML подсказки
@author: a.rudenko
'''
import json
from com.jayway.jsonpath import JsonPath
from common._common_orm import htmlHintsCursor
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from security.functions import userHasPermission
from org.apache.commons.lang3.StringEscapeUtils import unescapeHtml4
from common.sysfunctions import toHexForXml, getGridHeight

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

def xformTemplate(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    htmlHints = htmlHintsCursor(context)
    if htmlHints.tryGet(elementId):
        fullScreen = htmlHints.fullScreen
    else:
        fullScreen = 0
    if fullScreen==1:
        if not isinstance(session, dict):
            width = unicode(int(json.loads(session)["sessioncontext"]["currentDatapanelWidth"])) + "px"
        else:
            width = unicode(int(session["sessioncontext"]["currentDatapanelWidth"])) + "px"
            
        if not isinstance(session, dict):
            height = unicode(int(json.loads(session)["sessioncontext"]["currentDatapanelHeight"])) + "px"
        else:
            height = unicode(int(session["sessioncontext"]["currentDatapanelHeight"])) + "px"
        #костыль до 5 версии шоукейза
        height="100%"
    else:
        height="300px"
    #raise Exception (height)
    
    xformXml = u'''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet href="xsltforms/xsltforms.xsl" type="text/xsl"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ev="http://www.w3.org/2001/xml-events"
    xmlns:xsd="http://www.w3.org/2001/XMLschema" xmlns:fs="http://www.curs.ru/ns/FormServer"
    xmlns:xf="http://www.w3.org/2002/xforms" xmlns:xsltforms="http://www.agencexml.com/xsltforms" xmlns:rte="http://www.agencexml.com/xsltforms/rte">
    <head>
    <style type="text/css">
    .htmlOutput {
            display: block;
            width: 96%;
            background: rgba(210, 227, 243, 0.25);
            padding: 2%;
            margin-left: 2px;
            overflow: auto;
            max-height: '''+height+''';
            clear: both;
            }
    .htmlOutput .xforms-value {
        white-space: normal;
    }
            
            
    </style>
        <xf:model id="xformId_mainModel">
        
            <xf:instance id="xformId_mainInstance">
                <schema xmlns=""/>
            </xf:instance>
            <xf:instance id="xformId_errorInstance">
                <schema xmlns="">
                    <error/>
                </schema>
            </xf:instance>

            <xf:instance id="xformId_quot">
                <schema xmlns="">"</schema>
            </xf:instance>

            <xf:instance id="xformId_genderInstance">
                <schema xmlns="">
                </schema>
            </xf:instance>

            <xf:bind>
                <xf:bind nodeset="instance('xformId_mainInstance')/htmlText" readonly="false()"></xf:bind>
                <xf:bind nodeset="instance('xformId_mainInstance')/fullScreen" type="boolean"></xf:bind>
                <xf:bind nodeset="instance('xformId_mainInstance')/showOnLoad" type="boolean"></xf:bind>
            </xf:bind>
            
            
            <xf:submission id="xformId_showOnLoadSave" method="post" instance="xformId_mainInstance" replace="none"
                ref="instance('xformId_mainInstance')"
                action="secured/submit?proc=common.htmlhints.htmlHint.showOnLoadSave.celesta">
                <xf:action ev:event="xforms-submit-done">
                </xf:action>
                <xf:action if="event('response-body')!='null'" ev:event="xforms-submit-error">
                    <!--  xf:message>Ошибки при заполнении:<xf:output value="event('response-body')"/>
                    </xf:message-->
                 </xf:action>

            </xf:submission>
        </xf:model>
        <script type="text/javascript"/>
        
    </head>
    <body>
        <!--xf:output value="serialize(instance('xformId_mainInstance'))"></xf:output-->
        <!--div style="min-height: 0px; margin-bot: 10px; float: left; clear: both; width:20px; height:20px;">
            <xf:trigger class="groupHeader" id="xformId_Tab0001Button" appearance="minimal">
                <xf:label><xf:output value="''"></xf:output><xf:output mediatype="image/*" value="if(instance('xformId_mainInstance')/showHideHint = 0, './solutions/default/resources/help.png', './solutions/default/css/images/window-close.png')"></xf:output></xf:label>
                <xf:action ev:event="DOMActivate">
                    <xf:setvalue ref="instance('xformId_mainInstance')/showHideHint" value="1 - instance('xformId_mainInstance')/showHideHint"></xf:setvalue>
                </xf:action>
            </xf:trigger>
        </div-->
        <xf:group ref=".[instance('xformId_mainInstance')/showHideHint = 'false']">
            <div class="break button100" style="width: 100px; margin-top: 2px; float: left; ">
                <xf:trigger class="break" style="margin-top: 0px">
                    <xf:label>Справка</xf:label>
                    <xf:action ev:event="DOMActivate">
                            <xf:setvalue ref="instance('xformId_mainInstance')/showHideHint" value="'true'"></xf:setvalue>
                            <xf:send submission="xformId_showOnLoadSave"/>
                    </xf:action>
                </xf:trigger>
            </div>
        </xf:group>
        <xf:group ref=".[instance('xformId_mainInstance')/showHideHint = 'true']">
            <div class="break button100" style="width: 100px; margin-top: 2px; margin-bottom: 2px; float: left; ">
                <xf:trigger class="break" style="margin-top: 0px">
                    <xf:label>Свернуть</xf:label>
                    <xf:action ev:event="DOMActivate">
                            <xf:setvalue ref="instance('xformId_mainInstance')/showHideHint" value="'false'"></xf:setvalue>
                            <xf:send submission="xformId_showOnLoadSave"/>
                    </xf:action>
                </xf:trigger>
            </div>
        </xf:group>
        <xf:group ref=".[instance('xformId_mainInstance')/showHideHint = 'true']">
                <xf:output class="htmlOutput" value="instance('xformId_mainInstance')/htmlText" mediatype="application/xhtml+xml"></xf:output>
            <xf:group ref=".[instance('xformId_mainInstance')/userPerm = 1]">
                <!--div style="min-height: 0px; margin-top: 2px; float: right; clear: both; width:20px; height:20px;">
                    <xf:trigger class="groupHeader" id="xformId_Tab0002Button" appearance="minimal">
                        <xf:label><xf:output value="''"></xf:output><xf:output mediatype="image/*" value="if(instance('xformId_mainInstance')/showHideEdit = 0, './solutions/default/resources/edit3.png', './solutions/default/css/images/window-close.png')"></xf:output></xf:label>
                        <xf:action ev:event="DOMActivate">
                            <xf:setvalue ref="instance('xformId_mainInstance')/showHideEdit" value="1 - instance('xformId_mainInstance')/showHideEdit"></xf:setvalue>
                        </xf:action>
                    </xf:trigger>
                </div-->
                <xf:group ref=".[instance('xformId_mainInstance')/showHideEdit = 0]">
                    <div class="break button100" style="width: 100px; margin-top: 2px; float: right;">
                        <xf:trigger class="break" style="margin-top: 0px">
                            <xf:label>Настройки</xf:label>
                            <xf:action ev:event="DOMActivate">
                                    <xf:setvalue ref="instance('xformId_mainInstance')/showHideEdit" value="1 - instance('xformId_mainInstance')/showHideEdit"></xf:setvalue>
                        </xf:action>
                        </xf:trigger>
                    </div>
                </xf:group>
                <xf:group ref=".[instance('xformId_mainInstance')/showHideEdit = 1]">
                    <div class="break button100" style="width: 100px; margin-top: 2px; float: right; ">
                        <xf:trigger class="break" style="margin-top: 0px">
                            <xf:label>Свернуть</xf:label>
                            <xf:action ev:event="DOMActivate">
                                    <xf:setvalue ref="instance('xformId_mainInstance')/showHideEdit" value="1 - instance('xformId_mainInstance')/showHideEdit"></xf:setvalue>
                        </xf:action>
                        </xf:trigger>
                    </div>
                </xf:group>
            </xf:group>
            <xf:group ref=".[instance('xformId_mainInstance')/showHideEdit = 1]">
                <div class="button200" style="width: 200px; margin-top: 2px; float: right; clear: both;">
                    <xf:trigger class="break" style="margin-top: 0px">
                        <xf:label>Редактировать подсказку</xf:label>
                        <xf:action ev:event="DOMActivate">
                            <xf:load
                                resource="javascript:gwtCreatePlugin({
                                id:'xformId',
                                /*parentId:'pluginWraper',*/
                                plugin:'htmlEditorTinymce',
                                generalFilters: ['XPath(instance(quot(xformId_mainInstance))/htmlText)'],
                                proc:'common.htmlhints.htmlHint.htmlEdit.celesta',
                                params:{
                                tinymce: {
                                plugins: ['textcolor', 'code', 'image', 'table', 'link', 'fullscreen', 'media', 'paste', 'textcolor', 'wordcount', 'visualblocks', 'preview', 'colorpicker'],
                                width: '1000',
                                height: '480'
                                }
                                },
                                options: {                                
                                dataWidth: '1000px',
                                dataHeight: '600px',
                                windowCaption: 'Редактирование HTML',
                                onSelectionComplete: function(ok, plugin) {
                                if (ok) {
                                var elem = document.getElementById('html_editor').getElementsByTagName('textarea')[0];
                                elem.value = plugin.getTinymceEditor().getContent();
                                elem.style.visibility = 'visible';
                                elem.focus();
                                elem.blur();
                                elem.style.visibility = 'visible';
                                }
                                }
                                }
                                });"
                                ></xf:load>
                        </xf:action>
                    </xf:trigger>
                </div>
                <div class="boolInput200 break" style="width: 200px;  margin-right: 15px; float: right; ">
                    <xf:input ref="instance('xformId_mainInstance')/fullScreen">
                        <xf:label>Показывать на весь экран</xf:label>
                        <xf:action ev:event="xforms-value-changed">
                            <xf:action ev:event="DOMActivate">
                                <xf:load resource="javascript:gwtXFormSave('xformId','1',  Writer.toString(getSubformInstanceDocument('xformId_mainModel', 'xformId_mainInstance')))"></xf:load>
                            </xf:action>
                        </xf:action>
                    </xf:input>
                </div>
                <div class="boolInput200 break" style="width: 200px;  margin-right: 15px; float: right; ">
                    <xf:input ref="instance('xformId_mainInstance')/showOnLoad">
                        <xf:label>Показывать при загрузке</xf:label>
                        <xf:action ev:event="xforms-value-changed">
                            <xf:action ev:event="DOMActivate">
                                <xf:load resource="javascript:gwtXFormSave('xformId','1',  Writer.toString(getSubformInstanceDocument('xformId_mainModel', 'xformId_mainInstance')))"></xf:load>
                            </xf:action>
                        </xf:action>
                    </xf:input>
                </div>
                <!--xf:group ref=".[instance('xformId_mainInstance')/showOnLoad = 1]">
                    <div class="button200" style="width: 200px; margin-top: 2px; margin-right: 2px; float: right; ">
                        <xf:trigger class="break" style="margin-top: 0px">
                            <xf:label>Скрывать при загрузке  </xf:label>
                            <xf:action ev:event="DOMActivate">
                                    <xf:setvalue ref="instance('xformId_mainInstance')/showOnLoad" value="1 - instance('xformId_mainInstance')/showOnLoad"></xf:setvalue>
                                    <xf:load resource="javascript:gwtXFormSave('xformId','1',  Writer.toString(getSubformInstanceDocument('xformId_mainModel', 'xformId_mainInstance')))"></xf:load>
                            </xf:action>
                        </xf:trigger>
                    </div>
                </xf:group>
                <xf:group ref=".[instance('xformId_mainInstance')/showOnLoad != 1]">
                    <div class="button200" style="width: 200px; margin-top: 2px; margin-right: 2px; float: right; ">
                        <xf:trigger class="break" style="margin-top: 0px">
                            <xf:label>Показывать при загрузке</xf:label>
                            <xf:action ev:event="DOMActivate">
                                    <xf:setvalue ref="instance('xformId_mainInstance')/showOnLoad" value="1 - instance('xformId_mainInstance')/showOnLoad"></xf:setvalue>
                                    <xf:load resource="javascript:gwtXFormSave('xformId','1',  Writer.toString(getSubformInstanceDocument('xformId_mainModel', 'xformId_mainInstance')))"></xf:load>
                            </xf:action>
                        </xf:trigger>
                    </div>
                </xf:group-->
                <xf:textarea id="html_editor" style="visibility: visible; padding: 5px; margin-top: 2px; margin-left: 2px; overflow: scroll; width: 50%; height: 20vh;"
                    ref="instance('xformId_mainInstance')/htmlText">
                    <xf:action ev:event="xforms-value-changed">
                        <xf:action ev:event="DOMActivate">
                            <xf:load resource="javascript:gwtXFormSave('xformId','1',  Writer.toString(getSubformInstanceDocument('xformId_mainModel', 'xformId_mainInstance')))"></xf:load>
                        </xf:action>
                    </xf:action>
                </xf:textarea>
            </xf:group>
        </xf:group>
    </body>
</html>'''
    return JythonDTO(xformXml)