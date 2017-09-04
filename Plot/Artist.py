'''
Created on 2017/9/4

@author: dsou
'''
from matplotlib.artist import Artist as MPLArtist
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Plot.MPLCanvas import MPLCanvas
import numpy as np
from Plot.GraphObject import GraphObjectBase
from PyQt5 import QtCore

class ArtistBase(GraphObjectBase,QtCore.QObject):
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
    def _initilizePlot(self)->MPLArtist:
        '''
        Create the plot. Implimented by the child
        This is called when a new artist is requested
        The function returns the new MPL artist ploted on the canvas
        @return: The new MPL artist
        '''
        raise NotImplementedError("GraphObjectBase._initilize has to be implemented")
        pass

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
        raise NotImplementedError("GraphObjectBase._updatePlot has to be implemented")
        pass

    def _clearPlotBefore(self, artist:MPLArtist):
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
    def setCanvas(self,canvas:FigureCanvas):
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
    def getArtist(self)->MPLArtist:
        return self.__artist
    def setArtist(self, artist:MPLArtist):
        self.__artist=artist
    artist=property(
        lambda self: self.getArtist(), 
        lambda self, val: self.setArtist(val)
        )

    # clear the artist from the canvas    
    def clear(self):
        if self.__artist is not None:
            self._clearPlotBefore(self.__artist)
            self.__artist.remove()
            self.__artist=None
            self.__canvas.update()
            
def generateSample(axis):
    l,r = axis.get_xlim()
    sample = np.append(np.arange(-1.0, l, 0.001), np.arange(l, r, (r-l)/1000.0))
    sample = np.append(sample, np.arange(r, 1.001, 0.001))
    return np.float64(sample)