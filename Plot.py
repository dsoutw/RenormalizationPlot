from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need

import PlotWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer

# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl
    
import Setting
        
class PlotWindow(QtWidgets.QMainWindow, PlotWindow.Ui_plotWindow):
    _level=None
    _rParent=None
    _period:int=2
    
    # Arguments
    # func: unimodal class
    # level: the level of renormalization
    # rParent: a unimodal map for the previous level
    def __init__(self, level:int = 0, rParent:PlotWindow = None):
        #func: Unimodal
        #level: nonnegative integer
        self._level=level
        self._rParent=rParent
        self._period=2

        super().__init__(rParent)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined

        # Adjust the size of the options to fit with the contents
        self.renormalizationScroll.setMinimumWidth(self.renormalizationContents.sizeHint().width() + self.renormalizationScroll.verticalScrollBar().sizeHint().width() )
        
        # setup the parent button    
        if rParent is not None:
            def showParent():
                self.focusWindow(rParent)
            self.parentButton.clicked.connect(showParent)
        else:
            self.parentButton.hide()

        # setup graph
        self.canvas.setParent(self.centralwidget)

        # Add graph toolbar
        self.mplToolbar = NavigationToolbar(self.canvas, self.centralwidget)
        self.addToolBar(self.mplToolbar)

        # Plot the initial graph
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0

        self.canvas.setUpdatesEnabled(False)
        self._plotCurrentLevel()
        self.canvas.setUpdatesEnabled(True)

        # setup renormalizable features
        self.periodSpinBox.setValue(self._period)
        self.selfReturnCheckBox.setChecked(Setting.figureSelfReturn)
        self.periodSpinBox.valueChanged.connect(self.setPeriod)
        self._rChild=None
        self.renormalizeButton.clicked.connect(self.openRChild)
        self.canvas.setMinimumSize(0,0)

        # update renormalizable
        self._updateRenormalizable()
        
        # setup level grapgs
        self.levelBox.setEnabled(False)

    # inherited from QtWidgets.QMainWindow
    # close child renormalization when the window is closed
    def closeEvent(self, evnt):
        #print("close event ", self._level)
        if self._rParent is not None:
            self._rParent._rChildClosed()
        self.closeRChild()
        super().closeEvent(evnt)
        
    # UI callbacks
    @QtCore.pyqtSlot(int)
    def setPeriod(self, period):
        if period != self._period:
            self._period=period
            self.periodSpinBox.setValue(period)
            self._updateRenormalizable()
    
    def getPeriod(self):
        return self._period
    
    period=property(setPeriod,getPeriod)
    
    def _renormalizable(self, period):
        raise NotImplementedError("PlotWindow._renormalizable")

    # update status of renormlaizable
    def _updateRenormalizable(self):
        if self._renormalizable(self._period) == True:
            self.renormalizableResultLabel.setText("Yes")
            self.renormalizeButton.setEnabled(True)
            self.selfReturnLabel.setEnabled(True)
            self.selfReturnCheckBox.setEnabled(True)

            self._plotRenormalizableGraph()
            if self._rChild != None:
                if self._updateRChild(self._rChild, self._period)==True:
                    # plot sub-structures if possible
                    self._updateRChildGraph()
                else:
                    self._removeRChildGraph()
                    self.closeRChild()
        else:
            self.renormalizableResultLabel.setText("No")
            self.renormalizeButton.setEnabled(False)
            self.selfReturnLabel.setEnabled(False)
            self.selfReturnCheckBox.setEnabled(False)
            
            self._removeRenormalizableGraph()
            self._removeRChildGraph()
            self.closeRChild()

    # variables for renormalization
    
    # Stores the child window 
    _rChild=None

    def _newRChild(self, period):
        raise NotImplementedError("PlotWindow._renormalizable")

    def _updateRChild(self, period):
        raise NotImplementedError("PlotWindow._renormalizable")
    
    # open child renormalization window
    def openRChild(self):
        # create window if not exist then renormalize
        if self._rChild == None:
            self._rChild =self._newRChild(self._period)
            if self._rChild == None:
                return

            self.levelBox.setEnabled(True)
            self.openWindow(self._rChild)
            
            self._findPeriodicInterval()
            self._plotRChildGraph()
            
            # Notify the ancestors that the unimodal map is renormalized
            level=2
            ancestor=self._rParent
            while ancestor is not None:
                ancestor._descendantRenormalized(level,self._rChild)
                ancestor=ancestor._rParent
                level=level+1
        else:
            self.focusWindow(self._rChild)

        
    # close child renormalization window
    def closeRChild(self):
        if self._rChild != None:
            self.closeWindow(self._rChild)
            self._rChildClosed()

    # called when the child is closed.
    #isThisClosed=False
    def _rChildClosed(self):
        if self._rChild != None:
            self._removeNextLevelOrbits()
            self._removeDeepLevelOrbits()
    
            self.levelBox.setEnabled(False)
            self._rChild=None


    # window utilities
    # modify this method if created by mdi window
    def openWindow(self, widget):
        widget.show()

    def focusWindow(self, widget):
        widget.show()
        widget.activateWindow()
        widget.raise_()

    def closeWindow(self, widget):
        widget.close()

