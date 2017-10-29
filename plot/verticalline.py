'''
Renormalization Plot - plot/verticalline.py
    Add a vertical line to the plot

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
'''

from .artist import ArtistBase
from PyQt5 import QtCore
import logging

class VerticalLine(ArtistBase):
    def __init__(self, xValue, logger=None, **kwargs):
        '''
        Add a vertical line to the plot
        @param xValue: x coordinate of the vertical line
        @type xValue: float
        @param logger: Logging instance (optional)
        @type logger: logging.Logger
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