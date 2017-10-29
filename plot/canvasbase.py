'''
Renormalization Plot - plot/canvasbase.py
    Control for canvas

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
'''


from PyQt5 import QtCore

class CanvasBase(object):
    '''
    classdocs
    '''

    def __init__(self, parent):
        '''
        Constructor
        '''
        self.parent=parent

    __parent=None
    def getParent(self):
        return self.__parent
    @QtCore.pyqtSlot(bool)
    def setParent(self,parent):
        oldCanvas=self.canvas
        if parent is None:
            newCanvas=None
        else:
            newCanvas=parent.canvas
        self.__parent=parent
        
        if oldCanvas != newCanvas:
            self.canvasChangedEvent(oldCanvas, newCanvas)
    parent=property(
        lambda self: self.getParent(), 
        lambda self, parent: self.setParent(parent)
        )

    def getCanvas(self)->"CanvasBase":
        if self.parent is not None:
            return self.parent.canvas
        else:
            return None
    canvas=property(lambda self: self.getCanvas())
    
    def canvasChangedEvent(self,oldCanvas,newCanvas):
        pass
    
    # update the graph from the screen
    def update(self):
        raise NotImplementedError("CanvasBase.update has to be implemented")
