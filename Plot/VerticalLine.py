'''
Created on 2017/9/3

@author: dsou
'''
from Plot.GraphObject import GraphObject
from PyQt5 import QtCore

class VerticalLine(GraphObject):
    def __init__(self, canvas, xValue, axis=None, visible=True, **kwargs):
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
        self._xValue=xValue
        self._kwargs=kwargs
        if axis == None:
            self._axis=canvas.axes
        else:
            self._axis=axis
        
        super().__init__(canvas, visible)

    def _initilizePlot(self):
        return self.__plot(self._axis)

    def __plot(self, axis):
        return axis.axvline(x=self.xValue,**self._kwargs)
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,curve):
        curve.set_xdata([self.xValue,self.xValue])

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