'''
Renormalization Plot - plot/function.py
    Draw the plot for a function of one variable

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

from .artist import ArtistBase,generateSample
import logging

class Function(ArtistBase):
    '''
    Plot a function
    '''

    # Function of one variable
    __func=None
    _axis=None
    _xEventId=None
    _yEventId=None
    plotOptions=()
    
    def __init__(self, func, logger=None, reflection=False, **kwargs):
        '''
        Plot a function
        :param func: function to be plot
        :type func: real function of one variable
        @param logger: Logging instance (optional)
        @type logger: logging.Logger
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        self.__func=func
        self.__reflection=reflection

        # set sample points
        super().__init__(logger=logger, **kwargs)
    
    
    def _initilizePlot(self):
        artist = self.__plot(self.canvas.axes)

        # update the resolution automatically when the plot is zoomed
        def on_xlims_change(axis):
            self._sample = generateSample(axis)
            self.update()
        self._xEventId=self.canvas.axes.callbacks.connect('xlim_changed', on_xlims_change)

        return artist

    def __plot(self, axis):
        self._sample = generateSample(axis)
        try:
            data=list(map(self.function,self._sample))
        except Exception as e:
            raise RuntimeError('Unable to generate sample points') from e

        if not self.__reflection:
            curve, = axis.plot(self._sample, data, **self.plotOptions)
        else:
            curve, = axis.plot(data, self._sample, **self.plotOptions)
        
        return curve
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,artist):
        artist.set_xdata(self._sample)
        try:
            data=list(map(self.function,self._sample))
        except Exception as e:
            raise RuntimeError('Unable to generate sample points') from e

        if not self.__reflection:
            artist.set_ydata(data)
        else:
            artist.set_xdata(data)
            
        return artist

    def _clearPlot(self):
        if self._xEventId != None:
            try:
                self.canvas.axes.callbacks.disconnect(self._xEventId)
            except:
                self._logger.exception('Unable to disconnect axes callback')
            self._xEventId=None
        super().__clearPlot()

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
    
