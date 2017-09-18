from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need

import PlotWindowUI # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from Binding import Binding
import Plot
# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl
from abc import ABCMeta,abstractmethod

import Setting
        
class PlotWindow(Binding, QtWidgets.QMainWindow, PlotWindowUI.Ui_plotWindow):
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

        QtWidgets.QMainWindow.__init__(self,rParent)

        self.ui = self
        self.ui.setupUi(self)

        ''' bindingList format
        graph object: (checkable component, enable other components when the graph is setted...)  
        '''
        __bindingList={
            # current level
            'gFunction':{},
            'gFunctionSecond':{'getVisible':'secondIterateCheckBox','setEnable':('secondIterateCheckBox',)},
            'gFunctionIterates':{'getVisible':'iteratedGraphCheckBox','setEnable':('iteratedGraphCheckBox',)},
            'gDiagonal':{'getVisible':'diagonalCheckBox','setEnable':('diagonalCheckBox',)},
            'gAlpha0':{},
            'gBeta0':{'getVisible':'beta0CheckBox','setEnable':('beta0CheckBox',)},
            # renormalizable
            'gSelfReturnIntervals':{},
            'gSelfReturnOrder':{
                'getVisible':'orderCheckBox',
                'setEnable':('orderCheckBox',),
                'getEnable':'selfReturnCheckBox'},
            'gSelfReturn':{
                'getVisible':'selfReturnCheckBox',
                'setEnable':('selfReturnCheckBox','selfReturnLabel')},
            # first level
            'gAlpha1':{
                'getVisible':'alpha1CheckBox',
                'setEnable':('alpha1CheckBox',),
                'getEnable':'partitionButton'},
            'gBeta1':{
                'getVisible':'beta1CheckBox',
                'setEnable':('beta1CheckBox',),
                'getEnable':'partitionButton'},
            'gLevel1':{
                'getVisible':'partitionButton',
                'setEnable':('partitionButton',)},
            # Deep level
            'gRescalingLevels':{
                'getVisible':'levelButton',
                'setEnable':('levelButton',)},
            }
        
        # Apply settings
        self.periodSpinBox.setValue(self.__period)
        self.selfReturnCheckBox.setChecked(Setting.figureSelfReturn)
        self.orderCheckBox.setChecked(Setting.figureSelfReturn)

        self.secondIterateCheckBox.setChecked(Setting.figureSecondIterate)
        self.iteratedGraphCheckBox.setChecked(Setting.figureMultipleIterate)
        self.diagonalCheckBox.setChecked(Setting.figureDiagonal)
        self.beta0CheckBox.setChecked(Setting.figureBeta0)
        self.alpha1CheckBox.setChecked(Setting.figureAlpha1)
        self.beta1CheckBox.setChecked(Setting.figureBeta1)
        
        Binding.__init__(self, self, __bindingList)
        #self.setupUi(self)  # This is defined in design.py file automatically
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

        # setup renormalizable features
        self.periodSpinBox.valueChanged.connect(self.setPeriod)
        self.__rChild=None
        self.renormalizeButton.clicked.connect(self.openRChild)
        self.canvas.setMinimumSize(0,0)


        # update renormalizable
        #self._updateRenormalizable()
        self.__renormalizable=renormalizable
        self.renormalizableChanged.connect(self.__setRenormalizableText)
        self.renormalizableChanged.connect(self.renormalizeButton.setEnabled)
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
            self.periodChangedEvent(period)
    def getPeriod(self)->int:
        return self.__period
    period=property(
        lambda self: self.getPeriod(), 
        lambda self, func: self.setPeriod(func)
        )
    def periodChangedEvent(self,period:int):
        pass

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
            self.renormalizableChangedEvent(value)
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
