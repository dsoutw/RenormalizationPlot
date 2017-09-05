from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need

import PlotWindowUI # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
import Plot
# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl
    
import Setting
        
class PlotWindow(QtWidgets.QMainWindow, PlotWindowUI.Ui_plotWindow):
    __level:int=None
    __rParent:'PlotWindow'=None
    __period:int=2
    __renormalizable:bool=None
    
    # Arguments
    # func: unimodal class
    # level: the level of renormalization
    # rParent: a unimodal map for the previous level
    def __init__(self, renormalizable:bool=False, level:int = 0, rParent:'PlotWindow' = None):
        #func: Unimodal
        #level: nonnegative integer
        self.__level=level
        self.__rParent=rParent
        self.__period=2

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
        self.periodSpinBox.setValue(self.__period)
        self.selfReturnCheckBox.setChecked(Setting.figureSelfReturn)
        self.periodSpinBox.valueChanged.connect(self.setPeriod)
        self._rChild=None
        self.renormalizeButton.clicked.connect(self.openRChild)
        self.canvas.setMinimumSize(0,0)

        # Apply settings
        self.secondIterateCheckBox.setChecked(Setting.figureSecondIterate)
        self.iteratedGraphCheckBox.setChecked(Setting.figureMultipleIterate)
        self.diagonalCheckBox.setChecked(Setting.figureDiagonal)
        self.beta0CheckBox.setChecked(Setting.figureBeta0)

        # update renormalizable
        #self._updateRenormalizable()
        self.__renormalizable=renormalizable
        self.renormalizableChanged.connect(self.__setRenormalizableText)
        self.renormalizableChanged.connect(self.renormalizeButton.setEnabled)
        self.renormalizableChanged.connect(self.selfReturnLabel.setEnabled)
        self.renormalizableChanged.connect(self.selfReturnCheckBox.setEnabled)
        self.renormalizableChanged.emit(renormalizable)
        
        # setup level grapgs
        self.levelBox.setEnabled(False)
        
        self.updatePlot()


    def __setRenormalizableText(self,value:bool):
        text={True:"Yes",False:"No"} 
        self.renormalizableResultLabel.setText(text[value])

    def closeEvent(self, evnt):
    # inherited from QtWidgets.QMainWindow
    # close child renormalization when the window is closed
        if self.__rParent is not None:
            self.__rParent._rChildClosed()
        self.closeRChild()
        super().closeEvent(evnt)


    '''
    Properties
    '''
    
    @QtCore.pyqtSlot(int)
    def setPeriod(self, period:int):
        if period != self.__period:
            self.__period=period
            self.periodSpinBox.setValue(period)
            self._updatePeriod()
    def getPeriod(self)->int:
        return self.__period
    period=property(
        lambda self: self.getPeriod(), 
        lambda self, func: self.setPeriod(func)
        )

    @QtCore.pyqtSlot(int)
    def setLevel(self, level:int):
        self.__level=level
    def getLevel(self)->int:
        return self.__level
    level=property(
        lambda self: self.getLevel(), 
        lambda self, level: self.setLevel(level)
        )


    renormalizableChanged = QtCore.pyqtSignal(bool)
    @QtCore.pyqtSlot(bool)
    def setRenormalizable(self, value:bool):
        if self.__renormalizable!=value:
            if self.renormalizableChangedEvent(value)!=False:
                self.__renormalizable=value
                self.renormalizableChanged.emit(value)
    def getRenormalizable(self)->bool:
        return self.__renormalizable
    renormalizable=property(
        lambda self: self.getRenormalizable(), 
        lambda self, value: self.setRenormalizable(value)
        )
    def renormalizableChangedEvent(self,value:bool):
        return True
    
        
#     def _renormalizable(self, period:int):
#         raise NotImplementedError("PlotWindow._renormalizable")
# 
#     # update status of renormlaizable
#     def _updateRenormalizable(self):
#         if self._renormalizable(self.period) == True:
#             self.renormalizableResultLabel.setText("Yes")
#             self.renormalizeButton.setEnabled(True)
#             self.selfReturnLabel.setEnabled(True)
#             self.selfReturnCheckBox.setEnabled(True)
# 
#             self._plotRenormalizableGraph(self.period)
#             if self._rChild != None:
#                 if self._updateRChildEvent(self._rChild, self.period)==True:
#                     # plot sub-structures if possible
#                     self._updateRChildGraph()
#                 else:
#                     self._removeRChildGraph()
#                     self.closeRChild()
#         else:
#             self.renormalizableResultLabel.setText("No")
#             self.renormalizeButton.setEnabled(False)
#             self.selfReturnLabel.setEnabled(False)
#             self.selfReturnCheckBox.setEnabled(False)
#             
#             self._removeRenormalizableGraph()
#             self._removeRChildGraph()
#             self.closeRChild()

    # Stores the child window 
    _rChild:'PlotWindow'=None

    def _newRChildEvent(self, period:int)->'PlotWindow':
        '''
        Create a renormalized function window
        :param period: The period of renormalization
        :type period: int
        @return: The new window. Return Null if false
        @type return: PlotWindow
        '''
        raise NotImplementedError("PlotWindow._renormalizable")

    def _updateRChildEvent(self, period:int):
        '''
        Update the renormalized function window
        Called when the renormalized function is modified
        :param period: The period of renormalization
        :type period: int
        '''
        raise NotImplementedError("PlotWindow._renormalizable")
    
    def openRChild(self):
    # open child renormalization window
        # create window if not exist then renormalize
        if self._rChild == None:
            self._rChild =self._newRChildEvent(self.__period)
            if self._rChild == None:
                return

            self.levelBox.setEnabled(True)
            self.openWindow(self._rChild)
            
            self._findPeriodicInterval()
            self._plotRChildGraph()
            
            # Notify the ancestors that the unimodal map is renormalized
            level=2
            ancestor=self.__rParent
            while ancestor is not None:
                ancestor._descendantRenormalized(level,self._rChild)
                ancestor=ancestor.__rParent
                level=level+1
        else:
            self.focusWindow(self._rChild)

    def updateRChild(self):
        if self._rChild != None:
            if self.renormalizable:
                self._updateRChildEvent(self.period)
            else:
                self.closeRChild()
        
    def closeRChild(self):
    # close child renormalization window
        if self._rChild != None:
            self.closeWindow(self._rChild)
            #self._rChildClosed()

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
    def openWindow(self, widget:'PlotWindow'):
        widget.show()

    def focusWindow(self, widget:'PlotWindow'):
        widget.show()
        widget.activateWindow()
        widget.raise_()

    def closeWindow(self, widget:'PlotWindow'):
        widget.close()


    '''
    Plot Utilities
    '''
    def updatePlot(self):
        self.canvas.setUpdatesEnabled(False)
        self._updateCurrentLevel()
        self._updateRenormalizableGraph()
        self._updateRChildGraph()
        self.canvas.setUpdatesEnabled(True)

    def updateRenormalizablePlot(self):
        self.canvas.setUpdatesEnabled(False)
        self._updateRenormalizableGraph()
        self._updateRChildGraph()
        self.canvas.setUpdatesEnabled(True)

    '''
    Plot current level
    '''
    
    def _plotCurrentLevel(self):
        self._plotCurrentLevelGraphs()
        self._plotCurrentLevelOrbits()
        self._plotPeriod()

    def _updateCurrentLevel(self):
        self._updateCurrentLevelGraphs()
        self._updateCurrentLevelOrbits()
        self._updatePeriod()

    '''
    Plot current level graphs
    '''
        
    def _plotCurrentLevelGraphs(self):
        # Plot function
        self._plotFunction()
        
        # Plot second iterate
        gFunctionSecond=self._plotFunctionSecond(visible=self.secondIterateCheckBox.isChecked())
        self.secondIterateCheckBox.toggled.connect(gFunctionSecond.setVisible)
        
        # Draw diagonal line
        gDiagonal = self._plotDiagonal(visible=self.diagonalCheckBox.isChecked())
        self.diagonalCheckBox.toggled.connect(gDiagonal.setVisible)
        
    def _updateCurrentLevelGraphs(self):
        self._updateFunction()
        self._updateFunctionSecond()
    
    def _plotFunction(self)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotFunction")
    def _updateFunction(self):
        raise NotImplementedError("PlotWindow._updateFunction")

    def _plotFunctionSecond(self)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotFunctionSecond")
    def _updateFunctionSecond(self):
        raise NotImplementedError("PlotWindow._updateFunctionSecond")

    def _plotDiagonal(self)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotDiagonal")


    '''
    Plot Current Level Orbits
    '''
   
    def _plotCurrentLevelOrbits(self):
        self._plotAlpha0()

        # Plot the beta orbits
        gBeta0=self._plotBeta0(visible=self.beta0CheckBox.isChecked())
        self.beta0CheckBox.toggled.connect(gBeta0.setVisible)

    def _updateCurrentLevelOrbits(self):
        self._updateAlpha0()
        self._updateBeta0()

    def _plotAlpha0(self)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotAlpha0")
    def _updateAlpha0(self):
        raise NotImplementedError("PlotWindow._updateAlpha0")

    def _plotBeta0(self)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotBeta0")
    def _updateBeta0(self):
        raise NotImplementedError("PlotWindow._updateBeta0")

    '''
    Plot current level period plots
    '''

    def _plotPeriod(self):
        # Plot multiple iterate
        gFunctionIterates = self._plotFunctionIterates(visible=self.iteratedGraphCheckBox.isChecked())
        self.iteratedGraphCheckBox.toggled.connect(gFunctionIterates.setVisible)
        
    def _updatePeriod(self):
        self._updateFunctionIterates()

    def _plotFunctionIterates(self)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotFunctionIterates")
    def _updateFunctionIterates(self):
        raise NotImplementedError("PlotWindow._updateFunctionIterates")
    
    '''
    Plot Renormalizable Objects
    '''
    __isSelfReturnIntervalsPlotted=False
    __selfReturnIntervalsSlot=None
    def _plotRenormalizableGraph(self):
        if self.__isSelfReturnIntervalsPlotted == False:
            # Plot the intervals that defines the self-return map 
            gSelfReturnIntervals=self._plotSelfReturnIntervals(self.period,visible=self.selfReturnCheckBox.isChecked())
            self.__selfReturnIntervalsSlot=gSelfReturnIntervals.setVisible
            self.selfReturnCheckBox.toggled.connect(self.__selfReturnIntervalsSlot)
            self.__isSelfReturnIntervalsPlotted=True
        else:
            self._updateSelfReturnIntervals(self.period)

    def _updateRenormalizableGraph(self):
        if self.renormalizable:
            self._plotRenormalizableGraph()
        else:
            self._removeRenormalizableGraph()

    def _removeRenormalizableGraph(self):
        if self.__isSelfReturnIntervalsPlotted == True:
            try:
                self.selfReturnCheckBox.toggled.disconnect(self.__selfReturnIntervalsSlot)
            except:
                pass
            self.__selfReturnIntervalsSlot=None
            self._removeSelfReturnIntervals()
            self.__isSelfReturnIntervalsPlotted = False
    
    def _plotSelfReturnIntervals(self,period)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotSelfReturnIntervals")
    def _updateSelfReturnIntervals(self,period):
        raise NotImplementedError("PlotWindow._updateSelfReturnIntervals")
    def _removeSelfReturnIntervals(self):
        raise NotImplementedError("PlotWindow._removeSelfReturnIntervals")
    

    '''
    Plot RChild objects
    '''
    def _plotRChildGraph(self):
        self._plotNextLevelOrbits()
        self._plotDeepLevelOrbits()

    def _updateRChildGraph(self):
        if self._rChild != None:
            self._updateNextLevelOrbits()
            self._updateDeepLevelOrbits()
        else:
            self._removeRChildGraph()

    def _removeRChildGraph(self):
        self._removeNextLevelOrbits()
        self._removeDeepLevelOrbits()
        
    ''' Next Level Orbits '''
    # plot orbits obtained from next level
    _isNextLevelOrbitsPlotted=False
    _level1Slot=None
    def _plotNextLevelOrbits(self):
        if self._isNextLevelOrbitsPlotted==False:
            gAlpha1=self._plotAlpha1(visible=self.alpha1CheckBox.isChecked())
            self.alpha1CheckBox.toggled.connect(gAlpha1.setVisible)

            gBeta1=self._plotBeta1(visible=self.beta1CheckBox.isChecked())
            self.beta1CheckBox.toggled.connect(gBeta1.setVisible)
    
            gLevel1=Plot.Group([self.gAlpha1,self.f_bB1List],visible=self.partitionButton.isChecked())
            self._level1Slot=gLevel1.setVisible
            self.partitionButton.toggled.connect(self._level1Slot)
            
            self._isNextLevelOrbitsPlotted=True
        else:
            self._updateAlpha1()
            self._updateBeta1()

    def _updateNextLevelOrbits(self):
        if self.renormalizable:
            self._plotNextLevelOrbits()
        else:
            self._removeNextLevelOrbits()

    def _removeNextLevelOrbits(self):
        if self._isNextLevelOrbitsPlotted==True:
            # clear sub-structures
            try:
                self.alpha1CheckBox.toggled.disconnect()
            except:
                pass
            try:
                self.beta1CheckBox.toggled.disconnect()
            except:
                pass
            try:
                self.partitionButton.toggled.disconnect(self._level1Slot)
            except:
                pass
            self._level1Slot=None
            self._removeAlpha1()
            self._removeBeta1()
            self._isNextLevelOrbitsPlotted=False
            
    def _plotAlpha1(self,visible:bool=True)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotAlpha1")
    def _updateAlpha1(self):
        raise NotImplementedError("PlotWindow._updateAlpha1")
    def _removeAlpha1(self):
        raise NotImplementedError("PlotWindow._removeAlpha1")

    def _plotBeta1(self,visible:bool=True)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotBeta1")
    def _updateBeta1(self):
        raise NotImplementedError("PlotWindow._updateBeta1")
    def _removeBeta1(self):
        raise NotImplementedError("PlotWindow._removeBeta1")

