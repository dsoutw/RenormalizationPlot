'''
Created on 2017/9/25

@author: dsou
'''
import logging
import typing as tp
from .graphobject import GraphObject

# Sync a group of GraphObject items
# sync methods: visible, clear
class Group(GraphObject):
    __graphList:tp.List[GraphObject]=[]
    def __init__(self,graphList:tp.Iterable[GraphObject],visible=True,parent=None,logger=None,**kwargs):
        if logger is None:
            logger=logging.getLogger(__name__)

        for member in graphList:
            member.parent=self

        self.__graphList=list(graphList)
        GraphObject.__init__(self,visible=visible,parent=parent,logger=logger,**kwargs)
        self._setVisibleInternal(visible=visible)
        
    def _setVisibleInternal(self, visible):
        for member in self.__graphList:
            try:
                member.setVisibleMask(visible)
            except:
                self._logger.exception('Unable to set visible %s: %s' % (member,visible))
    
    # clear all artist in the list from the canvas    
    def update(self):
        for member in self.__graphList:
            member.update()

    # clear all artist in the list from the canvas    
    def clear(self):
        for member in self.__graphList:
            try:
                member.setParent(None)
            except:
                self._logger.exception('Unable to clear %s' % member)
                
        del self.__graphList[:]
    
    def canvasChangedEvent(self, oldCanvas, newCanvas):
        for member in self.__graphList:
            member.canvasChangedEvent(oldCanvas, newCanvas)
        GraphObject.canvasChangedEvent(self, oldCanvas, newCanvas)
        
    '''
    List methods
    '''
    def __getitem__(self,key):
        return self.__graphList[key]
    def __setitem__(self,key,value):
        self.__graphList[key].parent=None
        self.__graphList[key]=value
        value.parent=self
    def __iter__(self):
        return self.__graphList
    def append(self,x:GraphObject):
        x.setVisibleMask(self.visible)
        x.parent=self
        self.__graphList.append(x)
    def extend(self,l:tp.Iterable[GraphObject]):
        for member in l:
            member.setVisibleMask(self.isShowed())
            member.parent=self
        self.__graphList.extend(l)

