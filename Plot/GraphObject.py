'''
Created on 2017/9/3

@author: dsou
'''

from PyQt5 import QtCore
from Plot.MPLCanvas import MPLCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.artist import Artist
import numpy as np
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

class GraphObject(GraphObjectBase,QtCore.QObject):
    '''
    An container for matplotlib artist
    '''
    __canvas=None
    __artist=None
    
    def __init__(self, canvas:MPLCanvas, visible:bool=True):
        '''
        An container for matplotlib artist
        :param canvas: The canvas storing the artist
        :type canvas: MPLCanvas
        :param visible: Set visible of the artist
        :type visible: bool
        '''
        self.__canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # Plot only when visible
        if visible == True:
            self.__artist=self._initilizePlot()
        else:
            self.__artist=None

    # return: matplotlib artist
    def _initilizePlot(self)->Artist:
        '''
        Create the plot. Implimented by the child
        This is called when a new artist is requested
        The function returns the new MPL artist ploted on the canvas
        @return: The new MPL artist
        '''
        #raise NotImplementedError("GraphObjectBase._initilize has to be implemented")
        pass

    def _updatePlot(self, artist:Artist)->Artist:
        '''
        Update the plot. Implimented by the child
        This is called when the artist needs to be updated
        The child updates the input MPL artist and returns the updated MPL artist
        The input and output can be the same
        :param artist: The original MPL artist
        :type artist: matplotlib.artist
        @return: The updated MPL artist
        '''
        #raise NotImplementedError("GraphObjectBase._updatePlot has to be implemented")
        pass

    def _clearPlot(self, artist:Artist):
        '''
        Clear the plot. Implimented by the child
        This is called before the artist is removed
        :param artist: The artist to be clear
        :type artist: matplotlib.artist
        '''
        pass

    @QtCore.pyqtSlot()
    def update(self):
        if self.__artist is not None:
            self.__artist=self._updatePlot(self.__artist)
            self.__canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self.__artist=self._initilizePlot()
            self.__canvas.update()

    # canvas
    # useless?
    def getCanvas(self):
        return self.__canvas
    @QtCore.pyqtSlot(FigureCanvas)
    def setCanvas(self,canvas):
        self.__canvas=canvas
    canvas=property(
        lambda self: self.getCanvas(), 
        lambda self, val: self.setCanvas(val)
        )
        
    # visible
    def _setVisibleInternal(self,visible):
        if self.__artist is not None:
            self.__artist.set_visible(visible)
            self.__canvas.update()
        elif visible == True:
            self.__artist=self._initilizePlot()
            self.__canvas.update()
        
    # artist
    # useless?
    def getArtist(self):
        return self.__artist
    def setArtist(self, curve):
        self.__artist=curve
    artist=property(
        lambda self: self.getArtist(), 
        lambda self, val: self.setArtist(val)
        )

    # clear the artist from the canvas    
    def clear(self):
        if self.__artist is not None:
            self._clearPlot(self.__artist)
            self.__artist.remove()
            self.__artist=None
            self.__canvas.update()
            
def generateSample(axis):
    l,r = axis.get_xlim()
    sample = np.append(np.arange(-1.0, l, 0.001), np.arange(l, r, (r-l)/1000.0))
    sample = np.append(sample, np.arange(r, 1.001, 0.001))
    return np.float64(sample)
