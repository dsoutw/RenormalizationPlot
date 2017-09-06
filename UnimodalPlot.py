import numpy as np

# Matplotlib library
from matplotlib import (cm,colors)

import Plot
import Setting
from Unimodal import Unimodal
from PyQt5 import QtCore # Import the PyQt4 module we'll need

#_contourQRLevel= lambda x,y:x+y
def frange(x, y, jump):
	while x < y:
		yield x
		x += jump

def PlotVetricalLines(canvas,pointList):
	return [Plot.VerticalLine(canvas, point, visible=True) for point in pointList]

class UnimodalPlot:
	'''
	Methods to plot a unimodal map
	'''
	__func=None
	
	def __init__(self,func:Unimodal):
		self.__func = func

	'''
	Properties
	'''
	
	# unimodal map for the plot
	def getFunction(self)->Unimodal:
		return self.__func
	@QtCore.pyqtSlot(Unimodal)
	def setFunction(self, func:Unimodal):
		self.__func = func
	function=property(
		lambda self: self.getFunction(), 
		lambda self, func: self.setFunction(func)
		)

	''' Periodic intervals and Trapping intervals '''

	def getOrbit_alpha1(self):
		raise NotImplementedError("UnimodalPlot.getOrbit_alpha1")
	orbit_alpha1=property(
		lambda self: self.getOrbit_alpha1() 
		)
	def getOrbit_Alpha1(self):
		raise NotImplementedError("UnimodalPlot.getOrbit_Alpha1")
	orbit_Alpha1=property(
		lambda self: self.getOrbit_Alpha1() 
		)
	def getOrbit_beta1(self):
		raise NotImplementedError("UnimodalPlot.getOrbit_beta1")
	orbit_beta1=property(
		lambda self: self.getOrbit_beta1() 
		)
	def getOrbit_Beta1(self):
		raise NotImplementedError("UnimodalPlot.getOrbit_Beta1")
	orbit_Beta1=property(
		lambda self: self.getOrbit_Beta1() 
		)

	''' Rescaling levels'''
	
	def getLevels_alpha(self):
		raise NotImplementedError("UnimodalPlot.getLevels_alpha")
	levels_alpha=property(
		lambda self: self.getLevels_alpha() 
		)
	def getLevels_Alpha(self):
		raise NotImplementedError("UnimodalPlot.getLevels_Alpha")
	levels_Alpha=property(
		lambda self: self.getLevels_Alpha() 
		)
	def getLevels_beta(self):
		raise NotImplementedError("UnimodalPlot.getLevels_beta")
	levels_beta=property(
		lambda self: self.getLevels_beta() 
		)
	def getLevels_Beta(self):
		raise NotImplementedError("UnimodalPlot.getLevels_Beta")
	levels_Beta=property(
		lambda self: self.getLevels_Beta() 
		)

	'''
	Plot Current Level
	'''
	
	'''Current level graphs'''
	
	def _plotFunction(self,visible:bool=True)->Plot.GraphObject:
		self.gFunction = Plot.Function(self.canvas,self.function,visible=visible,lw=1)
		return self.gFunction
	def _updateFunction(self):
		self.gFunction.setFunction(self.function)

	def _plotFunctionSecond(self,visible:bool=True)->Plot.GraphObject:
		self.gFunctionSecond = Plot.Function(self.canvas,lambda x:self.function.iterates(x,2),visible=visible,lw=1)
		return self.gFunctionSecond
	def _updateFunctionSecond(self):
		self.gFunctionSecond.setFunction(lambda x:self.function.iterates(x,2))

	def _plotFunctionIterates(self,period:int,visible:bool=True)->Plot.GraphObject:
		def _func_p(x):
			# The p-iterate of the function
			return self.function.iterates(x,period)
		self.gFunctionIterates = Plot.Function(self.canvas,_func_p,visible=visible,lw=1)
		return self.gFunctionIterates
	def _updateFunctionIterates(self,period):
		def _func_p(x):
			# The p-iterate of the function
			return self.function.iterates(x,period)
		self.gFunctionIterates.setFunction(_func_p)

	def _plotDiagonal(self,visible:bool=True)->Plot.GraphObject:
		self.gDiagonal = Plot.Function(self.canvas,lambda x:x,visible=visible,lw=1)
		return self.gDiagonal

	'''Current level orbits'''

	def _plotAlpha0(self,visible:bool=True)->Plot.GraphObject:
		self.gAlpha0=Plot.Ticks(self.canvas,"top",
								[-1,1,self.function.p_c],
								[r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$"],
								visible=visible)
		return self.gAlpha0
	def _updateAlpha0(self):
		self.gAlpha0.setTicks([-1,1,self.function.p_c])

	def _plotBeta0(self,visible:bool=True)->Plot.GraphObject:
		# Draw beta(0) points
		# Draw b
		self.gBeta0_0=Plot.VerticalLine(self.canvas,self.function.p_b,color='gray',lw=0.5)
		# Draw B
		self.gBeta0_Bar0=Plot.VerticalLine(self.canvas,self.function.p_B,color='gray',lw=0.5)
		# Draw B2
		self.gBeta0_Bar1=Plot.VerticalLine(self.canvas,self.function.p_B2,color='gray',lw=0.5)
		
		
		self.gBeta0Ticks=Plot.Ticks(self.canvas,"top",
								[self.function.p_b,self.function.p_B,self.function.p_B2],
								[r"$\beta^{0}$",r"$\overline{\beta^{1}}$"]
								)
		self.gBeta0=Plot.Group([self.gBeta0_0,self.gBeta0_Bar0,self.gBeta0_Bar1,self.gBeta0Ticks],visible=visible)
		return self.gBeta0
	def _updateBeta0(self):
		# Find fixed point
		self.gBeta0_0.setXValue(self.function.p_b)
		# Find a1(1)bar
		self.gBeta0_Bar0.setXValue(self.function.p_B)
		# Find a0(1)bar
		self.gBeta0_Bar1.setXValue(self.function.p_B2)
		# Set ticks
		self.gBeta0Ticks.setTicks([self.function.p_b,self.function.p_B,self.function.p_B2])


	'''
	Plot renormalizable objects
	'''

	# For plotting the intervals that defines the self-return map
	gSelfReturnIntervals = None
	def _plotSelfReturnIntervals(self,period,visible:bool=True)->Plot.GraphObject:
		f_selfReturnBoxesList=[None]*period
		for t in range(period):
			f_selfReturnBoxesList[t]=Plot.Rectangle(self.canvas,
					self.function.p_a1[period][t], self.function.p_a1[period][t], #x,y
					self.function.p_A1[period][t]-self.function.p_a1[period][t], self.function.p_A1[period][t]-self.function.p_a1[period][t], #width, height
					visible=visible, color='gray', lw=1, fill=None
				)
		self.gSelfReturnIntervals=Plot.Group(f_selfReturnBoxesList)
		return self.gSelfReturnIntervals
	def _updateSelfReturnIntervals(self,period):
		for t in range(period):
		# Set the self return intervals
			self.gSelfReturnIntervals[t].setBounds(
				self.function.p_a1[period][t], self.function.p_a1[period][t],
				self.function.p_A1[period][t]-self.function.p_a1[period][t], self.function.p_A1[period][t]-self.function.p_a1[period][t]
				)
	def _removeSelfReturnIntervals(self):
		self.gSelfReturnIntervals.clear()
		self.gSelfReturnIntervals=None


	'''
	Plot RChild objects
	'''
	
	''' Next Level Orbits '''

	def _plotAlpha1(self,visible:bool=True)->Plot.GraphObject:
		f_a1List=PlotVetricalLines(self.canvas,self.orbit_alpha1)
		f_A1List=PlotVetricalLines(self.canvas,self.orbit_Alpha1)
		self.gAlpha1=Plot.Group(f_a1List+f_A1List,visible=visible)
		return self.gAlpha1
	def _updateAlpha1(self):
		self.gAlpha1.clear()
		f_a1List=PlotVetricalLines(self.canvas,self.orbit_alpha1)
		f_A1List=PlotVetricalLines(self.canvas,self.orbit_Alpha1)
		self.gAlpha1.extend(f_a1List+f_A1List)
	def _removeAlpha1(self):
		self.gAlpha1.clear()
		self.gAlpha1=None

	def _plotBeta1(self,visible:bool=True)->Plot.GraphObject:
		f_b1List=PlotVetricalLines(self.canvas,self.orbit_beta1)
		f_B1List=PlotVetricalLines(self.canvas,self.orbit_Beta1)
		self.gBeta1=Plot.Group(f_b1List+f_B1List,visible=visible)
		return self.gBeta1
	def _updateBeta1(self):
		self.gBeta1.clear()
		f_b1List=PlotVetricalLines(self.canvas,self.orbit_beta1)
		f_B1List=PlotVetricalLines(self.canvas,self.orbit_Beta1)
		self.gBeta1.extend(f_b1List+f_B1List)
	def _removeBeta1(self):
		self.gBeta1.clear()
		self.gBeta1=None

	''' Deep Level Orbits '''
		
	def _plotRescalingLevels(self,visible:bool=True)->Plot.GraphObject:
		#self._findRescalingBoundaries()
		
		def _contourRLevel(x,y):
			lList=self.levels_alpha
			rList=self.levels_Alpha
			
			i=0
			while i<len(lList):
				if x < lList[i] or rList[i] < x:
					return i-1
				i=i+1
			return i-1

		def _contourQLevel(x,y):
			return _contourRLevel(self.function(x),y) 
	
		def _contourQRLevel(x,y):
			return _contourQLevel(x,y) if x < self.function.p_b else _contourRLevel(x,y)
			
		_contourQRLevel=np.vectorize(_contourQRLevel,signature='(),()->()')
		
		self.gRescalingLevels = Plot.Contour(self.canvas, _contourQRLevel, visible=visible,levels=list(frange(-0.5,Setting.figureMaxLevels+0.6,1)),cmap=cm.get_cmap("gray_r"),norm=colors.Normalize(vmin=0,vmax=10))
		return self.gRescalingLevels
	def _updateRescalingLevels(self):
		self.gRescalingLevels.update()
	def _removeRescalingLevels(self):
		self.gRescalingLevels.clear()
		self.gRescalingLevels=None