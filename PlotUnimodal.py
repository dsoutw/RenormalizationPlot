from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need
import sys # We need sys so that we can pass argv to QApplication

from Plot import PlotWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer

from scipy import optimize
import numpy as np

# Matplotlib library
from matplotlib import (cm,colors)

# renormalization 
from Unimodal import Unimodal
from PlotCurve import (FunctionG,VerticalLineG,RectangleG,GroupG,TicksG,ContourG)
        
class PlotUnimodalWindow(PlotWindow):
    _func=None
    _p_aLevels=None
    
    def __init__(self, func:Unimodal, level:int = 0, rParent:PlotWindow=None):
        '''
        Create a window for a unimodal map
        :param func: the unimodal map to plot
        :type func: Unimodal
        :param level: the level of renormalization
        :type level: int
        :param rParent: Previous level of renormalization
        :type rParent: PlotUnimodalWindow
        '''
        #func: Unimodal
        #level: nonnegative integer
        self._func=func

        self._p_aLevels=[self._func.p_a]
        self._p_ALevels=[self._func.p_A]
        self._p_bLevels=[self._func.p_b]
        self._p_BLevels=[self._func.p_B]
    
        super().__init__(level, rParent)

    # User input
    # bug: does not update(remove) contour plot when deep level period is changed
    @QtCore.pyqtSlot(int)
    def setPeriod(self, period:int):
        self.f_unimodal_p.setFunction(lambda x: self._func.iterates(x,period))
        super().setPeriod(period)

    def getPeriod(self):
        return super.getPeriod()

    period=property(setPeriod,getPeriod)

    # unimodal map for the plot
    def getFunction(self)->Unimodal:
        return self._func

    @QtCore.pyqtSlot(Unimodal)
    def setFunction(self, func:Unimodal):
        self._func = func

        self.canvas.setUpdatesEnabled(False)
        self._updateCurrentLevel()
        self.canvas.setUpdatesEnabled(True)

        self._updateRenormalizable()

    function=property(getFunction, setFunction)

    # Stores the renormalized function
    _rFunc=None
    # Stores the affine rescaling map
    _r_s=None
    _r_si=None
    def _renormalize(self,period:int):
        try:
            func_renormalize=self._func.renomalize(period)
        #except RuntimeError as e:
        except BaseException as e:
            print("Unable to renormalize at level ",str(self._level))
            print("Parameter ",str(Setting.parameterValue))
            print(str(e))
            return False

        if func_renormalize != None:
            (self._rFunc,self._r_s,self._r_si)=func_renormalize
            return True
        else:
            return False

    def _renormalizable(self, period):
        return self._func.renomalizable(period)

    # variables for renormalization
    
    # Stores the renormalized function
    _rFunc=None
    # Stores the affine rescaling map
    _r_s=None
    _r_si=None
    
    # open child renormalization window
    def _newRChild(self, period:int):
        # create window if not exist then renormalize
        if self._renormalize(period) == False:
            return None

        rChild=PlotUnimodalWindow(self._rFunc, self._level+1, self)
        rChild.setWindowTitle("Level "+str(self._level+1))
        rChild.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        rChild.setParent(None)
        
        return rChild

    def _updateRChild(self, rChild, period):
        if rChild is not None:
            if self._renormalize(period) == True:
                # Update child
                self._rChild.function=self._rFunc
                return True
            else:
                return False

    # called when the child is closed.
    #isThisClosed=False
    def _rChildClosed(self):
        super()._rChildClosed()

        self._rFunc=None
        self._r_s=None
        self._r_si=None


    # Notified by the child whne a child is renormalized
    # called by child window
    def _descendantRenormalized(self, level, window):
        if self._updateRescalingLevels() == True:
            #print("Level ", self._level, ": ", str(self._p_aLevels))
            #print("Level ", self._level+1, ": ", str(self._rChild._p_aLevels))
            self._updateDeepLevelOrbits()
            
        
    # Plotting sub-routine

    # plot graphs for current level
    def _func_p(self, x):
        for i in range(self._period):
            x=self._func(x)
        return x
    
    # Plot Functions
    def _plotCurrentLevel(self):
        self.canvas.axes.axis([-1, 1, -1, 1])
        self.canvas.axes.set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')

        self._plotCurrentLevelGraphs()
        self._plotCurrentLevelOrbits()

        #self.canvas.fig.tight_layout()

        #self.axes2.set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        self.f_Alpha0Ticks.artist.set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        self.f_Beta0Ticks.artist.set(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')


    def _updateCurrentLevel(self):
        self._updateCurrentLevelGraphs()
        self._updateCurrentLevelOrbits()
            
    # return: function, second iterate, multiple iterates, diagonal
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

        return (self.f_unimodal, self.f_unimodal_2, self.f_unimodal_p, self.f_diagonal)

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


    # For plotting the intervals that defines the self-return map
    f_selfReturnBoxes = None
    _isRenormalizableGraphPlotted=False
    
    # Plot the intervals that defines the self-return map
    def _plotRenormalizableGraph(self):
        if self._isRenormalizableGraphPlotted != True:
            period=self._period
            f_selfReturnBoxesList=[None]*period
            for t in range(period):
                f_selfReturnBoxesList[t]=RectangleG(self.canvas,
                        self._func.p_a1[period][t], self._func.p_a1[period][t], #x,y
                        self._func.p_A1[period][t]-self._func.p_a1[period][t], self._func.p_A1[period][t]-self._func.p_a1[period][t], #width, height
                        visible=True, color='gray', lw=1, fill=None
                    )
            self.f_selfReturnBoxes=GroupG(f_selfReturnBoxesList)
            self.selfReturnCheckBox.toggled.connect(self.f_selfReturnBoxes.setVisible)
            self._isRenormalizableGraphPlotted=True
        else:
            self._updateRenormalizableGraph()
            

    def _updateRenormalizableGraph(self):
        if self._isRenormalizableGraphPlotted == True:
            period=self._period
            for t in range(period):
            # Set the self return intervals
                self.f_selfReturnBoxes[t].setBounds(
                    self._func.p_a1[period][t], self._func.p_a1[period][t],
                    self._func.p_A1[period][t]-self._func.p_a1[period][t], self._func.p_A1[period][t]-self._func.p_a1[period][t]
                    )


    def _removeRenormalizableGraph(self):
        if self._isRenormalizableGraphPlotted == True:
            self.selfReturnCheckBox.toggled.disconnect()
            self.f_selfReturnBoxes.clear()
            self.f_selfReturnBoxes=None
            self._isRenormalizableGraphPlotted = False
    
    def _plotRChildGraph(self):
        self._plotNextLevelOrbits()
        self._plotDeepLevelOrbits()

    def _updateRChildGraph(self):
        self._updateNextLevelOrbits()
        self._updateDeepLevelOrbits()

    def _removeRChildGraph(self):
        self._removeNextLevelOrbits()
        self._removeDeepLevelOrbits()

    # The inverse function of nonlinear rescaling
    def _iRescaling(self,y):
        if not (-1.0<y and y<1.0):
            raise ValueError("_iRescaling: Unable to compute the inverse rescaling. The value ",str(y)," is out of bound")

        y1=self._r_si(y)
            
        def solve(x):
            return self._func.iterates(x,self._period-1)-y1
        return optimize.brenth(solve, self._p_a1Orbit[0],self._p_A1Orbit[0])

    # Periodic intervals and levels 
    _p_a1Orbit=None
    _p_A1Orbit=None
    _p_b1Orbit=None
    _p_B1Orbit=None

    # Find the periodic intervals
    def _findPeriodicInterval(self):
        # build period intervals from the next level
        self._p_a1Orbit=self._func.p_a1[self._period]
        self._p_A1Orbit=self._func.p_A1[self._period]
        self._p_b1Orbit=self._func.orbit(self._func(self._r_si(self._rFunc.p_b)),self._period)
        self._p_B1Orbit=self._func.reflexOrbit(self._p_b1Orbit)

    def _findRescalingLevels(self):
        # update the list for the levels
        self._p_aLevels=[self._func.p_a,self._p_a1Orbit[0]]
        self._p_ALevels=[self._func.p_A,self._p_A1Orbit[0]]
        self._p_bLevels=[self._func.p_b,self._p_b1Orbit[0]]
        self._p_BLevels=[self._func.p_B,self._p_B1Orbit[0]]
        self._updateRescalingLevels()

    def _updateRescalingLevels(self):
        i=len(self._p_aLevels)
        updated=False
        
        # update the list of the periodic points if new renormalization level is available
        while i-1 < len(self._rChild._p_aLevels) and i <= Setting.figureMaxLevels:
            self._p_aLevels.append(self._iRescaling(self._rChild._p_aLevels[i-1]))
            self._p_ALevels.append(self._iRescaling(self._rChild._p_ALevels[i-1]))
            self._p_bLevels.append(self._iRescaling(self._rChild._p_bLevels[i-1]))
            self._p_BLevels.append(self._iRescaling(self._rChild._p_BLevels[i-1]))
            i=i+1
            updated=True
            
        return updated


    # plot orbits obtained from next level
    _isNextLevelOrbitsPlotted=False
    def _plotNextLevelOrbits(self):
        if self._isNextLevelOrbitsPlotted==False:
            self.canvas.setUpdatesEnabled(False)
            
            self._findPeriodicInterval()
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
            self._isNextLevelOrbitsPlotted=True
        else:
            self._updateNextLevelOrbits()

    def _updateNextLevelOrbits(self):
        if self._isNextLevelOrbitsPlotted==True:
            self._removeNextLevelOrbits()
            self._plotNextLevelOrbits()

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
                self.partitionButton.toggled.disconnect(self.f_level1.setVisible)
            except:
                pass
            self.f_level1.clear()
            self.f_level1=None
            self.f_aA1List=None
            self.f_bB1List=None
            self._p_a1Orbit=None
            self._p_A1Orbit=None
            self._p_b1Orbit=None
            self._p_B1Orbit=None
            self._isNextLevelOrbitsPlotted=False
    
    _isDeepLevelOrbitsPlotted=False
    def _plotDeepLevelOrbits(self):
        if self._isDeepLevelOrbitsPlotted==False:
            self._findRescalingLevels()
            lList=self._p_aLevels
            rList=self._p_ALevels
            
            def _contourRLevel(x,y):
                i=0
                while i<len(lList):
                    if x < lList[i] or rList[i] < x:
                        return i-1
                    i=i+1
                return i-1
    
            def _contourQLevel(x,y):
                return _contourRLevel(self._func(x),y) 
        
            def _contourQRLevel(x,y):
                return _contourQLevel(x,y) if x < self._func.p_b else _contourRLevel(x,y)
                
            _contourQRLevel=np.vectorize(_contourQRLevel,signature='(),()->()')
            
            #_contourQRLevel= lambda x,y:x+y
            def frange(x, y, jump):
                while x < y:
                    yield x
                    x += jump
            
            self.f_rLevel = ContourG(self.canvas, _contourQRLevel, visible=self.levelButton.isChecked(),levels=list(frange(-0.5,Setting.figureMaxLevels+0.6,1)),cmap=cm.get_cmap("gray_r"),norm=colors.Normalize(vmin=0,vmax=10))
            self.levelButton.toggled.connect(self.f_rLevel.setVisible)
            
            self._isDeepLevelOrbitsPlotted=True
        else:
            self._updateDeepLevelOrbits()

    def _updateDeepLevelOrbits(self):
        if self._isDeepLevelOrbitsPlotted==True:
            self._removeDeepLevelOrbits()
            self._plotDeepLevelOrbits()

    def _removeDeepLevelOrbits(self):
        if self._isDeepLevelOrbitsPlotted==True:
            self.levelButton.toggled.disconnect(self.f_rLevel.setVisible)
            self.f_rLevel.clear()
            self.f_rLevel=None
            self._p_aLevels=[self._func.p_a]
            self._p_ALevels=[self._func.p_A]
            self._p_bLevels=[self._func.p_b]
            self._p_BLevels=[self._func.p_B]
            self._isDeepLevelOrbitsPlotted=False

import Setting
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = PlotUnimodalWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  