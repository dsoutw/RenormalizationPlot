from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need
#from PyQt5.QtCore import QObject, pyqtProperty
import sys # We need sys so that we can pass argv to QApplication

import PlotWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer

# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
#from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib as mpl
#from matplotlib import (
#    figure as Figure,
#    patches as patches)


# renormalization 
from Unimodal import Unimodal
from PlotCurve import (FunctionG,VerticalLineG,RectangleG,GroupG,TicksG)
        
class PlotWindow(QtWidgets.QMainWindow, PlotWindow.Ui_plotWindow,QtWidgets.QMdiSubWindow):
    def __init__(self, func, level=0, parent=None, mdi=None):
        #func: Unimodal
        #level: nonnegative integer
        self._func=func
        self._level=level
        self._parent=parent
        self._child=None
        self._childWindow=None
        self._mdi=mdi
    
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined

        # Adjust the size of the options to fit with the contents
        self.renormalizationScroll.setMinimumWidth(self.renormalizationContents.sizeHint().width() + self.renormalizationScroll.verticalScrollBar().sizeHint().width() )
        
        # setup graph

        # Plot the initial graph
        self.canvas.setParent(self.centralwidget)
        canvas=self.canvas
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0

        self.canvas.setUpdatesEnabled(False)

        # Draw unimodal map        
        self.f_unimodal = FunctionG(self.canvas,self._func,lw=1)

        # Draw second iterate
        self.f_unimodal_2 = FunctionG(self.canvas,lambda x:self._func(self._func(x)),visible=Setting.figureSecondIterate,lw=1)
        self.secondIterateCheckBox.setChecked(Setting.figureSecondIterate)
        self.secondIterateCheckBox.clicked.connect(self.f_unimodal_2.setVisible)

        # Draw diagonal line
        self.f_diagonal = FunctionG(self.canvas,lambda x:x,visible=Setting.figureDiagonal,lw=1)
        self.diagonalCheckBox.setChecked(Setting.figureDiagonal)
        self.diagonalCheckBox.clicked.connect(self.f_diagonal.setVisible)
        
        # Draw beta(0) points
        # Draw b
        self.f_b=VerticalLineG(self.canvas,self._func.p_b,color='gray',lw=0.5)
        # Draw B
        self.f_B=VerticalLineG(self.canvas,self._func.p_B,color='gray',lw=0.5)
        # Draw B2
        self.f_B2=VerticalLineG(self.canvas,self._func.p_B2,color='gray',lw=0.5)
        self.f_Beta0Ticks=TicksG(self.canvas,"top",
                                [self._func.p_b,self._func.p_B,self._func.p_B2],
                                [r"$\beta^{0}$",r"$\overline{\beta^{1}}$"]
                                )
        self.f_Beta0=GroupG([self.f_b,self.f_B,self.f_B2,self.f_Beta0Ticks],visible=Setting.figureBeta0)
        self.beta0CheckBox.setChecked(Setting.figureBeta0)
        self.beta0CheckBox.clicked.connect(self.f_Beta0.setVisible)
        
        # Draw self-return interval
        self.f_SelfReturnBetaR=RectangleG(self.canvas,
                self._func.p_b, self._func.p_b, #x,y
                self._func.p_B2-self._func.p_b, self._func.p_B2-self._func.p_b, #width, height
                visible=True, color='gray', lw=1, fill=None
            )
        self.f_SelfReturnBetaQ=RectangleG(self.canvas,
                self._func.p_B, self._func.p_B, #x,y
                self._func.p_b-self._func.p_B, self._func.p_b-self._func.p_B, #width, height
                visible=True, color='gray', lw=1, fill=None
            )
        self.f_SelfReturnBeta=GroupG([self.f_SelfReturnBetaR,self.f_SelfReturnBetaQ],visible=Setting.figureSelfReturn)
        self.selfReturnCheckBox.setChecked(Setting.figureSelfReturn)
        self.selfReturnCheckBox.clicked.connect(self.f_SelfReturnBeta.setVisible)
        
        # Set ticks
        self.f_Alpha0Ticks=TicksG(self.canvas,"top",
                                [-1,1,self._func.p_c],
                                [r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$"]
                                )
        
        #self.axes2=canvas.axes.twiny()  # ax2 is responsible for "top" axis and "right" axis
        #self.axes2.set_xticks([-1,1,self._func.p_c,self._func.p_b,self._func.p_B,self._func.p_B2])
        #self.axes2.set_xticklabels([r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$", r"$\alpha^{0}(1)$",r"$\overline{\alpha^{1}(1)}$",r"$\overline{\alpha^{0}(1)}$"])

        canvas.axes.axis([-1, 1, -1, 1])
        canvas.axes.set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        #self.axes2.set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        self.f_Alpha0Ticks.getCurve().set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        self.f_Beta0Ticks.getCurve().set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        #canvas.fig.tight_layout()
        
        self.canvas.setUpdatesEnabled(True)

        # Add graph toolbar
        self.mplToolbar = NavigationToolbar(self.canvas, self.centralwidget)
        self.addToolBar(self.mplToolbar)
    
        # connect parent
        # bug: does not work
        if parent is not None:
            def showParent():
                if self._mdi is not None:
                    self._mdi.setActiveSubWindow(self._parent.parentWidget())
                else:
                    self._parent.raise_()
                    self._parent.activateWindow()
                
            self.parentButton.clicked.connect(showParent)
        else:
            self.parentButton.hide()
        
        # setup renormalizable features
        self._period=2
        self.periodSpinBox.setValue(self._period)
        self._updateRenormalizable()
        self.periodSpinBox.valueChanged.connect(self._periodSpinBoxChanged)
        self._child=None
        self.renormalizeButton.clicked.connect(self._renormalizeWindow)
        self.canvas.setMinimumSize(0,0)
        
        # setup multiple iterates 
        def _fp(x):
            for i in range(self._period):
                x=self._func(x)
            return x
        self.f_unimodal_p = FunctionG(self.canvas,_fp,visible=Setting.figureMultipleIterate,lw=1)
        self.iteratedGraphCheckBox.setChecked(Setting.figureMultipleIterate)
        self.iteratedGraphCheckBox.clicked.connect(self.f_unimodal_p.setVisible)
        
    def closeChild(self):
        if self._child is not None:
            self._child=None
            self._childWindow.close()
            self._childWindow=None
                    
    def closeEvent(self, evnt):
        if self._parent is not None:
            #print("close captured")
            self._parent._child=None
        self.closeChild()
        super().closeEvent(evnt)
        
    def _periodSpinBoxChanged(self, value):
        self._period=value
        def _fp(x):
            for i in range(value):
                x=self._func(x)
            return x
        self.f_unimodal_p.setFunction(_fp)
        self._updateRenormalizable()
    
    def _updateRenormalizable(self):
        if(self._func.renomalizable(self._period)):
            self.renormalizableResultLabel.setText("Yes")
            self.renormalizeButton.setEnabled(True)
        else:
            self.renormalizableResultLabel.setText("No")
            self.renormalizeButton.setEnabled(False)
            self.closeChild()
    
    def _renormalize(self,period):
        try:
            func_renormalize=self._func.renomalize(period)
            return func_renormalize
        #except RuntimeError as e:
        except BaseException as e:
            print("Unable to renormalize at level ",str(self._level))
            print("Parameter ",str(Setting.parameterValue))
            print(str(e))
            return None
    
    def _renormalizeWindow(self):
        # create window if not exist then renormalize
        if self._child is None:
            func_renormalize=self._renormalize(self._period)
            if func_renormalize is None:
                return

            self._child=PlotWindow(func_renormalize, self._level+1,self,mdi=self._mdi)
            self._child.setWindowTitle("Level "+str(self._level+1))
            self._child.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            if self._mdi is not None:
                #self._mdi.addSubWindow(self._child)
                self._childWindow = self._mdi.addSubWindow(self._child,
                    QtCore.Qt.SubWindow | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowSystemMenuHint |
                    QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
            else:
                self._childWindow = self._child
            self._childWindow.show()
        #self._childWindow.show()
        #self._childWindow.raise_()
        if self._mdi is not None:
            self._mdi.setActiveSubWindow(self._childWindow)
        else:
            self._childWindow.raise_()
            self._childWindow.activateWindow()

    def getFunction(self):
        return self._func

    @QtCore.pyqtSlot(Unimodal)
    def setFunction(self, func):
        self._func = func
        self._updateRenormalizable()
        if self._child is not None:
            func_renormalize=self._renormalize(self._period)
            if func_renormalize is None:
                self.closeChild()
            else:
                self._child.function=func_renormalize
        
        self.canvas.setUpdatesEnabled(False)
        
        # Update Graph
        self.f_unimodal.setFunction(func)
        self.f_unimodal_2.setFunction(lambda x:self._func(self._func(x)))
        
        # Find fixed point
        self.f_b.setXValue(func.p_b)
        # Find a1(1)bar
        self.f_B.setXValue(func.p_B)
        # Find a0(1)bar
        self.f_B2.setXValue(func.p_B2)
        
        # Set the self return interval
        self.f_SelfReturnBetaR.setBounds(func.p_b,func.p_b,func.p_B2-func.p_b,func.p_B2-func.p_b)
        self.f_SelfReturnBetaQ.setBounds(func.p_B,func.p_B,func.p_b-func.p_B,func.p_b-func.p_B)
        
        # Set ticks
        #self.axes2.set_xticks([-1,1,func.p_c,func.p_b,func.p_B,func.p_B2])
        self.f_Alpha0Ticks.setTicks([-1,1,func.p_c])
        self.f_Beta0Ticks.setTicks([func.p_b,func.p_B,func.p_B2])

        self.canvas.setUpdatesEnabled(True)
        #self.canvas.draw_idle()

    function=property(getFunction, setFunction)

import Setting
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = PlotWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  