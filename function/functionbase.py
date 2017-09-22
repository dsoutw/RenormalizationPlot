'''
Created on 2017/9/20

@author: dsou
'''
#from abc import ABCMeta,abstractmethod
from abc import ABCMeta,abstractmethod

class FunctionBaseMeta(ABCMeta):
    def __init__(self, name, bases, dct):
        ABCMeta.__init__(self, name, bases, dct)
        #self.__call__=self.function
        #print(str(self))
        #print(str(name))
        #print(str(bases))
        #print(str(dct))
    
class FunctionBase(metaclass=FunctionBaseMeta):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        #self.__call__=self.function
        pass
        
    @abstractmethod
    def function(self, *args, **kwargs): pass
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def iterates(self, *args, iteration:int=2, **kwargs):
        '''
        Apply multiple iterations of the function
        @param iteration: number of iterations
        @type iteration: int
        '''
        if len(args)==1:
            self.iterates=self.__iteratesOneVariable
        else:
            self.iterates=self.__iteratesMultipleVariable
        return self.iterates(*args, iteration=iteration, **kwargs)
    
    def __iteratesOneVariable(self, x, iteration:int=2, **kwargs):
        '''
        Apply multiple iterations of the function with one variable
        @param iteration: number of iterations
        @type iteration: int
        '''
        function=self.function
        for t in range(iteration):
            x=function(x,**kwargs)
        return x
    
    def __iteratesMultipleVariable(self, *args, iteration:int=2, **kwargs):
        '''
        Apply multiple iterations of the function with multiple variables
        @param iteration: number of iterations
        @type iteration: int
        '''
        function=self.function
        for t in range(iteration):
            args=function(*args,**kwargs)
        return args
