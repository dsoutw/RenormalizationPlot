from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need
import sys # We need sys so that we can pass argv to QApplication

import PlotWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer

from scipy import optimize
import numpy as np

# Matplotlib library
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl

# renormalization 
from Unimodal import Unimodal
from PlotCurve import (FunctionG,VerticalLineG,RectangleG,GroupG,TicksG,ContourG)
        
class PlotWindow(QtWidgets.QMainWindow, PlotWindow.Ui_plotWindow):
    
    # Arguments
    # func: unimodal class
    # level: the level of renormalization
    # rParent: a unimodal map for the previous level
    def __init__(self, func, level=0, rParent=None):
        #func: Unimodal
        #level: nonnegative integer
        self._func=func
        self._level=level
        self._rParent=rParent
        self._rChild=None
        self._rFunc=None
        self._r_si=None
    
        super(self.__class__, self).__init__(rParent)
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

        self._plotCurrentLevelGraphs()
        self._plotCurrentLevelOrbits()
        self._plotSelfReturnBoxes()
        
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

        # setup the parent button    
        if rParent is not None:
            def showParent():
                self.focusWindow(rParent)
            self.parentButton.clicked.connect(showParent)
        else:
            self.parentButton.hide()
        
        # setup renormalizable features
        self._period=2
        self.periodSpinBox.setValue(self._period)
        self.updateRChild()
        self.periodSpinBox.valueChanged.connect(self._periodSpinBoxChanged)
        self._rChild=None
        self.renormalizeButton.clicked.connect(self.openRChild)
        self.canvas.setMinimumSize(0,0)
        
        # setup level grapgs
        self.levelBox.setEnabled(False)
    
    # inherited from QtWidgets.QMainWindow
    # close child renormalization when the window is closed
    def closeEvent(self, evnt):
        if self._rParent is not None:
            #print("close captured")
            self._rParent._rChild=None
        self.closeRChild()
        super().closeEvent(evnt)
        
    # UI callbacks
    def _periodSpinBoxChanged(self, value):
        self._period=value
        def _fp(x):
            for i in range(value):
                x=self._func(x)
            return x
        self.f_unimodal_p.setFunction(_fp)
        self.updateRChild()
        
    # do renormalization
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

    # variables for renormalization
    
    # Stores the child window 
    _rChild=None
    # Stores the renormalized function
    _rFunc=None
    # Stores the affine rescaling map
    _r_s=None
    _r_si=None
    # Periodic intervals and levels 
    _p_a1Orbit=None
    _p_A1Orbit=None
    _p_b1Orbit=None
    _p_B1Orbit=None
    
    # open child renormalization window
    def openRChild(self):
        # create window if not exist then renormalize
        if self._rChild is None:
            rFunc, r_s, r_si =self._renormalize(self._period)
            if rFunc is None:
                return

            self._rFunc=rFunc
            self._r_s=r_s
            self._r_si=r_si
            
            self._rChild=PlotWindow(rFunc, self._level+1,self)
            self._rChild.setWindowTitle("Level "+str(self._level+1))
            self._rChild.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self._rChild.setParent(None)
            self.levelBox.setEnabled(True)
            self.openWindow(self._rChild)
            
            # update the list for the levels
            self._p_aLevels=[self._func.p_a,r_si(rFunc.p_a)]
            self._p_ALevels=[self._func.p_A,r_si(rFunc.p_A)]
            self._p_bLevels=[self._func.p_b,r_si(rFunc.p_b)]
            self._p_BLevels=[self._func.p_B,r_si(rFunc.p_B)]
            
            self._findPeriodicInterval()
            
            self._plotNextLevelOrbits()
            self._plotDeepLevelOrbits()
            
            # Notify the ancestors that the unimodal map is renormalized
            level=2
            ancestor=self._rParent
            while ancestor is not None:
                ancestor._descendantRenormalized(level,self._rChild)
                ancestor=ancestor._rParent
                level=level+1
        else:
            self.focusWindow(self._rChild)

    # Find the periodic intervals
    def _findPeriodicInterval(self):
        # build period orbit from the next level
        def _nextLevelOrbit(p_x,p_X):
            p_xList=[]
            for i in range(self._period):
                p_x=self._func(p_x)
                p_xList.append(p_x)
                
            p_XList=[None] * self._period
            p_XList[self._period-1]=p_X
            i=self._period-2
            while i >= 0:
                if p_xList[i] < self._func.p_c:
                    p_X=optimize.brenth(lambda x: self._func(x)-p_X,self._func.p_a,self._func.p_c)
                else:
                    p_X=optimize.brenth(lambda x: self._func(x)-p_X,self._func.p_c,self._func.p_A)
                p_XList[i]=p_X
                i=i-1
            return p_xList, p_XList

        self._p_a1Orbit, self._p_A1Orbit=_nextLevelOrbit(self._r_si(self._rFunc.p_a),self._r_si(self._rFunc.p_A))
        self._p_b1Orbit, self._p_B1Orbit=_nextLevelOrbit(self._r_si(self._rFunc.p_b),self._r_si(self._rFunc.p_B))

    # update status of renormlaizable
    def updateRChild(self):
        if(self._func.renomalizable(self._period)):
            self.renormalizableResultLabel.setText("Yes")
            self.renormalizeButton.setEnabled(True)

            if self._rChild is not None:
                rFunc, r_s, r_si = self._renormalize(self._period)
                if rFunc is not None:
                    # Update child
                    self._rFunc=rFunc
                    self._r_s=r_s
                    self._r_si=r_si
                    self._rChild.function=rFunc
                    
                    # plot sub-structures if possible
                    self._findPeriodicInterval()
                    self._updateNextLevelOrbits()
                    self._updateDeepLevelOrbits()
                else:
                    self.closeRChild()
                    
        else:
            self.renormalizableResultLabel.setText("No")
            self.renormalizeButton.setEnabled(False)
            self.closeRChild()
    
    # close child renormalization window
    def closeRChild(self):
        if self._rChild is not None:
            self.closeWindow(self._rChild)
            self.levelBox.setEnabled(False)
            self._rChild=None
            self._rFunc=None
            self._r_s=None
            self._r_si=None
            self._p_a1Orbit=None
            self._p_A1Orbit=None
            self._p_b1Orbit=None
            self._p_B1Orbit=None

            # remove sub-structures
            self._removeNextLevelOrbits()
            self._removeDeepLevelOrbits()

    # Notified by the child whne a child is renormalized
    # called by child window
    def _descendantRenormalized(self, level, window):
        i=len(self._p_aLevels)
        updated=False
        
        # update the list of the periodic points if new renormalization level is available
        while i-1 < len(self._rChild._p_aLevels):
            self._p_aLevels.append(self._r_si(self._rChild._p_aLevels[i-1]))
            self._p_ALevels.append(self._r_si(self._rChild._p_ALevels[i-1]))
            self._p_bLevels.append(self._r_si(self._rChild._p_bLevels[i-1]))
            self._p_BLevels.append(self._r_si(self._rChild._p_BLevels[i-1]))
            i=i+1
            updated=True
            
        if updated is True:
            self._updateDeepLevelOrbits()
            print("Level ", self._level, ": ", str(self._p_aLevels))
            print("Level ", self._level+1, ": ", str(self._rChild._p_aLevels))
            
    # unimodal map for the plot
    def getFunction(self):
        return self._func

    @QtCore.pyqtSlot(Unimodal)
    def setFunction(self, func):
        self._func = func

        self.canvas.setUpdatesEnabled(False)
        self._updateCurrentLevelGraphs()
        self._updateCurrentLevelOrbits()
        self._updateSelfReturnBoxes()
        self.canvas.setUpdatesEnabled(True)

        self.updateRChild()


    function=property(getFunction, setFunction)

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

    # Plotting sub-routine

    # plot graphs for current level
    def _func_p(self, x):
        for i in range(self._period):
            x=self._func(x)
        return x
     
    def _plotCurrentLevelGraphs(self):
        # Draw unimodal map        
        self.f_unimodal = FunctionG(self.canvas,self._func,lw=1)

        # Draw second iterate
        self.f_unimodal_2 = FunctionG(self.canvas,lambda x:self._func(self._func(x)),visible=Setting.figureSecondIterate,lw=1)
        self.secondIterateCheckBox.setChecked(Setting.figureSecondIterate)
        self.secondIterateCheckBox.toggled.connect(self.f_unimodal_2.setVisible)

        # Draw diagonal line
        self.f_diagonal = FunctionG(self.canvas,lambda x:x,visible=Setting.figureDiagonal,lw=1)
        self.diagonalCheckBox.setChecked(Setting.figureDiagonal)
        self.diagonalCheckBox.toggled.connect(self.f_diagonal.setVisible)
        
        # Draw multiple iterates 
        self.f_unimodal_p = FunctionG(self.canvas,self._func_p,visible=Setting.figureMultipleIterate,lw=1)
        self.iteratedGraphCheckBox.setChecked(Setting.figureMultipleIterate)
        self.iteratedGraphCheckBox.toggled.connect(self.f_unimodal_p.setVisible)

    def _updateCurrentLevelGraphs(self):
        # Update Graph
        self.f_unimodal.setFunction(self._func)
        self.f_unimodal_2.setFunction(lambda x:self._func(self._func(x)))

        # Update multiple iterates 
        self.f_unimodal_p.setFunction(self._func_p)

    def _plotCurrentLevelOrbits(self):
        # Draw beta(0) points
        # Draw b
        self.f_b=VerticalLineG(self.canvas,self._func.p_b,color='gray',lw=0.5)
        # Draw B
        self.f_B=VerticalLineG(self.canvas,self._func.p_B,color='gray',lw=0.5)
        # Draw B2
        self.f_B2=VerticalLineG(self.canvas,self._func.p_B2,color='gray',lw=0.5)
        
        # Set ticks
        self.f_Alpha0Ticks=TicksG(self.canvas,"top",
                                [-1,1,self._func.p_c],
                                [r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$"]
                                )
        
        self.f_Beta0Ticks=TicksG(self.canvas,"top",
                                [self._func.p_b,self._func.p_B,self._func.p_B2],
                                [r"$\beta^{0}$",r"$\overline{\beta^{1}}$"]
                                )
        self.f_Beta0=GroupG([self.f_b,self.f_B,self.f_B2,self.f_Beta0Ticks],visible=Setting.figureBeta0)
        self.beta0CheckBox.setChecked(Setting.figureBeta0)
        self.beta0CheckBox.toggled.connect(self.f_Beta0.setVisible)

    def _updateCurrentLevelOrbits(self):
        # Find fixed point
        self.f_b.setXValue(self._func.p_b)
        # Find a1(1)bar
        self.f_B.setXValue(self._func.p_B)
        # Find a0(1)bar
        self.f_B2.setXValue(self._func.p_B2)

        # Set ticks
        self.f_Alpha0Ticks.setTicks([-1,1,self._func.p_c])
        self.f_Beta0Ticks.setTicks([self._func.p_b,self._func.p_B,self._func.p_B2])

    # Plot the intervals that defines the self-return map
    def _plotSelfReturnBoxes(self):
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
        self.selfReturnCheckBox.toggled.connect(self.f_SelfReturnBeta.setVisible)

    def _updateSelfReturnBoxes(self):
        # Set the self return interval
        self.f_SelfReturnBetaR.setBounds(self._func.p_b,self._func.p_b,self._func.p_B2-self._func.p_b,self._func.p_B2-self._func.p_b)
        self.f_SelfReturnBetaQ.setBounds(self._func.p_B,self._func.p_B,self._func.p_b-self._func.p_B,self._func.p_b-self._func.p_B)

        
    # plot orbits obtained from next level
    def _plotNextLevelOrbits(self):
        self.canvas.setUpdatesEnabled(False)
        
        f_a1List=[VerticalLineG(self.canvas, self._p_a1Orbit[i], visible=True) for i in range(self._period)]
        f_A1List=[VerticalLineG(self.canvas, self._p_A1Orbit[i], visible=True) for i in range(self._period)]
        self.f_aA1List=GroupG(f_a1List+f_A1List,visible=self.alpha1CheckBox.isChecked())
        self.alpha1CheckBox.toggled.connect(self.f_aA1List.setVisible)

        f_b1List=[VerticalLineG(self.canvas, self._p_b1Orbit[i], visible=True) for i in range(self._period)]
        f_B1List=[VerticalLineG(self.canvas, self._p_B1Orbit[i], visible=True) for i in range(self._period)]
        self.f_bB1List=GroupG(f_b1List+f_B1List,visible=self.beta1CheckBox.isChecked())
        self.beta1CheckBox.toggled.connect(self.f_bB1List.setVisible)
        
        self.f_level1=GroupG([self.f_aA1List,self.f_bB1List],visible=self.partitionButton.isChecked())
        self.partitionButton.toggled.connect(self.f_level1.setVisible)
        
        self.canvas.setUpdatesEnabled(True)

    def _updateNextLevelOrbits(self):
        self._removeNextLevelOrbits()
        self._plotNextLevelOrbits()

    def _removeNextLevelOrbits(self):
        # remove sub-structures
        self.alpha1CheckBox.toggled.disconnect()
        self.beta1CheckBox.toggled.disconnect()
        self.partitionButton.toggled.disconnect(self.f_level1.setVisible)
        self.f_level1.remove()
        self.f_level1=None
        self.f_aA1List=None
        self.f_bB1List=None
        
    def _plotDeepLevelOrbits(self):
        lList=self._p_aLevels
        rList=self._p_ALevels
        
        def _contourRLevel(x,y):
            i=0
            while i<len(lList):
                if x < lList[i] or rList[i] < x:
                    return i 
                i=i+1
            return i

        def _contourQLevel(x,y):
            i=0
            while i<len(lList):
                f_xPoint=self._func(x)
                if f_xPoint < lList[i] or rList[i] < f_xPoint:
                    return i 
                i=i+1
            return i
    
        def _contourQRLevel(x,y):
            return _contourQLevel(x,y) if x < self._func.p_b else _contourRLevel(x,y)
            
        _contourQRLevel=np.vectorize(_contourQRLevel,signature='(),()->()')
        
        #_contourQRLevel= lambda x,y:x+y
        
        self.f_rLevel = ContourG(self.canvas, _contourQRLevel, visible=self.levelButton.isChecked(),levels=[-1,0,1,2,3,4,5])
        self.levelButton.toggled.connect(self.f_rLevel.setVisible)

    def _updateDeepLevelOrbits(self):
        self._removeDeepLevelOrbits()
        self._plotDeepLevelOrbits()

    def _removeDeepLevelOrbits(self):
        self.levelButton.toggled.disconnect(self.f_rLevel.setVisible)
        self.f_rLevel.remove()
        self.f_rLevel=None

import Setting
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = PlotWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  