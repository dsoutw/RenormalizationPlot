'''
Created on 2017/9/3

@author: dsou
'''

from Plot.GraphObject import GraphObject
import matplotlib.patches as patches

class Rectangle(GraphObject):
    def __init__(self, canvas, xValue, yValue, width, height, axis=None, visible=True, **kwargs):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self._kwargs=kwargs
        if axis == None:
            self._axis=canvas.axes
        else:
            self._axis=axis
        
        super().__init__(canvas, visible)

    def _initilizePlot(self):
        return self.__plot(self._axis)

    def __plot(self, axis):
        (xValue,yValue,width,height)=self.bounds
        artist = patches.Rectangle((xValue,yValue), width, height, **self._kwargs)
        axis.add_patch(artist)
        return artist
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,curve):
        curve.set_bounds(*self.bounds)

    # function
    def getBounds(self):
        return (self._xValue, self._yValue, self._width, self._height)
    def setBounds(self, xValue, yValue, width, height):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self.update()
    bounds=property(
        lambda self: self.getBounds(), 
        lambda self, *args: self.setBounds(*args)
        )