'''
Created on 2017/9/20

@author: dsou
'''
from .functionbase import FunctionBase 

class Affine(FunctionBase):
    def __init__(self, x1, y1, x2, y2):
        '''
        Affine map that intersects (x1,y1) and (x2,y2)
        @param x1:
        @type x1: float
        @param y1:
        @type y1: float
        @param x2:
        @type x2: float
        @param y2:
        @type y2: float
        '''
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.slope=(self.y1-self.y2)/(self.x1-self.x2)

        super().__init__(1)

    def function(self, x):
        return (x-self.x2)*self.slope+self.y2
