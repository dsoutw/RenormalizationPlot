'''
Created on 2017/9/14

@author: dsou
'''

from .artist import ArtistBase
from PyQt5 import QtCore
from typing import Tuple
import logging

class Text(ArtistBase):
    def __init__(self, text:str, xy:Tuple[int,int], xyOffset:Tuple[int,int]=(0,0), logger=None, **kwargs):
        '''
        Plot a vertical line on a canvas
        :param canvas:
        :type canvas:
        :param text: 
        :type text: str
        :param axis:
        :type axis:
        :param visible:
        :type visible:
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        (self._xValue,self._yValue)=xy
        (self._xOffset,self._yOffset)=xyOffset
        self._text=text
        
        super().__init__(logger=logger, **kwargs)

    def _initilizePlot(self):
        return self.__plot(self.canvas.axes)

    def __plot(self, axis):
        return axis.annotate(self._text,xy=(self._xValue,self._yValue),xytext=(self._xOffset,self._yOffset),textcoords='offset points',**self.plotOptions)
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,artist):
        artist.xy=(self._xValue,self._yValue)
        artist.set_position(self.offset)
        artist.set_text(self.text)
        return artist

    # properties
    def getPosition(self):
        return (self._xValue,self._yValue)
    @QtCore.pyqtSlot(int)
    def setPosition(self,value):
        (self._xValue,self._yValue)=value
        self.update()
    position=property(
        lambda self: self.getPosition(), 
        lambda self, value: self.setPosition(value)
        )

    def getOffset(self):
        return (self._xOffset,self._yOffset)
    @QtCore.pyqtSlot(int)
    def setOffset(self,value):
        (self._xOffset,self._yOffset)=value
        self.update()
    offset=property(
        lambda self: self.getOffset(), 
        lambda self, value: self.setOffset(value)
        )
    
    def getText(self):
        return self._text
    @QtCore.pyqtSlot(int)
    def setText(self,text):
        self._text=text
        self.update()
    text=property(
        lambda self: self.getText(), 
        lambda self, text: self.setText(text)
        )