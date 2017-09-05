from PyQt5 import QtCore, QtWidgets # Import the PyQt4 module we'll need
import sys # We need sys so that we can pass argv to QApplication

from PlotWindow import PlotWindow # This file holds our MainWindow and all design related things
                    # it also keeps events etc that we defined in Qt Designer
from UnimodalPlot import UnimodalPlot
import Setting

# renormalization 
from Unimodal import Unimodal

        
class UnimodalWindow(UnimodalPlot,PlotWindow):
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
        :type rParent: UnimodalWindow
        '''
        #func: Unimodal
        #level: nonnegative integer
        self._func=func

        self._p_aLevels=[self._func.p_a]
        self._p_ALevels=[self._func.p_A]
        self._p_bLevels=[self._func.p_b]
        self._p_BLevels=[self._func.p_B]
    
        PlotWindow.__init__(self, level, rParent)
        UnimodalPlot.__init__(self, func)

        self.canvas.setAxesOptions(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
        self.setRenormalizable(self._renormalizable(self.period))
        self.updateRenormalizablePlot()
        #self.canvas.fig.tight_layout()

    # User input
    # bug: does not update(remove) contour plot when deep level period is changed
    @QtCore.pyqtSlot(int)
    def setPeriod(self, period):
        super().setPeriod(period)
        self.setRenormalizable(self._renormalizable(period))
        self._findPeriodicInterval(period)
        self.updateRChild()
        self.updateRenormalizablePlot()
        #self._updateRenormalizable()

    def getPeriod(self):
        return super().getPeriod()

    # unimodal map for the plot
    def getFunction(self)->Unimodal:
        return self._func
    @QtCore.pyqtSlot(Unimodal)
    def setFunction(self, func:Unimodal):
        super().setFunction(func)

        self.canvas.setUpdatesEnabled(False)
        self.setRenormalizable(self._renormalizable(self.period))
        self._findPeriodicInterval(self.period)
        self.updateRChild()
        self.updatePlot()
        self.canvas.setUpdatesEnabled(True)

        #self._updateRenormalizable()

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
            print("Unable to renormalize at level ",str(self.level))
            print("Parameter ",str(Setting.parameterValue))
            print(str(e))
            return False

        if func_renormalize != None:
            (self._rFunc,self._r_s,self._r_si)=func_renormalize
            return True
        else:
            return False

    def _renormalizable(self, period):
        return self._func.renormalizable(period)

    # variables for renormalization
    
    # Stores the renormalized function
    _rFunc=None
    # Stores the affine rescaling map
    _r_s=None
    _r_si=None
    
    # open child renormalization window
    def _newRChildEvent(self, period:int):
        # create window if not exist then renormalize
        if self._renormalize(period) == False:
            return None

        rChild=UnimodalWindow(self._rFunc, self.level+1, self)
        rChild.setWindowTitle("Level "+str(self.level+1))
        rChild.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        rChild.setParent(None)
        
        return rChild

    def _updateRChildEvent(self, rChild, period):
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
            
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = UnimodalWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  