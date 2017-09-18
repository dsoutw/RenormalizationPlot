'''
Created on 2017/9/16

Bind graph objects with UI components
Use string to work around on nonexistence of pointers

@author: dsou
'''
import typing as tp
import warnings
import operator
import Plot

def readAttr(ui,attr):
    if isinstance(attr, str):
        return operator.attrgetter(attr)(ui)
    else:
        return attr

class graphLink:
    setEnableUI=None
    setVisibleUI=None
    bindUI=[]
    __graph:tp.Optional[Plot.GraphObject]=None
    ui=None
    
    def __init__(self,ui,optionList):
        self.bindUI=[]
        self.ui=ui
        
        for optionName, option in optionList.items():
            if optionName=='getVisible':
                self.setVisibleUI=readAttr(ui,option)
                self.setVisibleUI.toggled.connect(self.__setVisibleSlot)
                self.__visibledUI=self.setVisibleUI.isChecked()
            elif optionName=='setEnable':
                self.bindUI=[readAttr(ui,uiName) for uiName in option]
            elif optionName=='getEnable':
                self.setEnableUI=readAttr(ui,option)
                self.setEnableUI.toggled.connect(self.__setEnableSlot)
                self.__enabledUI=self.setEnableUI.isChecked()
        
        self.__setEnable(self.isEnabled())
        #self.__setVisible(self.isVisibled())
    
    __enabledUI:bool=True
    def __setEnableSlot(self,value):
        if (self.graph is not None and value) != (self.graph is not None and self.__enabledUI):
            self.__setEnable(self.graph is not None and value)
        self.__enabledUI=value
        
    def __setEnable(self,value):
        for component in self.bindUI:
            component.setEnabled(value)
            
    def isEnabled(self):
        return (self.graph is not None) and self.__enabledUI

    __visibledUI:bool=True
    def __setVisibleSlot(self,value):
        if value != self.__visibledUI:
            self.__setVisible(value)
            self.__visibledUI=value
            
    def __setVisible(self,value):
        graph=self.graph
        if graph is not None:
            graph.setVisible(value)
            
    def isVisibled(self):
        return self.__visibledUI
            
    def getGraph(self)->tp.Optional[Plot.GraphObject]:
        return self.__graph
    
    def setGraph(self, value:tp.Optional[Plot.GraphObject]):
        oldGraph:tp.Optional[Plot.GraphObject]=self.__graph
        newGraph:tp.Optional[Plot.GraphObject]=value
        
        if oldGraph!=newGraph:
            self.__graph=value
            
            if oldGraph is not None:
                oldGraph.parent=None
                
            self.__setEnable(self.isEnabled())
                
            if newGraph is not None:
                newGraph.parent=self.ui.canvas
                newGraph.setVisible(self.isVisibled())

    graph=property(getGraph,setGraph)
    
class Binding(object):
    '''
    classdocs
    '''
    __graphList:tp.Dict[str,graphLink]={}
    
    def __setVisible(self,name):
        pass

    def __init__(self, ui:object, binding:tp.Dict[str,dict]):
        self.__graphList:typing.Dict[graphLink]={graphName: graphLink(ui,optionList) for graphName, optionList in binding.items()}
    
    def __dir__(self, *args, **kwargs):
        return super().__dir__( *args, **kwargs).extend(self.__graphList.keys())
    
    def __getattr__(self, name):
        if name in self.__graphList:
            return self.__graphList[name].graph
        else:
            super().__getattr__(name)

    def __setattr__(self, name, value):
        '''
        Set the graph instance
        @param name: name of graph
        @type name: str
        @param value: graph to be connected
        @type value: class which has methods setEnable and setVisible
        '''
        
        if name not in self.__graphList:
            return super().__setattr__(name, value)
        
        self.__graphList[name].graph=value
