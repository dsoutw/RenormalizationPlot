'''
Created on 2017/9/3

@author: dsou
'''

from Plot.GraphObject import GraphObjectBase,generateSample
from PyQt5 import QtCore
import numpy as np
import matplotlib.ticker as ticker

# QuadContourSet is not inherted from artist
# have to rewrite the base
class Contour(GraphObjectBase,QtCore.QObject):
    _contour=None
    _cbaxes=None
    _cbar=None
    
    def __init__(self, canvas, func, visible=True, **kwargs):
        self._func=func
        self._kwargs=kwargs
        self.__canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # set sample points
        x = generateSample(self.__canvas.axes)
        y = np.arange(-1.0, 1.1, 2)
        self.sampleX,self.sampleY = np.meshgrid(x,y)
        
        # Plot only when visible
        if visible == True:
            self._initilizePlot()
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
            self._updatePlot()
            self.__canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self._initilizePlot()
            self.__canvas.update()

    # visible
    # todo: create a new axis and set the visibility of the axis 
    def _setVisibleInternal(self,visible):
        if self._contour != None:
            for item in self._contour.collections:
                item.set_visible(visible)
            self._cbaxes.set_visible(visible)
            #self._removePlot()
            self.__canvas.update()
        elif visible == True and self._contour == None:
            self._initilizePlot()
            self.__canvas.update()
            
    # function
    def getFunction(self):
        return self._func
    def setFunction(self,func):
        self._func=func
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