# coding: utf-8

class BasicForm(object):
    u'''Базовый класс для любой формы, реализованной в Лире'''
    def _getCursor(self, context):
        '''TO BE OVERRIDEN'''
        pass

    def _buildForm(self, context, request, response):
        '''TO BE OVERRIDEN'''
        pass

    def setContext(self, session, main, add, elemetId):
        self.session = session
        self.main = main
        self.add = add
        self.elemetId = elemetId
