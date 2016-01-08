# coding: utf-8
import ru.curs.lyra.BasicGridForm as BasicGridForm

class GridForm(BasicGridForm):
    u'''Basic class for a grid form'''
    def __init__(self, context):
        BasicGridForm.__init__(self, context)
        
    u'''OVERRIDE THIS TO RETURN CORRECT NUMBER OF ROWS IN GRID!'''
    def getGridHeight(self):
        return 10