# coding: utf-8
import ru.curs.lyra.BasicGridForm as BasicGridForm

class GridForm(BasicGridForm):
    u'''Basic class for a grid form'''
    def __init__(self, context):
        BasicGridForm.__init__(self, context)
    
    def _getId(self):
        return self.__class__.__module__ + "." + self.__class__.__name__
    
