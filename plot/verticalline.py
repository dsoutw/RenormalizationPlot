'''
Created on 2017/9/3

@author: dsou
'''
from .artist import ArtistBase
from PyQt5 import QtCore
import logging

class VerticalLine(ArtistBase):
    def __init__(self, xValue, logger=None, **kwargs):
        '''
        Plot a vertical line on a canvas
        :param canvas:
        :type canvas:
        :param xValue:
        :type xValue:
        :param axis:
        :type axis:
        :param visible:
        :type visible:
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        self._xValue=xValue
        
        super().__init__(logger=logger, **kwargs)

    def _initilizePlot(self):
        return self.__plot(self.canvas.axes)

    def __plot(self, axis):
        return axis.axvline(x=self.xValue,**self.plotOptions)
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,artist):
        artist.set_xdata([self.xValue,self.xValue])
        return artist

    # function
    def getXValue(self):
        return self._xValue
    @QtCore.pyqtSlot(int)
    def setXValue(self,xValue):
        self._xValue=xValue
        self.update()
    xValue=property(
        lambda self: self.getXValue(), 
        lambda self, value: self.setXValue(value)
        )