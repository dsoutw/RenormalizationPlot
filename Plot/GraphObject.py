'''
Created on 2017/9/3

@author: dsou
'''

from PyQt5 import QtCore
from typing import Iterable

class GraphObject:
    '''
    classdocs
    '''
    
    # Variable to store visible state
    _visible=True
    
    # variable to store the mask for visible state 
    _visibleMask=True
    
    def __init__(self,visible=True,visibleMask=True):
        #self._visible=visible
        self._visibleMask=visibleMask
        self._visible=visible
    
    # visible
    def getVisible(self)->bool:
        return self._visible
    @QtCore.pyqtSlot(bool)
    def setVisible(self,visible:bool):
        if (visible & self._visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(visible & self._visibleMask)
        self._visible=visible
    visible=property(
        lambda self: self.getVisible(), 
        lambda self, val: self.setVisible(val)
        )

    def _setVisibleInternal(self,visible):
        # implimentation for visible if state changed
        raise NotImplementedError("GraphObject._setVisibleInternal has to be implemented")
        
    def getVisibleMask(self):
        return self._visibleMask
    @QtCore.pyqtSlot(bool)
    def setVisibleMask(self,visibleMask):
        if (self._visible & visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(self._visible & visibleMask)
        self._visibleMask=visibleMask
    visibleMask=property(
        lambda self: self.getVisibleMask(), 
        lambda self, val: self.setVisibleMask(val)
        )

    
    def isShowed(self)->bool:
        '''
        @return: bool. Return True if the graph is shown on the plot 
        '''
        return self._visible & self._visibleMask 

    # update the graph from the screen
    def update(self):
        raise NotImplementedError("GraphObject.update has to be implemented")

    # clear the graph from the screen
    def clear(self):
        raise NotImplementedError("GraphObject.clear has to be implemented")

# Sync a group of GraphObject items
# sync methods: visible, clear
class Group(GraphObject):
    __graphList=[]
    def __init__(self,graphList:Iterable[GraphObject],visible=True):
        self.__graphList=list(graphList)
        GraphObject.__init__(self,visible=visible)
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
            member.clear()
        del self.__graphList[:]
        
    '''
    List methods
    '''
    def __getitem__(self,key):
        return self.__graphList[key]
    def __setitem__(self,key,value):
        self.__graphList[key]=value
    def __iter__(self):
        return self.__graphList
    def append(self,x:GraphObject):
        x.setVisibleMask(self.visible)
        self.__graphList.append(x)
    def extend(self,l:Iterable[GraphObject]):
        for member in l:
            member.setVisibleMask(self.visible)
        self.__graphList.extend(l)

