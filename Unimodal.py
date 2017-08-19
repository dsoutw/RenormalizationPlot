import numpy as np
import copy
from scipy import optimize
from scipy.misc import derivative
from scipy.interpolate import interp1d
import time
import Setting

#import error

class Affine:
    def __init__(self, x1, y1, x2, y2):
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2

    def __call__(self, x):
        return (x-self.x2)*(self.y1-self.y2)/(self.x1-self.x2)+self.y2
    
class Unimodal:
    """A simple example class"""
    __TOL_EQUAL = np.float64(1e-05)
    #_map = None
    def __map_solve(self, x, y):
        return self._map(x)-y

    def __init__(self,func,p_c):
        global __TOL_EQUAL

        self._map = copy.deepcopy(func)
        self.p_c = p_c
        
        # Check if it is a unimodal map with the standard convention
        # i.e. -1=f(-1)=f(1)
        
        self.p_a=np.float64(-1.0)
        if not np.isclose(self._map(self.p_a),self.p_a,rtol=self.__TOL_EQUAL):
            raise ValueError('Not a unimodal map')
            
        self.p_A=np.float64(1.0)
        #if not np.isclose(self._map(self.p_A),self.p_a,rtol=self.__TOL_EQUAL):
        #    raise ValueError('Not a unimodal map')
        
        # Check if the unimodal map has a fixed point with negative multiplier
        # i.e f(c)>c (not guarentee that the fixed point is expanding)
        # One could use finite difference to check the point's derivative
        if self._map(self.p_c) < self.p_c:
            raise ValueError('Not a unimodal map')
        
        # Set critical value
        self.p_v=self(self.p_c)
        
        # Find beta fixed point
        self.p_b=optimize.fixed_point(self._map, (self.p_c+self.p_A)/np.float64(2))
        self.p_B=optimize.brenth(self.__map_solve, self.p_a, self.p_c, args=(self.p_b,))
        self.p_B2=optimize.brenth(self.__map_solve, self.p_b, self.p_A, args=(self.p_B,))
        
    def __call__(self, x):
        return self._map(x)

    def renomalizable(self, period=2):
        if period == 2:
            return self.renomalizable2()
        else:
            return self.renomalizableOther(period)

    def renomalize(self, period=2):
        if period == 2:
            return self.renomalize2()
        else:
            return self.renomalizeOther(period)
    
    def renomalizable2(self):
        # The condition f(v) < c ensures that there exists a fixed point with negative multiplier
        return self.p_b < self.p_v and self.p_v < self.p_B2 and self._map(self.p_v) < self.p_c

    def renomalize2(self):
        # check if the function is renormalizable
        if self.renomalizable2():
            s=Affine(self.p_b,np.float64(-1),self.p_B,np.float64(1))
            s_i=Affine(np.float64(-1),self.p_b,np.float64(1),self.p_B)
            #return Unimodal(lambda x: s(self._map(self._map(s_i(x)))),s(self.p_c))

            return UnimodalRescaleIterate(s, self._map, 2, s_i, s(self.p_c))
        else:
            return None
    
    # todo
    def renomalizableOther(self,period):
        return False
    
    # todo
    def renomalizeOther(self,period):
        pass
    
class UnimodalRescaleIterate(Unimodal):
    def __init__(self, rescale1, func, iterate, rescale2, p_c):
        self._rescale1=rescale1
        self._rescale2=rescale2
        self._rawfunc=func
        self._iterate=iterate
        
        def evaluate(x):
            x=rescale2(x)
            for i in range(iterate):
                x=func(x)
            return rescale1(x)
        
        super().__init__(evaluate, p_c)
                
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
                
            return rfunc

        else:
            return None
        
