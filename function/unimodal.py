import numpy as np
#import copy
from scipy import optimize
from enum import Enum
import importlib
import logging

from .affine import Affine
from .functionbase import FunctionBase

class Renormalizable(Enum):
    under=False
    renormalizable=True
    above=False
    pass

class Unimodal(FunctionBase):
    """A unimodal class"""
    __TOL_EQUAL = np.float64(1e-02)
    
    function = None
    __renormalizable={}
    p_a1={}
    p_A1={}
    
    # critical point
    p_c=None
    p_v=None
    
    # name of the map
    _signiture=None
    _level=[]
    _logger=None
    
    def __map_solve(self, x, y):
        return self.function(x)-y

    def __init__(self,func,p_c,config=None,signiture=None,level:list=[]):
        global __TOL_EQUAL
        self.__loadConfig(config)

        self._signiture=signiture
        self._level=level
        
        _logger=logging.getLogger(__name__)
        
        #self.function = copy.deepcopy(func)
        self.function=func
        self.p_c = p_c
        
        self._setupVariable()
        super().__init__(1,logger=_logger)

    def __str__(self):
        name='Unimodal:%s' % self._signiture
        for period in self._level:
            name+=',%s' % period
        return name 
        
    # Todo: load to attr
    def __loadConfig(self,config):
        if config is None:
            self.config=importlib.import_module("Setting")
        else:
            self.config=config
        
    def _setupVariable(self):
        self.__renormalizable={}
        self.p_a1={}
        self.p_A1={}
        
        # Set critical value
        self.p_v=self.function(self.p_c)

        # Check if it is a unimodal function with the standard convention
        # i.e. -1=f(-1)=f(1)
        self.p_a=np.float64(-1.0)
        value=self.function(self.p_a)
        if not np.isclose(self.function(self.p_a),self.p_a,rtol=self.__TOL_EQUAL):
            self._logger.warning('f(-1) is far from -1: f(-1)=%s' % (value))
        
        # Check if f(-1)=1
        self.p_A=np.float64(1.0)
        value=self.function(self.p_A)
        if not np.isclose(value,self.p_a,rtol=self.__TOL_EQUAL):
            self._logger.warning('f(1) is far from -1: f(1)=%s' % (value))
        
        # Check if the unimodal map has a fixed point with negative multiplier
        # i.e f(c)>c (not guarentee that the fixed point is expanding)
        # One could use finite difference to check the point's derivative
        if self.function(self.p_c) < self.p_c:
            raise ValueError('Not a unimodal map: c>v')
        
        # Find beta fixed point
        try:
            self.p_b=optimize.brentq(lambda x: self.function(x)-x, self.p_c, self.p_A, xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError('Unable to find beta fixed point\n') from e
        try:
            self.p_B=optimize.brentq(self.__map_solve, self.p_a, self.p_c, args=(self.p_b,), xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError('Unable to find beta_bar point') from e
        try:
            self.p_B2=optimize.brentq(self.__map_solve, self.p_b, self.p_A, args=(self.p_B,), xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError('Unable to find beta_2bar point') from e
    
    ''' Renormalization Tools '''

    def renormalizable(self, period:int=2):
        '''
        Check if the unimodal function is renormalizable
        :param period: the period of renormalization
        :type period: positive integer
        '''
        if period not in self.__renormalizable:
            if period == 2:
                self.__renormalizable[period]=self.renormalizable2()
            else:
                self.__renormalizable[period]=self.renomalizableOther(period)
        return self.__renormalizable[period]

    def renomalize(self, period:int=2):
        '''
        Renormalize the unimodal map
        @param period: The period of the self-return map
        @type period: positive integer
        '''
        # check if the function is renormalizable
        if self.renormalizable(period):
            s=Affine(self.p_a1[period][period-1],np.float64(-1),self.p_A1[period][period-1],np.float64(1))
            s_i=Affine(np.float64(-1),self.p_a1[period][period-1],np.float64(1),self.p_A1[period][period-1])
            #return Unimodal(lambda x: s(self.function(self.function(s_i(x)))),s(self.p_c))

            try:
                r_f=UnimodalRenormalized(s, self.function, period, s_i, s(self.p_c), 
                    config=self.config, signiture=self._signiture, level=self._level+[period])
            except Exception as e:
                raise RuntimeError('Unable to created the renormalized map class. period=%s' % period) from e
            
            return r_f, s, s_i
        else:
            return None

    def renormalizable2(self):
        '''
        Check if the unimodal map is period-doubling renormalizable
        :return: enum Renormalizable
        '''
        # The condition f(v) < c ensures that there exists a fixed point with negative multiplier
        if not self.p_b < self.p_v:
            #return Renormalizable.under
            return False
        if not self.function(self.p_v) < self.p_c:
            #return Renormalizable.under
            return False
        if not self.p_v < self.p_B2:
            #return Renormalizable.above
            return False
            
        self.p_a1[2]=[self.p_b,self.p_b]
        self.p_A1[2]=[self.p_B2,self.p_B]
        
        #return Renormalizable.renormalizable
        return True

    
    def renomalizableOther(self,period):
        # period doubling renormalizable
        if self.p_v < self.p_c:
            return False
        if period % 2 == 1:
            if self.p_v < self.p_B2:
                return False
        
        # Find all critical points
        otherLocalExtremals=[]
        maximalPoints=[self.p_c]    # abs max
        
        try:
            for t in range(period-1):
                otherLocalExtremals=otherLocalExtremals+maximalPoints
                maximalPoints=self.preimage(maximalPoints)
        except Exception as e:
            raise RuntimeError('Unable to find the preimages of the critical orbits') from e

        # Search for the periodic points
        maximalPoints=[x for x in maximalPoints if self.p_B<x and x<self.p_v]
        if len(maximalPoints) < 1:
            return False
        maxPoint=max(maximalPoints)
        otherLocalExtremals=[x for x in otherLocalExtremals if self.p_B<x and x<maxPoint]
        if len(otherLocalExtremals) < 1:
            return False
        minPoint=max(otherLocalExtremals)
        # todo: check precisioncy
        #if (maxPoint-minPoint)/minPoint<self.config.precisionPeriodicA:
        #    print("Insufficient precisioncy")

        # Test min point
        if period%2 ==0:
            if minPoint<self.p_b:
                # Avoid finding a fixed point
                return False
        else:
            if minPoint<self.p_B:
                return False

        # The root is the periodic point
        def __iteration(x):
            return self.iterates(x, period)-x
        
        #if not __iteration(maxPoint) > 0:
        #    return False
        if not __iteration(minPoint) < 0:
            return False
        
        # Find periodic orbit
        try:
            tol=np.square(np.abs(maxPoint-minPoint))*self.config.precisionPeriodicA/2
            periodicPoint=optimize.brentq(__iteration, minPoint, maxPoint, xtol=tol, rtol=self.config.precisionPeriodicR)
            #print("periodic point: ",periodicPoint, "    critical value:",self.p_v)
            periodicOrbit=self.orbit(periodicPoint, period)
        except Exception as e:
            raise RuntimeError('Cannot find the periodic orbit. period=%s' % period) from e
            
        # Find periodic intervals
        try:
            periodicReflex=self.reflexOrbit(periodicOrbit,tol)
        except Exception as e:
            raise RuntimeError('Cannot find the periodic intervals. period=%s' % period) from e

        # check if the interval defines a self return map
        if periodicReflex[0] < self.p_v:
            return False
        
        self.p_a1[period]=periodicOrbit
        self.p_A1[period]=periodicReflex
        return True
        
    ''' Orbit tools '''
    
    def orbit(self, point, length:int):
        '''
        Build an orbit starting from point
        @param point: point
        @type point:
        @param length: length of the orbit
        @type length:
        '''
        p_orbit=[None]*length
        p_orbit[0]=point
        for t in range(1,length):
            point=self.function(point)
            p_orbit[t]=point
        return p_orbit
    
    
    def reflexOrbit(self, p_inOrbit, absError=None):
        '''
        Build an orbit that is a reflection of the input periodic orbit
        The input and output orbits will satisfies the relation 
           The two points p_inOrbit[j] and p_outOrbit[j] have same orientation for j<len-1
           The two points p_inOrbit[len-1] and p_outOrbit[len-1] have opposite orientation
           p_inOrbit[0]=f(p_inOrbit[len-1])=f(p_outOrbit[len-1])
        @param p_inOrbit: input orbit
        @type p_inOrbit: list of points
        @param absError:
        @type absError: float
        '''
        if absError is None:
            absError=self.config.precisionPeriodicA

        period=len(p_inOrbit)
        p_outOrbit=[None]*period

        try:
            point=p_inOrbit[0]        
            # Build p-1
            if p_inOrbit[period-1] < self.p_c:
                point=optimize.brentq(lambda x: self.function(x)-point,self.p_c,self.p_A, xtol=absError, rtol=self.config.precisionPeriodicR)
            else:
                point=optimize.brentq(lambda x: self.function(x)-point,self.p_a,self.p_c, xtol=absError, rtol=self.config.precisionPeriodicR)
            p_outOrbit[period-1]=point
            
            t=period-2
            while t >= 0:
                if p_inOrbit[t] < self.p_c:
                    point=optimize.brentq(lambda x: self.function(x)-point,self.p_a,self.p_c, xtol=absError, rtol=self.config.precisionPeriodicR)
                else:
                    point=optimize.brentq(lambda x: self.function(x)-point,self.p_c,self.p_A, xtol=absError, rtol=self.config.precisionPeriodicR)
                p_outOrbit[t]=point
                t=t-1
        except Exception as e:
            raise RuntimeError('Unable to reflex the orbit: %s' % p_inOrbit) from e
        
        return p_outOrbit
    
    def preimage(self,points):
        '''
        Find all preimages of a point or a list of points
        :param points: point(s) to find the preimages
        :type points: float or a list of floats
        '''
        result=[]
        if not isinstance(points, list):
            points=[points]
            
        try:
            for pt in points:
                if pt < self.p_v:
                    result.append(optimize.brentq(lambda x: self.function(x)-pt,self.p_a,self.p_c, xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR))
                    result.append(optimize.brentq(lambda x: self.function(x)-pt,self.p_c,self.p_A, xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR))
        except Exception as e:
            raise RuntimeError('[%s] Unable to find the preimage of: %s' % (self,points)) from e

        return result
    
from .unimodalrenormalized import UnimodalRenormalized

