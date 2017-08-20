'''
Created on 2017/8/15

@author: dsou
'''
import numpy as np
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
import random

class GraphObjectBase():
    '''
    classdocs
    '''
    
    def __init__(self,visible=True):
        #self._visible=visible
        self._visibleMask=True
        self._visible=visible
        self._setVisibleInternal(visible)
        pass
    
    # visible
    def getVisible(self):
        return self._visible
    @QtCore.pyqtSlot(bool)
    def setVisible(self,visible):
        if (visible & self._visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(visible & self._visibleMask)
        self._visible=visible
    visible=property(getVisible, setVisible)

    def _setVisibleInternal(self,visible):
        raise NotImplementedError("GraphObjectBase._setVisibleInternal has to be implemented")
        
    def getVisibleMask(self):
        return self._visibleMask
    @QtCore.pyqtSlot(bool)
    def setVisibleMask(self,visibleMask):
        if (self._visible & visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(self._visible & visibleMask)
        self._visibleMask=visibleMask
    visibleMask=property(getVisibleMask, setVisibleMask)

    def remove(self):
        raise NotImplementedError("GraphObjectBase.remove has to be implemented")


#
class GraphObject(GraphObjectBase,QtCore.QObject):
    '''
    classdocs
    '''
    
    def __init__(self,canvas,visible=True):
        self._canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible)
    
    # canvas
    def getCanvas(self):
        return self._canvas
    @QtCore.pyqtSlot(FigureCanvas)
    def setCanvas(self,canvas):
        self._canvas=canvas
    canvas=property(getCanvas, setCanvas)

    @QtCore.pyqtSlot()
    def update(self):
        self._canvas.update()
        pass

class GroupG(GraphObjectBase,list):
    def __init__(self,*args,visible=True):
        list.__init__(self,*args)
        GraphObjectBase.__init__(self,visible)
        
    def _setVisibleInternal(self, visible):
        for member in self:
            member.setVisibleMask(visible)
        
    def remove(self):
        for member in self:
            member.remove()
            
# line=matplotlib.lines.Line2D object
class CurveG(GraphObject):
    def __init__(self, canvas, curve, visible=True):
        self._curve=curve
        super().__init__(canvas, visible)
        
    # visible
    def _setVisibleInternal(self,visible):
        self._curve.set_visible(visible)
        self.update()
        
    # curve
    def getCurve(self):
        return self._curve
    def setCurve(self, curve):
        self._curve=curve
    curve=property(getCurve, setCurve)
    
    def remove(self):
        self._curve.remove()
        self.update()
    
class FunctionG(CurveG):
    def __init__(self, canvas, func, visible=True, **kwargs):
        self._func=func
        self._kwargs=kwargs
        self._sample = np.arange(-1.0, 1.0, 0.001)
        
        # plot when visible
        if visible == True:
            curve, = canvas.axes.plot(self._sample, self._func(self._sample), **kwargs)
            self._updated = True
        else:
            curve, = canvas.axes.plot(self._sample, self._sample, **kwargs)
            self._updated = False
        
        super().__init__(canvas, curve, visible)

    def _setVisibleInternal(self,visible):
        if (self._updated == False) and (visible == True):  
            self._curve.set_ydata(self._func(self._sample))
            self._updated=True

        self._curve.set_visible(visible)
        self.update()

    # function
    def getFunction(self):
        return self._func
    def setFunction(self,func):
        self._func=func
        # Update when visible
        if self._visible == True:
            self._curve.set_ydata(func(self._sample))
            self.update()
        else:
            self._updated=False

    function=property(getFunction, setFunction)

class VerticalLineG(CurveG):
    def __init__(self, canvas, xValue, visible=True, **kwargs):
        self._xValue=xValue
        self._kwargs=kwargs
        curve=canvas.axes.axvline(x=xValue,**kwargs)
        
        super().__init__(canvas, curve, visible)

    # function
    def getXValue(self):
        return self._xValue
    @QtCore.pyqtSlot(int)
    def setXValue(self,xValue):
        self._xValue=xValue
        self._curve.set_xdata([xValue,xValue])
        self.update()
    xValue=property(getXValue, setXValue)
    
class RectangleG(CurveG):
    def __init__(self, canvas, xValue, yValue, width, height, visible=True, **kwargs):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self._kwargs=kwargs
        curve = patches.Rectangle((xValue,yValue), width, height,**kwargs)
        canvas.axes.add_patch(curve)
        
        super().__init__(canvas, curve, visible)

    # function
    def getBounds(self):
        return (self._xValue, self._yValue, self._width, self._height)
    def setBounds(self, xValue, yValue, width, height):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self._curve.set_bounds(xValue, yValue, width, height)
        self.update()
    bounds=property(getBounds, setBounds)
    
class TicksG(CurveG):
    positionValues = ["left", "right", "top", "bottom"]
    xPosition = ["top", "bottom"]
    yPosition = ["left", "right"]
    
    def __init__(self, canvas, position, ticks=[], ticksLabel=[], visible=True, **kwargs):
        if position not in TicksG.positionValues:
            raise ValueError("position [%s] must be one of %s" %
                             (position, TicksG.positionValues))
        
        if position == "left":
            curve=canvas.figure.add_axes(canvas.axes.get_position(True),sharex=canvas.axes,label=str(random.getrandbits(128)))
            curve.yaxis.tick_left()
            curve.yaxis.set_label_position('left')
            curve.yaxis.set_offset_position('left')
            curve.set_autoscalex_on(canvas.axes.get_autoscalex_on())
            curve.xaxis.set_visible(False)
            curve.set_yticks(ticks)
            curve.set_yticklabels(ticksLabel)
        elif position == "right":
            curve=canvas.figure.add_axes(canvas.axes.get_position(True),sharex=canvas.axes,label=str(random.getrandbits(128)))
            curve.yaxis.tick_right()
            curve.yaxis.set_label_position('right')
            curve.yaxis.set_offset_position('right')
            curve.set_autoscalex_on(canvas.axes.get_autoscalex_on())
            curve.xaxis.set_visible(False)
            curve.set_yticks(ticks)
            curve.set_yticklabels(ticksLabel)
        elif position == "top":
            curve=canvas.figure.add_axes(canvas.axes.get_position(True),sharey=canvas.axes,label=str(random.getrandbits(128)))
            curve.xaxis.tick_top()
            curve.xaxis.set_label_position('top')
            #curve.xaxis.set_offset_position('top')
            curve.set_autoscaley_on(canvas.axes.get_autoscaley_on())
            curve.yaxis.set_visible(False)
            curve.set_xticks(ticks)
            curve.set_xticklabels(ticksLabel)
        elif position == "bottom":
            curve=canvas.figure.add_axes(canvas.axes.get_position(True),sharey=canvas.axes,label=str(random.getrandbits(128)))
            curve.xaxis.tick_bottom()
            curve.xaxis.set_label_position('bottom')
            #curve.xaxis.set_offset_position('bottom')
            curve.set_autoscaley_on(canvas.axes.get_autoscaley_on())
            curve.yaxis.set_visible(False)
            curve.set_xticks(ticks)
            curve.set_xticklabels(ticksLabel)
            
        curve.patch.set_visible(False)
        self._position=position
     
        super().__init__(canvas, curve, visible)
        pass
    
    def setTicks(self, ticks):
        if self._position in TicksG.xPosition:
            self._curve.set_xticks(ticks)
        elif self._position in TicksG.yPosition:
            self._curve.set_yticks(ticks)
        self.update()
        
    def setTicksLabel(self, ticksLabel):
        if self._position in TicksG.xPosition:
            self._curve.set_xticklabels(ticksLabel)
        elif self._position in TicksG.yPosition:
            self._curve.set_yticklabels(ticksLabel)
        self.update()
        
