'''
Created on 2017/9/3

@author: dsou
'''

from Plot.GraphObject import GraphObject
import random

# todo: sync axes
# https://stackoverflow.com/questions/4999014/matplotlib-pyplot-how-to-zoom-subplots-together-and-x-scroll-separately
class Ticks(GraphObject):
    positionValues = ["left", "right", "top", "bottom"]
    xPosition = ["top", "bottom"]
    yPosition = ["left", "right"]
    
    def __init__(self, canvas, position, ticks=[], ticksLabel=[], figure=None, axis=None, visible=True):
        if position not in Ticks.positionValues:
            raise ValueError("position [%s] must be one of %s" %
                             (position, Ticks.positionValues))
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
        if self._position in Ticks.xPosition:
            xLimit=curve.get_xlim()
            curve.set_xticks(self._ticks)
            curve.set_xticklabels(self._ticksLabel)
            curve.set_xlim(*xLimit)
        elif self._position in Ticks.yPosition:
            yLimit=curve.get_ylim()
            curve.set_yticks(self._ticks)
            curve.set_yticklabels(self._ticksLabel)
            curve.set_ylim(*yLimit)
    
    def getTicks(self):
        return self._ticks
    def setTicks(self, ticks):
        self._ticks=ticks
        self.update()
    ticks=property(
        lambda self: self.getTicks(), 
        lambda self, *args: self.setTicks(*args)
        )
        
    def getTicksLabel(self):
        return self._ticksLabel
    def setTicksLabel(self, ticksLabel):
        self._ticksLabel=ticksLabel
        self.update()
    ticksLabel=property(
        lambda self: self.getTicksLabel(), 
        lambda self, *args: self.setTicksLabel(*args)
        )
        