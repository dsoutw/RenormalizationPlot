import numpy as np
#import copy
from scipy import optimize
#from scipy.misc import derivative
from scipy.interpolate import interp1d
import time
#import timeit
#import traceback
from enum import Enum
import importlib

from function.affine import Affine
from function.functionbase import FunctionBase

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
    
    def __map_solve(self, x, y):
        return self.function(x)-y

    def __init__(self,func,p_c,config=None):
        global __TOL_EQUAL
        self.__loadConfig(config)

        #self.function = copy.deepcopy(func)
        self.function=func
        self.p_c = p_c
        
        self._setupVariable()
        super().__init__(1)

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
        #val=self.function(self.p_a)
        #if not np.isclose(self.function(self.p_a),self.p_a,rtol=self.__TOL_EQUAL):
        #    raise ValueError('Not a unimodal map: f(-1)=',val)
            
        self.p_A=np.float64(1.0)
        #if not np.isclose(self.function(self.p_A),self.p_a,rtol=self.__TOL_EQUAL):
        #    raise ValueError('Not a unimodal map')
        
        # Check if the unimodal map has a fixed point with negative multiplier
        # i.e f(c)>c (not guarentee that the fixed point is expanding)
        # One could use finite difference to check the point's derivative
        if self.function(self.p_c) < self.p_c:
            raise ValueError('Not a unimodal map: c>v')
        
        # Find beta fixed point
        #self.p_b=optimize.fixed_point(self.function, (self.p_c+self.p_A)/np.float64(2))
        try:
            self.p_b=optimize.brentq(lambda x: self.function(x)-x, self.p_c, self.p_A, xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError("Unimodal.__init__: Unable to find beta fixed point\n"+str(e))
        try:
            self.p_B=optimize.brentq(self.__map_solve, self.p_a, self.p_c, args=(self.p_b,), xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError("Unimodal.__init__: Unable to find beta_bar point"+str(e))
        try:
            self.p_B2=optimize.brentq(self.__map_solve, self.p_b, self.p_A, args=(self.p_B,), xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError("Unimodal.__init__: Unable to find beta_2bar point"+str(e))
        

    def renormalizable(self, period:int=2):
        '''
        Check if the unimodal function is renormalizable
        :param period: the period of renormalization
        :type period: positive integer
        '''
        if period not in self.__renormalizable:
            if period == 2:
                self.__renormalizable[period]=self.renormalizable2()
            #elif period % 2 == 1:
            else:
                self.__renormalizable[period]=self.renomalizableOther(period)
            #else:
                # Not implimented
            #    self.__renormalizable[period]=False
        return self.__renormalizable[period]

    def renomalize(self, period:int=2, logger=None):
        # check if the function is renormalizable
        if self.renormalizable(period):
            s=Affine(self.p_a1[period][period-1],np.float64(-1),self.p_A1[period][period-1],np.float64(1))
            s_i=Affine(np.float64(-1),self.p_a1[period][period-1],np.float64(1),self.p_A1[period][period-1])
            #return Unimodal(lambda x: s(self.function(self.function(s_i(x)))),s(self.p_c))

            return UnimodalRescaleIterate(s, self.function, period, s_i, s(self.p_c), config=self.config), s, s_i
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

    def renomalize2(self):
        # check if the function is renormalizable
        if self.renormalizable2():
            s=Affine(self.p_b,np.float64(-1),self.p_B,np.float64(1))
            s_i=Affine(np.float64(-1),self.p_b,np.float64(1),self.p_B)
            #return Unimodal(lambda x: s(self.function(self.function(s_i(x)))),s(self.p_c))

            return UnimodalRescaleIterate(s, self.function, 2, s_i, s(self.p_c)), s, s_i
        else:
            return None
    
    # todo
    def renomalizableOther(self,period):
        
        # period doubling renormalizable
        if self.p_v < self.p_c:
            return False
        if period % 2 == 1:
            if self.p_v < self.p_B2:
                return False
        
        # Find all critical points
        otherLocalExtremals=[]
        maximalPoints=[self.p_c]
        
        for t in range(period-1):
            otherLocalExtremals=otherLocalExtremals+maximalPoints
            maximalPoints=self.preimage(maximalPoints)

        # Search for the periodic points
        maximalPoints=[x for x in maximalPoints if self.p_B<x and x<self.p_v]
        if len(maximalPoints) < 1:
            return False
        maxPoint=max(maximalPoints)
        otherLocalExtremals=[x for x in otherLocalExtremals if self.p_B<x and x<maxPoint]
        if len(otherLocalExtremals) < 1:
            return False
        minPoint=max(otherLocalExtremals)
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
        
        tol=np.square(np.abs(maxPoint-minPoint))*self.config.precisionPeriodicA/2
        periodicPoint=optimize.brentq(__iteration, minPoint, maxPoint, xtol=tol, rtol=self.config.precisionPeriodicR)
        #print("periodic point: ",periodicPoint, "    critical value:",self.p_v)
        periodicOrbit=self.orbit(periodicPoint, period)
        #print(periodicOrbit)
        try:
            periodicReflex=self.reflexOrbit(periodicOrbit,tol)
        except BaseException as e:
            print("Unimodal: renomalizableOther: Cannot find reflex orbit")
            print(str(e))
            return False
        #print("periodic point: ",periodicPoint, "    critical value:",self.p_v,"    reflection:",periodicReflex[0])

        # check if the interval defines a self return map
        if periodicReflex[0] < self.p_v:
            return False
        
        self.p_a1[period]=periodicOrbit
        self.p_A1[period]=periodicReflex
        return True
        
#         try:
#             fp=optimize.fixed_point(self.iterates, self.p_v, args=(period,))
#             periodicOrbit=self.orbit(fp, period)
#             periodicPoint=max(periodicOrbit)
#             print("periodic point: ",periodicPoint, "    critical value:",self.p_v)
#             return False
#         except BaseException as e:
#             print(str(e))
#             return False
    

    # Orbit tools
    
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
    
    
    # Build an orbit that is a reflection of the input periodic orbit
    # The input and output orbits will satisfies the relation 
    #    The two points p_inOrbit[j] and p_outOrbit[j] have same orientation for j<len-1
    #    The two points p_inOrbit[len-1] and p_outOrbit[len-1] have opposite orientation
    #    p_inOrbit[0]=f(p_inOrbit[len-1])=f(p_outOrbit[len-1])
    def reflexOrbit(self, p_inOrbit, absError=None):
        if absError is None:
            absError=self.config.precisionPeriodicA
            
        period=len(p_inOrbit)
        p_outOrbit=[None]*period

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
            
        for pt in points:
            if pt < self.p_v:
                result.append(optimize.brentq(lambda x: self.function(x)-pt,self.p_a,self.p_c, xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR))
                result.append(optimize.brentq(lambda x: self.function(x)-pt,self.p_c,self.p_A, xtol=self.config.precisionPeriodicA, rtol=self.config.precisionPeriodicR))

        return result
    
class UnimodalRescaleIterate(Unimodal):
    _rescale1=None
    _rescale2=None
    _rawfunc=None
    _iterate=None
    _interpolated=False
    
    def __init__(self, rescale1, func, iterate:int, rescale2, p_c, *args, **kwargs):
        self._rescale1=rescale1
        self._rescale2=rescale2
        self._rawfunc=func
        self._iterate=iterate
        self._interpolated=False
        
        def evaluate(x):
            x=rescale2(x)
            for i in range(iterate):
                x=func(x)
            return rescale1(x)
        
        start = time.time()
        super().__init__(evaluate, p_c, *args, **kwargs)
        end = time.time()

        if self.config.interpolationEnabled == True:
            # Test machine error
            #print(np.finfo(np.float64).eps)
            #print(np.absolute(self._rescale1.x1-self._rescale1.x2))
            #print(iterate)
            #print("rel error",np.finfo(np.float64).eps/np.absolute(self._rescale1.x1-self._rescale1.x2))
            machineError=(np.power(np.finfo(np.float64).eps*10/np.absolute(self._rescale1.x1-self._rescale1.x2)+1,iterate)-1)*1000
            #print("guess",machineError)
            #print(isinstance(self._rescale1.x1, np.float64))
            if machineError>self.config.interpolationPrecision:
                self._interpolated=True
                sampleSize=machineError*10
                print("Warning: machine precision exceeded. the unimodal function is approximated by intepolation")
            # Test speed
            elif end-start>self.config.interpolationThreshold:
                self._interpolated=True
                sampleSize=self.config.interpolationPrecision
                print("Warning: the unimodal function is approximated by intepolation to speed up the performance")

                
            if self._interpolated == True:
                sample=np.arange(np.float64(-1),np.float64(1),np.float64(sampleSize))
                data=evaluate(sample)
                self.function=interp1d(sample, data, kind='cubic', fill_value='extrapolate')
                
        #if self._interpolated == True:
        #    self.renormalize=super().renomalize
        #    self.iterates=super().iterates

    def renomalize(self, period:int=2):
        if self._interpolated == False:
            # check if the function is renormalizable
            if self.renormalizable(period):
                s=Affine(self._rescale2(self.p_a1[period][period-1]),np.float64(-1),self._rescale2(self.p_A1[period][period-1]),np.float64(1))
                s_i=Affine(np.float64(-1),self._rescale2(self.p_a1[period][period-1]),np.float64(1),self._rescale2(self.p_A1[period][period-1]))
                return (UnimodalRescaleIterate(s, self._rawfunc, self._iterate*period, s_i, s(self._rescale2(self.p_c)), config=self.config), 
                    Affine(self.p_a1[period][period-1],np.float64(-1),self.p_A1[period][period-1],np.float64(1)), 
                    Affine(np.float64(-1),self.p_a1[period][period-1],np.float64(1),self.p_A1[period][period-1])
                    )
            else:
                return None
        else:
            return super().renomalize(period)

    def renomalize2(self):
        # check if the function is renormalizable
        if self.renormalizable2():
            s=Affine(self._rescale2(self.p_b),np.float64(-1),self._rescale2(self.p_B),np.float64(1))
            s_i=Affine(np.float64(-1),self._rescale2(self.p_b),np.float64(1),self._rescale2(self.p_B))
            #return Unimodal(lambda x: s(self.function(self.function(s_i(x)))),s(self.p_c))
            rfunc=UnimodalRescaleIterate(s, self._rawfunc, self._iterate*2, s_i, s(self._rescale2(self.p_c)))
            
            # test the evaluation time for the function
            # if the time exceed the threshold, then cache the data by interpolation
            #if self.config.interpolationEnabled == True:
            #    x=s(self._rescale2(self.p_c))
            #    start = time.time()
            #    for i in range(100):
            #        x=rfunc(x)
            #    end = time.time()
            #    
            #    if end-start > self.config.interpolationThreshold:
            #        sample=np.arange(np.float64(-1),np.float64(1),np.float64(self.config.interpolationPrecision))
            #        data=self.function(sample)
            #        rfunc=Unimodal(interp1d(sample, data, kind='cubic', fill_value='extrapolate'),s(self._rescale2(self.p_c)))
            #        print("Warning: the unimodal function is approximated by intepolation to speed up the performance")
                
            return rfunc, Affine(self.p_b,np.float64(-1),self.p_B,np.float64(1)), Affine(np.float64(-1),self.p_b,np.float64(1),self.p_B)

        else:
            return None
                       
    # repeat iterate the unimodal function p-times
    def iterates(self, x, iteration:int):
        if self._interpolated == False:
            _rawfunc=self._rawfunc
            x=self._rescale2(x)
            for i in range(self._iterate*iteration):
                x=_rawfunc(x)
            return self._rescale1(x)
        else:
            return super().iterates(x, iteration)
