import viz
import math

from PointingTechnique import PointingTechnique

class Raycasting(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "Ray-casting"
		
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
	
	# update()
	# main update function for ray-casting, needs to be called every frame/every time the cursor is updated
	def update(self):
		x = max(0, min(self.cursorPosition[0], self.windowSize[0]-1))
		y = max(0, min(self.cursorPosition[1], self.windowSize[1]-1))
		
		self.crosshair.visible(viz.ON)
		self.scSphere.visible(viz.OFF)
		
		obj = viz.pick(pos = [x/self.windowSize[0],y/self.windowSize[1]])
		if obj.valid():
			obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
			#print intersectObj,": ",obj_size
			if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
				self.intersectingObjects = []
				self.intersectingObjects.append(obj)
			else:
				self.intersectingObjects = []
		else:
			self.intersectingObjects = []
		self.drawIntersectObjsBoundingBoxes()
		
		self.crosshair.setPosition(x/self.windowSize[0],y/self.windowSize[1],0)
		
	# selectButtonPressed()
	# callback for the selection button
	def selectButtonPressed(self):
		#print 'select pressed'
		if len(self.intersectingObjects) > 0:
			self.selectedObject = self.intersectingObjects[0]
		
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		#print 'select released'
		pass
	
	def clean(self):
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
	
	def reset(self):
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
	