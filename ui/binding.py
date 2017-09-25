'''
Created on 2017/9/16

Bind graph objects with UI components
Use string to work around on nonexistence of pointers

@author: dsou
'''
import typing as tp
import warnings
import logging
import operator
import plot
import weakref

def readAttr(ui,attr):
    if isinstance(attr, str):
        try:
            return operator.attrgetter(attr)(ui)
        except Exception as e:
            print(str(e))
            print(attr)
            return None
    else:
        return attr

class graphLink:
    __logger:tp.Optional[logging.Logger]=None
    getEnableUI=None
    getVisibleUI=None
    setEnableUI=[]
    __graph:tp.Optional[plot.GraphObject]=None
    ui=None
    
    def __init__(self,ui,optionList,logger:tp.Optional[logging.Logger]=None):
        if logger is None:
            self.__logger:logging.Logger=logging.getLogger(__name__)
        else:
            self.__logger:logging.Logger=logger
            
        self.setEnableUI=[]
        self.ui=ui
        
        for optionName, option in optionList.items():
            if optionName=='getVisible':
                self.getVisibleUI=readAttr(ui,option)
                self.getVisibleUI.toggled.connect(self.__setVisibleSlot)
                self.__visibledUI=self.getVisibleUI.isChecked()
            elif optionName=='setEnable':
                if isinstance(option,str):
                    self.setEnableUI=[readAttr(ui,option)]
                else:
                    self.setEnableUI=weakref.WeakSet([readAttr(ui,uiName) for uiName in option])
            elif optionName=='getEnable':
                self.getEnableUI=readAttr(ui,option)
                self.getEnableUI.toggled.connect(self.__setEnableSlot)
                self.__enabledUI=self.getEnableUI.isChecked()
        
        self.__setEnable(self.isEnabled())
        #self.__setVisible(self.isVisibled())
    
    __enabledUI:bool=True
    def __setEnableSlot(self,value):
        if (self.graph is not None and value) != (self.graph is not None and self.__enabledUI):
            self.__setEnable(self.graph is not None and value)
        self.__enabledUI=value
        
    def __setEnable(self,value):
        for component in self.setEnableUI:
            try:
                component.setEnabled(value)
            except:
                self.__logger.exception('Unable to set component (%s) enable: %s' % (component,value))
            
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
            try:
                graph.setVisible(value)
            except:
                self.__logger.exception('Unable to set graph (%s) visible: %s' % (graph,value))
            
    def isVisibled(self):
        return self.__visibledUI
            
    def getGraph(self)->tp.Optional[plot.GraphObject]:
        return self.__graph
    
    def setGraph(self, value:tp.Optional[plot.GraphObject]):
        oldGraph:tp.Optional[plot.GraphObject]=self.__graph
        newGraph:tp.Optional[plot.GraphObject]=value
        
        if oldGraph!=newGraph:
            self.__graph=value
            
            if oldGraph is not None:
                try:
                    oldGraph.parent=None
                except:
                    self.__logger.exception('Unable to clear graph')
                
            if newGraph is not None:
                try:
                    newGraph.setVisible(self.isVisibled())
                    newGraph.parent=self.ui.canvas
                except Exception as e:
                    self.__graph=None
                    try:
                        newGraph.parent=None
                    except:
                        pass
                    raise RuntimeError('Unable to set new graph') from e
                finally:
                    self.__setEnable(self.isEnabled())

    graph=property(getGraph,setGraph)
    
class Binding(object):
    '''
    classdocs
    '''
    __graphList:tp.Dict[str,graphLink]={}
    __logger:tp.Optional[logging.Logger]=None
    
    def __setVisible(self,name):
        pass

    def __init__(self, ui:object, binding:tp.Dict[str,dict], logger:tp.Optional[logging.Logger]=None):
        if logger is None:
            self.__logger:logging.Logger=logging.getLogger(__name__)
        else:
            self.__logger:logging.Logger=logger
        
        self.__graphList:typing.Dict[graphLink]={graphName: graphLink(ui,optionList,logger=self.__logger) for graphName, optionList in binding.items()}
    
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
