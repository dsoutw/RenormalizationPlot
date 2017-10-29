'''
Renormalization Plot - plot/contour.py
    Draw contour plot

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

from .artist import ArtistBase,generateSample
import numpy as np
import matplotlib.ticker as ticker
import logging

# QuadContourSet is not inherted from artist
# have to rewrite the base
class Contour(ArtistBase):
    _contour=None
    _cbaxes=None
    _cbar=None

    __updateDirty=False
    
    def __init__(self, func, logger=None, **kwargs):
        '''
        Draw the contour plot of a function of two variables 
        @param func: Function to be plotted
        @type func: real function of two variables
        @param logger: Logging instance (optional)
        @type logger: logging.Logger
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        self.__func=np.vectorize(func,signature='(),()->()')

        # set sample points
        super().__init__(logger=logger, **kwargs)
        
    def _initilizePlot(self):
        x = generateSample(self.canvas.axes)
        y = np.arange(-1.0, 1.1, 2)
        self.sampleX,self.sampleY = np.meshgrid(x,y)
        try:
            #data=list(map(self.function,self.sampleX,self.sampleY))
            data=self.function(self.sampleX,self.sampleY)
        except Exception as e:
            raise RuntimeError('Unable to generate sample points') from e

        self._contour = self.canvas.axes.contourf(self.sampleX, self.sampleY, data, **self.plotOptions)
        self._cbaxes = self.canvas.fig.add_axes([0.9, 0.1, 0.03, 0.8]) 
        self._cbar = self.canvas.fig.colorbar(self._contour, cax=self._cbaxes, ticks=ticker.MaxNLocator(integer=True))
        artistList=[self._cbaxes]
        artistList.extend(self._contour.collections)
        return artistList

    def _updatePlot(self,artist):
        for item in self._contour.collections:
            item.remove()
        try:
            data=list(map(self.function,self.sampleX,self.sampleY))
        except Exception as e:
            raise RuntimeError('Unable to generate sample points') from e
        self._contour = self.canvas.axes.contourf(self.sampleX, self.sampleY, data,**self.plotOptions)
        artistList=[self._cbaxes]
        artistList.extend(self._contour.collections)
        return artistList
    
    def _clearPlot(self):
        self._contour=None
        self._cbaxes=None
        self._cbar=None
        super()._clearPlot()
            
    # function
    def getFunction(self):
        return self.__func
    def setFunction(self,func):
        self.__func=np.vectorize(func,signature='(),()->()')
        self.update()
    function=property(
        lambda self: self.getFunction(), 
        lambda self, func: self.setFunction(func)
        )
