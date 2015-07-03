import viz
import math
from math import sqrt
import vizmat

from PointingTechnique import PointingTechnique
from ZoomTechnique import ZoomTechnique
from Vector3 import Vector3

class DiscreteZoom(ZoomTechnique):
	def __init__(self,sceneObjects,hfov,vfov):
		ZoomTechnique.__init__(self,sceneObjects,hfov,vfov)
		
		self.name = "Discrete Zoom"
		
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
		self.registerButtonCallbacks(self.zoomInButtonPressed,self.zoomInButtonReleased)
		self.registerButtonCallbacks(self.zoomOutButtonPressed,self.zoomOutButtonReleased)
		
		self.showMenu = False
		self.hideMenu = False
		
		self.zoomingStack = []
		
		self.totalAnimationFrames = 60*0.25 # fps * animation_time(s)
		
		# initializes quadrants for the discrete zoom, quad-based
		self.quadrants = self.createQuadrantsZoom()
		for quad in self.quadrants:
			quad.alpha(.3)
			quad.visible(viz.OFF)
	
	# update()
	# main update function for the discrete zoom technique, equivalent to updateDiscreteCursor()
	def update(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		self.raycasting.cursorPosition = self.cursorPosition
		self.raycasting.windowSize = self.windowSize
		self.raycasting.aspectRatio = self.aspectRatio
		
		self.raycasting.update()
		
		if self.zoomingAnimation == 0:
			self.showMenu = True
		else:
			self.showMenu = False
		
		# quadrants calculation
		cursor = self.cursorOverQuadrant()
		
		matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		
		if self.zoomingAnimation != 0:
			#calculate the direction vector based on the selected quadrant
			x,y = self.previousCenterOffset[0]+self.selectedQuadrant[0],self.previousCenterOffset[1]+self.selectedQuadrant[1]
			#print x,y
			
			self.updateFrustum(self.zoomingCount/self.totalAnimationFrames)
			
			if self.zoomingCount+1 < self.totalAnimationFrames:
				#print self.zoomingCount
				self.zoomingCount += 1
			else:
				#print "done!"
				self.zoomingCount = 0
				self.zoomingAnimation = 0
				self.previousCenterOffset = self.newCenterOffset
		else:
			self.updateFrustum()
		
		if self.showMenu == True and self.hideMenu == False:
			for quad in self.quadrants:
				quad.visible(viz.ON)
			self.colorQuadrants()
		
		if self.zooming == False:
			self.updateFrustum()

	# clean()
	# reset visual changes, equivalent to resetDiscrete()
	def clean(self):
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
		for quad in self.quadrants:
			quad.visible(viz.OFF)
		self.raycasting.clean()
	
	def updateWindowDimensions(self,animationState):
		if self.zoomingLevel > 1:
			if self.zoomingAnimation == 2.0: # zooming out
				self.previousWindow = [self.previousCenterOffset,[self.previousCenterOffset[0]+self.windowSize[0]/(self.zoomingLevel*2.0),self.previousCenterOffset[1]+self.windowSize[1]/(self.zoomingLevel*2.0)]]
			else: # zooming in
				self.previousWindow = [self.previousCenterOffset,[self.previousCenterOffset[0]+self.windowSize[0]/(self.zoomingLevel/2.0),self.previousCenterOffset[1]+self.windowSize[1]/(self.zoomingLevel/2.0)]]
			self.currentWindow  = [self.newCenterOffset,[self.newCenterOffset[0]+self.windowSize[0]/self.zoomingLevel,self.newCenterOffset[1]+self.windowSize[1]/self.zoomingLevel]]
		else:
			if animationState == 0.0 or animationState == 1.0:
				self.previousWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
			elif self.zoomingAnimation == 1.0:
				self.previousWindow = [self.previousCenterOffset,[self.previousCenterOffset[0]+self.windowSize[0]/(self.zoomingLevel/2.0),self.previousCenterOffset[1]+self.windowSize[1]/(self.zoomingLevel/2.0)]]
			else:
				self.previousWindow = [self.previousCenterOffset,[self.previousCenterOffset[0]+self.windowSize[0]/(self.zoomingLevel*2.0),self.previousCenterOffset[1]+self.windowSize[1]/(self.zoomingLevel*2.0)]]
			self.currentWindow  = [[0,0],[self.windowSize[0],self.windowSize[1]]]

	def zoomIn(self):
		self.zooming = True
		#print "discrete zoom"
		if self.zoomingLevel*2 > self.maxMultiplier:
			self.lastZoomingLevel = self.zoomingLevel
			self.zoomingLevel = self.maxMultiplier
			self.zoomingAnimation = 0
		else:
			if self.zoomingLevel == 1:
				self.previousCenterOffset = [0,0]
			self.selectedQuadrant = self.cursorOverQuadrant()
			self.zoomingStack.append(self.newCenterOffset)
			self.newCenterOffset = self.calculateDiscreteCursorOffset(self.zoomingLevel)
			self.zooming = True
			self.zoomingAnimation = 1 # zoom in
			self.zoomingCount = 1.0
			self.lastZoomingLevel = self.zoomingLevel
			self.zoomingLevel *= 2

	def zoomOut(self):
		#print "discrete zoom cancel"
		if self.zoomingLevel > 1:
			self.zoomingLevel /= 2
			self.zooming = True
			self.zoomingAnimation = 2 # zoom out
			self.zoomingCount = 1.0
			self.previousCenterOffset = self.newCenterOffset
			self.newCenterOffset = self.zoomingStack.pop()

	# selectButtonPressed()
	# callback for the selection button
	def selectButtonPressed(self):
		self.raycasting.selectButtonPressed()
		self.lastZoomingCount = 0
		self.zooming = False
		self.zoomingLevel = 1.0
		self.zoomingCount = 0.0
		# this should be in the discrete zoom and things that derive from it
		self.zoomingStack = []
		
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		pass
		
	# zoomInButtonPressed()
	# callback for the zoom in button, equivalent to zoomInButton()
	def zoomInButtonPressed(self):
		pass
	
	# zoomInButtonReleased()
	# callback for the zoom in button
	def zoomInButtonReleased(self):	
		if self.zoomingAnimation == 0:
			self.zoomIn()
	
	# zoomOutButtonPressed()
	# callback for the zoom out button
	def zoomOutButtonPressed(self):	
		pass

	# zoomOutButtonReleased()
	# callback for the zoom out button
	def zoomOutButtonReleased(self):
		self.zoomOut()

	# createQuadrantsZoom()
	# creates the quadrants of the discrete zoom technique
	def createQuadrantsZoom(self):
		quadrants = []
		
		# quadrants
		texQuad = viz.addTexQuad(viz.SCREEN)
		texQuad.setPosition(0.25,0.75)
		texQuad.setScale(5.115*1.25,5.115,1)
		#texQuad.setPosition(0.5,0.5)
		#texQuad.setScale(10.23*1.255,10.23,1)
		quadrants.append(texQuad)
		
		texQuad = viz.addTexQuad(viz.SCREEN)
		texQuad.setPosition(0.75,0.75)
		texQuad.setScale(5.115*1.25,5.115,1)
		quadrants.append(texQuad)
		
		texQuad = viz.addTexQuad(viz.SCREEN)
		texQuad.setPosition(0.25,0.25)
		texQuad.setScale(5.115*1.25,5.115,1)
		quadrants.append(texQuad)
		
		texQuad = viz.addTexQuad(viz.SCREEN)
		texQuad.setPosition(0.75,0.25)
		texQuad.setScale(5.115*1.25,5.115,1)
		quadrants.append(texQuad)
		
		# lines
		texQuad = viz.addTexQuad(viz.SCREEN)
		texQuad.setPosition(0.5,0.5)
		texQuad.setScale(10.23*1.255,0.025,1)
		texQuad.color(0,0,0)
		quadrants.append(texQuad)
		
		texQuad = viz.addTexQuad(viz.SCREEN)
		texQuad.setPosition(0.5,0.5)
		texQuad.setScale(0.025,10.23,1)
		texQuad.color(0,0,0)
		quadrants.append(texQuad)
		
		return quadrants

	# colorQuadrants()
	# changes the color of the quadrants based on the cursor position
	def colorQuadrants(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		if x < self.windowSize[0]/2.0 and y >= self.windowSize[1]/2.0:
			self.quadrants[0].color([0.2,0.6,1])
			self.quadrants[0].alpha(0.3)
		else:
			self.quadrants[0].color([0,0,0])
			self.quadrants[0].alpha(0.0)
		if x >= self.windowSize[0]/2.0 and y >= self.windowSize[1]/2.0:
			self.quadrants[1].color([0.2,0.6,1])
			self.quadrants[1].alpha(0.3)
		else:
			self.quadrants[1].color([0,0,0])
			self.quadrants[1].alpha(0.0)
		if x < self.windowSize[0]/2.0 and y < self.windowSize[1]/2.0:
			self.quadrants[2].color([0.2,0.6,1])
			self.quadrants[2].alpha(0.3)
		else:
			self.quadrants[2].color([0,0,0])
			self.quadrants[2].alpha(0.0)
		if x >= self.windowSize[0]/2.0 and y < self.windowSize[1]/2.0:
			self.quadrants[3].color([0.2,0.6,1])
			self.quadrants[3].alpha(0.3)
		else:
			self.quadrants[3].color([0,0,0])
			self.quadrants[3].alpha(0.0)
	
	# cursorOverQuadrant()
	# returns the center of the zoom window quadrant being currently highlighted 
	def cursorOverQuadrant(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		if x < self.windowSize[0]/2.0 and y >= self.windowSize[1]/2.0:
			cursor = [(self.windowSize[0]/4.0)/self.zoomingLevel,(3.0*self.windowSize[1]/4.0)/self.zoomingLevel] 
		elif x >= self.windowSize[0]/2.0 and y >= self.windowSize[1]/2.0:
			cursor = [(3.0*self.windowSize[0]/4.0)/self.zoomingLevel,(3.0*self.windowSize[1]/4.0)/self.zoomingLevel] 
		elif x < self.windowSize[0]/2.0 and y < self.windowSize[1]/2.0:
			cursor = [(self.windowSize[0]/4.0)/self.zoomingLevel,(self.windowSize[1]/4.0)/self.zoomingLevel] 
		elif x >= self.windowSize[0]/2.0 and y < self.windowSize[1]/2.0:
			cursor = [(3.0*self.windowSize[0]/4.0)/self.zoomingLevel,(self.windowSize[1]/4.0)/self.zoomingLevel] 
			
		return cursor
		
	# calculateDiscreteCursorOffset()
	# returns the origin position of the quadrant window
	def calculateDiscreteCursorOffset(self,level):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		if x < self.windowSize[0]/2.0 and y >= self.windowSize[1]/2.0:
			cursor = [0,(self.windowSize[1]/2.0)/level] 
		elif x >= self.windowSize[0]/2.0 and y >= self.windowSize[1]/2.0:
			cursor = [(self.windowSize[0]/2.0)/level,(self.windowSize[1]/2.0)/level] 
		elif x < self.windowSize[0]/2.0 and y < self.windowSize[1]/2.0:
			cursor = [0,0] 
		elif x >= self.windowSize[0]/2.0 and y < self.windowSize[1]/2.0:
			cursor = [(self.windowSize[0]/2.0)/level,0] 
		
		cursor = [self.previousCenterOffset[0]+cursor[0],self.previousCenterOffset[1]+cursor[1]]
		return cursor
