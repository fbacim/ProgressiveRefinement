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

def frange(x, y, jump):
	ret = []
	while x < y:
		ret.append(x)
		x += jump
	return ret
	
import ctypes

def ReadColorBuffer(id):
	w,h = viz.window.getSize()
	size = w * h
	data = (ctypes.c_char * size)()
	GL_RGBA = 0x1908
	GL_UNSIGNED_BYTE = 0x1401
	GL_FRONT = 0x0404
	GL_TEXTURE_2D = 0x0DE1
	ctypes.windll.opengl32.glBindTexture(GL_TEXTURE_2D, id);
	ctypes.windll.opengl32.glReadBuffer(GL_FRONT)
	ctypes.windll.opengl32.glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE, ctypes.byref(data))
	data_list = [data[i] for i in range(size)]
	return data_list

class InteractionMode:
	SELECTION = 0
	SELECTION_EXPAND = 1

class ExpandBubblev61(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "Expand+bubble cursor v6 - Abstract version"
		
		# initialize quadrants
		self.expandBackground = self.createQuad()
		self.expandBackground.color(0.8,0.8,0.8)
		self.expandBackground.alpha(0.6)
		self.expandBackground.depthFunc(viz.GL_ALWAYS)
		self.expandBackground.drawOrder(1)
		self.expandBackground.visible(viz.OFF)
		
		# object clone list for the quadrants
		self.clone_list = []
		
		# for calculating distances between the cursor and objects in the quad menu
		self.distance_list = []
		
		# SQUAD selection mode, can be SELECTION and SELECTION_QUADRANT
		self.mode = InteractionMode.SELECTION
		
		# flag that tells if there are intersecting objects
		self.intersecting = False
		
		# variable that controls the animation of the objects in the quadrants
		self.rotQUAD = 0
		
		# bubbles in the expand menu
		self.bubbleQuadMenu = None
		self.bubbleQuadMenuObj = None
		
		# object selected by expand menu
		self.objInBubble = None
		
		# line that connects the object in the menu to the real object
		self.menuObj2OjbLine = None
		
		# saving the bounding spheres and initial positions
		self.bs = []
		for obj in self.objects:
			self.bs.append(obj.getBoundingSphere(viz.ABS_GLOBAL))
			
		# Create the extension
		self.occlusionCheckExt = viz.add('extension/myextension.dle')
			
		# make sure we render the sphere last so it appears at the screen at all times
		self.ccCone = viz.addTexQuad(viz.ORTHO,1)
		self.ccCone.setPosition([0,0,0]) 
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
	
	#-------------------------------------------------------------------------------
	# SQUAD quadrants functions
	#-------------------------------------------------------------------------------
	# createExpandMenu()
	# distributes the items that were inside the sphere
	def createExpandMenu(self,list,centered=0):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		self.clone_list = []
		
		expandSize = math.ceil(math.sqrt(len(list))) # size of rows/columns
		print expandSize
		nrows = math.ceil(len(list)/expandSize)
		distance = expandSize*20
		
		#print "selecting an object among:",list
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		#print "size of the array:",len(list)
		
		index = 0
		#print "list"
		for clone in list:
			#clone.collideNone()
			clone.depthFunc(viz.GL_ALWAYS)
			clone.drawOrder(4)
			obj_position = []
			
			row = math.floor(index/expandSize)
			col = index%expandSize
			
			print row, col
			
			x,y = 0.2+0.6*(col/(expandSize-1.0)),0.2+0.6*((row/(nrows-1.0) if nrows > 1 else 0.5))
			
			line = viz.screentoworld(x,y)
			#print index," ",line.begin,"to",line.end,". Dir:",line.dir
			dir_vector = line.dir
			length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
			dir_vector[0] = (dir_vector[0]/length)#*1.3
			dir_vector[1] = (dir_vector[1]/length)#*1.3
			dir_vector[2] = (dir_vector[2]/length)#*1.3
			#print index,"  dir_vector[%.4f,"%((x*aspectRatio)-aspectRatio/2.0)+"%.4f"%y+"] =",dir_vector,"    length =",length
			#if index%4 == 0:
			#	print "going to",(user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4]
			clone.setMatrix(identity,viz.ABS_GLOBAL)		
			obj_position = clone.getBoundingBox(viz.ABS_GLOBAL).center
			curPos = clone.getPosition() #Save current position
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance,(user_position[1]-obj_position[1])+dir_vector[1]*distance,(user_position[2]-obj_position[2])+dir_vector[2]*distance, viz.ABS_GLOBAL)
			gotoPos = clone.getPosition() #Get computed local pos
			clone.setPosition(curPos) #Restore position
			clone.runAction(vizact.goto(gotoPos,.25,viz.TIME)) # animation
			#clone.setPosition(gotoPos) # static
			self.clone_list.append(clone)
			index+=1
	
	# selectObject()
	# callback for selection of objects
	def selectObject(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		if len(self.clone_list) > 0 and self.objInBubble != None:
			index = 0
			for clone in self.clone_list:
				#print "removing index",index,"..."
				clone.endAction(viz.ALL_POOLS)
				clone.setMatrix(identity,viz.ABS_GLOBAL)
				clone.depthFunc(viz.GL_LESS)
				clone.drawOrder(0)
				index+=1
			
			for i in self.intersectingObjects:
				if self.objInBubble == i:
					self.selectedObject = i
					self.intersectingObjects.remove(i)
					break
			self.reset()
			self.mode = InteractionMode.SELECTION

	# updateExpandBubble()
	# updates rendering of the quadrants and the objects in the quadrants
	def updateExpandBubble(self):
		if self.bubbleQuadMenu != None:
			self.bubbleQuadMenu.remove()
		if self.bubbleQuadMenuObj != None:
			self.bubbleQuadMenuObj.remove()
		if self.menuObj2OjbLine != None:
			self.menuObj2OjbLine.remove()
		
		self.bubbleQuadMenu = None
		self.bubbleQuadMenuObj = None
		self.menuObj2OjbLine = None
		self.objInBubble = None
		
		quadHighlighted = False
		
		x,y = self.cursorPositionNormalized[0],self.cursorPositionNormalized[1]#float(self.cursorPosition[0])/float(self.windowSize[0]), float(self.cursorPosition[1])/float(self.windowSize[1])
		
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		
		# bubble cursor in the quad menu
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
		begin = line[:3]
		end = line[3:]
		
		origin = Vector3(begin[0],begin[1],begin[2])
		#print "origin:",origin
		direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
		direction.normalize()
		#print "direction:",direction

		smallest_distance = sys.maxint
		#print smallest_distance
		central_point = Vector3(0,0,0)
		object_point = Vector3(0,0,0)
		object_radius = 0.0
		ray_pos = None
		ray_mult = 0.0
		original_position = [0,0,0]
		
		found = False
		
		for item in self.clone_list:
			if item.getAction() == None:
				#oldposition = item.getBoundingBox(viz.ABS_GLOBAL).center
				#screenposition = viz.MainWindow.worldToScreen(oldposition, eye = viz.BOTH_EYE, mode = viz.WINDOW_NORMALIZED)
				#distance = math.sqrt(math.pow((user_position[0]-oldposition[0]),2)+math.pow((user_position[1]-oldposition[1]),2)+math.pow((user_position[2]-oldposition[2]),2))
				#item.setMatrix(identity,viz.ABS_GLOBAL)
				oglpos = item.getBoundingBox(viz.ABS_GLOBAL).center
				#item.setAxisAngle(-.5,1,0,self.rotQUAD,viz.ABS_GLOBAL)
				#center = item.getBoundingBox(viz.ABS_GLOBAL).center
				#print "screen position:",screenposition
				#line = viz.screentoworld(screenposition[0],screenposition[1])
				#distance = screenposition[2]
				#dir_vector = line.dir
				#length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
				#dir_vector[0] = (dir_vector[0]/length)
				#dir_vector[1] = (dir_vector[1]/length)
				#dir_vector[2] = (dir_vector[2]/length)
				#point = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
				#item.setPosition(point[0]-center[0],point[1]-center[1],point[2]-center[2],viz.ABS_GLOBAL)
				
				boundingSphere = item.getBoundingSphere(viz.ABS_GLOBAL)
				obj_pos = boundingSphere.center
				object_radius = boundingSphere.radius
				point = Vector3(obj_pos[0],obj_pos[1],obj_pos[2])
				distance = Vector3.DistanceToLineSquared(origin,direction,point)
				#print index," -> ",distance, obj
				if distance < smallest_distance:
					smallest_distance = distance
					#print smallest_distance
					ray_mult = Vector3.PositionInRay(origin,direction,point)
					ray_pos = origin + direction*ray_mult
					central_point = (point+ray_pos)/2.0
					object_point = point
					self.objInBubble = item
					original_position = oglpos
					found = True
		
		#print "central:",central_point
		#print "object: ",object_point
		#print "ray mult:",ray_mult
		#print "ray pos:",ray_pos
		
		if found:
			smallest_distance = sqrt(smallest_distance)
			radius = smallest_distance/2.0
			
			self.bubbleQuadMenu = self.createSphere(20,20)
			self.bubbleQuadMenu.color(0,1,0)
			self.bubbleQuadMenu.alpha(0.5)
			self.bubbleQuadMenu.setPosition(central_point.x,central_point.y,central_point.z,viz.ABS_GLOBAL)		
			self.bubbleQuadMenu.setScale(radius,radius,radius)
			self.bubbleQuadMenu.depthFunc(viz.GL_ALWAYS)
			self.bubbleQuadMenu.drawOrder(2)
			
			self.bubbleQuadMenuObj = self.createSphere(20,20)
			self.bubbleQuadMenuObj.color(0,1,0)
			self.bubbleQuadMenuObj.alpha(0.5)
			self.bubbleQuadMenuObj.setPosition(object_point.x,object_point.y,object_point.z,viz.ABS_GLOBAL)		
			self.bubbleQuadMenuObj.setScale(object_radius,object_radius,object_radius)
			self.bubbleQuadMenuObj.depthFunc(viz.GL_ALWAYS)
			self.bubbleQuadMenuObj.drawOrder(2)
			
			self.menuObj2OjbLine = self.createLine([object_point.x,object_point.y,object_point.z],original_position)
			self.menuObj2OjbLine.color(1.0,0.0,0.0)
			self.menuObj2OjbLine.depthFunc(viz.GL_ALWAYS)
			self.menuObj2OjbLine.drawOrder(3)

	# reset()
	# resets SQUAD quadrants
	def reset(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		if self.mode == InteractionMode.SELECTION_EXPAND:
			for clone in self.clone_list:
				#print "removing index",index,"..."
				#clone.visible(viz.OFF)
				clone.endAction(viz.ALL_POOLS)
				clone.setMatrix(identity,viz.ABS_GLOBAL)
				clone.depthFunc(viz.GL_LESS)
				clone.drawOrder(0)
				#print len(self.clone_list)
			self.clone_list = []
		
		self.mode = InteractionMode.SELECTION
		
		if self.menuObj2OjbLine != None:
			self.menuObj2OjbLine.remove()

	# selectButtonPressed()
	# callback for the selection button
	def selectButtonPressed(self):
		if self.mode == InteractionMode.SELECTION and len(self.intersectingObjects) > 1:
			self.createExpandMenu(self.intersectingObjects)
			self.mode = InteractionMode.SELECTION_EXPAND
		elif self.mode == InteractionMode.SELECTION and len(self.intersectingObjects) == 1:
			print 'selected object ',self.intersectingObjects[0]
			self.selectedObject = self.intersectingObjects[0]
		elif self.mode == InteractionMode.SELECTION_EXPAND:
			self.selectObject()
			
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		pass
	
	def calculateSphereCastingFrustum(self):
		# first calculate near selection box
		cameraNear = viz.MainWindow.getNearClip()
		yfov = viz.MainWindow.getVerticalFOV()
		xfov = viz.MainWindow.getHorizontalFOV()
		ymax = cameraNear*math.tan(float(yfov)*math.pi/360.0)
		ymin = -ymax
		xmax = ymax*self.aspectRatio
		xmin = ymin*self.aspectRatio
		
		x,y = float(self.cursorPosition[0]),float(self.cursorPosition[1])
		#print x,y
		#print [xmin,xmax],[ymin,ymax]
		
		half_size = 200.0
		boxn = [((x-half_size)*xmax*2.0)/self.windowSize[0],
				((y-half_size)*ymax*2.0)/self.windowSize[1],
				((x+half_size)*xmax*2.0)/self.windowSize[0],
				((y+half_size)*ymax*2.0)/self.windowSize[1]]
		if boxn[0] < 0: 
			boxn[0] = 0
		if boxn[1] < 0:
			boxn[1] = 0
		if boxn[2] >= xmax*2.0:
			boxn[2] = xmax*2.0
		if boxn[3] >= ymax*2.0:
			boxn[3] = ymax*2.0
		
		#print "boxn: ",boxn[0],",",boxn[1]," by ",boxn[2],",",boxn[3]
		
		# 8 points that define the frustum quads
		P = []
		P.append(Vector3(-(xmin+boxn[0]), -(-ymin-boxn[1]), 5.0))
		P.append(Vector3.Adjust(P[0], 6.0))
		P.append(Vector3(-(xmin+boxn[0]), -(-ymin-boxn[3]), 5.0))
		P.append(Vector3.Adjust(P[2], 6.0))
		P.append(Vector3(-(xmin+boxn[2]), -(-ymin-boxn[3]), 5.0))
		P.append(Vector3.Adjust(P[4], 6.0))
		P.append(Vector3(-(xmin+boxn[2]), -(-ymin-boxn[1]), 5.0))
		P.append(Vector3.Adjust(P[6], 6.0))
		
		quat = viz.MainView.getQuat(viz.ABS_GLOBAL)
		pos = viz.MainView.getPosition(viz.ABS_GLOBAL)
		
		# transform things
		for i in range(8):
			#print "old: P[",i,"]:",P[i].x,",",P[i].y,",",P[i].z
			#P[i] = P[i].Transform(quat)
			P[i].x = P[i].x+pos[0]
			P[i].y = P[i].y+pos[1] 
			P[i].z = P[i].z+pos[2]
			#print "new: P[",i,"]:",P[i].x,",",P[i].y,",",P[i].z

		Frustum = []

		Frustum.append(Vector3.Cross( Vector3(P[1],P[0]), Vector3(P[3],P[2]) ))
		Frustum.append(Vector3.Cross( Vector3(P[3],P[2]), Vector3(P[5],P[4]) ))
		Frustum.append(Vector3.Cross( Vector3(P[5],P[4]), Vector3(P[7],P[6]) ))
		Frustum.append(Vector3.Cross( Vector3(P[7],P[6]), Vector3(P[1],P[0]) ))

		for i in range(4):
			Frustum[i].normalize() # this is unecessary
			#print "Frustum[",i,"]:",Frustum[i].x,",",Frustum[i].y,",",Frustum[i].z

		index = 0
		objects_in_frustum = []
		# Check which objects are within the Frustum formed by the sphere.
		for obj in self.objects:
			obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
			if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
				in_frustum = 0
				obj_pos = obj.getBoundingBox(viz.ABS_GLOBAL).center
				for x in range(4):
					fDot = Vector3.Dot( Vector3(P[x*2],Vector3(obj_pos[0],obj_pos[1],obj_pos[2])), Frustum[x] )
					if fDot > 0:
						break
					in_frustum += 1
				if in_frustum == 4:
					#print in_frustum
					objects_in_frustum.append(obj)
			index += 1
		
		#print len(objects_in_frustum)
		
		return objects_in_frustum
	
	def initializeObjects(self):
		# Create a dictionary (std::map equiv) for the rgb/object key
		self.objectMap = {None:[-1,0,0,0,255,255]}#{(0,0,0,255):[-1,None]}
		
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
		g = 0.05882353
		b = 0.60784314
		compositeColor = (int(r*255) << 16) | (int(g*255) << 8) | int(b*255)
		compositeColorIncrement = int((math.floor(math.pow(256,3))/len(self.objects)))
		index = 0
		for obj in self.objects:
			print 'color (',int(compositeColor),':',hex(compositeColor),'):',hex(int(r*255)),hex(int(g*255)),hex(int(b*255))
			self.occlusionObjects.append(obj.copy(scene = 2))
			self.occlusionObjects[-1].disable(viz.LIGHTING)
			self.occlusionObjects[-1].texture(viz.OFF)
			self.occlusionObjects[-1].color(r,g,b)
			#self.occlusionCheckExt.modifyNode(obj, x=r, y=g, z=b)
			self.occlusionCheckExt.modifyNode(obj, x=compositeColor)
			
			#self.objectMap[compositeColor] = [index,r,g,b,255,obj]
			self.objectMap[obj] = [index,r,g,b,255,compositeColor]
			
			# calculate color of next node
			#self.occlusionObjects[-1].color(r/255.0,g/255.0,b/255.0)
			compositeColor += int(compositeColorIncrement)
			r = ((int(compositeColor) & 0x00ff0000) >> 16)/255.0
			g = ((int(compositeColor) & 0x0000ff00) >> 8)/255.0
			b = ((int(compositeColor) & 0x000000ff))/255.0
			#r = ((int(compositeColor) & 0x00ff0000) >> 16)
			#g = ((int(compositeColor) & 0x0000ff00) >> 8)
			#b = ((int(compositeColor) & 0x000000ff))
			#a = 0xff
			
			index += 1
		
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
		
			# Set render color to white
			self.renderNode.setClearColor(viz.WHITE)

			# Do not inherit view/projection settings from main window
			self.renderNode.setInheritView(True)

			# Render to video feed texture
			self.renderNode.setRenderTexture(self.colorTexture)
		
			self.window = viz.addWindow(pos=(1.0,1.0),size=(1.0,1.0)) 
			#self.debugWindow = viz.addTexQuad(parent = viz.ORTHO)
			
			self.scSphere.renderToAllRenderNodesExcept([self.renderNode])
			self.window.setScene(viz.Scene2) 
		
		#self.debugWindow.setPosition(400,300)
		#self.debugWindow.setScale(800,600,1)
		#self.debugWindow.texture(self.colorTexture)
		
		# Create shader object and assosiate it with our texture blending frag program
		#shader = viz.addShader( frag = 'process.frag' )

		# Create the shader parameter objects
		# They tell the shader the texture numbers of blendable textures and blend amount
		#self.pointerXUniform = viz.addUniformFloat( 'PointerX', 0.0 )
		#self.pointerYUniform = viz.addUniformFloat( 'PointerY', 0.0 )
		#self.pointerRadiusUniform = viz.addUniformFloat( 'PointerRadius', 10.0 )
		#self.textureUnit1Uniform = viz.addUniformInt( 'TextureUnit1', 0 )
		
		# Make Vizard use the created shader when rendering the logo node
		#self.debugWindow.apply(shader)
		# Provide the shader with its parameters
		#self.debugWindow.apply(self.pointerXUniform)
		#self.debugWindow.apply(self.pointerYUniform)
		#self.debugWindow.apply(self.pointerRadiusUniform)
		#self.debugWindow.apply(self.textureUnit1Uniform)
	
	# update()
	# main update function for squad, needs to be called every frame/every time the cursor is updated
	def update(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		user_position = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		user_position_v3 = Vector3(user_position[12],user_position[13],user_position[14])
		#print "User Position:", user_position[12], user_position[13], user_position[14]
		#print "orientation:",viz.MainView.getEuler()
		
		# Set FOV for video camera
		VFOV = 2.0 * math.atan( math.tan( (90.0/57.2957795) / 2.0 ) / self.aspectRatio ) * 57.2957795
		self.window.fov(VFOV)
		
		timer = Timer()
		timer.start()
		
		if self.mode == InteractionMode.SELECTION:			
			if self.bubbleQuadMenu != None:
				self.bubbleQuadMenu.remove()
			if self.bubbleQuadMenuObj != None:
				self.bubbleQuadMenuObj.remove()
			if self.menuObj2OjbLine != None:
				self.menuObj2OjbLine.remove()
			self.quadrantSelected = False
			self.expandBackground.visible(viz.OFF)
			self.scSphere.visible(viz.ON)
			self.crosshair.visible(viz.OFF)
			
			print timer.elapsed()
			
			self.intersecting = False
			
			# get the objects in the frustum formed by the sphere
			#objects_in_cone = self.objects
			
			line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
			begin = line[:3]
			end = line[3:]
			
			origin = Vector3(begin[0],begin[1],begin[2])
			direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
			direction.normalize()
			#print origin, direction
			#print viz.MainView.getPosition(viz.ABS_GLOBAL)
			
			min_distance = 200.0
			min_distance_squared = min_distance**2
			
			print "[",timer.elapsed(),"] started update "

			# restrict selection to objects that are visible and within the selection area
			xmin = (x-min_distance)/self.windowSize[0] if x-min_distance >= 0 else 0
			ymin = (y-min_distance)/self.windowSize[1] if y-min_distance >= 0 else 0
			xmax = (x+min_distance)/self.windowSize[0] if x+min_distance < self.windowSize[0] else 1.0
			ymax = (y+min_distance)/self.windowSize[1] if y+min_distance < self.windowSize[1] else 1.0
			print [xmin,ymin,xmax,ymax]
			
			objects_in_cone = viz.MainWindow.pickRect([xmin,ymin,xmax,ymax],viz.WORLD)
			
			print "[",timer.elapsed(),"] initial pickrect ->", len(objects_in_cone),"objects"
			
			# testing distance from line to objects in the scene 
			min_distance_obj = None
			min_distance_point = []
			distance_to_point = 0
			screen_pos = [0,0]
			
			# for the minimum visual size
			objects_to_remove = []
			center_to_object_distance = []
			for obj in objects_in_cone:
				bb = obj.getBoundingBox(viz.ABS_GLOBAL)#obj.getBoundingSphere(viz.ABS_GLOBAL)
				obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
				if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
					point = Vector3(bb.center[0],bb.center[1],bb.center[2])#self.initialPositions[obj]#objects_positions_in_cone[index]
					screen_pos = viz.MainWindow.worldToScreen(point[0],point[1],point[2],mode=viz.WINDOW_PIXELS)
					# calculate distance from line to object
					distance = math.pow(screen_pos[0]-x,2)+math.pow(screen_pos[1]-y,2) # distance is squared
					center_to_object_distance.append(distance)
					if distance < min_distance_squared:
						min_distance_squared = distance #distance squared
						min_distance_obj = obj
						min_distance_point = point
						distance_to_point = user_position_v3.distanceSquared(point)
				else:
					objects_to_remove.append(obj)
				
			# remove objects that are too big 
			while(len(objects_to_remove) > 0):
				objects_in_cone.remove(objects_to_remove[0])
				objects_to_remove.remove(objects_to_remove[0])
			
			print "[",timer.elapsed(),"] calculated minimum distance ->", len(objects_in_cone),"objects"
			
			# if we found an object within the minimal distance, calculate the size of the sphere
			if min_distance_obj != None:
				self.intersecting = True
				#intersection = Vector3.IntersectionPoint(origin,direction,min_distance_point)
				self.min_distance_squared = (self.windowSize[0]*0.035)**2
				if min_distance_squared < self.min_distance_squared:
					min_distance_squared = self.min_distance_squared 
				min_distance = min_distance_squared**0.5 # distance squared
				self.ccCone.setPosition(float(x),float(y),0)
				self.ccCone.setScale(min_distance*2.0,min_distance*2.0)
							
			print "[",timer.elapsed(),"] calculated cone size"
			
			# update shader
			#self.pointerXUniform.set(x)
			#self.pointerYUniform.set(y)
			#self.pointerRadiusUniform.set(min_distance)	
			
			#imageData = self.colorTexture.saveToBuffer('<raw>')
			#print imageData
			#f = open('file1', 'w')
			#f.write(imageData)
			#im.save("test.png")
			self.occlusionCheckExt.modifyTexture(self.colorTexture, x=x, y=y, z=min_distance)
			#print self.occlusionCheckExt.command(mesg=imageData, x=x, y=y, z=min_distance, w=self.colorTexture.getSize()[0]*self.colorTexture.getSize()[1])
			
			print "[",timer.elapsed(),"] got colors from texture"
			
			self.intersectingObjects = []
			
			removed = 0
			colorRemoved = 0
			insideCount = 0
			# determine which objects are in the sphere
			if self.intersecting == True:
				# calculate objects that are in the cone
				min_distance_squared_with_error = min_distance_squared*1.2
				index = 0
				for obj in objects_in_cone:
					if center_to_object_distance[index] < min_distance_squared_with_error:
						insideCount += 1
						#compositeColor = self.objectMap[obj][5]
						#print compositeColor
						result = self.occlusionCheckExt.modifyNode(obj)
						#print result
						if result:
							self.intersectingObjects.append(obj)
						else:
							removed += 1
							colorRemoved += 1
					else:
						removed += 1
					index += 1
					
			print "[",timer.elapsed(),"]",removed,"total objects removed,",len(objects_in_cone),"total)"
			print "[",timer.elapsed(),"]",colorRemoved,"objects removed by color,",insideCount,"tested)"
			print "[",timer.elapsed(),"] determined objects in cone"
			
			self.drawIntersectObjsBoundingBoxes()
			
			print "[",timer.elapsed(),"] bounding boxes"
			
		elif self.mode == InteractionMode.SELECTION_EXPAND:
			#self.rotQUAD += 1
			#if self.rotQUAD == 360:
			#	self.rotQUAD = 1
			
			self.expandBackground.setMatrix(user_position, viz.ABS_GLOBAL)
			self.expandBackground.setPosition([0,0,50], viz.REL_LOCAL)
			self.expandBackground.setScale(self.aspectRatio,1,1)
			self.expandBackground.visible(viz.ON)
			
			self.crosshair.visible(viz.ON)
			self.scSphere.visible(viz.OFF)
			
			self.crosshair.setPosition(x/self.windowSize[0],y/self.windowSize[1],0)
			
			# calculates distance between the cursor and objects
			x,y = self.cursorPosition[0],self.cursorPosition[1]
			
			line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
			begin = line[:3]
			end = line[3:]
			
			origin = Vector3(begin[0],begin[1],begin[2])
			direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
			direction.normalize()

			self.distance_list = []
			index = 0
			for obj in self.clone_list:
				obj_pos = obj.getBoundingBox(viz.ABS_GLOBAL).center
				point = Vector3(obj_pos[0],obj_pos[1],obj_pos[2])
				distance = Vector3.DistanceToLineSquared(origin,direction,point)
				#print index," -> ",distance
				self.distance_list.append(distance)
				index += 1
			
			self.updateExpandBubble()
			
			#self.drawIntersectObjsBoundingBoxes()

	# clean()
	# reset visual aids/quadrants
	def clean(self):	
		self.expandBackground.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
