'''
Created on 2017/9/3

@author: dsou
'''

from PyQt5 import QtCore
from Plot.CanvasBase import CanvasBase
import typing

class GraphObject(CanvasBase):
    '''
    classdocs
    '''
    
    # Variable to store visible state
    __visible=True
    
    # variable to store the mask for visible state 
    __visibleMask=True
    
    plotOptions={}
    
    def __init__(self,visible=True,visibleMask=True,parent=None,**kwargs):
        #self.__visible=visible
        self.__visibleMask=visibleMask
        self.__visible=visible
        CanvasBase.__init__(self, parent)
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __del__(self):
        #self.parent=None
        pass
    
    # visible
    def getVisible(self)->bool:
        return self.__visible
    @QtCore.pyqtSlot(bool)
    def setVisible(self,visible:bool):
        if (visible and self.__visibleMask) != (self.__visible and self.__visibleMask):
            self._setVisibleInternal(visible and self.__visibleMask)
        self.__visible=visible
    visible=property(
        lambda self: self.getVisible(), 
        lambda self, val: self.setVisible(val)
        )

    def _setVisibleInternal(self,visible):
        # implimentation for visible if state changed
        raise NotImplementedError("GraphObject._setVisibleInternal has to be implemented")
        
    def getVisibleMask(self):
        return self.__visibleMask
    @QtCore.pyqtSlot(bool)
    def setVisibleMask(self,visibleMask):
        if (self.__visible and visibleMask) != (self.__visible and self.__visibleMask):
            self._setVisibleInternal(self.__visible and visibleMask)
        self.__visibleMask=visibleMask
    visibleMask=property(
        lambda self: self.getVisibleMask(), 
        lambda self, val: self.setVisibleMask(val)
        )

    
    def isShowed(self)->bool:
        '''
        @return: bool. Return True if the graph is shown on the plot 
        '''
        return self.__visible and self.__visibleMask

    # clear the graph from the screen
    # todo: remove this method
    def clear(self):
        raise NotImplementedError("GraphObject.clear has to be implemented")

# Sync a group of GraphObject items
# sync methods: visible, clear
class Group(GraphObject):
    __graphList:typing.List[GraphObject]=[]
    def __init__(self,graphList:typing.Iterable[GraphObject],visible=True,parent=None,**kwargs):
        for member in graphList:
            member.parent=self

        self.__graphList=list(graphList)
        GraphObject.__init__(self,visible=visible,parent=parent,**kwargs)
        self._setVisibleInternal(visible=visible)
        
    def _setVisibleInternal(self, visible):
        for member in self.__graphList:
            member.setVisibleMask(visible)
    
    # clear all artist in the list from the canvas    
    def update(self):
        for member in self.__graphList:
            member.update()

    # clear all artist in the list from the canvas    
    def clear(self):
        for member in self.__graphList:
            member.setParent(None)
            member.clear()
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
    def extend(self,l:typing.Iterable[GraphObject]):
        for member in l:
            member.setVisibleMask(self.isShowed())
            member.parent=self
        self.__graphList.extend(l)

