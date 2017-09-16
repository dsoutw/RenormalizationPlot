'''
Created on 2017/9/3

@author: dsou
'''

from Plot.Artist import ArtistBase,generateSample

class Function(ArtistBase):
    '''
    Plot a function
    '''

    # Function of one variable
    __func=None
    _axis=None
    _xEventId=None
    _yEventId=None
    _kwargs=()
    
    def __init__(self, parent, func, axis=None, visible=True, **kwargs):
        '''
        Plot a function
        :param canvas: the canvas showing the plot
        :type canvas:
        :param func: function to be plot
        :type func: function of one variable
        :param axis: axis to be plot. 
        :type axis:
        :param visible: set visible 
        :type visible:
        '''
        self.__func=func
        self._kwargs=kwargs

        # set sample points
        super().__init__(parent, visible=visible)
    
    
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
        curve, = axis.plot(self._sample, self.function(self._sample), **self._kwargs)
        return curve
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,artist):
        artist.set_xdata(self._sample)
        artist.set_ydata(self.function(self._sample))
        return artist

    def _clearPlot(self, artist):
        if self._xEventId != None:
            self.canvas.axes.callbacks.disconnect(self._xEventId)
            self._xEventId=None
        super().__clearPlot(artist)

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
    
