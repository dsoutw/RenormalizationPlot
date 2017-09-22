from PyQt5 import QtCore, QtWidgets, QtGui # Import the PyQt4 module we'll need
from PyQt5.QtWidgets import QFileDialog
import sys # We need sys so that we can pass argv to QApplication
import functools
import inspect
import importlib.util
import os.path
import numpy as np

import MainWindowUI # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from UnimodalWindow import UnimodalWindow
from function import Unimodal

class MainWindow(QtWidgets.QMainWindow, MainWindowUI.Ui_mainWindow):
    title="Renormalization Plot"
    
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
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
        
        self.parameterWidget.setEnabled(False)
        self.setWindowTitle(self.title)
    
    # load function
    # todo: support for cython file
    def loadFile(self, path):
        spec = importlib.util.spec_from_file_location('functionConf', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    functionConf=None
    __originalPlot=None
    
    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file=QFileDialog.getOpenFileName(self, 
            'Open File',
            '',
            "Python Files (*.py);;All Files (*)", 
            options=options)
        
        if not os.path.isfile(file[0]):
            return
        
        try:
            conf=self.loadFile(file[0])
        except Exception as e:
            print(str(e))
            return

        self.setWindowTitle("%s - [%s]" % (self.title,os.path.basename(file[0])))
        if self.__originalPlot is not None:
            print("close from open")
            self.__originalPlot.destroyed.disconnect()
            self.__originalPlot.mdiSubWindow.close()
            self.__originalPlot=None
        self.functionConf=conf
        
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

        # Create the window for the original plot
        #kwargs={inspect.getargspec(self.functionConf.func).args[1]:self.functionConf.parameterValue}
        #function=functools.partial(self.functionConf.func,**kwargs)
        #print(self.functionConf.parameterValue)
        self.functionConf.parameterValue=np.float64(self.functionConf.parameterValue)
        functionWithParameter=self.functionConf.func
        function=lambda x: functionWithParameter(x,self.functionConf.parameterValue)
        self.__originalPlot=UnimodalWindow(Unimodal(
                function,
                self.functionConf.func_c(self.functionConf.parameterValue)
                ),0)
        self.__originalPlot.setWindowTitle("Original Function")
        self.__originalPlot.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.__originalPlot.mdiSubWindow=self.mdiArea.addSubWindow(self.__originalPlot,
            QtCore.Qt.SubWindow | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowSystemMenuHint |
            QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
        self.__originalPlot.showMaximized()
        
        # Set the initial values of the parameter selector
        self.parameterMinEdit.setText(str(self.functionConf.parameterMin))
        self.parameterMinEdit.setValidator(QtGui.QDoubleValidator())
        self.parameterMaxEdit.setText(str(self.functionConf.parameterMax))
        self.parameterMaxEdit.setValidator(QtGui.QDoubleValidator())
        
        self.parameterEdit.setValidator(QtGui.QDoubleValidator())

        self.setParameter(self.functionConf.parameterValue)
        
        self.__originalPlot.destroyed.connect(self.fileClosedSlot)
        self.parameterWidget.setEnabled(True)
    
    def fileClosedSlot(self):
        print("file closed slot")
        self.setWindowTitle(self.title)
        self.parameterWidget.setEnabled(False)
        self.functionConf=None
        self.__originalPlot=None
    
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

        self.functionConf.parameterValue=value
        self.parameterSlider.setValue(int(self.parameterToPercentage(value)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        self.parameterEdit.setText(str(value))
        self.__updatePlot()

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

    def __updatePlot(self):
        kwargs={inspect.getargspec(self.functionConf.func).args[1]:self.functionConf.parameterValue}
        self.__originalPlot.function=Unimodal(
            functools.partial(self.functionConf.func,**kwargs),
            self.functionConf.func_c(self.functionConf.parameterValue)
            )
        
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
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = MainWindow()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':
    main()  