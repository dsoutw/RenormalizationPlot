'''
Renormalization Plot - plot/group.py
    Group a list of GraphObject instances

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

import logging
import typing as tp
from .graphobject import GraphObject

class Group(GraphObject):
    __graphList:tp.List[GraphObject]=[]
    def __init__(self,graphList:tp.Iterable[GraphObject],visible:bool=True,logger=None,**kwargs):
        '''
        Group a list of graphobject instances
        @param graphList: A list of graphs
        @type graphList: class GraphObject
        @param visible: Visibility of the group
        @type visible: bool
        @param logger:
        @type logger:
        @param logger: Logging instance (optional)
        @type logger: logging.Logger
        '''
        if logger is None:
            logger=logging.getLogger(__name__)

        for member in graphList:
            member.parent=self

        self.__graphList=list(graphList)
        self._setVisibleInternal(visible=visible)
        GraphObject.__init__(self,visible=visible,logger=logger,**kwargs)
        
    def _setVisibleInternal(self, visible):
        for member in self.__graphList:
            try:
                member.setVisibleMask(visible)
            except:
                self._logger.exception('Unable to set visible %s: %s' % (member,visible))
    
    # clear all artist in the list from the canvas    
    def update(self):
        for member in self.__graphList:
            member.update()

    # clear all artist in the list from the canvas    
    def clear(self):
        for member in self.__graphList:
            try:
                member.setParent(None)
            except:
                self._logger.exception('Unable to clear %s' % member)
                
        del self.__graphList[:]
    
    def canvasChangedEvent(self, oldCanvas, newCanvas):
        for member in self.__graphList:
            member.canvasChangedEvent(oldCanvas, newCanvas)
        GraphObject.canvasChangedEvent(self, oldCanvas, newCanvas)
        
    '''
    List methods
    '''
    def __getitem__(self,key):
        return self.__graphList[key]
    def __setitem__(self,key,value):
        self.__graphList[key].parent=None
        self.__graphList[key]=value
        value.parent=self
    def __iter__(self):
        return self.__graphList
    def append(self,x:GraphObject):
        x.setVisibleMask(self.visible)
        x.parent=self
        self.__graphList.append(x)
    def extend(self,l:tp.Iterable[GraphObject]):
        for member in l:
            member.setVisibleMask(self.isShowed())
            member.parent=self
        self.__graphList.extend(l)

