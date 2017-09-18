from PyQt5 import QtCore, QtWidgets
import sys # We need sys so that we can pass argv to QApplication
from scipy import optimize
import numpy as np
from matplotlib import (cm,colors)

from PlotWindow import PlotWindow 
import Setting

import Plot

# renormalization 
from Unimodal import Unimodal

def PlotVetricalLines(pointList,*args):
    return [Plot.VerticalLine(point, *args) for point in pointList]

def frange(x, y, jump):
    while x < y:
        yield x
        x += jump

class UnimodalWindow(PlotWindow):
    def __init__(self, func:Unimodal, level:int = 0, rParent:PlotWindow=None):
        '''
        Create a window for a unimodal map
        :param func: the unimodal map to plot
        :type func: Unimodal
        :param level: the level of renormalization
        :type level: int
        :param rParent: Previous level of renormalization
        :type rParent: UnimodalWindow
        '''

        self.__levels_alpha=[func.p_a]
        self.__levels_Alpha=[func.p_A]
        self.__levels_beta=[func.p_b]
        self.__levels_Beta=[func.p_B]

        self.__func:Unimodal = func
        PlotWindow.__init__(self, level, rParent)

        self.canvas.setAxesOptions(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        #self.canvas.fig.tight_layout()

        self.__plotCurrentLevel()
        self.__checkRenormalizable()
        #self.setRenormalizable(self.__renormalizable(self.period))

    '''
    Properties
    '''
    
    # unimodal map for the plot
    def getFunction(self)->Unimodal:
        return self.__func
    @QtCore.pyqtSlot(Unimodal)
    def setFunction(self, func:Unimodal):
        if self.__func != func:
            self.__func = func
            self.functionChangedEvent(func)
    function=property(
        lambda self: self.getFunction(), 
        lambda self, func: self.setFunction(func)
        )

    '''
    Plot current level
    '''
    def __plotCurrentLevel(self):
        self.canvas.setUpdatesEnabled(False)

        '''Plot graphs'''
        # Plot function
        self.gFunction = Plot.Function(self.function,plotOptions={'lw':1})
        # Plot second iterate
        self.gFunctionSecond = Plot.Function(lambda x:self.function.iterates(x,2),plotOptions={'lw':1})
        # Plot multiple iterate
        self.gFunctionIterates = Plot.Function(lambda x:self.function.iterates(x,self.period),plotOptions={'lw':1})
        # Draw diagonal line
        self.gDiagonal = Plot.Function(lambda x:x,plotOptions={'lw':1})
        
        '''Plot orbits'''
        self.gAlpha0=Plot.Ticks("top",
            [-1,1,self.function.p_c],
            [r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$"])
        self.gBeta0_0=Plot.VerticalLine(self.function.p_b,plotOptions={'color':'gray','lw':0.5})
        # Draw B
        self.gBeta0_Bar0=Plot.VerticalLine(self.function.p_B,plotOptions={'color':'gray','lw':0.5})
        # Draw B2
        self.gBeta0_Bar1=Plot.VerticalLine(self.function.p_B2,plotOptions={'color':'gray','lw':0.5})
        # Beta ticks
        self.gBeta0Ticks=Plot.Ticks("top",
                                [self.function.p_b,self.function.p_B,self.function.p_B2],
                                [r"$\beta^{0}$",r"$\overline{\beta^{1}}$"]
                                )
        self.gBeta0=Plot.Group([self.gBeta0_0,self.gBeta0_Bar0,self.gBeta0_Bar1,self.gBeta0Ticks])

        self.canvas.setUpdatesEnabled(True)

    def __updateCurrentLevel(self):
        self.gFunction.setFunction(self.function)
        self.gFunctionSecond.setFunction(lambda x:self.function.iterates(x,2))
        self.gFunctionIterates.update()
        
        self.gAlpha0.setTicks([-1,1,self.function.p_c])
        self.gBeta0_0.setXValue(self.function.p_b)
        self.gBeta0_Bar0.setXValue(self.function.p_B)
        self.gBeta0_Bar1.setXValue(self.function.p_B2)
        self.gBeta0Ticks.setTicks([self.function.p_b,self.function.p_B,self.function.p_B2])
        
    '''
    Plot renormalizable objects
    '''
    __isSelfReturnIntervalsPlotted=False
    def __plotRenormalizableGraph(self):
        period=self.period
        self.gSelfReturnIntervals=Plot.Group([Plot.Rectangle(
            self.function.p_a1[period][t], self.function.p_a1[period][t], #x,y
            self.function.p_A1[period][t]-self.function.p_a1[period][t], self.function.p_A1[period][t]-self.function.p_a1[period][t], #width, height
            plotOptions={'color':'gray', 'lw':1, 'fill':None}
            ) for t in range(period)])
        self.gSelfReturnOrder=Plot.Group([Plot.Text(
            str(t),
            ((self.function.p_a1[period][t]+self.function.p_A1[period][t])/2,max(self.function.p_a1[period][t],self.function.p_A1[period][t])),
            (0,1),
            plotOptions={'horizontalalignment':'center'}
            ) for t in range(period)])
        self.gSelfReturn=Plot.Group([self.gSelfReturnIntervals,self.gSelfReturnOrder])
            

    def __updateRenormalizableGraph(self):
        period=self.period
        for t in range(period):
            # Set the self return intervals
            self.gSelfReturnIntervals[t].setBounds(
                self.function.p_a1[period][t], self.function.p_a1[period][t],
                self.function.p_A1[period][t]-self.function.p_a1[period][t], self.function.p_A1[period][t]-self.function.p_a1[period][t]
                )
            # Set the self return intervals
            self.gSelfReturnOrder[t].setPosition(
                ((self.function.p_a1[period][t]+self.function.p_A1[period][t])/2,max(self.function.p_a1[period][t],self.function.p_A1[period][t])),
                )

    def __removeRenormalizableGraph(self):
        self.gSelfReturn=None
        self.gSelfReturnOrder=None
        self.gSelfReturnIntervals=None
        self.__isSelfReturnIntervalsPlotted = False
        
    '''
    Plot RChild objects
    '''
    
    ''' Next Level Orbits '''
    # plot orbits obtained from next level
    def __plotNextLevelOrbits(self):
        self.gAlpha1=Plot.Group(PlotVetricalLines(self.orbit_alpha1+self.orbit_Alpha1))
        self.gBeta1=Plot.Group(PlotVetricalLines(self.orbit_beta1+self.orbit_Beta1))
        self.gLevel1=Plot.Group([self.gAlpha1,self.gBeta1])

    def __updateNextLevelOrbits(self):
        self.gAlpha1.clear()
        self.gAlpha1.extend(PlotVetricalLines(self.orbit_alpha1+self.orbit_Alpha1))

        self.gBeta1.clear()
        self.gBeta1.extend(PlotVetricalLines(self.orbit_beta1+self.orbit_Beta1))

    def __removeNextLevelOrbits(self):
        self.gLevel1=None
        self.gAlpha1=None
        self.gBeta1=None

    def _plotDeepLevelOrbits(self):
        def _contourRLevel(x,y):
            lList=self.levels_alpha
            rList=self.levels_Alpha
            
            i=0
            while i<len(lList):
                if x < lList[i] or rList[i] < x:
                    return i-1
                i=i+1
            return i-1

        def _contourQLevel(x,y):
            return _contourRLevel(self.function(x),y) 
    
        def _contourQRLevel(x,y):
            return _contourQLevel(x,y) if x < self.function.p_b else _contourRLevel(x,y)
        
        _contourQRLevel=np.vectorize(_contourQRLevel,signature='(),()->()')
        
        self.gRescalingLevels = Plot.Contour(_contourQRLevel,
            plotOptions={'levels':list(frange(-0.5,Setting.figureMaxLevels+0.6,1)),'cmap':cm.get_cmap("gray_r"),'norm':colors.Normalize(vmin=0,vmax=10)})

    def _updateDeepLevelOrbits(self):
        self.gRescalingLevels.update()

    def _removeDeepLevelOrbits(self):
        self.gRescalingLevels=None
                    
    '''
    Events
    '''
    
    # User input
    # bug: does not update(remove) contour plot when deep level period is changed
    def periodChangedEvent(self, period:int):
        self.__checkRenormalizable()
        self.gFunctionIterates.update()
        #super().periodChangedEvent(period)

    # unimodal map for the plot
    def functionChangedEvent(self, func:Unimodal):
        self.canvas.setUpdatesEnabled(False)
        self.__updateCurrentLevel()
        self.__checkRenormalizable()
        self.canvas.setUpdatesEnabled(True)
    
    def __checkRenormalizable(self):
        renormalizable=self.__renormalizable(self.period)
        if renormalizable != self.renormalizable:
            self.setRenormalizable(renormalizable)
        elif renormalizable:
            self.rFunctionChangedEvent()
        
    def rFunctionChangedEvent(self):
        self.__updateRenormalizableGraph()
        self.updateRChild()

    def renormalizableChangedEvent(self,value):
        if value is True:
            self.__plotRenormalizableGraph()
        else:
            self.closeRChild()
            self.__removeRenormalizableGraph()
        #super().renormalizableChangedEvent(value)
        #self._updateRenormalizable()

    ''' Periodic intervals and Trapping intervals '''
    # Periodic intervals and levels 
    __orbit_alpha1=[]
    __orbit_Alpha1=[]
    __orbit_beta1=[]
    __orbit_Beta1=[]
    def getOrbit_alpha1(self):
        return self.__orbit_alpha1
    def getOrbit_Alpha1(self):
        return self.__orbit_Alpha1
    def getOrbit_beta1(self):
        return self.__orbit_beta1
    def getOrbit_Beta1(self):
        return self.__orbit_Beta1

    # Find the periodic intervals
    # todo: exception
    def _findPeriodicInterval(self,period):
        if self._rFunc!=None:
            # build period intervals from the next level
            self.__orbit_alpha1=self.function.p_a1[period]
            self.__orbit_Alpha1=self.function.p_A1[period]
            self.__orbit_beta1=self.function.orbit(self.function(self._r_si(self._rFunc.p_b)),period)
            self.__orbit_Beta1=self.function.reflexOrbit(self.orbit_beta1)
        else:
            self.__orbit_alpha1=[]
            self.__orbit_Alpha1=[]
            self.__orbit_beta1=[]
            self.__orbit_Beta1=[]
    
    ''' Rescaling levels '''
    __levels_alpha=[]
    __levels_Alpha=[]
    __levels_beta=[]
    __levels_Beta=[]
    def getLevels_alpha(self):
        return self.__levels_alpha
    def getLevels_Alpha(self):
        return self.__levels_Alpha
    def getLevels_beta(self):
        return self.__levels_beta
    def getLevels_Beta(self):
        return self.__levels_Beta

    def _iRescaling(self,y):
    # The inverse function of nonlinear rescaling
        if not (-1.0<y and y<1.0):
            raise ValueError("_iRescaling: Unable to compute the inverse rescaling. The value ",str(y)," is out of bound")

        y1=self._r_si(y)
            
        def solve(x):
            return self.function.iterates(x,self.period-1)-y1
        return optimize.brenth(solve, self.orbit_alpha1[0],self.orbit_Alpha1[0])

    def _findRescalingBoundaries(self,rChild):
        # update the list for the levels
        self.__levels_alpha=[self.function.p_a,self.orbit_alpha1[0]]
        self.__levels_Alpha=[self.function.p_A,self.orbit_Alpha1[0]]
        self.__levels_beta=[self.function.p_b,self.orbit_beta1[0]]
        self.__levels_Beta=[self.function.p_B,self.orbit_Beta1[0]]
        self._updateRescalingBoundaries(rChild)
    def _updateRescalingBoundaries(self,rChild):
        i=len(self.__levels_alpha)
        updated=False
        
        # update the list of the periodic points if new renormalization level is available
        while i-1 < len(rChild.__levels_alpha) and i <= Setting.figureMaxLevels:
            self.__levels_alpha.append(self._iRescaling(rChild.levels_alpha[i-1]))
            self.__levels_Alpha.append(self._iRescaling(rChild.levels_Alpha[i-1]))
            self.__levels_beta.append(self._iRescaling(rChild.levels_beta[i-1]))
            self.__levels_Beta.append(self._iRescaling(rChild.levels_Beta[i-1]))
            i=i+1
            updated=True
            
        return updated


    '''
    Next
    '''
    
    # Stores the renormalized function
    _rFunc=None
    # Stores the affine rescaling map
    _r_s=None
    _r_si=None
    def __renormalize(self,period:int):
        try:
            func_renormalize=self.function.renomalize(period)
        #except RuntimeError as e:
        except BaseException as e:
            print("Unable to renormalize at level ",str(self.level))
            print("Parameter ",str(Setting.parameterValue))
            print(str(e))
            return False

        if func_renormalize != None:
            (self._rFunc,self._r_s,self._r_si)=func_renormalize
            return True
        else:
            return False

    def __renormalizable(self, period):
        return self.function.renormalizable(period)

    '''
    Child Events
    '''
   
    # variables for renormalization
    
    # Stores the renormalized function
    _rFunc=None
    # Stores the affine rescaling map
    _r_s=None
    _r_si=None
    
    # open child renormalization window
    def _newRChildEvent(self, period:int):
        # create window if not exist then renormalize
        if self.__renormalize(period) == False:
            return None

        rChild=UnimodalWindow(self._rFunc, self.level+1, self)
        rChild.setWindowTitle("Level "+str(self.level+1))
        rChild.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        rChild.setParent(None)
        
        self._findPeriodicInterval(self.period)
        self._findRescalingBoundaries(rChild)

        self.__plotNextLevelOrbits()
        self._plotDeepLevelOrbits()

        return rChild

    def _updateRChildEvent(self, rChild:PlotWindow, period:int):
        if rChild is not None:
            if self.__renormalize(period) == True:
                # Update child
                rChild.function=self._rFunc
                
                self._findPeriodicInterval(self.period)
                self._findRescalingBoundaries(rChild)

                self.__updateNextLevelOrbits()
                self._updateDeepLevelOrbits()
                return True
            else:
                return False

    # called when the child is closed.
    #isThisClosed=False
    def _closeRChildEvent(self):
        self.__removeNextLevelOrbits()
        self._removeDeepLevelOrbits()
        
        self._rFunc=None
        self._r_s=None
        self._r_si=None
        
        self.__orbit_alpha1=[]
        self.__orbit_Alpha1=[]
        self.__orbit_beta1=[]
        self.__orbit_Beta1=[]

        self.__levels_alpha=[self.function.p_a]
        self.__levels_Alpha=[self.function.p_A]
        self.__levels_beta=[self.function.p_b]
        self.__levels_Beta=[self.function.p_B]


    # Notified by the child whne a child is renormalized
    # called by child window
    def _descendantRenormalizedEvent(self, level, window):
        if self._updateRescalingBoundaries(self.rChild) == True:
            #print("Level ", self._level, ": ", str(self.levels_alpha))
            #print("Level ", self._level+1, ": ", str(self._rChild.levels_alpha))
            self._updateDeepLevelOrbits()
            
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = UnimodalWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  