'''
Created on 2017/9/4

@author: dsou
'''
from matplotlib.artist import Artist as MPLArtist
import numpy as np
from plot.graphobject import GraphObject
from plot.canvasbase import CanvasBase
from PyQt5 import QtCore
import typing as tp
import logging
from abc import ABCMeta,abstractmethod

class ArtistBase(GraphObject,QtCore.QObject):
    '''
    An abstract container for matplotlib artist
    '''
    __metaclass__=ABCMeta
    __canvas:tp.Optional[CanvasBase]=None
    __artist=None
    __updateDirty=False
    
    def __init__(self, logger=None, **kwargs):
        '''
        An abstract container for matplotlib artist
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        GraphObject.__init__(self, logger=logger, **kwargs)
        QtCore.QObject.__init__(self, self.canvas)

    @abstractmethod
    def _initilizePlot(self)->MPLArtist:
        '''
        Create the plot. Implimented by the child
        This is called when a new artist is requested
        The function returns the new MPL artist ploted on the canvas
        @return: The new MPL artist
        '''
        raise NotImplementedError("GraphObject._initilize has to be implemented")
        pass

    @abstractmethod
    def _updatePlot(self, artist:MPLArtist)->MPLArtist:
        '''
        Update the plot. Implimented by the child
        This is called when the artist needs to be updated
        The child updates the input MPL artist and returns the updated MPL artist
        The input and output can be the same
        :param artist: The original MPL artist
        :type artist: matplotlib.artist
        @return: The updated MPL artist
        '''
        raise NotImplementedError("GraphObject._updatePlot has to be implemented")
        pass

    def _clearPlot(self):
        '''
        Clear the plot.
        The default behavior is to call artist.remove
        Override this method if want to change the default behavior
        :param artist: The artist to be clear
        :type artist: matplotlib.artist
        '''
        if self.__artist is not None:
            if not isinstance(self.__artist, list):
                artistList=[self.__artist]
            else:
                artistList=self.__artist
    
            for element in artistList:
                try:
                    element.remove()
                except:
                    self._logger.exception('Unable to remove artist: %s' % element)
            
            self.__artist=None

    @QtCore.pyqtSlot()
    def update(self):
        if self.canvas is not None:
            if self.isShowed() is True:
                if self.__artist is not None:
                    try:
                        self.__artist=self._updatePlot(self.__artist)
                        self.__updateDirty=False
                    except:
                        try:
                            self._clearPlot()
                        except Exception as e:
                            pass
                        raise RuntimeError('Unable to update plot: %s' % self.__artist) from e
                    finally:
                        self.canvas.update()
                else:
                    try:
                        self.__artist=self._initilizePlot()
                        self.__updateDirty=False
                    except Exception as e:
                        raise RuntimeError('Unable to initialize the plot') from e
            else:
                # Only update the contents when the plot is visible
                self.__updateDirty=True

    # visible
    def _setVisibleInternal(self,visible):
        if self.canvas is not None:
            if self.__artist is not None:
                if visible and self.__updateDirty:
                    # Update the plot before showing the contents
                    self.__artist=self._updatePlot(self.__artist)
                    self.__updateDirty=False
                
                if not isinstance(self.__artist, list):
                    artistList=[self.__artist]
                else:
                    artistList=self.__artist
                    
                for element in artistList:
                    try:
                        element.set_visible(visible)
                    except:
                        self._logger.exception('Unable to set visible: %s' % visible)
                
                self.canvas.update()
            elif visible is True:
                try:
                    self.__artist=self._initilizePlot()
                    self.__updateDirty=False
                except:
                    self._logger.exception('Unable to initialize the plot')
        
    # artist
    # useless?
    def getArtist(self)->tp.Union[MPLArtist,tp.List[MPLArtist]]:
        return self.__artist
    def setArtist(self, artist:tp.Union[MPLArtist,tp.List[MPLArtist]]):
        self.__artist=artist
    artist=property(
        lambda self: self.getArtist(), 
        lambda self, val: self.setArtist(val)
        )

            
    def canvasChangedEvent(self, oldCanvas, newCanvas):
        if (oldCanvas is not None) and (self.__artist is not None):
            try:
                self._clearPlot()
                oldCanvas.update()
            except:
                self._logger.exception('Unable to remove the plot from the old canvas')

        if (newCanvas is not None) and self.isShowed():
            try:
                self.__artist=self._initilizePlot()
                self.__updateDirty=False
            except:
                self._logger.exception('Unable to initialize the plot')
        else:
            self.__artist=None            
                        
        GraphObject.canvasChangedEvent(self, oldCanvas, newCanvas)
    
def generateSample(axis):
    l,r = axis.get_xlim()
    sample = np.append(np.arange(-1.0, l, 0.001), np.arange(l, r, (r-l)/1000.0))
    sample = np.append(sample, np.arange(r, 1.001, 0.001))
    return np.float64(sample)