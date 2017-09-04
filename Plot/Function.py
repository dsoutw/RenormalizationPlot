'''
Created on 2017/9/3

@author: dsou
'''

from Plot.GraphObject import GraphObject,generateSample

class Function(GraphObject):
    '''
    Plot a function
    '''

    # Function of one variable
    _func=None
    _axis=None
    _xEventId=None
    _yEventId=None
    _kwargs=()
    
    def __init__(self, canvas, func, axis=None, visible=True, **kwargs):
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
        self._func=func
        self._kwargs=kwargs
        if axis == None:
            self._axis=canvas.axes
        else:
            self._axis=axis

        # set sample points
        self._sample = generateSample(self._axis)

        super().__init__(canvas, visible=visible)
    
    
    def _initilizePlot(self):
        artist = self.__plot(self._axis)

        def on_xlims_change(axis):
            self._sample = generateSample(axis)
            self.update()
        self._xEventId=self._axis.callbacks.connect('xlim_changed', on_xlims_change)

        return artist

    def __plot(self, axis):
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

    def _clearPlot(self, artist):
        if self._xEventId != None:
            self._axis.callbacks.disconnect(self._xEventId)
            self._xEventId=None
        GraphObject._clearPlot(self, artist)

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
    
