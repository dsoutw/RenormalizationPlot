import numpy as np
import copy
from scipy import optimize
#from scipy.misc import derivative
from scipy.interpolate import interp1d
import time
#import timeit
import Setting
import traceback
from enum import Enum

class Renormalizable(Enum):
    under=False
    renormalizable=True
    above=False
    pass

class Affine:
    def __init__(self, x1, y1, x2, y2):
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2

    def __call__(self, x):
        return (x-self.x2)*(self.y1-self.y2)/(self.x1-self.x2)+self.y2

def fixedPoint(func):
    pass
# 
class Unimodal:
    """A unimodal class"""
    __TOL_EQUAL = np.float64(1e-02)
    
    _map = None
    _renormalizable={}
    p_a1={}
    p_A1={}
    
    # critical point
    p_c=None
    p_v=None
    
    def __map_solve(self, x, y):
        return self._map(x)-y

    def __init__(self,func,p_c):
        global __TOL_EQUAL

        self._map = copy.deepcopy(func)
        #self._map=func
        self.p_c = p_c
        
        self._setupVariable()
        
        
    def _setupVariable(self):
        self._renormalizable={}
        self.p_a1={}
        self.p_A1={}
        
        # Set critical value
        self.p_v=self(self.p_c)

        # Check if it is a unimodal map with the standard convention
        # i.e. -1=f(-1)=f(1)
        self.p_a=np.float64(-1.0)
        val=self._map(self.p_a)
        if not np.isclose(self._map(self.p_a),self.p_a,rtol=self.__TOL_EQUAL):
            print(val)
            raise ValueError('Not a unimodal map: f(-1)=',val)
            
        self.p_A=np.float64(1.0)
        #if not np.isclose(self._map(self.p_A),self.p_a,rtol=self.__TOL_EQUAL):
        #    raise ValueError('Not a unimodal map')
        
        # Check if the unimodal map has a fixed point with negative multiplier
        # i.e f(c)>c (not guarentee that the fixed point is expanding)
        # One could use finite difference to check the point's derivative
        if self._map(self.p_c) < self.p_c:
            raise ValueError('Not a unimodal map: c>v')
        
        # Find beta fixed point
        #self.p_b=optimize.fixed_point(self._map, (self.p_c+self.p_A)/np.float64(2))
        try:
            self.p_b=optimize.brenth(lambda x: self._map(x)-x, self.p_c, self.p_A, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError("Unimodal.__init__: Unable to find beta fixed point\n"+str(e))
        try:
            self.p_B=optimize.brenth(self.__map_solve, self.p_a, self.p_c, args=(self.p_b,), xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError("Unimodal.__init__: Unable to find beta_bar point"+str(e))
        try:
            self.p_B2=optimize.brenth(self.__map_solve, self.p_b, self.p_A, args=(self.p_B,), xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
        except BaseException as e:
            raise RuntimeError("Unimodal.__init__: Unable to find beta_2bar point"+str(e))
        
    def __call__(self, x):
        return self._map(x)

    # repeat iterate the unimodal map p-times
    def iterates(self, x, p):
        '''
        Evaluate the iterates of the unimodal map
        :param x: point to be evaluated
        :type x: float
        :param p: number of iterates
        :type p: nonnegative integer
        '''
        for t in range(p):
            x=self._map(x)
        return x
    
    def renomalizable(self, period=2):
        '''
        Check if the unimodal map is renormalizable
        :param period: the period of renormalization
        :type period: positive integer
        '''
        if period not in self._renormalizable:
            if period == 2:
                self._renormalizable[period]=self.renomalizable2()
            elif period % 2 == 1:
                self._renormalizable[period]=self.renomalizableOdd(period)
            else:
                # Not implimented
                self._renormalizable[period]=False
        return self._renormalizable[period]

    def renomalize(self, period=2):
        # check if the function is renormalizable
        if self.renomalizable(period):
            s=Affine(self.p_a1[period][period-1],np.float64(-1),self.p_A1[period][period-1],np.float64(1))
            s_i=Affine(np.float64(-1),self.p_a1[period][period-1],np.float64(1),self.p_A1[period][period-1])
            #return Unimodal(lambda x: s(self._map(self._map(s_i(x)))),s(self.p_c))

            return UnimodalRescaleIterate(s, self._map, period, s_i, s(self.p_c)), s, s_i
        else:
            return None

#         if period == 2:
#             return self.renomalize2()
#         else:
#             return self.renomalizeOther(period)
    
    def renomalizable2(self):
        '''
        Check if the unimodal map is period-doubling renormalizable
        :return: enum Renormalizable
        '''
        # The condition f(v) < c ensures that there exists a fixed point with negative multiplier
        if not self.p_b < self.p_v:
            #return Renormalizable.under
            return False
        if not self._map(self.p_v) < self.p_c:
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
        if self.renomalizable2():
            s=Affine(self.p_b,np.float64(-1),self.p_B,np.float64(1))
            s_i=Affine(np.float64(-1),self.p_b,np.float64(1),self.p_B)
            #return Unimodal(lambda x: s(self._map(self._map(s_i(x)))),s(self.p_c))

            return UnimodalRescaleIterate(s, self._map, 2, s_i, s(self.p_c)), s, s_i
        else:
            return None
    
    # todo
    def renomalizableOdd(self,period):
        
        # period doubling renormalizable
        if self.p_v < self.p_B2:
            return False
        
        # Find all critical points
        otherLocalExtremals=[]
        maximalPoints=[self.p_c]
        
        for t in range(period-1):
            otherLocalExtremals=otherLocalExtremals+maximalPoints
            maximalPoints=self.preimage(maximalPoints)

        # Search for the periodic points
        maximalPoints=[x for x in maximalPoints if x<self.p_v]
        otherLocalExtremals=[x for x in otherLocalExtremals if x<self.p_v]
        maxPoint=max(maximalPoints)
        minPoint=max(otherLocalExtremals)
        #print("max:", maxPoint, ", min:", minPoint)

        def __iteration(x):
            y=x
            for t in range(period):
                y=self._map(y)
            return y-x
        
        # need f^p(c)>c => __iteration(minPoint) > 0
        #if not maxPoint < self.p_v:
        if not __iteration(maxPoint) > 0:
            return False
        if not __iteration(minPoint) < 0:
            return False
        
        periodicPoint=optimize.brenth(__iteration, minPoint, maxPoint, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
        #print("periodic point: ",periodicPoint, "    critical value:",self.p_v)
        periodicOrbit=self.orbit(periodicPoint, period)
        periodicReflex=self.reflexOrbit(periodicOrbit)
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
    
    def orbit(self,point,length):
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
            point=self._map(point)
            p_orbit[t]=point
        return p_orbit
    
    
    # Build an orbit that is a reflection of the input periodic orbit
    # The input and output orbits will satisfies the relation 
    #    The two points p_inOrbit[j] and p_outOrbit[j] have same orientation for j<len-1
    #    The two points p_inOrbit[len-1] and p_outOrbit[len-1] have opposite orientation
    #    p_inOrbit[0]=f(p_inOrbit[len-1])=f(p_outOrbit[len-1])
    def reflexOrbit(self, p_inOrbit):
        period=len(p_inOrbit)
        p_outOrbit=[None]*period

        point=p_inOrbit[0]        
        # Build p-1
        if p_inOrbit[period-1] < self.p_c:
            point=optimize.brenth(lambda x: self._map(x)-point,self.p_c,self.p_A, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
        else:
            point=optimize.brenth(lambda x: self._map(x)-point,self.p_a,self.p_c, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
        p_outOrbit[period-1]=point
        
        t=period-2
        while t >= 0:
            if p_inOrbit[t] < self.p_c:
                point=optimize.brenth(lambda x: self._map(x)-point,self.p_a,self.p_c, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
            else:
                point=optimize.brenth(lambda x: self._map(x)-point,self.p_c,self.p_A, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR)
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
                result.append(optimize.brenth(lambda x: self._map(x)-pt,self.p_a,self.p_c, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR))
                result.append(optimize.brenth(lambda x: self._map(x)-pt,self.p_c,self.p_A, xtol=Setting.precisionPeriodicA, rtol=Setting.precisionPeriodicR))

        return result
    
class UnimodalRescaleIterate(Unimodal):
    _rescale1=None
    _rescale2=None
    _rawfunc=None
    _iterate=None
    _interpolated=False
    
    def __init__(self, rescale1, func, iterate, rescale2, p_c):
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
        super().__init__(evaluate, p_c)
        end = time.time()

        if Setting.interpolationEnabled == True:
            if end-start>Setting.interpolationThreshold:
                sample=np.arange(np.float64(-1),np.float64(1),np.float64(Setting.interpolationPrecision))
                data=evaluate(sample)
                self._map=interp1d(sample, data, kind='cubic', fill_value='extrapolate')
                self._interpolated=True
                print("Warning: the unimodal map is approximated by intepolation to speed up the performance")
                
        #if self._interpolated == True:
        #    self.renormalize=super().renomalize
        #    self.iterates=super().iterates

    def renomalize(self, period=2):
        if self._interpolated == False:
            # check if the function is renormalizable
            if self.renomalizable(period):
                s=Affine(self._rescale2(self.p_a1[period][period-1]),np.float64(-1),self._rescale2(self.p_A1[period][period-1]),np.float64(1))
                s_i=Affine(np.float64(-1),self._rescale2(self.p_a1[period][period-1]),np.float64(1),self._rescale2(self.p_A1[period][period-1]))
                return UnimodalRescaleIterate(s, self._rawfunc, self._iterate*period, s_i, s(self._rescale2(self.p_c))), Affine(self.p_a1[period][period-1],np.float64(-1),self.p_A1[period][period-1],np.float64(1)), Affine(np.float64(-1),self.p_b,np.float64(1),self.p_B)
            else:
                return None
        else:
            return super().renomalize(period)

    def renomalize2(self):
        # check if the function is renormalizable
        if self.renomalizable2():
            s=Affine(self._rescale2(self.p_b),np.float64(-1),self._rescale2(self.p_B),np.float64(1))
            s_i=Affine(np.float64(-1),self._rescale2(self.p_b),np.float64(1),self._rescale2(self.p_B))
            #return Unimodal(lambda x: s(self._map(self._map(s_i(x)))),s(self.p_c))
            rfunc=UnimodalRescaleIterate(s, self._rawfunc, self._iterate*2, s_i, s(self._rescale2(self.p_c)))
            
            # test the evaluation time for the function
            # if the time exceed the threshold, then cache the data by interpolation
            if Setting.interpolationEnabled == True:
                x=s(self._rescale2(self.p_c))
                start = time.time()
                for i in range(100):
                    x=rfunc(x)
                end = time.time()
                
                if end-start > Setting.interpolationThreshold:
                    sample=np.arange(np.float64(-1),np.float64(1),np.float64(Setting.interpolationPrecision))
                    data=self._map(sample)
                    rfunc=Unimodal(interp1d(sample, data, kind='cubic', fill_value='extrapolate'),s(self._rescale2(self.p_c)))
                    print("Warning: the unimodal map is approximated by intepolation to speed up the performance")
                
            return rfunc, Affine(self.p_b,np.float64(-1),self.p_B,np.float64(1)), Affine(np.float64(-1),self.p_b,np.float64(1),self.p_B)

        else:
            return None
                       
    # repeat iterate the unimodal map p-times
    def iterates(self, x, p):
        if self._interpolated == False:
            x=self._rescale2(x)
            for i in range(self._iterate*p):
                x=self._rawfunc(x)
            return self._rescale1(x)
        else:
            return super().iterates(x, p)
