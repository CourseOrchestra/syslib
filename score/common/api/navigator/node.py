# coding: UTF-8

'''@package common.api.navigator.node Модуль содержит классы для работы с
навигатором 

Created on 15 сент. 2015 г.

@author tugushev.rr
'''

from common.api.core import ShowcaseBaseNamedElement
from common.api.events.action import Action
from common.api.events.activities import DatapanelActivity
from common.api.tree.treenode import Node


class NavigatorNode(ShowcaseBaseNamedElement, Node):
    """Класс узла дерева навигатора.
    
    Для построения дерева всегда необходим фиктивный корневой узел, у
    которого нет родителей (<em>#parent is None</em>);
    Этот узел не отображается, и может иметь любые ИД и наименование, и 
    задаётся, например, так: 
    @code
    rootNode = NavigatorNode('root', 'root')
    @endcode
    
    NavigatorNode сам расчитывает уровни иерархии пунктов навигатора 
    (тэг *<level>*). Достаточно только использовать метод #addChild.
    
    @see common.api.tree.treenode.Node, common.api.common.ShowcaseBaseNamedElement
    """
    
    def __init__(self, inId, inName, inAction=None):
        """
        @param inId (@c string) ИД узла навигатора
        @param inName (@c string) отображаемое наименование узла
        @param inAction (@c common.api.events.action.Action) действие при клике
        на узел навигатора   
        """
        
        super(NavigatorNode, self).__init__(inId, inName)
        self.__action = inAction
        self.initializeNode()
    
    
    def setAction(self, inAction):
        """Устанавливает действие, вызываемое при клике на узел
        @param inAction (@c common.api.events.action.Action) действие при клике
        на узел навигатора
        @return ссылка на себя
        """
        self.__action = inAction
        return self
    
    
    def getLevel(self):
        """Возвращает уровень узла навигатора:
        
        Возможные значения:
        - 0 - раздел (group)
        - 1-5 - уровни
        - -1 - корневой элемент
        
        @return @c int
        """
        
        # -2 - т.к. корневой элмент имеет rank=1, 
        # разделы имеют индексы вида 0.1, 0.2 и т.п.
        return self.index.rank() - 2
        
    
    def toJSONDict(self):
        d = {}
        
        childrenLevel = self.getLevel() + 1
        
        # если корневой элемент, то не надо записывать атрибуты
        if childrenLevel > 0:
            d = super(NavigatorNode, self).toJSONDict()
            if self.__action:
                d.update(self.__action.toJSONDict()) 
        
        levelNodes = [n.toJSONDict() for n in self.getChildren()]
        
#         it = self.getChildren().listIterator()
#         while it.hasNext():
#             n = it.next()
#             levelNodes.append(n.toJSONDict())
            
        
        if levelNodes or childrenLevel == 0:
            levelText = None
            if childrenLevel > 0:
                levelText = 'level%i' % childrenLevel 
                d[levelText] = levelNodes 
            else: 
                levelText = 'group'
                d[levelText] = {}
                d[levelText].update(levelNodes[0])
        
        return d 
            


if __name__ == '__main__':
    rootNode = NavigatorNode(None, None) 
    
    n1 = NavigatorNode('g1', u'Group 1')
    
    n11 = NavigatorNode('n1.1', u'Node 1.1', 
            Action().addActivity(
                DatapanelActivity().add('datapanel1.xml','firstOrCurrent')
            )
        ) 
    
    n1.addChild(n11)
    
    n1.addChild(
        NavigatorNode('n1.2', u'Node 1.2', 
            Action().addActivity(
                DatapanelActivity().add('datapanel2.xml','firstOrCurrent')
            )
        )
    )
    
    n11.addChild(NavigatorNode('n1.1.1', u'Node 1.1.1', 
            Action().addActivity(
                DatapanelActivity().add('datapanel3.xml','firstOrCurrent')
            )
        ))
    
    n2 = NavigatorNode('n1.3', u'Node 1.3',
            Action().addActivity(
                    DatapanelActivity().add('datapanel4.xml','firstOrCurrent')
                )
        )
    n21 = NavigatorNode('n1.3.1', u'Node 1.3') 
    
    rootNode.addChild(n1)

    
    
    
#     print t.getRoot().toJSONDict()
    print rootNode.toJSONDict()
    