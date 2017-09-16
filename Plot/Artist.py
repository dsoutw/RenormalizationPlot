'''
Created on 2017/9/4

@author: dsou
'''
from matplotlib.artist import Artist as MPLArtist
import numpy as np
from Plot.GraphObject import GraphObject
from Plot.CanvasBase import CanvasBase
from PyQt5 import QtCore
import typing
from abc import ABCMeta,abstractmethod

class ArtistBase(GraphObject,QtCore.QObject):
    '''
    An abstract container for matplotlib artist
    '''
    __metaclass__=ABCMeta
    __canvas=None
    __artist=None
    __updateDirty=False
    
    def __init__(self, parent:CanvasBase=None, visible:bool=True):
        '''
        An abstract container for matplotlib artist
        :param canvas: The canvas storing the artist
        :type canvas: MPLCanvas
        :param visible: Set visible of the artist
        :type visible: bool
        '''
        GraphObject.__init__(self,visible=visible,parent=parent)
        QtCore.QObject.__init__(self,self.canvas)

    @abstractmethod
    def _initilizePlot(self)->MPLArtist:
        '''
        Create the plot. Implimented by the child
        This is called when a new artist is requested
        The function returns the new MPL artist ploted on the canvas
        @return: The new MPL artist
        '''
        raise NotImplementedError("GraphObject._initilize has to be implemented")
        pass

    @abstractmethod
    def _updatePlot(self, artist:MPLArtist)->MPLArtist:
        '''
        Update the plot. Implimented by the child
        This is called when the artist needs to be updated
        The child updates the input MPL artist and returns the updated MPL artist
        The input and output can be the same
        :param artist: The original MPL artist
        :type artist: matplotlib.artist
        @return: The updated MPL artist
        '''
        raise NotImplementedError("GraphObject._updatePlot has to be implemented")
        pass

    def _clearPlot(self, artist:MPLArtist):
        '''
        Clear the plot.
        The default behavior is to call artist.remove
        Override this method if want to change the default behavior
        :param artist: The artist to be clear
        :type artist: matplotlib.artist
        '''
        if not isinstance(artist, list):
            artist.remove()
        else:
            for element in artist:
                element.remove()

    @QtCore.pyqtSlot()
    def update(self):
        if self.canvas is not None:
            if self.isShowed() is True:
                if self.__artist is not None:
                    self.__artist=self._updatePlot(self.__artist)
                    self.canvas.update()
                    self.__updateDirty=False
                else:
                    self.__artist=self._initilizePlot()
                    self.__updateDirty=False
            else:
                self.__updateDirty=True

    # visible
    def _setVisibleInternal(self,visible):
        if self.canvas is not None:
            if self.__artist is not None:
                if visible and self.__updateDirty:
                    # Only update the contents when the plot is visible
                    self.__artist=self._updatePlot(self.__artist)
                    self.__updateDirty=False
                if not isinstance(self.__artist, list):
                    self.__artist.set_visible(visible)
                else:
                    for element in self.__artist:
                        element.set_visible(visible)
                self.canvas.update()
            elif visible is True:
                self.__artist=self._initilizePlot()
                self.__updateDirty=False
                self.canvas.update()
        
    # artist
    # useless?
    def getArtist(self)->typing.Union[MPLArtist,typing.List[MPLArtist]]:
        return self.__artist
    def setArtist(self, artist:typing.Union[MPLArtist,typing.List[MPLArtist]]):
        self.__artist=artist
    artist=property(
        lambda self: self.getArtist(), 
        lambda self, val: self.setArtist(val)
        )

    # clear the artist from the canvas    
    def clear(self):
        if self.__artist != None:
            self._clearPlot(self.__artist)
            self.__artist=None
            self.canvas.update()
            
    def canvasChangedEvent(self, oldCanvas, newCanvas):
        if (oldCanvas is not None) and (self.__artist is not None):
            self._clearPlot(self.__artist)
            self.__artist=None
            oldCanvas.update()

        if (newCanvas is not None) and self.isShowed():
            self.__artist=self._initilizePlot()
            self.__updateDirty=False
        else:
            self.__artist=None            
                        
        GraphObject.canvasChangedEvent(self, oldCanvas, newCanvas)
    
def generateSample(axis):
    l,r = axis.get_xlim()
    sample = np.append(np.arange(-1.0, l, 0.001), np.arange(l, r, (r-l)/1000.0))
    sample = np.append(sample, np.arange(r, 1.001, 0.001))
    return np.float64(sample)