'''
Created on 2017/9/3

@author: dsou
'''

from PyQt5 import QtCore
from typing import Iterable

class GraphObjectBase:
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
        raise NotImplementedError("GraphObjectBase._setVisibleInternal has to be implemented")
        
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
        raise NotImplementedError("GraphObjectBase.update has to be implemented")

    # clear the graph from the screen
    def clear(self):
        raise NotImplementedError("GraphObjectBase.clear has to be implemented")

# Sync a group of GraphObjectBase items
# sync methods: visible, clear
class Group(GraphObjectBase,list):
    def __init__(self,artistList:Iterable[GraphObjectBase],visible=True):
        list.__init__(self,artistList)
        GraphObjectBase.__init__(self,visible=visible)
        self._setVisibleInternal(visible=visible)
        
    def _setVisibleInternal(self, visible):
        for member in self:
            member.setVisibleMask(visible)
    
    # clear all artist in the list from the canvas    
    def update(self):
        for member in self:
            member.update()

    # clear all artist in the list from the canvas    
    def clear(self):
        for member in self:
            member.clear()
        del self[:]


