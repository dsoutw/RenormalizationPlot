'''
Created on 2017/9/3

@author: dsou
'''

from Plot.GraphObject import GraphObject
from Plot.Artist import generateSample
from PyQt5 import QtCore
import numpy as np
import matplotlib.ticker as ticker

# QuadContourSet is not inherted from artist
# have to rewrite the base
class Contour(GraphObject,QtCore.QObject):
    _contour=None
    _cbaxes=None
    _cbar=None

    __updateDirty=False
    
    def __init__(self, canvas, func, visible=True, **kwargs):
        self.__func=func
        self._kwargs=kwargs
        self.__canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObject.__init__(self,visible=visible)

        # set sample points
        x = generateSample(self.__canvas.axes)
        y = np.arange(-1.0, 1.1, 2)
        self.sampleX,self.sampleY = np.meshgrid(x,y)
        
        # Plot only when visible
        if visible == True:
            self._initilizePlot()
            self.__updateDirty=False
        else:
            self._contour=None
        

    def _initilizePlot(self):
        self._contour = self.__canvas.axes.contourf(self.sampleX, self.sampleY, self.function(self.sampleX,self.sampleY),**self._kwargs)
        self._cbaxes = self.__canvas.fig.add_axes([0.9, 0.1, 0.03, 0.8]) 
        self._cbar = self.__canvas.fig.colorbar(self._contour, cax=self._cbaxes, ticks=ticker.MaxNLocator(integer=True))

    def draw(self, figure, axis):
        if self.isShowed():
            contour=axis.contourf(self.sampleX, self.sampleY, self.function(self.sampleX,self.sampleY),**self._kwargs)
            cbar=figure.add_axes([0.9, 0.1, 0.03, 0.8]) 
            figure.colorbar(contour, cax=cbar, ticks=ticker.MaxNLocator(integer=True))

    def _updatePlot(self):
        for item in self._contour.collections:
            item.remove()
        self._contour = self.__canvas.axes.contourf(self.sampleX, self.sampleY, self.function(self.sampleX,self.sampleY),**self._kwargs)
    
    def _removePlot(self):
        for item in self._contour.collections:
            item.remove()
        self._contour=None
        self._cbaxes.remove()
        self._cbaxes=None
        self._cbar=None
    
    @QtCore.pyqtSlot()
    def update(self):
        if self._contour is not None:
            if self.isShowed()==True:
                self._updatePlot()
                self.__canvas.update()
                self.__updateDirty=False
            else:
                self.__updateDirty=True
        elif self._visible == True and self._visibleMask == True:
            self._initilizePlot()
            self.__canvas.update()

    # visible
    # todo: create a new axis and set the visibility of the axis 
    def _setVisibleInternal(self,visible):
        if self._contour != None:
            if visible and self.__updateDirty:
                self._updatePlot()
                self.__updateDirty=False
            else:
                for item in self._contour.collections:
                    item.set_visible(visible)
            self._cbaxes.set_visible(visible)
            self.__canvas.update()
        elif visible == True and self._contour == None:
            self._initilizePlot()
            self.__canvas.update()
            
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
        
    def clear(self):
        if self._contour is not None:
            self._removePlot()
            self.__canvas.update()

    function=property(getFunction, setFunction)