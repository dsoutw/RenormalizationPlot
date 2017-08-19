from PyQt5 import QtCore, QtWidgets, QtGui # Import the PyQt4 module we'll need
import sys # We need sys so that we can pass argv to QApplication

import Setting
import MainWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
import Plot
from Unimodal import Unimodal

def parameterToPercentage(value):
    return (float(value)-float(Setting.parameterMin))/(float(Setting.parameterMax)-float(Setting.parameterMin))
    

def percentageToParameter(percentage):
    return float(Setting.parameterMin)+(percentage*(float(Setting.parameterMax)-float(Setting.parameterMin)))

class MainWindow(QtWidgets.QMainWindow, MainWindow.Ui_mainWindow):
    
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super().__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        # Set the initial values of the parameter selector
        self.parameterMinEdit.setText(str(Setting.parameterMin))
        self.parameterMinEdit.setValidator(QtGui.QDoubleValidator())
        self.parameterMaxEdit.setText(str(Setting.parameterMax))
        self.parameterMaxEdit.setValidator(QtGui.QDoubleValidator())
        
        self.parameterEdit.setText(str(Setting.parameterValue))
        self.parameterEdit.setValidator(QtGui.QDoubleValidator())

        self.parameterSlider.setValue(int(parameterToPercentage(Setting.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        
        # Update Parameter
        self.parameterEdit.editingFinished.connect(self.__parameterEditUpdate)
        self.parameterSlider.valueChanged.connect(self.__parameterSliderUpdate)
        self.__parameterUpdate=False

        # Update Bounds
        self.parameterMinEdit.editingFinished.connect(self.__parameterMinBoundUpdate)
        self.parameterMaxEdit.editingFinished.connect(self.__parameterMaxBoundUpdate)
        self.parameterZInButton.clicked.connect(self.__parameterZoomIn)
        self.parameterZOutButton.clicked.connect(self.__parameterZoomOut)
        
        # Add the window for the initial plot
        #sub = QMdiSubWindow()
        #sub.setWidget(QTextEdit())
        #sub.setWindowTitle("subwindow"+str(MainWindow.count))
        self.__originalPlot=Plot.PlotWindow(
            Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)),
            0,
            mdi=self.mdiArea)
        self.__originalPlot.setWindowTitle("Original Function")
        self.__originalPlot.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.mdiArea.addSubWindow(self.__originalPlot)
        self.mdiArea.addSubWindow(self.__originalPlot,QtCore.Qt.SubWindow | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.__originalPlot.showMaximized()
        
        
    # Update Parameter
    def __parameterEditUpdate(self):
        if self.__parameterUpdate != True:
            self.__parameterUpdate=True
            if (Setting.parameterMin <= float(self.parameterEdit.text())) and (float(self.parameterEdit.text()) <= Setting.parameterMax):
                Setting.parameterValue=float(self.parameterEdit.text())
                self.parameterSlider.setValue(int(parameterToPercentage(Setting.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
                self.__updatePlot()
            else:
                #revert change if out of bound
                self.parameterEdit.setText(str(Setting.parameterValue))
            self.__parameterUpdate=False
        
    def __parameterSliderUpdate(self):
        if self.__parameterUpdate != True:
            self.__parameterUpdate=True
            Setting.parameterValue=percentageToParameter(float(self.parameterSlider.value())/(self.parameterSlider.maximum()-self.parameterSlider.minimum()))
            self.parameterEdit.setText(str(Setting.parameterValue))
            self.__updatePlot()
            self.__parameterUpdate=False

    def __updatePlot(self):
        Setting.func_c(Setting.parameterValue)
        self.__originalPlot.function=Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue))
        
    # Update Bound
    def __parameterMinBoundUpdate(self):
        if float(self.parameterMinEdit.text()) < Setting.parameterMax:
            #set new min bound
            Setting.parameterMin=float(self.parameterMinEdit.text())
            self.__parameterBoundUpdate()
        else:
            # revert change
            self.parameterMinEdit.setText(str(Setting.parameterMin))
            print("revert")

    def __parameterMaxBoundUpdate(self):
        if Setting.parameterMin < float(self.parameterMaxEdit.text()):
            #set new max bound
            Setting.parameterMax=float(self.parameterMaxEdit.text())
            self.__parameterBoundUpdate()
        else:
            # revert change
            self.parameterMaxEdit.setText(str(Setting.parameterMax))
            print("revert")
    
    # The current parameter will be centered and the scale will be zoomed by the factor Setting.parameterZoom
    def __parameterZoomIn(self):
        size=(Setting.parameterMax-Setting.parameterMin)/Setting.parameterZoom
        Setting.parameterMin=Setting.parameterValue-size/2
        Setting.parameterMax=Setting.parameterValue+size/2
        self.parameterMinEdit.setText(str(Setting.parameterMin))
        self.parameterMaxEdit.setText(str(Setting.parameterMax))
        self.__parameterBoundUpdate()

    def __parameterZoomOut(self):
        size=(Setting.parameterMax-Setting.parameterMin)*Setting.parameterZoom
        Setting.parameterMin=Setting.parameterValue-size/2
        Setting.parameterMax=Setting.parameterValue+size/2
        self.parameterMinEdit.setText(str(Setting.parameterMin))
        self.parameterMaxEdit.setText(str(Setting.parameterMax))
        self.__parameterBoundUpdate()
        
    def __parameterBoundUpdate(self):
        # Check if value is in the bound
        if Setting.parameterValue < Setting.parameterMin:
            Setting.parameterValue = Setting.parameterMin
            self.parameterEdit.setText(float(Setting.parameterValue))
        elif Setting.parameterValue > Setting.parameterMax:
            Setting.parameterValue = Setting.parameterMax
            self.parameterEdit.setText(float(Setting.parameterValue))

        # Update the percentage of the slider
        self.__parameterUpdate=True
        self.parameterSlider.setValue(int(parameterToPercentage(Setting.parameterValue)*(self.parameterSlider.maximum()-self.parameterSlider.minimum())))
        self.__parameterUpdate=False
        
        
        
def main():
    print("test print")
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = MainWindow()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app
    print("end")


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  