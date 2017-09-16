from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need

import PlotWindowUI # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
import Plot
# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl
from abc import ABCMeta,abstractmethod

import Setting
        
class PlotWindow(QtWidgets.QMainWindow, PlotWindowUI.Ui_plotWindow):
    __metaclass__=ABCMeta
    __level:int=None
    __rParent:'PlotWindow'=None
    __period:int=2
    __renormalizable:bool=None
    
    # Arguments
    # func: unimodal class
    # level: the level of renormalization
    # rParent: a unimodal map for the previous level
    def __init__(self, level:int = 0, rParent:'PlotWindow' = None, renormalizable:bool=False):
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
        self.__plotCurrentLevel()
        self.canvas.setUpdatesEnabled(True)

        # setup renormalizable features
        self.periodSpinBox.setValue(self.__period)
        self.selfReturnCheckBox.setChecked(Setting.figureSelfReturn)
        self.orderCheckBox.setChecked(Setting.figureSelfReturn)
        self.periodSpinBox.valueChanged.connect(self.setPeriod)
        self.__rChild=None
        self.renormalizeButton.clicked.connect(self.openRChild)
        self.canvas.setMinimumSize(0,0)

        # Apply settings
        self.secondIterateCheckBox.setChecked(Setting.figureSecondIterate)
        self.iteratedGraphCheckBox.setChecked(Setting.figureMultipleIterate)
        self.diagonalCheckBox.setChecked(Setting.figureDiagonal)
        self.beta0CheckBox.setChecked(Setting.figureBeta0)
        self.alpha1CheckBox.setChecked(Setting.figureAlpha1)
        self.beta1CheckBox.setChecked(Setting.figureBeta1)

        # update renormalizable
        #self._updateRenormalizable()
        self.__renormalizable=renormalizable
        self.renormalizableChanged.connect(self.__setRenormalizableText)
        self.renormalizableChanged.connect(self.renormalizeButton.setEnabled)
        self.renormalizableChanged.connect(self.selfReturnLabel.setEnabled)
        self.renormalizableChanged.connect(self.selfReturnCheckBox.setEnabled)
        self.renormalizableChanged.connect(self.orderLabel.setEnabled)
        self.renormalizableChanged.connect(self.orderCheckBox.setEnabled)
        self.renormalizableChanged.emit(renormalizable)
        
        # setup level grapgs
        self.levelBox.setEnabled(False)
        

    def __setRenormalizableText(self,value:bool):
        text={True:"Yes",False:"No"} 
        self.renormalizableResultLabel.setText(text[value])

    def closeEvent(self, evnt):
    # inherited from QtWidgets.QMainWindow
    # close child renormalization when the window is closed
        if self.__rParent is not None:
            self.__rParent.__rChildClosed()
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
            self.__updatePeriod()
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
    
    '''
    Child window
    '''
    
    # Stores the child window 
    __rChild:'PlotWindow'=None

    @abstractmethod
    def _newRChildEvent(self, period:int)->'PlotWindow':
        '''
        Create a renormalized function window
        :param period: The period of renormalization
        :type period: int
        @return: The new window. Return Null if false
        @type return: PlotWindow
        '''
        raise NotImplementedError("PlotWindow._renormalizable")

    @abstractmethod
    def _updateRChildEvent(self, rChild:'PlotWindow', period:int):
        '''
        Update the renormalized function window
        Called when the renormalized function is modified
        :param period: The period of renormalization
        :type period: int
        @return: True if success, False=close child
        '''
        raise NotImplementedError("PlotWindow._renormalizable")

    @abstractmethod
    def _closeRChildEvent(self):
        '''
        Update the renormalized function window
        Called when the renormalized function is modified
        :param period: The period of renormalization
        :type period: int
        '''
        raise NotImplementedError("PlotWindow._renormalizable")
    
    @abstractmethod
    def _descendantRenormalizedEvent(self):
        raise NotImplementedError("PlotWindow._renormalizable")
    
    def openRChild(self):
    # open child renormalization window
        # create window if not exist then renormalize
        if self.__rChild == None:
            self.__rChild =self._newRChildEvent(self.__period)
            if self.__rChild == None:
                return

            self.levelBox.setEnabled(True)
            self.openWindow(self.__rChild)
            self.__plotRChildGraph()
            
            #self.__plotRChildGraph()
            
            # Notify the ancestors that the unimodal map is renormalized
            level=2
            ancestor=self.__rParent
            while ancestor is not None:
                ancestor._descendantRenormalizedEvent(level,self.__rChild)
                ancestor=ancestor.__rParent
                level=level+1
        else:
            self.focusWindow(self.__rChild)

    def updateRChild(self):
        if self.__rChild != None:
            if self.renormalizable:
                if self._updateRChildEvent(self.__rChild,self.period):
                    return
            self.closeRChild()
        
    def closeRChild(self):
    # close child renormalization window
        if self.__rChild != None:
            self.closeWindow(self.__rChild)
            #self.__rChildClosed()

    # called when the child is closed.
    #isThisClosed=False
    def __rChildClosed(self):
        if self.__rChild != None:
            self._closeRChildEvent()
            self.__removeNextLevelOrbits()
            self.__removeDeepLevelOrbits()
    
            self.levelBox.setEnabled(False)
            self.__rChild=None


    def getRChild(self):
        return self.__rChild
    rChild=property(lambda self: self.getRChild())
    
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
        self.__updateCurrentLevel()
        self.__updateRenormalizableGraph()
        self.__updateRChildGraph()
        self.canvas.setUpdatesEnabled(True)

    def updateRenormalizablePlot(self):
        self.canvas.setUpdatesEnabled(False)
        self.__updateRenormalizableGraph()
        self.__updateRChildGraph()
        self.canvas.setUpdatesEnabled(True)

    def updateRescalingLevelPlot(self):
        self.canvas.setUpdatesEnabled(False)
        self._updateRescalingLevels()
        self.canvas.setUpdatesEnabled(True)

    '''
    Plot current level
    '''
    
    def __plotCurrentLevel(self):
        self.__plotCurrentLevelGraphs()
        self.__plotCurrentLevelOrbits()
        self.__plotPeriod()

    def __updateCurrentLevel(self):
        self.__updateCurrentLevelGraphs()
        self.__updateCurrentLevelOrbits()
        self.__updatePeriod()

    '''
    Plot current level graphs
    '''
        
    def __plotCurrentLevelGraphs(self):
        # Plot function
        self._plotFunction()
        
        # Plot second iterate
        gFunctionSecond=self._plotFunctionSecond(visible=self.secondIterateCheckBox.isChecked())
        self.secondIterateCheckBox.toggled.connect(gFunctionSecond.setVisible)
        
        # Draw diagonal line
        gDiagonal = self._plotDiagonal(visible=self.diagonalCheckBox.isChecked())
        self.diagonalCheckBox.toggled.connect(gDiagonal.setVisible)
        
    def __updateCurrentLevelGraphs(self):
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
   
    def __plotCurrentLevelOrbits(self):
        self._plotAlpha0()

        # Plot the beta orbits
        gBeta0=self._plotBeta0(visible=self.beta0CheckBox.isChecked())
        self.beta0CheckBox.toggled.connect(gBeta0.setVisible)

    def __updateCurrentLevelOrbits(self):
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

    def __plotPeriod(self):
        # Plot multiple iterate
        gFunctionIterates = self._plotFunctionIterates(self.period,visible=self.iteratedGraphCheckBox.isChecked())
        self.iteratedGraphCheckBox.toggled.connect(gFunctionIterates.setVisible)
        
    def __updatePeriod(self):
        self._updateFunctionIterates(self.period)

    def _plotFunctionIterates(self,period:int,visible:bool=True)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotFunctionIterates")
    def _updateFunctionIterates(self,period:int):
        raise NotImplementedError("PlotWindow._updateFunctionIterates")
    
    '''
    Plot Renormalizable Objects
    '''
    
    __isSelfReturnIntervalsPlotted=False
    __selfReturnIntervalsSlot=None
    __selfReturnOrderSlot=None
    def __plotRenormalizableGraph(self):
        if self.__isSelfReturnIntervalsPlotted == False:
            # Plot the intervals that defines the self-return map 
            gSelfReturnIntervals=self._plotSelfReturnIntervals(self.period,visible=True)
            gSelfReturnOrder=self._plotSelfReturnOrder(self.period,visible=self.orderCheckBox.isChecked())
            gSelfReturn=Plot.Group([gSelfReturnIntervals,gSelfReturnOrder],visible=self.selfReturnCheckBox.isChecked(),parent=self.canvas)
            self.__selfReturnOrderSlot=gSelfReturnOrder.setVisible
            self.__selfReturnIntervalsSlot=gSelfReturn.setVisible
            self.orderCheckBox.toggled.connect(self.__selfReturnOrderSlot)
            self.selfReturnCheckBox.toggled.connect(self.__selfReturnIntervalsSlot)
            
            self.__isSelfReturnIntervalsPlotted=True
        else:
            self._updateSelfReturnIntervals(self.period)
            self._updateSelfReturnOrder(self.period)

    def __updateRenormalizableGraph(self):
        if self.renormalizable:
            self.__plotRenormalizableGraph()
        else:
            self.__removeRenormalizableGraph()

    def __removeRenormalizableGraph(self):
        if self.__isSelfReturnIntervalsPlotted == True:
            try:
                self.selfReturnCheckBox.toggled.disconnect(self.__selfReturnIntervalsSlot)
                self.orderCheckBox.toggled.disconnect(self.__selfReturnOrderSlot)
            except:
                pass
            self.__selfReturnIntervalsSlot=None
            self._removeSelfReturnIntervals()
            self._removeSelfReturnOrder()
            self.__isSelfReturnIntervalsPlotted = False
    
    def _plotSelfReturnIntervals(self,period)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotSelfReturnIntervals")
    def _updateSelfReturnIntervals(self,period):
        raise NotImplementedError("PlotWindow._updateSelfReturnIntervals")
    def _removeSelfReturnIntervals(self):
        raise NotImplementedError("PlotWindow._removeSelfReturnIntervals")

    def _plotSelfReturnOrder(self,period)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotSelfReturnOrder")
    def _updateSelfReturnOrder(self,period):
        raise NotImplementedError("PlotWindow._updateSelfReturnOrder")
    def _removeSelfReturnOrder(self):
        raise NotImplementedError("PlotWindow._removeSelfReturnOrder")
    

    '''
    Plot RChild objects
    '''
    def __plotRChildGraph(self):
        self.__plotNextLevelOrbits()
        self.__plotDeepLevelOrbits()

    def __updateRChildGraph(self):
        if self.__rChild != None:
            self.__updateNextLevelOrbits()
            self.__updateDeepLevelOrbits()
        else:
            self.__removeRChildGraph()

    def __removeRChildGraph(self):
        self.__removeNextLevelOrbits()
        self.__removeDeepLevelOrbits()
        
    ''' Next Level Orbits '''
    # plot orbits obtained from next level
    __isNextLevelOrbitsPlotted=False
    __level1Slot=None
    def __plotNextLevelOrbits(self):
        if self.__isNextLevelOrbitsPlotted==False:
            gAlpha1=self._plotAlpha1(visible=self.alpha1CheckBox.isChecked())
            self.alpha1CheckBox.toggled.connect(gAlpha1.setVisible)

            gBeta1=self._plotBeta1(visible=self.beta1CheckBox.isChecked())
            self.beta1CheckBox.toggled.connect(gBeta1.setVisible)
    
            gLevel1=Plot.Group([self.gAlpha1,self.gBeta1],visible=self.partitionButton.isChecked(),parent=self.canvas)
            self.__level1Slot=gLevel1.setVisible
            self.partitionButton.toggled.connect(self.__level1Slot)
            
            self.__isNextLevelOrbitsPlotted=True
        else:
            self._updateAlpha1()
            self._updateBeta1()

    def __updateNextLevelOrbits(self):
        if self.renormalizable:
            self.__plotNextLevelOrbits()
        else:
            self.__removeNextLevelOrbits()

    def __removeNextLevelOrbits(self):
        if self.__isNextLevelOrbitsPlotted==True:
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
                self.partitionButton.toggled.disconnect(self.__level1Slot)
            except:
                pass
            self.__level1Slot=None
            self._removeAlpha1()
            self._removeBeta1()
            self.__isNextLevelOrbitsPlotted=False
            
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

    ''' Deep Level Orbits '''
   
    _isDeepLevelOrbitsPlotted=False
    _rescalingLevelSlot=None
    def __plotDeepLevelOrbits(self):
        if self._isDeepLevelOrbitsPlotted==False:
            gRescalingLevels=self._plotRescalingLevels(visible=self.levelButton.isChecked())
            self._rescalingLevelSlot=gRescalingLevels.setVisible
            self.levelButton.toggled.connect(self._rescalingLevelSlot)
            self._isDeepLevelOrbitsPlotted=True
        else:
            self._updateRescalingLevels()

    def __updateDeepLevelOrbits(self):
        if self.__rChild!=None:
            self.__plotDeepLevelOrbits()
        else:
            self.__removeDeepLevelOrbits()

    def __removeDeepLevelOrbits(self):
        if self._isDeepLevelOrbitsPlotted==True:
            try:
                self.levelButton.toggled.disconnect(self._rescalingLevelSlot)
            except:
                pass
            self._rescalingLevelSlot=None
            self._removeRescalingLevels()
            self._isDeepLevelOrbitsPlotted=False
            
    def _plotRescalingLevels(self,visible:bool=True)->Plot.GraphObject:
        raise NotImplementedError("PlotWindow._plotRescalingLevels")
    def _updateRescalingLevels(self):
        raise NotImplementedError("PlotWindow._updateRescalingBoundaries")
    def _removeRescalingLevels(self):
        raise NotImplementedError("PlotWindow._removeRescalingLevels")
