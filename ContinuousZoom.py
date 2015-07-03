import viz
import math
from math import sqrt
import vizmat

from PointingTechnique import PointingTechnique
from ZoomTechnique import ZoomTechnique
from Vector3 import Vector3

class ContinuousZoom(ZoomTechnique):
	def __init__(self,sceneObjects,hfov,vfov):
		ZoomTechnique.__init__(self,sceneObjects,hfov,vfov)
		
		self.name = "Continuous Zoom"
		
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
		self.registerButtonCallbacks(self.zoomInButtonPressed,self.zoomInButtonReleased)
		self.registerButtonCallbacks(self.zoomOutButtonPressed,self.zoomOutButtonReleased)
	
	# update()
	# main update function for the zoom techniques, equivalent to updateContinuousCursor()
	def update(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		self.raycasting.cursorPosition = self.cursorPosition
		self.raycasting.windowSize = self.windowSize
		self.raycasting.aspectRatio = self.aspectRatio
		
		self.raycasting.update()
		
		if self.zooming == True:
			self.previousCenterOffset = [0,0]
			if self.buttonState[1]:
				#print "zoom in button pressed"
				if self.zoomingLevel < self.maxMultiplier:
					#print "setting new center offset"
					self.newCenterOffset = [(self.animationCurrentWindow[0][0]+x * ((self.animationCurrentWindow[1][0]-self.animationCurrentWindow[0][0]) / self.windowSize[0])), 
											(self.animationCurrentWindow[0][1]+y * ((self.animationCurrentWindow[1][1]-self.animationCurrentWindow[0][1]) / self.windowSize[1]))]
					#print " ",newCenterOffset
					#print " ",zoomingLevel
				if self.VFOV-self.minFOV-self.lastZoomingCount == 0:
					self.updateFrustum(0.0)
				else:
					self.updateFrustum((self.zoomingCount-self.lastZoomingCount)/(self.VFOV-self.minFOV-self.lastZoomingCount))
				self.zoomIn()
			elif self.buttonState[2]:
				#print "zoom out button pressed"
				self.previousWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
				self.zoomOut()
				if self.lastZoomingCount != 0:
					self.updateFrustum(self.zoomingCount/self.lastZoomingCount)
				else:
					self.updateFrustum(0.0)
			else:
				#print "zoom button released"
				self.updateFrustum(0.0)
				self.lastZoomingCount = self.zoomingCount
		else:
			self.updateFrustum()

	# clean()
	# reset visual changes, equivalent to resetContinuous()
	def clean(self):
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
		self.raycasting.clean()
	
	def updateWindowDimensions(self,animationState):
		if self.zoomingLevel > 1:
			if self.buttonState[1] == True and self.zoomingLevel < self.maxMultiplier:
				self.currentWindow  = [[self.newCenterOffset[0]-((self.cursorPosition[0]/self.windowSize[0]) * (self.windowSize[0]/self.maxMultiplier)),
								        self.newCenterOffset[1]-((self.cursorPosition[1]/self.windowSize[1]) * (self.windowSize[1]/self.maxMultiplier))],
								       [self.newCenterOffset[0]+((1.0 - (self.cursorPosition[0]/self.windowSize[0])) * (self.windowSize[0]/self.maxMultiplier)),
								        self.newCenterOffset[1]+((1.0 - (self.cursorPosition[1]/self.windowSize[1])) * (self.windowSize[1]/self.maxMultiplier))]]
		else:
			self.previousWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
			self.currentWindow  = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		
		self.animationCurrentWindow = [[(1 - animationState) * self.previousWindow[0][0] + animationState * self.currentWindow[0][0],
								        (1 - animationState) * self.previousWindow[0][1] + animationState * self.currentWindow[0][1]],
								       [(1 - animationState) * self.previousWindow[1][0] + animationState * self.currentWindow[1][0],
								        (1 - animationState) * self.previousWindow[1][1] + animationState * self.currentWindow[1][1]]]

	def zoomIn(self):
		#print "continuous zoom - iteration",zoomingCount
		if self.zoomingLevel < self.maxMultiplier:
			if self.zoomingCount > 0.0:
				self.zoomingCount += 1.0 - sqrt(self.zoomingCount*0.01)
			else:
				self.zoomingCount += 1.0
			self.lastZoomingLevel = self.zoomingLevel
			self.zoomingLevel = 1.0 + (self.zoomingCount / (self.VFOV-self.minFOV)) * (self.maxMultiplier-1.0)

	def zoomOut(self):
		#print "continuous zoom - iteration",zoomingCount
		if self.zoomingCount > 0.0:
			self.zoomingCount -= .5
			self.lastZoomingLevel = self.zoomingLevel
			self.zoomingLevel = 1.0 + (self.zoomingCount / (self.VFOV-self.minFOV)) * (self.maxMultiplier-1.0)

	# selectButtonPressed()
	# callback for the selection button
	def selectButtonPressed(self):
		self.raycasting.selectButtonPressed()
		self.lastZoomingCount = 0
		self.zooming = False
		self.zoomingLevel = 1.0
		self.zoomingCount = 0.0
		# this should be in the discrete zoom and things that derive from it
		#zoomingStack = []
		
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		pass
		
	# zoomInButtonPressed()
	# callback for the zoom in button, equivalent to zoomInButton()
	def zoomInButtonPressed(self):	
		self.zooming = True
	
	# zoomInButtonReleased()
	# callback for the zoom in button
	def zoomInButtonReleased(self):	
		self.previousWindow = self.animationCurrentWindow
	
	# zoomOutButtonPressed()
	# callback for the zoom out button
	def zoomOutButtonPressed(self):	
		self.currentWindow = self.animationCurrentWindow

	# zoomOutButtonReleased()
	# callback for the zoom out button
	def zoomOutButtonReleased(self):
		self.previousWindow = self.animationCurrentWindow
