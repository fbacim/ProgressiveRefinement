import viz
import math
from math import sqrt
import vizmat

from PointingTechnique import PointingTechnique
from ZoomTechnique import ZoomTechnique
from Vector3 import Vector3

class CombinedZoomv2(ZoomTechnique):
	def __init__(self,sceneObjects,hfov,vfov):
		ZoomTechnique.__init__(self,sceneObjects,hfov,vfov)
		
		self.name = "Combined Zoom v2"
		
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
		self.registerButtonCallbacks(self.zoomInButtonPressed,self.zoomInButtonReleased)
		self.registerButtonCallbacks(self.zoomOutButtonPressed,self.zoomOutButtonReleased)
		
		self.showMenu = False
		self.hideMenu = False
		
		self.zoomingStack = []
		
		self.totalAnimationFrames = 60*0.25 # fps * animation_time(s)
		
		# initializes the quadrant that is used discrete zoom, cursor-based techniques
		self.zoomPreview = self.createZoomQuad(2.0)
		self.zoomPreview.visible(viz.OFF)
	
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
		
		if self.zoomingLevel < self.maxMultiplier:
			#print "setting new center offset"
			possiblenewoffset = [0,0]
			if x < float(self.windowSize[0])/4.0:
				possiblenewoffset[0] = 0.0
			elif x > self.windowSize[0]-float(self.windowSize[0])/4.0:
				possiblenewoffset[0] = float(self.windowSize[0])-float(self.windowSize[0])/2.0
			else:
				possiblenewoffset[0] = float(x)-float(self.windowSize[0])/4.0
				
			if y < float(self.windowSize[1])/4.0:
				possiblenewoffset[1] = 0.0
			elif y > self.windowSize[1]-float(self.windowSize[1])/4.0:
				possiblenewoffset[1] = float(self.windowSize[1])-float(self.windowSize[1])/2.0
			else:
				possiblenewoffset[1] = float(y)-float(self.windowSize[1])/4.0
			
			#print possiblenewoffset[0],possiblenewoffset[1]
			
			self.zoomPreview.setPosition((possiblenewoffset[0]+float(self.windowSize[0])/4.0)/float(self.windowSize[0]),
									     (possiblenewoffset[1]+float(self.windowSize[1])/4.0)/float(self.windowSize[1]))
			
		matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		
		if self.zoomingAnimation != 0:
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
			#fov = (VFOV/zoomingLevel)
			self.updateFrustum()
		
		if self.showMenu == True and self.hideMenu == False:
			self.zoomPreview.visible(viz.ON)
		
		if self.zooming == False:
			self.updateFrustum()

	# clean()
	# reset visual changes, equivalent to resetDiscrete()
	def clean(self):
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
		self.zoomPreview.visible(viz.OFF)
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
		
		
		self.animationCurrentWindow = [[(1 - animationState) * self.previousWindow[0][0] + animationState * self.currentWindow[0][0],
								        (1 - animationState) * self.previousWindow[0][1] + animationState * self.currentWindow[0][1]],
								       [(1 - animationState) * self.previousWindow[1][0] + animationState * self.currentWindow[1][0],
								        (1 - animationState) * self.previousWindow[1][1] + animationState * self.currentWindow[1][1]]]

	def zoomIn(self):
		self.zooming = True
		#print "combined zoom"
		if self.zoomingLevel*2.0 > self.maxMultiplier:
			self.lastZoomingLevel = self.zoomingLevel
			self.zoomingAnimation = 0
		else:
			if self.zoomingLevel == 1:
				self.previousCenterOffset = [0,0]
			self.zoomingStack.append(self.newCenterOffset)
			x,y = self.cursorPosition[0],self.cursorPosition[1]
			self.newCenterOffset = [0,0]
			if x < float(self.windowSize[0])/4.0:
				self.newCenterOffset[0] = self.previousCenterOffset[0]
			elif x > self.windowSize[0]-float(self.windowSize[0])/4.0:
				self.newCenterOffset[0] = self.previousCenterOffset[0]+(float(self.windowSize[0])/(self.zoomingLevel*2.0))
			else:
				self.newCenterOffset[0] = self.previousCenterOffset[0]+(float(x)/self.zoomingLevel)-(float(self.windowSize[0])/(self.zoomingLevel*4.0))
				
			if y < float(self.windowSize[1])/4.0:
				self.newCenterOffset[1] = self.previousCenterOffset[1]
			elif y > self.windowSize[1]-float(self.windowSize[1])/4.0:
				self.newCenterOffset[1] = self.previousCenterOffset[1]+(float(self.windowSize[1])/(self.zoomingLevel*2.0))
			else:
				self.newCenterOffset[1] = self.previousCenterOffset[1]+(float(y)/self.zoomingLevel)-(float(self.windowSize[1])/(self.zoomingLevel*4.0))
			
			self.zooming = True
			self.zoomingAnimation = 1 # zoom in
			self.zoomingCount = 1.0
			self.lastZoomingLevel = self.zoomingLevel
			self.zoomingLevel *= 2.0

	def zoomOut(self):
		#print "combined zoom cancel"
		if self.zoomingLevel > 1:
			self.zoomingLevel /= 2.0
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
		if self.zoomingAnimation == 0:
			self.zoomOut()

	# createZoomQuad()
	# creates the quad used by the discrete zoom techniques based on cursor position
	def createZoomQuad(self,zoomFactor):
		texQuad = viz.addTexQuad(viz.SCREEN)
		#texQuad.setPosition(0.25,0.75)
		texQuad.setScale(5.115*1.25*2.0/zoomFactor,5.115*2.0/zoomFactor,1)
		texQuad.color([0.2,0.6,1])
		texQuad.alpha(0.3)
		#texQuad.setPosition(0.5,0.5)
		
		return texQuad
