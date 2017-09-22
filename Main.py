from PyQt5 import QtCore, QtWidgets, QtGui # Import the PyQt4 module we'll need
from PyQt5.QtWidgets import QFileDialog
import sys # We need sys so that we can pass argv to QApplication

import MainWindowUI # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from UnimodalWindow import UnimodalWindow
from function import Unimodal
import importlib.util
import os.path

def parameterToPercentage(value):
    return (float(value)-float(functionConf.parameterMin))/(float(functionConf.parameterMax)-float(functionConf.parameterMin))
    

def percentageToParameter(percentage):
    return float(functionConf.parameterMin)+(percentage*(float(functionConf.parameterMax)-float(functionConf.parameterMin)))

class MainWindow(QtWidgets.QMainWindow, MainWindowUI.Ui_mainWindow):
    
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
    
    # load function
    # todo: support for cython file
    def loadFile(self, path):
        spec = importlib.util.spec_from_file_location('functionConf', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
        
    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file=QFileDialog.getOpenFileName(self, 
            'Open File',
            '',
            "Python Files (*.py);;All Files (*)", 
            options=options)
        
        print(file)
        if not os.path.isfile(file[0]):
            return
        
        try:
            conf=self.loadFile(file[0])
        except Exception as e:
            print(str(e))
            return

        global functionConf
        functionConf=conf
        
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
        self.__originalPlot=UnimodalWindow(
            Unimodal(lambda x:functionConf.func(x,functionConf.parameterValue),functionConf.func_c(functionConf.parameterValue)),
            0)
        self.__originalPlot.setWindowTitle("Original Function")
        self.__originalPlot.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.__originalPlot.mdiSubWindow=self.mdiArea.addSubWindow(self.__originalPlot,QtCore.Qt.SubWindow | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.__originalPlot.showMaximized()

        
        # Set the initial values of the parameter selector
        self.parameterMinEdit.setText(str(functionConf.parameterMin))
        self.parameterMinEdit.setValidator(QtGui.QDoubleValidator())
        self.parameterMaxEdit.setText(str(functionConf.parameterMax))
        self.parameterMaxEdit.setValidator(QtGui.QDoubleValidator())
        
        self.parameterEdit.setText(str(functionConf.parameterValue))
        self.parameterEdit.setValidator(QtGui.QDoubleValidator())

        self.parameterSlider.setValue(int(parameterToPercentage(functionConf.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        
        # Update Parameter
        self.parameterEdit.editingFinished.connect(self.__parameterEditUpdate)
        self.parameterSlider.valueChanged.connect(self.__parameterSliderUpdate)
        self.__parameterUpdate=False

        # Update Bounds
        self.parameterMinEdit.editingFinished.connect(self.__parameterMinBoundUpdate)
        self.parameterMaxEdit.editingFinished.connect(self.__parameterMaxBoundUpdate)
        self.parameterZInButton.clicked.connect(self.__parameterZoomIn)
        self.parameterZOutButton.clicked.connect(self.__parameterZoomOut)
        
    '''
    Parameter Slider
    todo: create a new widgit to bind all of the features
    '''
    def __parameterEditUpdate(self):
        if self.__parameterUpdate != True:
            self.__parameterUpdate=True
            if (functionConf.parameterMin <= float(self.parameterEdit.text())) and (float(self.parameterEdit.text()) <= functionConf.parameterMax):
                functionConf.parameterValue=float(self.parameterEdit.text())
                self.parameterSlider.setValue(int(parameterToPercentage(functionConf.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
                self.__updatePlot()
            else:
                #revert change if out of bound
                self.parameterEdit.setText(str(functionConf.parameterValue))
            self.__parameterUpdate=False
        
    def __parameterSliderUpdate(self):
        if self.__parameterUpdate != True:
            self.__parameterUpdate=True
            functionConf.parameterValue=percentageToParameter(float(self.parameterSlider.value())/(self.parameterSlider.maximum()-self.parameterSlider.minimum()))
            self.parameterEdit.setText(str(functionConf.parameterValue))
            self.__updatePlot()
            self.__parameterUpdate=False

    def __updatePlot(self):
        functionConf.func_c(functionConf.parameterValue)
        self.__originalPlot.function=Unimodal(lambda x:functionConf.func(x,functionConf.parameterValue),functionConf.func_c(functionConf.parameterValue))
        
    # Update Bound
    def __parameterMinBoundUpdate(self):
        if float(self.parameterMinEdit.text()) < functionConf.parameterMax:
            #set new min bound
            functionConf.parameterMin=float(self.parameterMinEdit.text())
            self.__parameterBoundUpdate()
        else:
            # revert change
            self.parameterMinEdit.setText(str(functionConf.parameterMin))
            #print("revert")

    def __parameterMaxBoundUpdate(self):
        if functionConf.parameterMin < float(self.parameterMaxEdit.text()):
            #set new max bound
            functionConf.parameterMax=float(self.parameterMaxEdit.text())
            self.__parameterBoundUpdate()
        else:
            # revert change
            self.parameterMaxEdit.setText(str(functionConf.parameterMax))
            #print("revert")
    
    # The current parameter will be centered and the scale will be zoomed by the factor functionConf.parameterZoom
    def __parameterZoomIn(self):
        size=(functionConf.parameterMax-functionConf.parameterMin)/functionConf.parameterZoom
        functionConf.parameterMin=functionConf.parameterValue-size/2
        functionConf.parameterMax=functionConf.parameterValue+size/2
        self.parameterMinEdit.setText(str(functionConf.parameterMin))
        self.parameterMaxEdit.setText(str(functionConf.parameterMax))
        self.__parameterBoundUpdate()

    def __parameterZoomOut(self):
        size=(functionConf.parameterMax-functionConf.parameterMin)*functionConf.parameterZoom
        functionConf.parameterMin=functionConf.parameterValue-size/2
        functionConf.parameterMax=functionConf.parameterValue+size/2
        self.parameterMinEdit.setText(str(functionConf.parameterMin))
        self.parameterMaxEdit.setText(str(functionConf.parameterMax))
        self.__parameterBoundUpdate()
        
    def __parameterBoundUpdate(self):
        # Check if value is in the bound
        if functionConf.parameterValue < functionConf.parameterMin:
            functionConf.parameterValue = functionConf.parameterMin
            self.parameterEdit.setText(float(functionConf.parameterValue))
        elif functionConf.parameterValue > functionConf.parameterMax:
            functionConf.parameterValue = functionConf.parameterMax
            self.parameterEdit.setText(float(functionConf.parameterValue))

        # Update the percentage of the slider
        self.__parameterUpdate=True
        self.parameterSlider.setValue(int(parameterToPercentage(functionConf.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        self.__parameterUpdate=False
        
        
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = MainWindow()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':
    main()  