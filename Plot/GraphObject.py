'''
Created on 2017/9/3

@author: dsou
'''

from PyQt5 import QtCore
from Plot.MPLCanvas import MPLCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class GraphObjectBase():
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

    # clear the graph from the screen
    def clear(self):
        raise NotImplementedError("GraphObjectBase.clear has to be implemented")

# Sync a group of GraphObjectBase items
# sync methods: visible, clear
class Group(GraphObjectBase,list):
    def __init__(self,*args,visible=True):
        list.__init__(self,*args)
        GraphObjectBase.__init__(self,visible=visible)
        self._setVisibleInternal(visible=visible)
        
    def _setVisibleInternal(self, visible):
        for member in self:
            member.setVisibleMask(visible)
    
    # clear all artist in the list from the canvas    
    def clear(self):
        for member in self:
            member.clear()
        del self[:]

# Graphical object for artist
# line=matplotlib.lines.Line2D object
# canvas: matplotlib canvas
class GraphObject(GraphObjectBase,QtCore.QObject):
    _canvas=None
    _artist=None
    
    def __init__(self, canvas:MPLCanvas, visible=True):
        self._canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # Plot only when visible
        if visible == True:
            self._artist=self._initilizePlot()
        else:
            self._artist=None

    # return: matplotlib artist
    def _initilizePlot(self):
        raise NotImplementedError("GraphObjectBase._initilize has to be implemented")

    # artist: matplotlib artist
    def _updatePlot(self, artist):
        raise NotImplementedError("GraphObjectBase._updatePlot has to be implemented")

    def _clearPlot(self, artist):
        pass

    @QtCore.pyqtSlot()
    def update(self):
        if self._artist is not None:
            self._updatePlot(self._artist)
            self._canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self._artist=self._initilizePlot()
            self._canvas.update()

    # canvas
    # useless?
    def getCanvas(self):
        return self._canvas
    @QtCore.pyqtSlot(FigureCanvas)
    def setCanvas(self,canvas):
        self._canvas=canvas
    canvas=property(
        lambda self: self.getCanvas(), 
        lambda self, val: self.setCanvas(val)
        )
        
    # visible
    def _setVisibleInternal(self,visible):
        if self._artist is not None:
            self._artist.set_visible(visible)
            self._canvas.update()
        elif visible == True:
            self._artist=self._initilizePlot()
            self._canvas.update()
        
    # artist
    # useless?
    def getArtist(self):
        return self._artist
    def setArtist(self, curve):
        self._artist=curve
    artist=property(
        lambda self: self.getArtist(), 
        lambda self, val: self.setArtist(val)
        )

    # clear the artist from the canvas    
    def clear(self):
        if self._artist is not None:
            self._clearPlot(self._artist)
            self._artist.remove()
            self._artist=None
            self._canvas.update()
            
def generateSample(axis):
    l,r = axis.get_xlim()
    sample = np.append(np.arange(-1.0, l, 0.001), np.arange(l, r, (r-l)/1000.0))
    sample = np.append(sample, np.arange(r, 1.001, 0.001))
    return np.float64(sample)
