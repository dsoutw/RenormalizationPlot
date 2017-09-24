from PyQt5 import QtCore, QtWidgets
import sys # We need sys so that we can pass argv to QApplication
import logging
import typing as tp

from scipy import optimize
import numpy as np
from matplotlib import (cm,colors)

from ui.unimodalbasewindow import UnimodalBaseWindow 
from ui.loghandling import appendFunctionInfoAdapter

import plot

# renormalization 
from function import Unimodal

def frange(x, y, jump):
    while x < y:
        yield x
        x += jump

class UnimodalWindow(UnimodalBaseWindow):
    __logger:tp.Optional[logging.Logger]=None
    
    def __init__(self, func:Unimodal, level:int = 0, rParent:UnimodalBaseWindow=None, config=None, logger:tp.Optional[logging.Logger]=None):
        '''
        Create a window for a unimodal map
        :param func: the unimodal map to plot
        :type func: Unimodal
        :param level: the level of renormalization
        :type level: int
        :param rParent: Previous level of renormalization
        :type rParent: UnimodalWindow
        :param logger: Logger
        :type logger: logging.Logger
        '''

        self.levels_alpha=[func.p_a]
        self.levels_Alpha=[func.p_A]
        self.levels_beta=[func.p_b]
        self.levels_Beta=[func.p_B]

        self.__func:Unimodal = func
        if logger is None:
            self.__logger:logging.Logger=appendFunctionInfoAdapter(logging.getLogger(__name__),level)
        else:
            self.__logger:logging.Logger=logger
                
        UnimodalBaseWindow.__init__(self, level, rParent=rParent, config=config, logger=self.__logger)

        try:
            self.ui.canvas.setUpdatesEnabled(False)
            self.ui.canvas.setAxesOptions(adjustable='box-forced',xlim=[-1,1], ylim=[-1,1],aspect='equal')
            #self.canvas.fig.tight_layout()
            self.__plotCurrentLevel()
            #self.setRenormalizable(self.__renormalizable(self.period))
        except Exception as e:
            self.__logger.exception('Unable to draw function.')
            self.closeWindow(self)
            raise RuntimeError('Unable to draw function.') from e
        finally:
            self.ui.canvas.setUpdatesEnabled(True)

        self.__checkRenormalizable()
        
        self.__logger.info("Window Opened")

    def closeEvent(self, evnt):
        super().closeEvent(evnt)
        self.__logger.info("Window Closed")

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
    plot current level
    '''
    __currentLevelPlotted=False
    def __plotCurrentLevel(self):
        '''plot graphs'''
        # plot function
        self.gFunction = plot.Function(self.function,plotOptions={'lw':1})
        # plot second iterate
        self.gFunctionSecond = plot.Function(lambda x:self.function.iterates(x,iteration=2),plotOptions={'lw':1})
        # plot multiple iterate
        self.gFunctionIterates = plot.Function(lambda x:self.function.iterates(x,iteration=self.period),plotOptions={'lw':1})
        # Draw diagonal line
        self.gDiagonal = plot.Function(lambda x:x,plotOptions={'lw':1})
        
        '''plot orbits'''
        self.gAlpha0=plot.Ticks("top",
            [-1,1,self.function.p_c],
            [r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$"])
        self.gBeta0_0=plot.VerticalLine(self.function.p_b,plotOptions={'color':'gray','lw':0.5})
        # Draw B
        self.gBeta0_Bar0=plot.VerticalLine(self.function.p_B,plotOptions={'color':'gray','lw':0.5})
        # Draw B2
        self.gBeta0_Bar1=plot.VerticalLine(self.function.p_B2,plotOptions={'color':'gray','lw':0.5})
        # Beta ticks
        self.gBeta0Ticks=plot.Ticks("top",
                                [self.function.p_b,self.function.p_B,self.function.p_B2],
                                [r"$\beta^{0}$",r"$\overline{\beta^{1}}$"]
                                )
        self.gBeta0=plot.Group([self.gBeta0_0,self.gBeta0_Bar0,self.gBeta0_Bar1,self.gBeta0Ticks])
            
        self.__currentLevelPlotted=True

    def __updateCurrentLevel(self):
        if self.__currentLevelPlotted:
            try:
                self.gFunction.setFunction(self.function)
                self.gFunctionSecond.setFunction(lambda x:self.function.iterates(x,iteration=2))
                self.gFunctionIterates.update()
                
                self.gAlpha0.setTicks([-1,1,self.function.p_c])
                self.gBeta0_0.setXValue(self.function.p_b)
                self.gBeta0_Bar0.setXValue(self.function.p_B)
                self.gBeta0_Bar1.setXValue(self.function.p_B2)
                self.gBeta0Ticks.setTicks([self.function.p_b,self.function.p_B,self.function.p_B2])
            except:
                self.__currentLevelPlotted=False
                raise
        else:
            self.__plotCurrentLevel()
        
    '''
    plot renormalizable objects
    '''
    __renormalizableGraphPlotted=False
    def __plotRenormalizableGraph(self):
        period=self.period
        self.gSelfReturnIntervals=plot.Group([plot.Rectangle(
            self.function.p_a1[period][t], self.function.p_a1[period][t], #x,y
            self.function.p_A1[period][t]-self.function.p_a1[period][t], self.function.p_A1[period][t]-self.function.p_a1[period][t], #width, height
            plotOptions={'color':'gray', 'lw':1, 'fill':None}
            ) for t in range(period)])
        self.gSelfReturnOrder=plot.Group([plot.Text(
            str(t),
            ((self.function.p_a1[period][t]+self.function.p_A1[period][t])/2,max(self.function.p_a1[period][t],self.function.p_A1[period][t])),
            (0,1),
            plotOptions={'horizontalalignment':'center'}
            ) for t in range(period)])
        self.gSelfReturn=plot.Group([self.gSelfReturnIntervals,self.gSelfReturnOrder])
        
        self.__renormalizableGraphPlotted=True
            

    def __updateRenormalizableGraph(self):
        if self.__renormalizableGraphPlotted:
            try:
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
            except:
                self.__renormalizableGraphPlotted=False
                raise
        else:
            self.__plotRenormalizableGraph()

    def __removeRenormalizableGraph(self):
        self.gSelfReturn=None
        self.gSelfReturnOrder=None
        self.gSelfReturnIntervals=None
        self.__renormalizableGraphPlotted=False
        
    '''
    plot RChild objects
    '''
    
    ''' Next Level Orbits '''
    # plot orbits obtained from next level
    __nextLevelOrbitPlotted=False
    def __plotNextLevelOrbits(self):
        self.gAlpha1=plot.Group(plot.VetricalLineList(self.orbit_alpha1+self.orbit_Alpha1))
        self.gBeta1=plot.Group(plot.VetricalLineList(self.orbit_beta1+self.orbit_Beta1))
        self.gLevel1=plot.Group([self.gAlpha1,self.gBeta1])
        self.__nextLevelOrbitPlotted=True

    def __updateNextLevelOrbits(self):
        if self.__nextLevelOrbitPlotted:
            try:
                self.gAlpha1.clear()
                self.gAlpha1.extend(plot.VetricalLineList(self.orbit_alpha1+self.orbit_Alpha1))
        
                self.gBeta1.clear()
                self.gBeta1.extend(plot.VetricalLineList(self.orbit_beta1+self.orbit_Beta1))
            except:
                self.__nextLevelOrbitPlotted=False
                raise
        else:
            self.__plotNextLevelOrbits()

    def __removeNextLevelOrbits(self):
        self.gLevel1=None
        self.gAlpha1=None
        self.gBeta1=None
        self.__nextLevelOrbitPlotted=False

    ''' Deep Level Orbits '''
    __deepLevelOrbitPlotted=False
    def __plotDeepLevelOrbits(self,rChild):
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
        
        self.gRescalingLevels = plot.Contour(_contourQRLevel,
            plotOptions={'levels':list(frange(-0.5,self.config.figureMaxLevels+0.6,1)),'cmap':cm.get_cmap("gray_r"),'norm':colors.Normalize(vmin=0,vmax=10)})

        self.__deepLevelOrbitPlotted=True

    def __updateDeepLevelOrbits(self,rChild):
        if self.__deepLevelOrbitPlotted:
            try:
                self.gRescalingLevels.update()
            except:
                self.__deepLevelOrbitPlotted=False
                raise
        else:
            self.__plotDeepLevelOrbits()

    def __removeDeepLevelOrbits(self):
        self.gRescalingLevels=None
        self.__deepLevelOrbitPlotted=False
    
    def _iRescaling(self,y):
    # The inverse function of nonlinear rescaling
        if not (-1.0<y and y<1.0):
            raise ValueError("_iRescaling: Unable to compute the inverse rescaling. The value ",str(y)," is out of bound")

        y1=self._r_si(y)
            
        def solve(x):
            return self.function.iterates(x,iteration=self.period-1)-y1
        return optimize.brenth(solve, self.orbit_alpha1[0],self.orbit_Alpha1[0])

    def _updateRescalingLevels(self,rChild, level=None):
        updated=False
        
        if self.levels_alpha is None:
            self.levels_alpha=[self.function.p_a,self.orbit_alpha1[0]]
            self.levels_Alpha=[self.function.p_A,self.orbit_Alpha1[0]]
            self.levels_beta=[self.function.p_b,self.orbit_beta1[0]]
            self.levels_Beta=[self.function.p_B,self.orbit_Beta1[0]]
            updated=True

        i=len(self.levels_alpha)
        
        # update the list of the periodic points if new renormalization level is available
        while i-1 < len(rChild.levels_alpha) and i <= self.config.figureMaxLevels:
            self.levels_alpha.append(self._iRescaling(rChild.levels_alpha[i-1]))
            self.levels_Alpha.append(self._iRescaling(rChild.levels_Alpha[i-1]))
            self.levels_beta.append(self._iRescaling(rChild.levels_beta[i-1]))
            self.levels_Beta.append(self._iRescaling(rChild.levels_Beta[i-1]))
            i=i+1
            updated=True
            
        return updated
    
    '''
    Events
    '''
    
    # User input
    # bug: does not update(remove) contour plot when deep level period is changed
    def periodChangedEvent(self, period:int):
        try:
            self.ui.canvas.setUpdatesEnabled(False)
            self.gFunctionIterates.update()
        except Exception as e:
            self.__logger.exception('Unable to update graph when the perios is changed. period: %s',period)
        finally:
            self.ui.canvas.setUpdatesEnabled(True)
            
        self.__checkRenormalizable()

    # unimodal map for the plot
    def functionChangedEvent(self, func:Unimodal):
        try:
            self.ui.canvas.setUpdatesEnabled(False)
            self.__updateCurrentLevel()
        except Exception as e:
            self.__logger.exception('Unable to update function. %s', func)
        finally:
            self.ui.canvas.setUpdatesEnabled(True)

        self.__checkRenormalizable()
    
    def __checkRenormalizable(self):
        renormalizable=self.__renormalizable(self.period)
        if renormalizable != self.renormalizable:
            self.setRenormalizable(renormalizable)
        elif renormalizable:
            self.rFunctionChangedEvent()
        
    def renormalizableChangedEvent(self,value):
        if value is True:
            try:
                self.ui.canvas.setUpdatesEnabled(False)
                self.__plotRenormalizableGraph()
            except Exception as e:
                self.__logger.exception('Unable to draw renormalizable graph.')
            finally:
                self.ui.canvas.setUpdatesEnabled(True)
        else:
            self.closeRChild()
            try:
                self.__removeRenormalizableGraph()
            except Exception as e:
                self.__logger.exception('Unable to remove renormalizable graph.')
            finally:
                self.ui.canvas.setUpdatesEnabled(True)

    def rFunctionChangedEvent(self):
        try:
            self.ui.canvas.setUpdatesEnabled(False)
            self.__updateRenormalizableGraph()
        except Exception as e:
            self.__logger.exception('Unable to update renormalizable graph.')
        finally:
            self.ui.canvas.setUpdatesEnabled(True)

        if self.rChild is not None:
            self._updateRChildEvent(self.rChild,self.period)

    ''' Periodic intervals and Trapping intervals '''
    # Periodic intervals and levels 
    orbit_alpha1=[]
    orbit_Alpha1=[]
    orbit_beta1=[]
    orbit_Beta1=[]
    def getOrbit_alpha1(self):
        return self.orbit_alpha1
    def getOrbit_Alpha1(self):
        return self.orbit_Alpha1
    def getOrbit_beta1(self):
        return self.orbit_beta1
    def getOrbit_Beta1(self):
        return self.orbit_Beta1

    # Find the periodic intervals
    # todo: exception
    def _findPeriodicInterval(self,period):
        if self._rFunc!=None:
            # build period intervals from the next level
            self.orbit_alpha1=self.function.p_a1[period]
            self.orbit_Alpha1=self.function.p_A1[period]
            self.orbit_beta1=self.function.orbit(self.function(self._r_si(self._rFunc.p_b)),period)
            self.orbit_Beta1=self.function.reflexOrbit(self.orbit_beta1)
        else:
            self.orbit_alpha1=[]
            self.orbit_Alpha1=[]
            self.orbit_beta1=[]
            self.orbit_Beta1=[]

        self.levels_alpha=None
        self.levels_Alpha=None
        self.levels_beta=None
        self.levels_Beta=None
    
    ''' Rescaling levels '''
    levels_alpha=[]
    levels_Alpha=[]
    levels_beta=[]
    levels_Beta=[]

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
            self.__logger.exception("Unable to renormalize. period:%s",str(period))
            self._rFunc=None
            self._r_s=None
            self._r_si=None
            return False

        if func_renormalize != None:
            (self._rFunc,self._r_s,self._r_si)=func_renormalize
            return True
        else:
            return False

    def __renormalizable(self, period):
        try:
            return self.function.renormalizable(period)
        except Exception as e:
            self.__logger.exception('Unable to check renormalizable')
            return False

    '''
    Child Events
    '''
   
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

        try:
            rChild=UnimodalWindow(self._rFunc, self.level+1, rParent=self, config=self.config)
            rChild.setWindowTitle("Level "+str(self.level+1))
            rChild.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            rChild.setParent(None)
            
            self._findPeriodicInterval(self.period)
            self._updateRescalingLevels(rChild)
        except Exception:
            self.__logger.exception('Unable to open child window. period: %s', period)
            return None
    
        try:
            self.ui.canvas.setUpdatesEnabled(False)
            self.__plotNextLevelOrbits()
            self.__plotDeepLevelOrbits(rChild)
        except Exception:
            self.__logger.exception('Unable to draw child graph. period: %s', period)
        finally:
            self.ui.canvas.setUpdatesEnabled(True)

        return rChild

    def _updateRChildEvent(self, rChild:UnimodalBaseWindow, period:int):
        if self.__renormalize(period) == True:
            # Update child
            try:
                rChild.setFunction(self._rFunc)
            except Exception:
                self.__logger.exception('Unable to update child window. period: %s', period)
                self.closeRChild()
                return
            
            try:
                self._findPeriodicInterval(self.period)
    
                self.__updateNextLevelOrbits()
                if self._updateRescalingLevels(rChild):
                    self.__updateDeepLevelOrbits(rChild)
            except Exception:
                self.__logger.exception('Unable to update child graph. period: %s', period)
        else:
            self.closeRChild()

    # Notified by the child whne a child is renormalized
    # called by child window
    def _descendantRenormalizedEvent(self, level, window):
        try:
            self.ui.canvas.setUpdatesEnabled(False)
            if self._updateRescalingLevels(self.rChild, level):
                self.__updateDeepLevelOrbits(self.rChild)
        except Exception:
            self.__logger.exception('Unable to update deep renormalization graph. period: %s', self.period)
        finally:
            self.ui.canvas.setUpdatesEnabled(True)

    # called when the child is closed.
    #isThisClosed=False
    def _closeRChildEvent(self):
        try:
            self.ui.canvas.setUpdatesEnabled(False)
            self.__removeNextLevelOrbits()
            self.__removeDeepLevelOrbits()
        except Exception:
            self.__logger.exception('Unable to update remove child graph. period: %s', self.period)
        finally:
            self.ui.canvas.setUpdatesEnabled(True)
        
        self._rFunc=None
        self._r_s=None
        self._r_si=None
        
        self.orbit_alpha1=[]
        self.orbit_Alpha1=[]
        self.orbit_beta1=[]
        self.orbit_Beta1=[]

        self.levels_alpha=[self.function.p_a]
        self.levels_Alpha=[self.function.p_A]
        self.levels_beta=[self.function.p_b]
        self.levels_Beta=[self.function.p_B]

        
def main():
    import Setting
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = UnimodalWindow(Unimodal(lambda x:Setting.func(x,Setting.parameterValue),Setting.func_c(Setting.parameterValue)))                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  