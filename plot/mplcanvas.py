'''
Renormalization Plot - plot/mplcanvas.py
    A wrapper for matplotlib canvas

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

from PyQt5 import QtCore

# Matplotlib library
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from plot.canvasbase import CanvasBase

class MPLCanvas(FigureCanvas,CanvasBase):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    __axesList=[]

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.__axesList=[self.axes]

        self.compute_initial_figure()

        FigureCanvas.__init__(self,self.fig)
        CanvasBase.__init__(self, parent=None)
        self.setParent(parent)
        #self._updatePlot=False

        #super().setSizePolicy(QtWidgets.QSizePolicy.Expanding,
        #                           QtWidgets.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)
        #self.setMinimumSize(0, 0)
        self._plotDirty=False

    def compute_initial_figure(self):
        pass
    
    @QtCore.pyqtSlot()
    def update(self):
        if self._plotDirty == True:
            if self.updatesEnabled() == True:
                FigureCanvas.draw_idle(self)
                self._plotDirty=False
        FigureCanvas.update(self)
    
    @QtCore.pyqtSlot()
    def updatePlot(self):
        if self.updatesEnabled() == True:
            FigureCanvas.draw_idle(self)
        else:
            self._plotDirty=True
    
    @QtCore.pyqtSlot(bool)
    def setUpdatesEnabled(self, enable):
        if enable == False:
            #self._updateDirty=False
            pass
        elif enable == True:
            if self._plotDirty == True:
                FigureCanvas.draw_idle(self)
                self._plotDirty=False
        FigureCanvas.setUpdatesEnabled(self, enable)
   
    __axesOptions={}
    def setAxesOptions(self,**kwargs):
        self.__axesOptions.update(kwargs)
        for axes in self.__axesList:
            axes.set(**kwargs)
    def getAxesOptions(self):
        return self.__axesOptions
    axesOptions=property(
        lambda self: self.getAxesOptions(), 
        lambda self, **kwargs: self.setAxesOptions(**kwargs)
        )
    
    def addAxes(self, axes):
        axes.set(**self.axesOptions)
        self.__axesList.append(axes)
    
    def removeAxes(self, axes):
        self.__axesList.remove(axes)
        
    def getCanvas(self):
        return self
    
    __showXTicks=True
    @QtCore.pyqtSlot(bool)
    def setShowXTicks(self,show):
        self.__showXTicks=show
        self.axes.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=show,      # ticks along the bottom edge are off
            labelbottom=show
            )
        self.update()
    def getShowXTicks(self):
        return self.__showXTicks
    showXTicks=property(
        lambda self: self.getShowXTicks(), 
        lambda self, show: self.setShowXTicks(show)
        )

    __showYTicks=True
    @QtCore.pyqtSlot(bool)
    def setShowYTicks(self,show):
        self.__showYTicks=show
        self.axes.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=show,      # ticks along the bottom edge are off
            labelleft=show
            )
        self.update()
    def getShowYTicks(self):
        return self.__showYTicks
    showYTicks=property(
        lambda self: self.getShowYTicks(), 
        lambda self, show: self.setShowYTicks(show)
        )
