'''
Renormalization Plot - plot/graphobject.py
    Wrapper for matplotlib methods

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
'''

from PyQt5 import QtCore
from .canvasbase import CanvasBase
import typing as tp
import logging

class GraphObject(CanvasBase):
    '''
    classdocs
    '''
    
    # Variable to store visible state
    __visible=True
    
    # variable to store the mask for visible state 
    __visibleMask=True
    
    plotOptions={}
    _logger:tp.Optional[logging.Logger]=None
    
    def __init__(self,visible=True,visibleMask=True,parent=None,logger=None,**kwargs):
        #self.__visible=visible
        self.__visibleMask=visibleMask
        self.__visible=visible
        if logger is None:
            self._logger=logging.getLogger(__name__)
        else:
            self._logger=logger
            
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

    def _setVisibleInternal(self,visible:bool):
        # implimentation for visible if state changed
        raise NotImplementedError("GraphObject._setVisibleInternal has to be implemented")
        
    def getVisibleMask(self)->bool:
        return self.__visibleMask
    @QtCore.pyqtSlot(bool)
    def setVisibleMask(self,visibleMask:bool):
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
