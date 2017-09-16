'''
Created on 2017/9/3

@author: dsou
'''

from Plot.GraphObject import GraphObject
from Plot.Artist import ArtistBase,generateSample
from PyQt5 import QtCore
import numpy as np
import matplotlib.ticker as ticker

# QuadContourSet is not inherted from artist
# have to rewrite the base
class Contour(ArtistBase):
    _contour=None
    _cbaxes=None
    _cbar=None

    __updateDirty=False
    
    def __init__(self, parent, func, visible=True, **kwargs):
        self.__func=func
        self._kwargs=kwargs

        # set sample points
        super().__init__(parent, visible=visible)
        
    def _initilizePlot(self):
        x = generateSample(self.canvas.axes)
        y = np.arange(-1.0, 1.1, 2)
        self.sampleX,self.sampleY = np.meshgrid(x,y)

        self._contour = self.canvas.axes.contourf(self.sampleX, self.sampleY, self.function(self.sampleX,self.sampleY),**self._kwargs)
        self._cbaxes = self.canvas.fig.add_axes([0.9, 0.1, 0.03, 0.8]) 
        self._cbar = self.canvas.fig.colorbar(self._contour, cax=self._cbaxes, ticks=ticker.MaxNLocator(integer=True))
        artistList=[self._cbaxes]
        artistList.extend(self._contour.collections)
        return artistList

    def _updatePlot(self,artist):
        for item in self._contour.collections:
            item.remove()
        self._contour = self.canvas.axes.contourf(self.sampleX, self.sampleY, self.function(self.sampleX,self.sampleY),**self._kwargs)
        artistList=[self._cbaxes]
        artistList.extend(self._contour.collections)
        return artistList
    
    def _clearPlot(self, artist):
        self._contour=None
        self._cbaxes=None
        self._cbar=None
        super()._clearPlot(artist)
            
    # function
    def getFunction(self):
        return self.__func
    def setFunction(self,func):
        self.__func=func
        self.update()
    function=property(
        lambda self: self.getFunction(), 
        lambda self, func: self.setFunction(func)
        )
