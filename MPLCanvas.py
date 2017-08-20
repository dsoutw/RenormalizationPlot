from PyQt5 import QtCore

# Matplotlib library
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MPLCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, rParent=None, width=4, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self,self.fig)
        self.setParent(rParent)
        #self._updatePlot=False

        #super().setSizePolicy(QtWidgets.QSizePolicy.Expanding,
        #                           QtWidgets.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)
        #self.setMinimumSize(0, 0)
        self._updateDirty=False

    def compute_initial_figure(self):
        pass
    
#    def updatePlot(self):
#        #self._updatePlot=True
#        #self.update()
#        self.draw_idle()
#        pass

    @QtCore.pyqtSlot()
    def update(self):
        if self.updatesEnabled() == True:
            FigureCanvas.draw_idle(self)
        else:
            self._updateDirty=True
            
        FigureCanvas.update(self)
    
    @QtCore.pyqtSlot(bool)
    def setUpdatesEnabled(self, enable):
        if enable == False:
            #self._updateDirty=False
            pass
        elif enable == True:
            if self._updateDirty == True:
                FigureCanvas.draw_idle(self)
                self._updateDirty = False
        FigureCanvas.setUpdatesEnabled(self, enable)
        
    #@QtCore.pyqtSlot(int, int, int, int)
    #def update(self, x, y, w, h):
    #    FigureCanvas.update(self, x, y, w, h)
        
    #def paintEvent(self, e):
    #    if self._updatePlot == True:
    #        self.draw()
    #        self._updatePlot=False
    #    return FigureCanvas.paintEvent(self, e)