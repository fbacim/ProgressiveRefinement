import viz
import math
from math import sqrt
import vizmat
import abstractmethod

from PointingTechnique import PointingTechnique
from Vector3 import Vector3
from Raycasting import Raycasting

class ZoomTechnique(PointingTechnique):
	def __init__(self,sceneObjects,hfov,vfov):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "Zoom Technique"
		
		self.raycasting = Raycasting(sceneObjects)
		self.crosshair.visible(viz.OFF) # using raycasting's crosshair
		
		self.defaultHFOV = hfov
		self.VFOV = vfov
		self.maxMultiplier = 128.0
		self.minFOV = self.VFOV / self.maxMultiplier

		self.previousWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		self.currentWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		self.animationCurrentWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		
		self.zooming = False
		self.zoomingAnimation = 0
		self.zoomingCount = 0
		self.zoomingLevel = 1
		self.lastZoomingLevel = self.zoomingLevel
		self.previousZoomingLevel = 1
		self.previousCenterOffset = [0,0]
		self.newCenterOffset = [0,0]
		self.lastZoomingCount = 0
	
	# updateFrustum()
	# updates the frustum based on the zoom window dimensions and position
	def updateFrustum(self,animationState = 1.0):
		# calculate the window dimensions based on the technique being used
		self.updateWindowDimensions(animationState)
		
		# calculate frustum
		cameraNear = 0.1
		cameraFar  = 1000.0
		yfov = 2.0 * math.atan( math.tan( (self.defaultHFOV/57.2957795) / 2.0 ) / self.aspectRatio ) * 57.2957795;
		ymax = cameraNear*math.tan(yfov*math.pi/360.0)
		ymin = -ymax
		xmax = ymax*self.aspectRatio
		xmin = ymin*self.aspectRatio
		
		# previous window frustm
		pxmin = -((self.previousWindow[0][0]/self.windowSize[0]) * (xmin * 2.0) - xmin)
		pxmax = (self.previousWindow[1][0]/self.windowSize[0]) * (xmax * 2.0) - xmax
		pymin = -((self.previousWindow[0][1]/self.windowSize[1]) * (ymin * 2.0) - ymin)
		pymax = (self.previousWindow[1][1]/self.windowSize[1]) * (ymax * 2.0) - ymax
		
		# current window frustum
		cxmin = -((self.currentWindow[0][0]/self.windowSize[0]) * (xmin * 2.0) - xmin)
		cxmax = (self.currentWindow[1][0]/self.windowSize[0]) * (xmax * 2.0) - xmax
		cymin = -((self.currentWindow[0][1]/self.windowSize[1]) * (ymin * 2.0) - ymin)
		cymax = (self.currentWindow[1][1]/self.windowSize[1]) * (ymax * 2.0) - ymax
		
		# final frustum - linear interpolation
		xmin = (1 - animationState) * pxmin + animationState * cxmin
		xmax = (1 - animationState) * pxmax + animationState * cxmax
		ymin = (1 - animationState) * pymin + animationState * cymin
		ymax = (1 - animationState) * pymax + animationState * cymax
		
		# set main window frustum
		viz.MainWindow.frustum(xmin,xmax,ymin,ymax,cameraNear,cameraFar)
	
	# updateWindowDimensionsCombined()
	# updates zoom window position and dimensions for the zoom animation
	@abstractmethod.abstractmethod
	def updateWindowDimensions(self,animationState):
		pass
	
	# reset()
	# resets zoom variables and view
	def reset(self):
		self.zooming = False
		self.zoomingAnimation = 0
		self.zoomingCount = 0
		self.zoomingLevel = 1
		self.lastZoomingLevel = self.zoomingLevel
		self.previousZoomingLevel = 1
		self.previousCenterOffset = [0,0]
		self.newCenterOffset = [0,0]
		self.lastZoomingCount = 0
		
		# this should be in the discrete zoom and things that derive from it
		#zoomingStack = []
		
		self.previousWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		self.currentWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		self.animationCurrentWindow = [[0,0],[self.windowSize[0],self.windowSize[1]]]
		
		self.updateFrustum()
		self.raycasting.resetBoundingBoxes()
	
	# update()
	# main update function for the zoom techniques
	@abstractmethod.abstractmethod
	def update(self):
		pass

	# clean()
	# reset visual changes
	@abstractmethod.abstractmethod
	def clean(self):	
		pass

	# selectButtonPressed()
	# callback for the selection button
	@abstractmethod.abstractmethod
	def selectButtonPressed(self):
		pass
		
	# selectButtonReleased()
	# callback for the selection button
	@abstractmethod.abstractmethod
	def selectButtonReleased(self):
		pass

	# zoomInButtonPressed()
	# callback for the zoom in button
	@abstractmethod.abstractmethod
	def zoomInButtonPressed(self):	
		pass
		
	# zoomInButtonReleased()
	# callback for the zoom in button
	@abstractmethod.abstractmethod
	def zoomInButtonReleased(self):	
		pass
		
	# zoomOutButtonPressed()
	# callback for the zoom out button
	@abstractmethod.abstractmethod
	def zoomOutButtonPressed(self):
		pass
		
	# zoomOutButtonReleased()
	# callback for the zoom out button
	@abstractmethod.abstractmethod
	def zoomOutButtonReleased(self):
		pass
