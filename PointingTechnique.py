import viz
import math
import abstractmethod

from Vector3 import Vector3

# base class that contains functions needed by all techniques
class PointingTechnique:
	def __init__(self,sceneObjects):
		# used by ALL techniques 
		self.name = 'PointingTechnique'
		self.windowSize = [0,0]
		self.aspectRatio = 1.0
		self.cursorPosition = [0,0] # cursor position within the boundaries of the screensize
		self.cursorPositionNormalized = [0,0] # normalized cursor position, not limited to boundaries
		self.objects = sceneObjects
		self.fps = 0.0

		# this is the sphere-casting's sphere but also is used for ray-casting
		self.scSphereRadius = 0.0005953125 #Globals.TINY_SPHERE_RADIUS
		self.scSphere = self.createSphere(20,20)
		self.scSphere.setScale(self.scSphereRadius,self.scSphereRadius,self.scSphereRadius)
		self.scSphere.color(0.2,0.6,1.0)
		self.scSphere.visible(viz.OFF)
		self.scSphere.alpha(0.6)
		self.scSphere.disable(viz.PICKING)
		
		# this is the cone-casting part of this, uses same radius and everything
		self.ccCone = None
		
		# used for everything, contains all objects inside of/colliding with the sphere
		self.intersectingObjects = []
		
		# used to store the selected object to draw bounding box
		self.selectedObject = None
		self.selectedObjectBoundingBox = None
		
		# used for ray-casting and the QUAD menu
		self.crosshair = viz.addTexQuad(viz.SCREEN,texture=viz.add('bline.png'))
		
		# stores all active bounding boxes
		self.boundingBoxes = []
		
		# stores button state needed for some techniques
		self.buttonState = []
		
		# stores the button callbacks
		self.buttonPressedCallback = []
		self.buttonReleasedCallback = []
		
		# stores technique specific stuff or general user data to be written in the experiment files
		self.userdata = 0
		
	# createSphere()
	# creates a sphere 
	def createSphere(self,lats,longs):
		for i in range(lats+1):
			lat0 = math.pi * (-0.5 + (float(i) - 1.0) / lats)
			z0  = math.sin(lat0)
			zr0 = math.cos(lat0)
			
			lat1 = math.pi * (-0.5 + float(i) / lats)
			z1 = math.sin(lat1)
			zr1 = math.cos(lat1)
			
			viz.startlayer(viz.QUAD_STRIP) 
			for j in range(longs+1):
				lng = 2 * math.pi * (float(j) - 1.0) / longs
				x = math.cos(lng)
				y = math.sin(lng)
					
				viz.normal(x * zr0, y * zr0, z0)
				viz.vertex(x * zr0, y * zr0, z0)
				viz.normal(x * zr1, y * zr1, z1)
				viz.vertex(x * zr1, y * zr1, z1)
		
		return viz.endlayer()
		
	def perp(self, v):
		min = math.fabs(v.x)
		cardinalAxis = Vector3(1.0, 0.0, 0.0)

		if math.fabs(v.y) < min:
			min = math.fabs(v.y)
			cardinalAxis = Vector3(0.0, 1.0, 0.0)

		if math.fabs(v.z) < min:
			cardinalAxis = Vector3(0.0, 0.0, 1.0)

		return Vector3.Cross(v, cardinalAxis)

	# d – axis defined as a normalized vector from base to apex
	# a – position of apex
	# h – height
	# rd – radius of directrix
	# n – number of radial “slices”
	def createCone(self, d, a, h, rd, n):
		c = a + (-d * h)
		e0 = self.perp(d)
		e1 = Vector3.Cross(e0, d)
		angInc = 360.0 / n * 0.0174532925

		# draw cone top
		viz.startlayer(viz.TRIANGLE_FAN) 
		viz.vertex(a.x, a.y, a.z)
		for i in range(n+1):
			rad = angInc * i
			p = c + (((e0 * math.cos(rad)) + (e1 * math.sin(rad))) * rd)
			viz.vertex(p.x, p.y, p.z)

		# draw cone bottom
		viz.startlayer(viz.TRIANGLE_FAN) 
		viz.vertex(c.x, c.y, c.z)
		for i in range(n,0,-1):
			rad = angInc * i
			p = c + (((e0 * math.cos(rad)) + (e1 * math.sin(rad))) * rd)
			viz.vertex(p.x, p.y, p.z)
			viz.normal(d[0],d[1],d[2])

		return viz.endlayer()

	# createBoundingBox()
	# creates a bounding box with the given size
	def createBoundingBox(self,min,max,width=2.0):
		viz.startlayer(viz.LINE_LOOP, 'top') 
		viz.vertexcolor(1.0,1.0,0.0)
		viz.linewidth(width)
		
		#top
		#viz.vertexcolor(0.0,1.0,0.0)
		#viz.normal(0,1,0)
		viz.vertex( max[0], max[1], min[2])
		viz.vertex( min[0], max[1], min[2])
		viz.vertex( min[0], max[1], max[2])
		viz.vertex( max[0], max[1], max[2])

		viz.startlayer(viz.LINE_LOOP,'bottom') 
		viz.vertexcolor(.5,.5,0.0)
		viz.linewidth(width)
		
		#bottom
		#viz.vertexcolor(1.0,0.5,0.0)
		#viz.normal(0,-1,0)
		viz.vertex( max[0], min[1], max[2])
		viz.vertex( min[0], min[1], max[2])
		viz.vertex( min[0], min[1], min[2])
		viz.vertex( max[0], min[1], min[2])

		viz.startlayer(viz.LINE_LOOP,'front') 
		viz.vertexcolor(.5,.5,0.0)
		viz.linewidth(width)
		
		#front
		#viz.vertexcolor(1.0,0.0,0.0)
		#viz.normal(0,0,1)
		viz.vertex( max[0], max[1], max[2])
		viz.vertex( min[0], max[1], max[2])
		viz.vertex( min[0], min[1], max[2])
		viz.vertex( max[0], min[1], max[2])

		viz.startlayer(viz.LINE_LOOP,'back') 
		viz.vertexcolor(.5,.5,0.0)
		viz.linewidth(width)
		
		#back
		#viz.vertexcolor(1.0,1.0,0.0)
		#viz.normal(0,0,-1)
		viz.vertex( max[0], min[1], min[2])
		viz.vertex( min[0], min[1], min[2])
		viz.vertex( min[0], max[1], min[2])
		viz.vertex( max[0], max[1], min[2])

		viz.startlayer(viz.LINE_LOOP,'left') 
		viz.vertexcolor(.5,.5,0.0)
		viz.linewidth(width)
		
		#left
		#viz.vertexcolor(0.0,0.0,1.0)		
		#viz.normal(-1,0,0)
		viz.vertex( min[0], max[1], max[2])	
		viz.vertex( min[0], max[1], min[2])	
		viz.vertex( min[0], min[1], min[2])	
		viz.vertex( min[0], min[1], max[2])	

		viz.startlayer(viz.LINE_LOOP,'right') 
		viz.vertexcolor(.5,.5,0.0)
		viz.linewidth(width)
		
		#right
		#viz.vertexcolor(1.0,0.0,1.0)
		#viz.normal(1,0,0)
		viz.vertex( max[0], max[1], min[2])	
		viz.vertex( max[0], max[1], max[2])	
		viz.vertex( max[0], min[1], max[2])	
		viz.vertex( max[0], min[1], min[2])	
		
		return viz.endlayer()

	# resetBoundingBoxes()
	# reset the bounding boxes
	def resetBoundingBoxes(self):
		for bb in self.boundingBoxes:
			bb.remove()
		self.boundingBoxes = []
		if self.selectedObjectBoundingBox != None:
			self.selectedObjectBoundingBox.remove()
			self.selectedObjectBoundingBox = None
	
	# drawIntersectObjsBoundingBoxes()
	# creates the bounding boxes of all objects that are inside the sphere, independent of its size
	def drawIntersectObjsBoundingBoxes(self):
		self.resetBoundingBoxes()
		
		for object in self.intersectingObjects:
			aux_bb = object.getBoundingBox(viz.ABS_GLOBAL)
			min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
			bb = self.createBoundingBox(min,max)
			bb.disable(viz.PICKING)
			self.boundingBoxes.append(bb)
		
		if self.selectedObject != None:
			aux_bb = self.selectedObject.getBoundingBox(viz.ABS_GLOBAL)
			min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
			self.selectedObjectBoundingBox = self.createBoundingBox(min,max,5.0)
			self.selectedObjectBoundingBox.color(1.0,0.0,0.0)
			self.selectedObjectBoundingBox.disable(viz.PICKING)

	def registerButtonCallbacks(self,pressed,released):
		self.buttonPressedCallback.append(pressed)
		self.buttonReleasedCallback.append(released)
		self.buttonState.append(False)
	
	def buttonPressed(self,n): # n is the button number
		if n >= 0 and n < len(self.buttonPressedCallback):
			(self.buttonPressedCallback[n])()
			self.buttonState[n] = True
	
	def buttonReleased(self,n): # n is the button number
		if n >= 0 and n < len(self.buttonReleasedCallback):
			(self.buttonReleasedCallback[n])()
			self.buttonState[n] = False

	def resetSelectedObject(self):
		self.selectedObject = None

	@abstractmethod.abstractmethod
	def update(self): pass
	
	@abstractmethod.abstractmethod
	def clean(self): pass
	
	@abstractmethod.abstractmethod
	def reset(self): pass
