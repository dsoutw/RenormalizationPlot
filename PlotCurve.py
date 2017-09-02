'''
Created on 2017/8/15

@author: dsou
'''
import numpy as np
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
import matplotlib.ticker as ticker

import random

class GraphObjectBase():
    '''
    classdocs
    '''
    
    # Variable to store visible state
    _visible=True
    
    # variable to store the mask for visible state 
    _visibleMask=True
    
    def __init__(self,visible=True,visibleMask=True):
        #self._visible=visible
        self._visibleMask=visibleMask
        self._visible=visible
    
    # visible
    def getVisible(self):
        return self._visible
    @QtCore.pyqtSlot(bool)
    def setVisible(self,visible):
        if (visible & self._visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(visible & self._visibleMask)
        self._visible=visible
    visible=property(getVisible, setVisible)

    # implimentation for visible if state changed
    def _setVisibleInternal(self,visible):
        raise NotImplementedError("GraphObjectBase._setVisibleInternal has to be implemented")
        
    def getVisibleMask(self):
        return self._visibleMask
    @QtCore.pyqtSlot(bool)
    def setVisibleMask(self,visibleMask):
        if (self._visible & visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(self._visible & visibleMask)
        self._visibleMask=visibleMask
    visibleMask=property(getVisibleMask, setVisibleMask)

    
    def isShowed(self):
        '''
        @return: bool. Return True if the graph is shown on the plot 
        '''
        return self._visible & self._visibleMask 

    # clear the graph from the screen
    def clear(self):
        raise NotImplementedError("GraphObjectBase.clear has to be implemented")

# Sync a group of GraphObjectBase items
# sync methods: visible, clear
class GroupG(GraphObjectBase,list):
    def __init__(self,*args,visible=True):
        list.__init__(self,*args)
        GraphObjectBase.__init__(self,visible=visible)
        self._setVisibleInternal(visible=visible)
        
    def _setVisibleInternal(self, visible):
        for member in self:
            member.setVisibleMask(visible)
    
    # clear all artist in the list from the canvas    
    def clear(self):
        for member in self:
            member.clear()
        del self[:]

# Graphical object for artist
# line=matplotlib.lines.Line2D object
# canvas: matplotlib canvas
class GraphObject(GraphObjectBase,QtCore.QObject):
    _canvas=None
    _artist=None
    
    def __init__(self, canvas, visible=True):
        self._canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # Plot only when visible
        if visible == True:
            self._artist=self._initilizePlot()
        else:
            self._artist=None

    # return: matplotlib artist
    def _initilizePlot(self):
        raise NotImplementedError("GraphObjectBase._initilize has to be implemented")

    # artist: matplotlib artist
    def _updatePlot(self, artist):
        raise NotImplementedError("GraphObjectBase._updatePlot has to be implemented")

    def _clearPlot(self, artist):
        pass

    @QtCore.pyqtSlot()
    def update(self):
        if self._artist is not None:
            self._updatePlot(self._artist)
            self._canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self._artist=self._initilizePlot()
            self._canvas.update()

    # canvas
    # useless?
    def getCanvas(self):
        return self._canvas
    @QtCore.pyqtSlot(FigureCanvas)
    def setCanvas(self,canvas):
        self._canvas=canvas
    canvas=property(getCanvas, setCanvas)
        
    # visible
    def _setVisibleInternal(self,visible):
        if self._artist is not None:
            self._artist.set_visible(visible)
            self._canvas.update()
        elif visible == True:
            self._artist=self._initilizePlot()
            self._canvas.update()
        
    # artist
    # useless?
    def getArtist(self):
        return self._artist
    def setArtist(self, curve):
        self._artist=curve
    artist=property(getArtist, setArtist)

    # clear the artist from the canvas    
    def clear(self):
        if self._artist is not None:
            self._clearPlot(self._artist)
            self._artist.remove()
            self._artist=None
            self._canvas.update()

def _generateSample(axis):
    l,r = axis.get_xlim()
    sample = np.append(np.arange(-1.0, l, 0.001), np.arange(l, r, (r-l)/1000.0))
    sample = np.append(sample, np.arange(r, 1.001, 0.001))
    return sample

class FunctionG(GraphObject):
    '''
    Plot a function
    '''

    # Function of one variable
    _func=None
    _axis=None
    _xEventId=None
    _yEventId=None
    
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
        self._sample = _generateSample(self._axis)

        super().__init__(canvas, visible=visible)
    
    
    def _initilizePlot(self):
        artist = self.__plot(self._axis)

        def on_xlims_change(axis):
            self._sample = _generateSample(axis)
            self.update()
        self._xEventId=self._axis.callbacks.connect('xlim_changed', on_xlims_change)

        return artist

    def __plot(self, axis):
        curve, = axis.plot(self._sample, self._func(self._sample), **self._kwargs)
        return curve
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,curve):
        curve.set_xdata(self._sample)
        curve.set_ydata(self._func(self._sample))

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

    function=property(getFunction, setFunction)

# QuadContourSet is not inherted from artist
# have to rewrite the base
class ContourG(GraphObjectBase,QtCore.QObject):
    _contour=None
    _cbaxes=None
    _cbar=None
    
    def __init__(self, canvas, func, visible=True, **kwargs):
        self._func=func
        self._kwargs=kwargs
        self._canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # set sample points
        x = _generateSample(self._canvas.axes)
        y = np.arange(-1.0, 1.1, 2)
        self.sampleX,self.sampleY = np.meshgrid(x,y)
        
        # Plot only when visible
        if visible == True:
            self._initilizePlot()
        else:
            self._contour=None
        

    def _initilizePlot(self):
        self._contour = self._canvas.axes.contourf(self.sampleX, self.sampleY, self._func(self.sampleX,self.sampleY),**self._kwargs)
        self._cbaxes = self._canvas.fig.add_axes([0.9, 0.1, 0.03, 0.8]) 
        self._cbar = self._canvas.fig.colorbar(self._contour, cax=self._cbaxes, ticks=ticker.MaxNLocator(integer=True))

    def draw(self, figure, axis):
        if self.isShowed():
            contour=axis.contourf(self.sampleX, self.sampleY, self._func(self.sampleX,self.sampleY),**self._kwargs)
            cbar=figure.add_axes([0.9, 0.1, 0.03, 0.8]) 
            figure.colorbar(contour, cax=cbar, ticks=ticker.MaxNLocator(integer=True))

    def _updatePlot(self):
        for item in self._contour.collections:
            item.remove()
        self._contour = self._canvas.axes.contourf(self.sampleX, self.sampleY, self._func(self.sampleX,self.sampleY),**self._kwargs)
    
    def _removePlot(self):
        for item in self._contour.collections:
            item.remove()
        self._contour=None
        self._cbaxes.remove()
        self._cbaxes=None
        self._cbar=None
    
    @QtCore.pyqtSlot()
    def update(self):
        if self._contour is not None:
            self._updatePlot()
            self._canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self._initilizePlot()
            self._canvas.update()

    # visible
    # todo: create a new axis and set the visibility of the axis 
    def _setVisibleInternal(self,visible):
        if self._contour != None:
            for item in self._contour.collections:
                item.set_visible(visible)
            self._cbaxes.set_visible(visible)
            #self._removePlot()
            self._canvas.update()
        elif visible == True and self._contour == None:
            self._initilizePlot()
            self._canvas.update()
            
    # function
    def getFunction(self):
        return self._func
    def setFunction(self,func):
        self._func=func
        self.update()
        
    def clear(self):
        if self._contour is not None:
            self._removePlot()
            self._canvas.update()

    function=property(getFunction, setFunction)

class VerticalLineG(GraphObject):
    def __init__(self, canvas, xValue, axis=None, visible=True, **kwargs):
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
        return axis.axvline(x=self._xValue,**self._kwargs)
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,curve):
        curve.set_xdata([self._xValue,self._xValue])

    # function
    def getXValue(self):
        return self._xValue
    @QtCore.pyqtSlot(int)
    def setXValue(self,xValue):
        self._xValue=xValue
        self.update()
    xValue=property(getXValue, setXValue)
    
class RectangleG(GraphObject):
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
        artist = patches.Rectangle((self._xValue,self._yValue), self._width, self._height,**self._kwargs)
        axis.add_patch(artist)
        return artist
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,curve):
        curve.set_bounds(self._xValue, self._yValue, self._width, self._height)

    # function
    def getBounds(self):
        return (self._xValue, self._yValue, self._width, self._height)
    def setBounds(self, xValue, yValue, width, height):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self.update()
    bounds=property(getBounds, setBounds)

# todo: sync axes
# https://stackoverflow.com/questions/4999014/matplotlib-pyplot-how-to-zoom-subplots-together-and-x-scroll-separately
class TicksG(GraphObject):
    positionValues = ["left", "right", "top", "bottom"]
    xPosition = ["top", "bottom"]
    yPosition = ["left", "right"]
    
    def __init__(self, canvas, position, ticks=[], ticksLabel=[], figure=None, axis=None, visible=True):
        if position not in TicksG.positionValues:
            raise ValueError("position [%s] must be one of %s" %
                             (position, TicksG.positionValues))
        self._position=position
        self._ticks=ticks
        self._ticksLabel=ticksLabel
        if axis == None:
            self._axis=canvas.axes
        else:
            self._axis=axis
        if figure == None:
            self._figure=canvas.figure
        else:
            self._figure=figure
     
        super().__init__(canvas, visible)

    def _initilizePlot(self):
        return self.__plot(self._figure, self._axis)

    def __plot(self, figure, axis):
        if self._position == "left":
            artist=figure.add_axes(axis.get_position(True),sharex=axis,label=str(random.getrandbits(128)))
            #artist.update_from(self._canvas.axes)
            #artist.set_aspect(self._canvas.axes.get_aspect())
            artist.yaxis.tick_left()
            artist.yaxis.set_label_position('left')
            artist.yaxis.set_offset_position('left')
            artist.set_autoscalex_on(axis.get_autoscalex_on())
            artist.xaxis.set_visible(False)
            artist.set_yticks(self._ticks)
            artist.set_yticklabels(self._ticksLabel)
        elif self._position == "right":
            artist=figure.add_axes(axis.get_position(True),sharex=axis,label=str(random.getrandbits(128)))
            #artist.update_from(self._canvas.axes)
            #artist.set_aspect(self._canvas.axes.get_aspect())
            artist.yaxis.tick_right()
            artist.yaxis.set_label_position('right')
            artist.yaxis.set_offset_position('right')
            artist.set_autoscalex_on(axis.get_autoscalex_on())
            artist.xaxis.set_visible(False)
            artist.set_yticks(self._ticks)
            artist.set_yticklabels(self._ticksLabel)
        elif self._position == "top":
            artist=figure.add_axes(axis.get_position(True),sharey=axis,label=str(random.getrandbits(128)))
            #artist.update_from(self._canvas.axes)
            #artist.set_aspect(self._canvas.axes.get_aspect())
            artist.xaxis.tick_top()
            artist.xaxis.set_label_position('top')
            #artist.xaxis.set_offset_position('top')
            artist.set_autoscaley_on(axis.get_autoscaley_on())
            artist.yaxis.set_visible(False)
            artist.set_xticks(self._ticks)
            artist.set_xticklabels(self._ticksLabel)
        elif self._position == "bottom":
            artist=figure.add_axes(axis.get_position(True),sharey=axis,label=str(random.getrandbits(128)))
            #artist.update_from(self._canvas.axes)
            #artist.set_aspect(self._canvas.axes.get_aspect())
            artist.xaxis.tick_bottom()
            artist.xaxis.set_label_position('bottom')
            #artist.xaxis.set_offset_position('bottom')
            artist.set_autoscaley_on(axis.get_autoscaley_on())
            artist.yaxis.set_visible(False)
            artist.set_xticks(self._ticks)
            artist.set_xticklabels(self._ticksLabel)

        artist.patch.set_visible(False)
        return artist
    
    def draw(self, figure, axis):
        if self.isShowed():
            return self.__plot(figure, axis)
        else:
            return None
    
    def _updatePlot(self,curve):
        if self._position in TicksG.xPosition:
            xLimit=curve.get_xlim()
            curve.set_xticks(self._ticks)
            curve.set_xticklabels(self._ticksLabel)
            curve.set_xlim(*xLimit)
        elif self._position in TicksG.yPosition:
            yLimit=curve.get_ylim()
            curve.set_yticks(self._ticks)
            curve.set_yticklabels(self._ticksLabel)
            curve.set_ylim(*yLimit)
    
    def setTicks(self, ticks):
        self._ticks=ticks
        self.update()
        
    def setTicksLabel(self, ticksLabel):
        self._ticksLabel=ticksLabel
        self.update()
        
