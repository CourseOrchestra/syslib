# coding: utf-8
import ru.curs.lyra.BasicLyraForm as BasicLyraForm

class BasicForm(BasicLyraForm):
    u'''Базовый класс для любой формы, реализованной в Лире'''
    
    def _getId(self):
        return self.__class__.__module__ + "." + self.__class__.__name__
    
    def _buildForm(self):
        '''TO BE OVERRIDEN'''
        pass

    def getInstance(cls, context, session, main, add, elemetId):

        if 'lyraClasses' in context.data and cls.__name__ in context.data['lyraClasses']:
            testInst = context.data["lyraClasses"][cls.__name__]
        else:
            testInst = cls()
            if 'lyraClasses' in context.data:
                context.data['lyraClasses'][cls.__name__] = testInst
            else:
                context.data['lyraClasses'] = {cls.__name__ : testInst}

        testInst.setContext(context, session, main, add, elemetId)
        return testInst

    def setContext(self, context, session, main, add, elemetId):
        self.context = context
        self.session = session
        self.main = main
        self.add = add
        self.elemetId = elemetId

    getInstance = classmethod(getInstance)
