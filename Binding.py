'''
Created on 2017/9/16

Bind graph objects with UI components
Use string to work around on nonexistence of pointers

@author: dsou
'''
import typing
import warnings

class Binding(object):
    '''
    classdocs
    '''
    __graphList:dict={}
    __uiBindList:dict={}
    __uiEnableMaskList:dict={}

    def __init__(self, ui:object, binding:typing.Dict[str,dict]):
        '''
        Constructor
        '''
        
        self.__graphList=dict.fromkeys(binding.keys())
        self.__uiBindList={graphName: [getattr(ui,uiName) for uiName in options.get('link',())] for graphName, options in binding.items()}
        self.__uiEnableMaskList={graphName: getattr(ui,options.get('enable',""),None) for graphName, options in binding.items()}
        
        for graphName, uiEnableMaskComponent in self.__uiEnableMaskList.items():
            if uiEnableMaskComponent is not None:
                def setEnable():
                    self.__setEnable(graphName)
                uiEnableMaskComponent.toggled.connect(setEnable)
    
    def __dir__(self, *args, **kwargs):
        return super().__dir__( *args, **kwargs).extend(self.__graphList.keys())
    
    def __getattr__(self, name):
        if name in self.__graphList:
            return self.__graphList[name]
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
        
        oldGraph:Plot.GraphObject=self.__graphList[name]
        newGraph:Plot.GraphObject=value
        uiList=self.__uiBindList[name]
        self.__graphList[name]=newGraph
        
        if oldGraph!=newGraph:
            # Disconnect graph with UI
            if oldGraph is not None:
                # Disconnect clickable with visible
                try:
                    if len(uiList) >= 1:
                        uiList[0].toggled.disconnect(oldGraph.setVisible)
                except Exception as e:
                    warnings.warn(str(e))
                oldGraph.parent=None
                
            self.__setEnable(name)
            #enableUI:bool=newGraph is not None
            #for component in uiList:
            #    component.setEnabled(enableUI)
                
            if newGraph is not None:
                # Disconnect clickable with visible
                if len(uiList) >= 1:
                    newGraph.setVisible(uiList[0].isChecked())
                    uiList[0].toggled.connect(newGraph.setVisible)
                else:
                    newGraph.setVisible(True)
                newGraph.parent=self.ui.canvas

    def isEnabled(self,name):
        if self.__uiEnableMaskList[name] is None:
            return self.__graphList[name] is not None
        else:
            return (self.__graphList[name] is not None) and self.__uiEnableMaskList[name].isChecked()
    
    def __setEnable(self,name):
        for component in self.__uiBindList[name]:
            component.setEnabled(self.isEnabled(name))
