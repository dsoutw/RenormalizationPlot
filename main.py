from PyQt5 import QtCore, QtWidgets, QtGui # Import the PyQt4 module we'll need
from PyQt5.QtWidgets import QFileDialog
import sys # We need sys so that we can pass argv to QApplication
#import functools
#import inspect
import os.path
import numpy as np

from ui.mainwindowui import Ui_mainWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from ui.unimodalwindow import UnimodalWindow
from function import Unimodal
from lib.module import loadFile

import logging
import logging.config
logging.captureWarnings(True)
import typing as tp
import config

class MainWindow(QtWidgets.QMainWindow, Ui_mainWindow):
    title="Renormalization Plot"
    __logger:tp.Optional[logging.Logger]=None
    
    def __init__(self):
        self.__logger:logging.Logger=logging.getLogger(__name__)
        
        super().__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        # Setup open file dialog
        self.actionOpen.triggered.connect(self.openFileDialog)

        # Update Parameter
        self.parameterEdit.editingFinished.connect(self.__parameterEditUpdate)
        self.parameterSlider.valueChanged.connect(self.__parameterSliderUpdate)
        self.__parameterUpdate=False

        # Update Bounds
        self.parameterMinEdit.editingFinished.connect(self.__parameterMinBoundUpdate)
        self.parameterMaxEdit.editingFinished.connect(self.__parameterMaxBoundUpdate)
        self.parameterZInButton.clicked.connect(self.__parameterZoomIn)
        self.parameterZOutButton.clicked.connect(self.__parameterZoomOut)
        
        # overwrite the window utilities to support mdi window
        def openMdiWindow(sender,window):
            window.mdiSubWindow=self.mdiArea.addSubWindow(window,
                    QtCore.Qt.SubWindow | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowSystemMenuHint |
                    QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
            window.mdiSubWindow.show()
        def closeMdiWindow(sender,window):
            window.mdiSubWindow.close()
            window.mdiSubWindow=None
        def focusMdiWindow(sender,window):
            window.mdiSubWindow.show()
            self.mdiArea.setActiveSubWindow(window.mdiSubWindow)
        UnimodalWindow.openWindow=openMdiWindow
        UnimodalWindow.closeWindow=closeMdiWindow
        UnimodalWindow.focusWindow=focusMdiWindow
        
        self.parameterWidget.setEnabled(False)
        self.setWindowTitle(self.title)
        self.__logger.info("UI initilized")
        
    functionConf=None
    __originalPlot=None
    
    def showEvent(self, *args, **kwargs):
        QtWidgets.QMainWindow.showEvent(self, *args, **kwargs)
    
    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file=QFileDialog.getOpenFileName(self, 
            'Open File',
            '',
            "Python Files (*.py);;All Files (*)", 
            options=options)
        
        if file[0] == '' or file[0] is None:
            '''User cancel'''
            return
        
        if not os.path.isfile(file[0]):
            self.__logger.error('File does not exist: %s',file[0])
            return
        
        try:
            config=loadFile(file[0])
        except Exception:
            self.__logger.exception('Unable to load file: %s',file[0])
            return

        try:
            window=self.__openWindow(config)
        except Exception:
            self.__logger.exception('Unable to open window: %s',config.__name__)
            return

        self.__closeWindow()
        self.functionConf=config
        self.__originalPlot=window

        window.showMaximized()
        self.setWindowTitle("%s - [%s]" % (self.title,config.__name__))

        self.__loadConfig(config)
        self.parameterWidget.setEnabled(True)

        self.__logger.info('File opened: %s', os.path.basename(file[0]))

    
    def __openWindow(self,config):
        # Create the window for the original plot
        
        # Setup function
        #kwargs={inspect.getargspec(self.functionConf.func).args[1]:self.functionConf.parameterValue}
        #function=functools.partial(self.functionConf.func,**kwargs)
        #print(self.functionConf.parameterValue)
        functionParameter=np.float64(config.parameterValue)
        functionWithParameter=config.func
        function=lambda x: functionWithParameter(x,functionParameter)
        
        window=UnimodalWindow(Unimodal(
                function,
                config.func_c(functionParameter),
                config=config,
                signiture=functionParameter
                ),0,config=config)
        window.setWindowTitle("Original Function")
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        window.mdiSubWindow=self.mdiArea.addSubWindow(window,
            QtCore.Qt.SubWindow | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowSystemMenuHint |
            QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
        return window

    def __updateWindow(self):
        if self.__originalPlot is not None:
            try:
                #kwargs={inspect.getargspec(self.functionConf.func).args[1]:self.functionConf.parameterValue}
                #function=functools.partial(self.functionConf.func,**kwargs
                functionParameter=np.float64(self.functionConf.parameterValue)
                functionWithParameter=self.functionConf.func
                function=lambda x: functionWithParameter(x,functionParameter)
                self.__originalPlot.function=Unimodal(
                    function,
                    self.functionConf.func_c(functionParameter),
                    config=self.functionConf,
                    signiture=functionParameter
                    )
                return
            except Exception:
                self.__logger.exception('Unable to update plot: %s [%s]', self.functionConf.__name__, self.functionConf.parameterValue)
            self.__closeWindow()
    
    def __closeWindow(self):
        if self.__originalPlot is not None:
            self.__originalPlot.destroyed.disconnect()
            self.__originalPlot.mdiSubWindow.close()
            self.__originalPlot=None
    
    def __windowClosedSlot(self):
        self.__logger.info('File closed by user: %s', self.functionConf.__name__)
        self.setWindowTitle(self.title)
        self.parameterWidget.setEnabled(False)
        self.functionConf=None
        self.__originalPlot=None
    
    def __loadConfig(self,config):
        # Set the initial values of the parameter selector
        self.parameterMinEdit.setText(str(config.parameterMin))
        self.parameterMinEdit.setValidator(QtGui.QDoubleValidator())
        self.parameterMaxEdit.setText(str(config.parameterMax))
        self.parameterMaxEdit.setValidator(QtGui.QDoubleValidator())
        
        self.parameterEdit.setValidator(QtGui.QDoubleValidator())

        self.setParameter(config.parameterValue)
        
        self.__originalPlot.destroyed.connect(self.__windowClosedSlot)
    
    '''
    Parameter Slider
    todo: create a new widgit to bind all of the features
    '''
    def parameterToPercentage(self,value):
        return (float(value)-float(self.functionConf.parameterMin))/(float(self.functionConf.parameterMax)-float(self.functionConf.parameterMin))
        
    
    def percentageToParameter(self,percentage):
        return float(self.functionConf.parameterMin)+(percentage*(float(self.functionConf.parameterMax)-float(self.functionConf.parameterMin)))

    __parameterEditing=False
    def setParameter(self,value):
        self.__parameterEditing=True

        self.__logger.info('Parameter changed to %s',value)
        self.functionConf.parameterValue=value
        self.parameterSlider.setValue(int(self.parameterToPercentage(value)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        self.parameterEdit.setText(str(value))
        self.__updateWindow()

        self.__parameterEditing=False

    def __parameterEditUpdate(self):
        if not self.__parameterEditing:
            value=np.float64(self.parameterEdit.text())
            if (self.functionConf.parameterMin <= value and value <= self.functionConf.parameterMax):
                self.setParameter(value)
            else:
                #revert change if out of bound
                self.parameterEdit.setText(str(self.functionConf.parameterValue))
        
    def __parameterSliderUpdate(self):
        if not self.__parameterEditing:
            self.setParameter(self.percentageToParameter(float(self.parameterSlider.value())/(self.parameterSlider.maximum()-self.parameterSlider.minimum())))

    # Update Bound
    def __parameterMinBoundUpdate(self):
        if float(self.parameterMinEdit.text()) < self.functionConf.parameterMax:
            #set new min bound
            self.functionConf.parameterMin=float(self.parameterMinEdit.text())
            self.__parameterBoundUpdate()
        else:
            # revert change
            self.parameterMinEdit.setText(str(self.functionConf.parameterMin))
            #print("revert")

    def __parameterMaxBoundUpdate(self):
        if self.functionConf.parameterMin < float(self.parameterMaxEdit.text()):
            #set new max bound
            self.functionConf.parameterMax=float(self.parameterMaxEdit.text())
            self.__parameterBoundUpdate()
        else:
            # revert change
            self.parameterMaxEdit.setText(str(self.functionConf.parameterMax))
            #print("revert")
    
    # The current parameter will be centered and the scale will be zoomed by the factor functionConf.parameterZoom
    def __parameterZoomIn(self):
        size=(self.functionConf.parameterMax-self.functionConf.parameterMin)/self.functionConf.parameterZoom
        self.functionConf.parameterMin=self.functionConf.parameterValue-size/2
        self.functionConf.parameterMax=self.functionConf.parameterValue+size/2
        self.parameterMinEdit.setText(str(self.functionConf.parameterMin))
        self.parameterMaxEdit.setText(str(self.functionConf.parameterMax))
        self.__parameterBoundUpdate()

    def __parameterZoomOut(self):
        size=(self.functionConf.parameterMax-self.functionConf.parameterMin)*self.functionConf.parameterZoom
        self.functionConf.parameterMin=self.functionConf.parameterValue-size/2
        self.functionConf.parameterMax=self.functionConf.parameterValue+size/2
        self.parameterMinEdit.setText(str(self.functionConf.parameterMin))
        self.parameterMaxEdit.setText(str(self.functionConf.parameterMax))
        self.__parameterBoundUpdate()
        
    def __parameterBoundUpdate(self):
        # Check if value is in the bound
        if self.functionConf.parameterValue < self.functionConf.parameterMin:
            self.functionConf.parameterValue = self.functionConf.parameterMin
            self.parameterEdit.setText(float(self.functionConf.parameterValue))
        elif self.functionConf.parameterValue > self.functionConf.parameterMax:
            self.functionConf.parameterValue = self.functionConf.parameterMax
            self.parameterEdit.setText(float(self.functionConf.parameterValue))

        # Update the percentage of the slider
        self.__parameterEditing=True
        self.parameterSlider.setValue(int(self.parameterToPercentage(self.functionConf.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        self.__parameterEditing=False
        
        
def main():
    logging.config.dictConfig(config.log)
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = MainWindow()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    form.openFileDialog()
    app.exec_()                         # and execute the app


if __name__ == '__main__':
    main()  