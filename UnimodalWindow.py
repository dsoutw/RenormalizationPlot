from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need
import sys # We need sys so that we can pass argv to QApplication
from scipy import optimize

from PlotWindow import PlotWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from UnimodalPlot import UnimodalPlot
import Setting

# renormalization 
from Unimodal import Unimodal

        
class UnimodalWindow(UnimodalPlot,PlotWindow):
        
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

        UnimodalPlot.__init__(self, func)
        PlotWindow.__init__(self, level, rParent)

        self.canvas.setAxesOptions(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        self.setRenormalizable(self.__renormalizable(self.period))
        self.updateRenormalizablePlot()
        #self.canvas.fig.tight_layout()

    '''
    Properties
    '''
    
    # User input
    # bug: does not update(remove) contour plot when deep level period is changed
    @QtCore.pyqtSlot(int)
    def setPeriod(self, period):
        super().setPeriod(period)
        self.setRenormalizable(self.__renormalizable(period))
        self.updateRChild()
        self.updateRenormalizablePlot()
        #self._updateRenormalizable()

    def getPeriod(self):
        return super().getPeriod()

    # unimodal map for the plot
    @QtCore.pyqtSlot(Unimodal)
    def setFunction(self, func:Unimodal):
        super().setFunction(func)

        self.canvas.setUpdatesEnabled(False)
        self.setRenormalizable(self.__renormalizable(self.period))
        self.updateRChild()
        self.updatePlot()
        self.canvas.setUpdatesEnabled(True)

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

        return rChild

    def _updateRChildEvent(self, rChild:PlotWindow, period:int):
        if rChild is not None:
            if self.__renormalize(period) == True:
                # Update child
                rChild.function=self._rFunc
                
                self._findPeriodicInterval(self.period)
                self._findRescalingBoundaries(rChild)
                return True
            else:
                return False

    # called when the child is closed.
    #isThisClosed=False
    def _closeRChildEvent(self):
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
            self.updateRescalingLevelPlot()
            
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = UnimodalWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  