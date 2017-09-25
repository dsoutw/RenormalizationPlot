'''
Created on 2017/9/24

@author: dsou
'''
import numpy as np
from scipy.interpolate import CubicSpline
import time
import logging

from .unimodal import Unimodal
from .affine import Affine

class UnimodalRenormalized(Unimodal):
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
                sampleSize=0.001
                self._logger.warning('Machine precision exceeded. the unimodal function is approximated by intepolation')
            # Test speed
            elif end-start>self.config.interpolationThreshold:
                self._interpolated=True
                sampleSize=self.config.interpolationPrecision
                self._logger.warning('The unimodal map is approximated by intepolation to speed up the performance')

            if self._interpolated == True:
                try:
                    start = time.time()
                    sample=np.arange(np.float64(-1),np.float64(1),np.float64(sampleSize))
                    data=list(map(evaluate,sample))
                    end = time.time()
                    self._logger.info('Build data time: %s' % (end-start))
                    self.function=CubicSpline(sample, data, extrapolate=True)
                except:
                    self._logger.exception('Unable to approximate the map by interpolation')
                    self._interpolate=False
                
        #if self._interpolated == True:
        #    self.renormalize=super().renomalize
        #    self.iterates=super().iterates

    def renomalize(self, period:int=2):
        if self._interpolated == False:
            # check if the function is renormalizable
            if self.renormalizable(period):
                s=Affine(self._rescale2(self.p_a1[period][period-1]),np.float64(-1),self._rescale2(self.p_A1[period][period-1]),np.float64(1))
                s_i=Affine(np.float64(-1),self._rescale2(self.p_a1[period][period-1]),np.float64(1),self._rescale2(self.p_A1[period][period-1]))
                
                try:
                    r_f=UnimodalRenormalized(s, self._rawfunc, self._iterate*period, s_i, s(self._rescale2(self.p_c)),
                        config=self.config, signiture=self._signiture, level=self._level+[period])
                except Exception as e:
                    raise RuntimeError('Unable to created the renormalized map class. period=%s' % period) from e
                    
                return (r_f, 
                    Affine(self.p_a1[period][period-1],np.float64(-1),self.p_A1[period][period-1],np.float64(1)), 
                    Affine(np.float64(-1),self.p_a1[period][period-1],np.float64(1),self.p_A1[period][period-1])
                    )
            else:
                return None
        else:
            return super().renomalize(period)

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
