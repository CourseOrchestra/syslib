# coding: UTF-8

"""@package common.api.context.sessioncotext Модуль содержит описание классов
для работы с session context в Showcase

Created on 09 марта 2015 г.

@author tugushev.rr
"""

import json
from common.sysfunctions import getGridWidth, getGridHeight


class GridContext:
    """Описывает структуру контекста грида."""
    
    class PageInfo:
        """Описывает структуру информации о странице
        @todo Уточнить описание
        """
        
        def __init__(self, inNumber=-1, inSize=0):
            self.number = inNumber
            self.size = inSize
            
    class LiveInfo:
        """Описывает количественные характеристики грида
        @todo Уточнить описание
        """
        def __init__(self, totalCount, pageNumber, offset, limit):
            self.totalCount = totalCount
            self.pageNumber = pageNumber
            self.offset = offset 
            self.limit = limit 


    def __init__(self, gridContextJson):
        """
        @param gridContextJson (@c dict) JSON-словарь c содержимым тэга 
        gridContext  
        """
        
        ## (@c string) ИД выбранного столбца
        self.currentColumnId = gridContextJson.get('currentColumnId', None)
                
        pInfo = gridContextJson.get('pageInfo', None)
        pNum, pSize = -1, 0
          
        if pInfo is not None:
            pNum = pInfo['@number']
            pSize = pInfo['@size']
        
        ## (@c common.api.context.sessioncontext.GridContext.PageInfo) информация 
        # о странице
        # @todo Уточнить описание
        self.pageInfo =  GridContext.PageInfo(pNum, pSize)
             
        lInfo = gridContextJson.get('liveInfo', None)
        
        if lInfo is not None:
            totalCount = lInfo['@totalCount']
            pageNumber = lInfo['@pageNumber']
            offset = lInfo['@offset']
            limit  = lInfo['@limit']
        
        ## (@c common.api.context.sessioncontext.GridContext.LiveInfo) информация 
        # о странице
        # @todo Уточнить описание    
        self.liveInfo =  GridContext.LiveInfo(totalCount, pageNumber, offset, limit)
        
        ## (@c bool) флаг частичного обновления
        self.partialUpdate = (gridContextJson['partialUpdate'] == 'true')
        
        ## (@c string) ИД элемента грида на информационной панели
        self.id = gridContextJson['@id']
          
        recId = gridContextJson.get('selectedRecordId', None)
        recId = recId or None
        
        if recId and not isinstance(recId, list):
            recId = [recId]
         
        ## (<tt>list of string</tt>) список выбранных в гриде записей.
        # Состояние по умолчанию - пустой список.
        # Если выбрана только одна запись, то #selectedRecordIds - список
        # с одним элементом. 
        self.selectedRecordIds = recId or []
        
        recId = gridContextJson.get('currentRecordId', None)
        
        ## (@c string) текущая выбранная запись. 
        # Если ничего не выбрано, то @c None
        self.currentRecordId = recId or None
            
            
class FormsContext:
    """Описывает контекст формы"""

    def __init__(self, formContextJson):
        """
        @param gridContextJson (@c dict) JSON-словарь c содержимым тэга 
        xformsContext  
        """

        ## (@c string) ИД элемента формы на информационной панели
        self.id = formContextJson['@id']
        ## (@c dict) JSON-словарь данных формы. 
        # Если данные отсутствуют, т.е. нет @e formData, то @c None 
        self.data = formContextJson.get("formData", None)
        

class SessionContext:
    """Описывает структуру session context."""
    
    def __init__(self, jsonString, panelGridsCount = 1):
        """
        @param jsonString (@ string) JSON-строка, содержащая session context.
        Обычно такая строка приходит одним из параметров функции-обработчика
        Showcase
        @param panelGridsCount (@c int) количество гридов на датапанели.
        Исходя из количества гридов рассчитываются их размеры (см. #getGridWidth
        и #getGridHeight)
        """
        
        ## (@c int) количество гридов на датапанели
        self.gridsCount = panelGridsCount
        
        ## (@c string) JSON-строка, содержащая session context
        self.sessionString = jsonString
        
        sesJson = json.loads(jsonString)['sessioncontext']
        
        ## (@c string) логин
        self.login = sesJson['username']
        ## (@c string) SID пользователя
        self.sid = sesJson['sid']
        ## (@c string) IP
        self.ip = sesJson['ip']
        ## (@c string) e-mail пользователя
        self.email = sesJson['email']
        ## (@c string) полное имя пользователя
        self.username = sesJson['fullusername']
        ## (@c string) телефон пользователя
        self.phone = sesJson['phone']
        ## (@c string) текущая перспектива
        self.userdata = sesJson['userdata']
        
        ## (<tt>list of common.api.context.sessioncontext.GridContext</tt>) Список
        # контекстов связанных гридов. 
        # 
        # Состояние по умолчанию - пустой список.
        # Если существует только один связанный грид, то #relatedGrids - список
        # с одним элементом.
        #
        # Как правило прямое использование этого поля не требуется
        # (см. #getGridContext)
        self.relatedGrids = []
        ## (<tt>list of common.api.context.sessioncontext.FormsContext</tt>) Список
        # контекстов связанных форм. 
        #
        # Состояние по умолчанию - пустой список.
        # Если существует только одна связанная форма, то #relatedGrids - список
        # с одним элементом.
        #
        # Как правило прямое использование этого поля не требуется
        # (см. #getFromContext)
        self.relatedForms = []
        
        related = sesJson.get('related', None)
        if related is not None and related != "":
            gc = related.get('gridContext', None)
            if gc is not None:
                self._createRelatedGrids(gc)
                
            fc = related.get('xformsContext', None)
            if fc is not None:
                self._createRelatedForms(fc)
                
                   
    def getGridContext(self, gridId=None):
        """Возвращает контекст грида с ИД @a gridId.
        
        Если @a gridId не задан, возвращает первый элемент из списка контекстов
        гридов #relatedGrids.
        Если нет ни одного контекста или контекст для заданного @a gridId не
        найден, возвращает @c None
        
        @param gridId (@c string) ИД грида
        @return @c common.api.context.sessioncontext.GridContext
        """
        if not self.relatedGrids:
            return None
        
        if not gridId:
            return self.relatedGrids[0]
            
        foundGrid = filter(lambda x: x.id == gridId, self.relatedGrids)
        
        if len(foundGrid) == 0:
            return None
        
        return foundGrid[0] 
    
    
    def getFormContext(self, formId=None):
        """Возвращает контекст формы с ИД @a formId.
        
        Если @a formId не задан, возвращает первый элемент из списка контекстов
        форм #relatedForms.
        Если нет ни одного контекста или контекст для заданного @a formId не
        найден, возвращает @c None.
        
        @param formId (@c string) ИД грида
        @return @c common.api.context.sessioncontext.FormsContext
        """
        
        if not self.relatedForms:
            return None
        
        if not formId:
            return self.relatedForms[0]
        
        foundForm = filter(lambda x: x.id == formId, self.relatedForms)
        
        if len(foundForm) == 0:
            return None
        
        return foundForm[0]
    
    
    def getGridWidth(self):
        """Возвращает ширину грида исходя из размеров датапанели.
        @return (@c int) размер в пикселях
        
        @see common.sysfunctions.getGridWidth
        """
        return int(getGridWidth(self.sessionString).replace('px', ''))
    
    
    def getGridHeight(self):
        """Возвращает высоту грида исходя из размеров датапанели и количества
        гридов на ней.
        
        @return (@c int) размер в пикселях
        
        @see #gridsCount
        @see common.sysfunctions.getGridWidth
        """
        return int(getGridHeight(self.sessionString, self.gridsCount))
    
    
    def _createRelatedGrids(self, gridContextContent):
        gridContextList = gridContextContent
        if not isinstance(gridContextContent, list):
            gridContextList = [gridContextContent]
            
        self.relatedGrids = [GridContext(rg) for rg in gridContextList]
    
    
    def _createRelatedForms(self, formContextContent):
        formContextList = formContextContent
        if not isinstance(formContextContent, list):
            formContextList = [formContextList]
            
        self.relatedForms = [FormsContext(rg) for rg in formContextList]
    
    
                