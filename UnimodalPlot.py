from scipy import optimize
import numpy as np

# Matplotlib library
from matplotlib import (cm,colors)

import Plot
import Setting
from Unimodal import Unimodal
from PyQt5 import QtCore # Import the PyQt4 module we'll need

class UnimodalPlot:
	'''
	Methods to plot a unimodal map
	'''
	
	def __init__(self,func:Unimodal):
		self._func = func

	# unimodal map for the plot
	def getFunction(self)->Unimodal:
		return self._func
	@QtCore.pyqtSlot(Unimodal)
	def setFunction(self, func:Unimodal):
		self._func = func
	function=property(
		lambda self: self.getFunction(), 
		lambda self, func: self.setFunction(func)
		)
			
	'''
	Plot Current Level
	'''
	
	'''Current level graphs'''
	
	def _plotFunction(self,visible:bool=True)->Plot.GraphObject:
		self.gFunction = Plot.Function(self.canvas,self._func,visible=visible,lw=1)
		return self.gFunction
	def _updateFunction(self):
		self.gFunction.setFunction(self._func)

	def _plotFunctionSecond(self,visible:bool=True)->Plot.GraphObject:
		self.gFunctionSecond = Plot.Function(self.canvas,lambda x:self._func(self._func(x)),visible=visible,lw=1)
		return self.gFunctionSecond
	def _updateFunctionSecond(self):
		self.gFunctionSecond.setFunction(lambda x:self._func(self._func(x)))

	def _func_p(self, x):
		# The p-iterate of the function
		for i in range(self.period):
			x=self._func(x)
		return x
	def _plotFunctionIterates(self,visible:bool=True)->Plot.GraphObject:
		self.gFunctionIterates = Plot.Function(self.canvas,self._func_p,visible=visible,lw=1)
		return self.gFunctionIterates
	def _updateFunctionIterates(self):
		self.gFunctionIterates.setFunction(self._func_p)

	def _plotDiagonal(self,visible:bool=True)->Plot.GraphObject:
		self.gDiagonal = Plot.Function(self.canvas,lambda x:x,visible=visible,lw=1)
		return self.gDiagonal

	'''Current level orbits'''

	def _plotAlpha0(self,visible:bool=True)->Plot.GraphObject:
		self.gAlpha0=Plot.Ticks(self.canvas,"top",
								[-1,1,self._func.p_c],
								[r"$\alpha(0)$",r"$\overline{\alpha(0)}$",r"$c$"],
								visible=visible)
		return self.gAlpha0
	def _updateAlpha0(self):
		self.gAlpha0.setTicks([-1,1,self._func.p_c])

	def _plotBeta0(self,visible:bool=True)->Plot.GraphObject:
		# Draw beta(0) points
		# Draw b
		self.gBeta0_0=Plot.VerticalLine(self.canvas,self._func.p_b,color='gray',lw=0.5)
		# Draw B
		self.gBeta0_Bar0=Plot.VerticalLine(self.canvas,self._func.p_B,color='gray',lw=0.5)
		# Draw B2
		self.gBeta0_Bar1=Plot.VerticalLine(self.canvas,self._func.p_B2,color='gray',lw=0.5)
		
		
		self.gBeta0Ticks=Plot.Ticks(self.canvas,"top",
								[self._func.p_b,self._func.p_B,self._func.p_B2],
								[r"$\beta^{0}$",r"$\overline{\beta^{1}}$"]
								)
		self.gBeta0=Plot.Group([self.gBeta0_0,self.gBeta0_Bar0,self.gBeta0_Bar1,self.gBeta0Ticks],visible=visible)
		return self.gBeta0
	def _updateBeta0(self):
		# Find fixed point
		self.gBeta0_0.setXValue(self._func.p_b)
		# Find a1(1)bar
		self.gBeta0_Bar0.setXValue(self._func.p_B)
		# Find a0(1)bar
		self.gBeta0_Bar1.setXValue(self._func.p_B2)
		# Set ticks
		self.gBeta0Ticks.setTicks([self._func.p_b,self._func.p_B,self._func.p_B2])


	'''
	Plot renormalizable objects
	'''

	# For plotting the intervals that defines the self-return map
	gSelfReturnIntervals = None
	def _plotSelfReturnIntervals(self,period,visible:bool=True)->Plot.GraphObject:
		f_selfReturnBoxesList=[None]*period
		for t in range(period):
			f_selfReturnBoxesList[t]=Plot.Rectangle(self.canvas,
					self._func.p_a1[period][t], self._func.p_a1[period][t], #x,y
					self._func.p_A1[period][t]-self._func.p_a1[period][t], self._func.p_A1[period][t]-self._func.p_a1[period][t], #width, height
					visible=visible, color='gray', lw=1, fill=None
				)
		self.gSelfReturnIntervals=Plot.Group(f_selfReturnBoxesList)
		return self.gSelfReturnIntervals
	def _updateSelfReturnIntervals(self,period):
		for t in range(period):
		# Set the self return intervals
			self.gSelfReturnIntervals[t].setBounds(
				self._func.p_a1[period][t], self._func.p_a1[period][t],
				self._func.p_A1[period][t]-self._func.p_a1[period][t], self._func.p_A1[period][t]-self._func.p_a1[period][t]
				)
	def _removeSelfReturnIntervals(self):
		self.gSelfReturnIntervals.clear()
		self.gSelfReturnIntervals=None


	'''
	Plot RChild objects
	'''
	
	# The inverse function of nonlinear rescaling
	def _iRescaling(self,y):
		if not (-1.0<y and y<1.0):
			raise ValueError("_iRescaling: Unable to compute the inverse rescaling. The value ",str(y)," is out of bound")

		y1=self._r_si(y)
			
		def solve(x):
			return self._func.iterates(x,self.period-1)-y1
		return optimize.brenth(solve, self._p_a1Orbit[0],self._p_A1Orbit[0])

	# Periodic intervals and levels 
	_p_a1Orbit=None
	_p_A1Orbit=None
	_p_b1Orbit=None
	_p_B1Orbit=None

	# Find the periodic intervals
	# todo: exception
	def _findPeriodicInterval(self,period):
		if self._rFunc!=None:
			# build period intervals from the next level
			self._p_a1Orbit=self._rFunc.p_a1[self.period]
			self._p_A1Orbit=self._rFunc.p_A1[self.period]
			self._p_b1Orbit=self._rFunc.orbit(self._func(self._r_si(self._rFunc.p_b)),self.period)
			self._p_B1Orbit=self._rFunc.reflexOrbit(self._p_b1Orbit)
		else:
			self._p_a1Orbit=[]
			self._p_A1Orbit=[]
			self._p_b1Orbit=[]
			self._p_B1Orbit=[]

	def _findRescalingLevels(self):
		# update the list for the levels
		self._p_aLevels=[self._func.p_a,self._p_a1Orbit[0]]
		self._p_ALevels=[self._func.p_A,self._p_A1Orbit[0]]
		self._p_bLevels=[self._func.p_b,self._p_b1Orbit[0]]
		self._p_BLevels=[self._func.p_B,self._p_B1Orbit[0]]
		self._updateRescalingLevels()

	def _updateRescalingLevels(self):
		i=len(self._p_aLevels)
		updated=False
		
		# update the list of the periodic points if new renormalization level is available
		while i-1 < len(self._rChild._p_aLevels) and i <= Setting.figureMaxLevels:
			self._p_aLevels.append(self._iRescaling(self._rChild._p_aLevels[i-1]))
			self._p_ALevels.append(self._iRescaling(self._rChild._p_ALevels[i-1]))
			self._p_bLevels.append(self._iRescaling(self._rChild._p_bLevels[i-1]))
			self._p_BLevels.append(self._iRescaling(self._rChild._p_BLevels[i-1]))
			i=i+1
			updated=True
			
		return updated


	'''
	Plot first level
	'''

	def _plotAlpha1(self,visible:bool=True)->Plot.GraphObject:
		f_a1List=[Plot.VerticalLine(self.canvas, self._p_a1Orbit[i], visible=True) for i in range(self.period)]
		f_A1List=[Plot.VerticalLine(self.canvas, self._p_A1Orbit[i], visible=True) for i in range(self.period)]
		self.gAlpha1=Plot.Group(f_a1List+f_A1List,visible=visible)
		return self.gAlpha1
	def _updateAlpha1(self):
		self.gAlpha1.clear()
		f_a1List=[Plot.VerticalLine(self.canvas, self._p_a1Orbit[i], visible=True) for i in range(self.period)]
		f_A1List=[Plot.VerticalLine(self.canvas, self._p_A1Orbit[i], visible=True) for i in range(self.period)]
		self.gAlpha1.extend(f_a1List+f_A1List)
	def _removeAlpha1(self):
		self.gAlpha1.clear()
		self.gAlpha1=None

	def _plotBeta1(self,visible:bool=True)->Plot.GraphObject:
		f_b1List=[Plot.VerticalLine(self.canvas, self._p_b1Orbit[i], visible=True) for i in range(self.period)]
		f_B1List=[Plot.VerticalLine(self.canvas, self._p_B1Orbit[i], visible=True) for i in range(self.period)]
		self.gBeta1=Plot.Group(f_b1List+f_B1List,visible=visible)
		return self.gBeta1
	def _updateBeta1(self):
		self.gBeta1.clear()
		f_b1List=[Plot.VerticalLine(self.canvas, self._p_b1Orbit[i], visible=True) for i in range(self.period)]
		f_B1List=[Plot.VerticalLine(self.canvas, self._p_B1Orbit[i], visible=True) for i in range(self.period)]
		self.gBeta1.extend(f_b1List+f_B1List)
	def _removeBeta1(self):
		self.gBeta1.clear()
		self.gBeta1=None
	
	_isDeepLevelOrbitsPlotted=False
	def _plotDeepLevelOrbits(self):
		if self._isDeepLevelOrbitsPlotted==False:
			self._findRescalingLevels()
			lList=self._p_aLevels
			rList=self._p_ALevels
			
			def _contourRLevel(x,y):
				i=0
				while i<len(lList):
					if x < lList[i] or rList[i] < x:
						return i-1
					i=i+1
				return i-1
	
			def _contourQLevel(x,y):
				return _contourRLevel(self._func(x),y) 
		
			def _contourQRLevel(x,y):
				return _contourQLevel(x,y) if x < self._func.p_b else _contourRLevel(x,y)
				
			_contourQRLevel=np.vectorize(_contourQRLevel,signature='(),()->()')
			
			#_contourQRLevel= lambda x,y:x+y
			def frange(x, y, jump):
				while x < y:
					yield x
					x += jump
			
			self.f_rLevel = Plot.Contour(self.canvas, _contourQRLevel, visible=self.levelButton.isChecked(),levels=list(frange(-0.5,Setting.figureMaxLevels+0.6,1)),cmap=cm.get_cmap("gray_r"),norm=colors.Normalize(vmin=0,vmax=10))
			self.levelButton.toggled.connect(self.f_rLevel.setVisible)
			
			self._isDeepLevelOrbitsPlotted=True
		else:
			self._updateDeepLevelOrbits()

	def _updateDeepLevelOrbits(self):
		if self._isDeepLevelOrbitsPlotted==True:
			self._removeDeepLevelOrbits()
			self._plotDeepLevelOrbits()

	def _removeDeepLevelOrbits(self):
		if self._isDeepLevelOrbitsPlotted==True:
			self.levelButton.toggled.disconnect(self.f_rLevel.setVisible)
			self.f_rLevel.clear()
			self.f_rLevel=None
			self._p_aLevels=[self._func.p_a]
			self._p_ALevels=[self._func.p_A]
			self._p_bLevels=[self._func.p_b]
			self._p_BLevels=[self._func.p_B]
			self._isDeepLevelOrbitsPlotted=False
	