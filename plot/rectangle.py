'''
Renormalization Plot - plot/rectangle.py
    Plot a rectangle

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

from .artist import ArtistBase
import matplotlib.patches as patches
import logging

class Rectangle(ArtistBase):
    def __init__(self, xValue, yValue, width, height, logger=None, **kwargs):
        '''
        Plot a rectangle
        @param xValue: x coordinate of the lower left corner
        @type xValue: float
        @param yValue: y coordinate of the lower left corner
        @type yValue: float
        @param width: Width
        @type width: float
        @param height: Height
        @type height: float
        @param logger: Logging instance (optional)
        @type logger: logging.Logger
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        
        super().__init__(logger=logger, **kwargs)

    def _initilizePlot(self):
        return self.__plot(self.canvas.axes)

    def __plot(self, axis):
        (xValue,yValue,width,height)=self.bounds
        artist = patches.Rectangle((xValue,yValue), width, height, **self.plotOptions)
        axis.add_patch(artist)
        return artist
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,artist):
        artist.set_bounds(*self.bounds)
        return artist

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