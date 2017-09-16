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

    def __init__(self, ui:object, binding:typing.Dict[str,tuple]):
        '''
        Constructor
        '''
        
        self.__graphList=dict.fromkeys(binding.keys())
        self.__uiBindList={graphName: [getattr(ui,uiName) for uiName in uiList] for graphName, uiList in binding.items()}
        #getattr(self,"gFunction")
    
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
            
            # Connect graph with UI
            enableUI:bool=newGraph is not None
            for component in uiList:
                component.setEnabled(enableUI)

            if enableUI:
                # Disconnect clickable with visible
                if len(uiList) >= 1:
                    newGraph.setVisible(uiList[0].isChecked())
                    uiList[0].toggled.connect(newGraph.setVisible)
                else:
                    newGraph.setVisible(True)
                newGraph.parent=self.ui.canvas
            
        self.__graphList[name]=newGraph