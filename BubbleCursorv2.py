import viz
import math
import sys
from math import sqrt
import vizmat
import vizact

from PointingTechnique import PointingTechnique
from Vector3 import Vector3

from PIL import Image
from collections import defaultdict

from Timer import Timer

class BubbleCursorv2(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "Bubble Cursor v2"
		
		# flag that tells if there are intersecting objects
		self.intersecting = False
		
		# variable that controls the animation of the objects in the quadrants
		self.rotQUAD = 0
		
		# saving the bounding spheres and initial positions
		self.bs = []
		for obj in self.objects:
			self.bs.append(obj.getBoundingSphere(viz.ABS_GLOBAL))
			
		# Create the extension
		self.occlusionCheckExt = viz.add('extension/myextension.dle')
			
		# make sure we render the sphere last so it appears at the screen at all times
		self.ccCone = viz.addTexQuad(viz.ORTHO,1)
		self.ccCone.setPosition([0,0,0]) 
		self.ccCone.color(0.3,0.5,1.0)
		pic = viz.addTexture('cone.png')
		self.ccCone.texture(pic) 
		
		# register button callbacks
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
		
		# abstract environment has to initialize everything every time
		if len(self.objects) > 0:
			self.initializeObjects()
	
	# createQuad()
	# creates the triangles used in the quad menu quadrants
	def createQuad(self):
		viz.startlayer(viz.QUADS,'bg') 
		viz.vertex(-1000,-1000,0) #Vertices are split into pairs.
		viz.vertex( 1000,-1000,0)
		viz.vertex( 1000, 1000,0)
		viz.vertex(-1000, 1000,0)
		return viz.endlayer()
	
	def createLine(self,start,end):
		viz.startlayer(viz.LINES,'line') 
		viz.lineWidth(3.0)
		viz.vertex(start[0],start[1],start[2]) #Vertices are split into pairs.
		viz.vertex(end[0],end[1],end[2])
		return viz.endlayer()
		
	# reset()
	# resets SQUAD quadrants
	def reset(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
	
	# selectButtonPressed()
	# callback for the selection button
	def selectButtonPressed(self):
		if len(self.intersectingObjects) == 1:
			print 'selected object ',self.intersectingObjects[0]
			self.selectedObject = self.intersectingObjects[0]
			
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		pass
	
	def initializeObjects(self):
		# Create a dictionary (std::map equiv) for the rgb/object key
		self.objectMap = {None:[-1,0,0,0,255,255]}#{(0,0,0,255):[-1,None]}
		self.colorMap = {}
		
		# define the secondary scene for our custom render node to calculate occlusion culling
		try:
			self.occlusionObjects
		except AttributeError:
			self.occlusionObjects = []
		else:
			while len(self.occlusionObjects) > 0:
				tmp = self.occlusionObjects[0]
				self.occlusionObjects.remove(self.occlusionObjects[0])
				tmp.remove()
		
		r = 0
		g = 0#0.05882353
		b = 0#0.60784314
		compositeColor = (int(r*255) << 16) | (int(g*255) << 8) | int(b*255)
		compositeColorIncrement = int((math.floor(math.pow(256,3))/len(self.objects)))
		index = 0
		for obj in self.objects:
			# check object constraints
			obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
			if obj_size[0] > 40 or obj_size[1] > 40 or obj_size[2] > 40:
				# if it's too big to be selected, make it white like the background
				r = 1
				g = 1
				b = 1
				
			#print 'color (',int(compositeColor),':',hex(compositeColor),'):',hex(int(r*255)),hex(int(g*255)),hex(int(b*255))
			self.occlusionObjects.append(obj.copy(scene = 2))
			self.occlusionObjects[-1].disable(viz.LIGHTING)
			self.occlusionObjects[-1].texture(viz.OFF)
			self.occlusionObjects[-1].color(r,g,b)
	
			# send composite color to our extension to create map of colors
			#self.occlusionCheckExt.modifyNode(obj, x=compositeColor)
			
			# save composite locally
			self.objectMap[obj] = [index,r,g,b,255,compositeColor]
			self.colorMap[compositeColor] = obj
			
			# calculate color of next node
			compositeColor += int(compositeColorIncrement)
			r = ((int(compositeColor) & 0x00ff0000) >> 16)/255.0
			g = ((int(compositeColor) & 0x0000ff00) >> 8)/255.0
			b = ((int(compositeColor) & 0x000000ff))/255.0
			
			index += 1
		
		# make sure things are only initialized once
		try:
			self.colorTexture
			self.renderNode
			self.window
			#self.debugWindow 
		except AttributeError:
			# Create render texture for camera video feed
			self.colorTexture = viz.addRenderTexture()
			# Create render node for camera
			self.renderNode = viz.addRenderNode(scene = 2)
			self.renderNode.linkViewportSizeToWindow(viz.MainWindow)
		
			# Set background render color 
			self.renderNode.setClearColor(viz.WHITE)

			# Do not inherit view/projection settings from main window
			self.renderNode.setInheritView(True)

			# Render to video feed texture
			self.renderNode.setRenderTexture(self.colorTexture)
		
			self.scSphere.renderToAllRenderNodesExcept([self.renderNode])
			
			self.window = viz.addWindow(pos=(1.0,1.0),size=(1.0,1.0)) 
			self.view = viz.addView()
			self.view.setScene(2)
			self.window.setView(self.view)
			#self.window.setScene(viz.Scene2)
			
			'''
			# From here on, used to debug color map
			self.debugWindow = viz.addTexQuad(parent = viz.ORTHO)
			self.debugWindow.setPosition(400,300)
			self.debugWindow.setScale(800,600,1)
			self.debugWindow.texture(self.colorTexture)
			
			# Create shader object and assosiate it with our texture blending frag program
			shader = viz.addShader( frag = 'process.frag' )

			# Create the shader parameter objects
			# They tell the shader the texture numbers of blendable textures and blend amount
			self.pointerXUniform = viz.addUniformFloat( 'PointerX', 0.0 )
			self.pointerYUniform = viz.addUniformFloat( 'PointerY', 0.0 )
			self.pointerRadiusUniform = viz.addUniformFloat( 'PointerRadius', 10.0 )
			self.textureUnit1Uniform = viz.addUniformInt( 'TextureUnit1', 0 )
			
			# Make Vizard use the created shader when rendering the logo node
			self.debugWindow.apply(shader)
			# Provide the shader with its parameters
			self.debugWindow.apply(self.pointerXUniform)
			self.debugWindow.apply(self.pointerYUniform)
			self.debugWindow.apply(self.pointerRadiusUniform)
			self.debugWindow.apply(self.textureUnit1Uniform)
			'''
	
	
	# update()
	# main update function for squad, needs to be called every frame/every time the cursor is updated
	def update(self):
		self.window.visible(viz.ON)
		
		x = max(0, min(self.cursorPosition[0], self.windowSize[0]-1))
		y = max(0, min(self.cursorPosition[1], self.windowSize[1]-1))
		
		user_position = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		user_position_v3 = Vector3(user_position[12],user_position[13],user_position[14])
		#print "User Position:", user_position[12], user_position[13], user_position[14]
		#print "orientation:",viz.MainView.getEuler()
		
		self.view.setMatrix(viz.MainView.getMatrix())
		# Set FOV for video camera
		VFOV = 2.0 * math.atan( math.tan( (90.0/57.2957795) / 2.0 ) / self.aspectRatio ) * 57.2957795
		self.window.fov(VFOV)
		
		timer = Timer()
		timer.start()

		self.scSphere.visible(viz.ON)
		self.ccCone.visible(viz.ON)
		self.crosshair.visible(viz.ON)
		
		self.crosshair.setPosition(x/self.windowSize[0],y/self.windowSize[1],0)
		
		#print "[",timer.elapsed(),"] started update "
		
		min_distance = self.occlusionCheckExt.modifyTexture(self.colorTexture, x=x, y=y)
		#print min_distance
		self.ccCone.setPosition(float(x),float(y),0)
		visibleRadius = max(6,min_distance*2.0)
		self.ccCone.setScale(visibleRadius,visibleRadius)
		self.lastConeRadius = min_distance
		#print "[",timer.elapsed(),"] found minimum distance"
		
		self.intersectingObjects = []
		colors = self.occlusionCheckExt.command(2,x=x,y=y,z=min_distance)
		#print hex(colors)
		for icolor in colors:
			composite = (icolor & 0xffffff) # convert to unsigned integer
			#print hex(composite)
			
			# get object from local map
			if composite in self.colorMap:
				self.intersectingObjects.append(self.colorMap[composite])
		#print "[",timer.elapsed(),"] determined objects in cone"
		
		self.drawIntersectObjsBoundingBoxes()
		self.userdata = min_distance
		#print "[",timer.elapsed(),"] bounding boxes"

	# clean()
	# reset visual aids/quadrants
	def clean(self):
		self.scSphere.visible(viz.OFF)
		self.ccCone.visible(viz.OFF)
		self.crosshair.visible(viz.OFF)
	
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
			aux_bs = object.getBoundingSphere(viz.ABS_GLOBAL)
			bs = self.createSphere(20,20)
			bs.setPosition(aux_bs.center)
			bs.setScale(aux_bs.radius,aux_bs.radius,aux_bs.radius)
			bs.color(0.3,0.5,1.0)
			bs.alpha(0.5)
			bs.disable(viz.PICKING)
			self.boundingBoxes.append(bs)
		
		if self.selectedObject != None:
			aux_bs = object.getBoundingSphere(viz.ABS_GLOBAL)
			self.selectedObjectBoundingBox = self.createSphere(20,20)
			self.selectedObjectBoundingBox.setPosition(aux_bs.center)
			self.selectedObjectBoundingBox.setScale(aux_bs.radius,aux_bs.radius,aux_bs.radius)
			self.selectedObjectBoundingBox.color(1,0,0)
			self.selectedObjectBoundingBox.alpha(0.5)
			self.selectedObjectBoundingBox.disable(viz.PICKING)
