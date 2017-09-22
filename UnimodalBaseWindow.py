from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need

import UnimodalWindowUI # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from Binding import Binding
# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl
from abc import ABCMeta,abstractmethod
import typing as tp

class UnimodalBaseWindow(Binding, QtWidgets.QMainWindow):
    __metaclass__=ABCMeta
    __level:int=0
    __rParent:tp.Optional['UnimodalBaseWindow']=None
    __period:int=2
    __renormalizable:bool=None
    
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
    
    # Arguments
    # func: unimodal class
    # level: the level of renormalization
    # rParent: a unimodal map for the previous level
    def __init__(self, level:int = 0, rParent:tp.Optional['UnimodalBaseWindow'] = None, config=None):
        #func: Unimodal
        #level: nonnegative integer
        self.__level:int=level
        self.__rParent:tp.Optional['UnimodalBaseWindow']=rParent

        QtWidgets.QMainWindow.__init__(self,rParent)

        self.ui = UnimodalWindowUI.Ui_plotWindow()
        self.ui.setupUi(self)
        
        self.__loadConfig(config)
        
        Binding.__init__(self, self.ui, self.__bindingList)
        #self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined

        # Adjust the size of the options to fit with the contents
        self.ui.renormalizationScroll.setMinimumWidth(self.ui.renormalizationContents.sizeHint().width() + self.ui.renormalizationScroll.verticalScrollBar().sizeHint().width() )
        
        # setup the parent button    
        if rParent is not None:
            def showParent():
                self.focusWindow(rParent)
            self.ui.parentButton.clicked.connect(showParent)
        else:
            self.ui.parentButton.hide()

        # Add graph toolbar
        self.ui.mplToolbar = NavigationToolbar(self.ui.canvas, self.ui.centralwidget)
        self.addToolBar(self.ui.mplToolbar)

        # Plot the initial graph
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0
        #self.canvas.setMinimumSize(0,0)

        # setup renormalizable features
        self.ui.periodSpinBox.valueChanged.connect(self.setPeriod)
        self.__rChild=None
        self.__renormalizable=False
        self.ui.levelBox.setEnabled(False)
        self.ui.renormalizeButton.clicked.connect(self.openRChild)
        self.renormalizableChanged.emit(False)
    
    # Todo: load to attr
    def __loadConfig(self,config):
        self.__period=2
        self.ui.periodSpinBox.setValue(self.__period)

        self.ui.selfReturnCheckBox.setChecked(config.figureSelfReturn)
        self.ui.orderCheckBox.setChecked(config.figureSelfReturn)

        self.ui.secondIterateCheckBox.setChecked(config.figureSecondIterate)
        self.ui.iteratedGraphCheckBox.setChecked(config.figureMultipleIterate)
        self.ui.diagonalCheckBox.setChecked(config.figureDiagonal)
        self.ui.beta0CheckBox.setChecked(config.figureBeta0)
        self.ui.alpha1CheckBox.setChecked(config.figureAlpha1)
        self.ui.beta1CheckBox.setChecked(config.figureBeta1)
        self.config=config
    
    def __setRenormalizableText(self,value:bool):
        text={True:"Yes",False:"No"} 
        self.ui.renormalizableResultLabel.setText(text[value])

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
            self.ui.periodSpinBox.setValue(period)
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
            self.__renormalizable=value
            self.__setRenormalizableText(value)
            self.ui.renormalizeButton.setEnabled(value)
            self.renormalizableChangedEvent(value)
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
    __rChild:tp.Optional['UnimodalBaseWindow']=None

    @abstractmethod
    def _newRChildEvent(self, period:int)->'PlotWindow':
        '''
        Create a renormalized function window
        :param period: The period of renormalization
        :type period: int
        @return: The new window. Return Null if false
        @type return: UnimodalBaseWindow
        '''
        raise NotImplementedError("UnimodalBaseWindow._renormalizable")

    @abstractmethod
    def _closeRChildEvent(self):
        '''
        Update the renormalized function window
        Called when the renormalized function is modified
        :param period: The period of renormalization
        :type period: int
        '''
        raise NotImplementedError("UnimodalBaseWindow._renormalizable")
    
    @abstractmethod
    def _descendantRenormalizedEvent(self):
        raise NotImplementedError("UnimodalBaseWindow._renormalizable")
    
    def openRChild(self):
        # open child renormalization window
        # create window if not exist then renormalize
        if self.__rChild == None:
            self.__rChild =self._newRChildEvent(self.__period)
            if self.__rChild == None:
                return

            self.ui.levelBox.setEnabled(True)
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
    
            self.ui.levelBox.setEnabled(False)
            self.__rChild=None


    def getRChild(self):
        return self.__rChild
    rChild=property(lambda self: self.getRChild())
    
    # window utilities
    # modify this method if created by mdi window
    def openWindow(self, widget:'UnimodalBaseWindow'):
        widget.show()

    def focusWindow(self, widget:'UnimodalBaseWindow'):
        widget.show()
        widget.activateWindow()
        widget.raise_()

    def closeWindow(self, widget:'UnimodalBaseWindow'):
        widget.close()
