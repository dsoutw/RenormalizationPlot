'''
Created on 2017/9/3

@author: dsou
'''

from .artist import ArtistBase
import random
import logging

# todo: sync axes
# https://stackoverflow.com/questions/4999014/matplotlib-pyplot-how-to-zoom-subplots-together-and-x-scroll-separately
class Ticks(ArtistBase):
    positionValues = ["left", "right", "top", "bottom"]
    xPosition = ["top", "bottom"]
    yPosition = ["left", "right"]
    
    def __init__(self, position, ticks=[], ticksLabel=[], logger=None, **kwargs):
        if logger is None:
            logger=logging.getLogger(__name__)

        if position not in Ticks.positionValues:
            raise ValueError("position [%s] must be one of %s" %
                             (position, Ticks.positionValues))
        self._position=position
        self._ticks=ticks
        self._ticksLabel=ticksLabel
     
        super().__init__(logger=logger, **kwargs)

    def _initilizePlot(self):
        artist = self.__plot(self.canvas.figure, self.canvas.axes)
        artist.__ticksCanvas=self.canvas
        self.canvas.addAxes(artist)
        return artist

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
    
    def _updatePlot(self,artist):
        if self._position in Ticks.xPosition:
            xLimit=artist.get_xlim()
            artist.set_xticks(self._ticks)
            artist.set_xticklabels(self._ticksLabel)
            artist.set_xlim(*xLimit)
        elif self._position in Ticks.yPosition:
            yLimit=artist.get_ylim()
            artist.set_yticks(self._ticks)
            artist.set_yticklabels(self._ticksLabel)
            artist.set_ylim(*yLimit)
        return artist
    
    def _clearPlot(self):
        try:
            self.artist.__ticksCanvas.removeAxes(self.artist)
        except:
            self._logger.exception('Unable to remove axes from canvas')
        super()._clearPlot()

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
        