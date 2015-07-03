import viz
import math
import sys
from math import sqrt
import vizmat

from PointingTechnique import PointingTechnique
from Vector3 import Vector3

from Timer import Timer

from Octree import Octree, OctNode, NodeObject
from Frustum import Frustum

import vizmultiprocess
from multiprocessing import Pool

class InteractionMode:
	SELECTION = 0
	SELECTION_QUADRANTS = 1
	
class Quadrant:
	TOP=0
	BOTTOM=1
	LEFT=2
	RIGHT=3
	NONE=4

class SQUADBubblev8(PointingTechnique):
	def __init__(self,sceneObjects,useOctree=None):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "SQUAD+bubble cursor v8"
		
		# initialize quadrants
		self.quadrantLines = self.createQuadLin()
		self.quadrantLines.depthFunc(viz.GL_ALWAYS)
		self.quadrantLines.drawOrder(2)
		self.quadrantLines.color(0,0,0)
		self.quadrantLines.alpha(0.6)
		self.quadrantLines.visible(viz.OFF)
		self.quadrantTriangles = self.createQuadTri()
		self.quadrantTriangles.color(0.8,0.8,0.8)
		self.quadrantTriangles.alpha(0.6)
		self.quadrantTriangles.depthFunc(viz.GL_ALWAYS)
		self.quadrantTriangles.drawOrder(1)
		self.quadrantTriangles.visible(viz.OFF)
		
		# object clone list for the quadrants
		self.clone_list = []
		
		# for calculating distances between the cursor and objects in the quad menu
		self.distance_list = []
		
		# determines the selected quadrant
		self.selectedQuadrant = Quadrant.NONE
		
		# SQUAD selection mode, can be SELECTION and SELECTION_QUADRANT
		self.mode = InteractionMode.SELECTION
		
		# flag that tells if there are intersecting objects
		self.intersecting = False
		
		# variable that controls the animation of the objects in the quadrants
		self.rotQUAD = 0
		
		# bubbles in the quad menu
		self.bubbleQuadMenu = None
		self.bubbleQuadMenuObj = None
		
		# object selected by quad menu
		self.objInBubble = None
		
		# line that connects the object in the menu to the real object
		self.menuObj2OjbLine = None
		
		# flag to prevent continuous selection of quadrants
		self.quadrantSelected = False
		
		# register button callbacks
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
		
		# saving the bounding spheres
		self.bs = []
		for obj in self.objects:
			self.bs.append(obj.getBoundingSphere(viz.ABS_GLOBAL))
			
		self.useOctree = useOctree
		# if we want to use the octree method, need to initialize it
		# can only use it if dealing with static objects
		if self.useOctree:
			print "Creating Octree"
			size = self.useOctree[0]
			pos = [self.useOctree[1],self.useOctree[2],self.useOctree[3]]
			self.octree = Octree(size,pos[0],pos[1],pos[2]) # need to specify size of the world
			index = 0
			for obj in self.objects:
				print " ["+str(index)+"/"+str(len(self.objects))+"] adding new object"
				newObj = NodeObject(index, self.bs[index], obj)
				self.octree.insertNode(self.octree.root, 15.000, self.octree.root, newObj)
				index += 1
			self.frustumObj = []
			#self.octree.draw()
		
		# variable that stores the minimum distance (in pixels) for the technique to work
		self.min_distance = 200
		
		# variables for processes - NEED TO BE INITIALIZED IN MAIN
		self.plFilter = []
		self.plCalculate = []
		self.plUpdate = []
		
		# pipe lists; ppp -> process pipe parent; ppc -> process pipe child
		self.pppFilter = []
		self.ppcFilter = []
		self.pppCalculate = []
		self.ppcCalculate = []
		self.pppUpdate = []
		self.ppcUpdate = []
		
		#index = 1
		#for object in self.objects:
		#	object.stencilFunc(viz.StencilFunc.RenderMask(mask = index))
		#	#object.disable([viz.COLOR_WRITE,viz.DEPTH_WRITE])
		#	index += 1
			
		#viz.MainWindow.setClearMask(viz.GL_STENCIL_BUFFER_BIT,viz.MASK_ADD)
		
		#self.stencilRenderNode = viz.addRenderNode()
		#self.stencilTexture = viz.addRenderTexture()#[self.windowSize[0],self.windowSize[1]],viz.TEX_2D,viz.TEX_DEPTH_16)
		#self.stencilRenderNode.setRenderTexture(self.stencilTexture,viz.RENDER_STENCIL)
		
		self.pool = Pool(processes = 8)
		
	
	#-------------------------------------------------------------------------------
	# <node3d:on-the-fly> objects functions
	#-------------------------------------------------------------------------------
	# createQuadLin()
	# creates the lines used in the quad menu
	def createQuadLin(self):
		viz.startlayer(viz.LINES) 
		viz.linewidth(2)
		viz.vertex(-1000,-1000,0) #Vertices are split into pairs.
		viz.vertex( 1000, 1000,0)
		viz.vertex(-1000, 1000,0)
		viz.vertex( 1000,-1000,0)
		return viz.endlayer()

	# createQuadTri()
	# creates the triangles used in the quad menu quadrants
	def createQuadTri(self):
		viz.startlayer(viz.TRIANGLES,'bottom') 
		viz.vertex(-1000,-1000,0) #Vertices are split into pairs.
		viz.vertex( 1000,-1000,0)
		viz.vertex(    0,    0,0) 
		viz.startlayer(viz.TRIANGLES,'top') 
		viz.vertex(-1000, 1000,0)
		viz.vertex(    0,    0,0)
		viz.vertex( 1000, 1000,0)
		viz.startlayer(viz.TRIANGLES,'left') 
		viz.vertex(-1000, 1000,0)
		viz.vertex(-1000,-1000,0)
		viz.vertex(    0,    0,0)
		viz.startlayer(viz.TRIANGLES,'right') 
		viz.vertex(    0,    0,0)
		viz.vertex( 1000,-1000,0)
		viz.vertex( 1000, 1000,0)
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
	# createSQUADQuadrants()
	# distributes the items that were inside the sphere among the different quadrants
	#'''
	# old version, pre-defined division of objects
	def createSQUADQuadrants(self,list,centered=0):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		self.clone_list = []
		#print "selecting an object among:",list
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		#print "size of the array:",len(list)
		clone_total_level_1 = [0.0,0.0,0.0,0.0]
		clone_total_level_2 = [0.0,0.0,0.0,0.0]
		clone_total_level_3 = [0.0,0.0,0.0,0.0]
		clone_dist_level_1 = [0.0,0.0,0.0,0.0]
		clone_dist_level_2 = [0.0,0.0,0.0,0.0]
		clone_dist_level_3 = [0.0,0.0,0.0,0.0]
		index = 0
		for child in list:
			if clone_total_level_2[index%4] > clone_total_level_3[index%4]+2.0:
				clone_total_level_3[index%4]+=1.0
			elif clone_total_level_1[index%4] > clone_total_level_2[index%4]+2.0:
				clone_total_level_2[index%4]+=1.0
			else:
				clone_total_level_1[index%4]+=1.0
			index += 1
		#print "clone total        level 1:",clone_total_level_1,"         level 2:",clone_total_level_2,"         level 3:",clone_total_level_3
		distance_level_1 = [110 + 30*(clone_total_level_1[0]),110 + 30*(clone_total_level_1[1]),110 + 30*(clone_total_level_1[2]),110 + 30*(clone_total_level_1[3])]
		distance_level_2 = [110 + 30*(clone_total_level_2[0]),110 + 30*(clone_total_level_2[1]),110 + 30*(clone_total_level_2[2]),110 + 30*(clone_total_level_2[3])]
		distance_level_3 = [110 + 30*(clone_total_level_3[0]),110 + 30*(clone_total_level_3[1]),110 + 30*(clone_total_level_3[2]),110 + 30*(clone_total_level_3[3])]
		
		index = 0
		#print "list"
		for clone in list:
			#clone.collideNone()
			clone.depthFunc(viz.GL_ALWAYS)
			clone.drawOrder(4)
			obj_position = []
				
			x,y = 0.5,0.5
			if index%4 == 0: # top
				#print "-------- TOP ---------"
				if clone_dist_level_2[0] > clone_dist_level_3[0]+2.0 and clone_total_level_3[0] > 1:
					x,y = 0.4+((clone_dist_level_3[0]/(clone_total_level_3[0]-1.0))*0.2),0.66
					clone_dist_level_3[0]+=1.0
					#print "if"
				elif clone_dist_level_2[0] > clone_dist_level_3[0]+2.0:
					x,y = 0.5,0.66
					clone_dist_level_3[0]+=1.0
					#print "elif"
				elif clone_dist_level_1[0] > clone_dist_level_2[0]+2.0 and clone_total_level_2[0] > 1:
					x,y = 0.3+((clone_dist_level_2[0]/(clone_total_level_2[0]-1.0))*0.4),0.78
					clone_dist_level_2[0]+=1.0
					#print "if"
				elif clone_dist_level_1[0] > clone_dist_level_2[0]+2.0:
					x,y = 0.5,0.78
					clone_dist_level_2[0]+=1.0
					#print "elif"
				elif clone_total_level_1[0] > 1:
					x,y = 0.2+((clone_dist_level_1[0]/(clone_total_level_1[0]-1.0))*0.6),0.9
					clone_dist_level_1[0]+=1.0
					#print "elif"
				else:
					x,y = 0.5,0.9
					clone_dist_level_1[0]+=1.0
					#print "else"
				#print "top      level 1:",clone_dist_level_1[0],"  level 2:",clone_dist_level_2[0]
			elif index%4 == 1: # bottom
				#print "-------- BOTTOM ---------"
				if clone_dist_level_2[1] > clone_dist_level_3[1]+2.0 and clone_total_level_3[1] > 1:
					x,y = 0.4+((clone_dist_level_3[1]/(clone_total_level_3[1]-1.0))*0.2),0.34
					clone_dist_level_3[1]+=1.0
					#print "if"
				elif clone_dist_level_2[1] > clone_dist_level_3[1]+2.0:
					x,y = 0.5,0.34
					clone_dist_level_3[1]+=1.0
					#print "if"
				elif clone_dist_level_1[1] > clone_dist_level_2[1]+2.0 and clone_total_level_2[1] > 1:
					x,y = 0.3+((clone_dist_level_2[1]/(clone_total_level_2[1]-1.0))*0.4),0.22
					clone_dist_level_2[1]+=1.0
					#print "if"
				elif clone_dist_level_1[1] > clone_dist_level_2[1]+2.0:
					x,y = 0.5,0.22
					clone_dist_level_2[1]+=1.0
					#print "if"
				elif clone_total_level_1[1] > 1:
					x,y = 0.2+((clone_dist_level_1[1]/(clone_total_level_1[1]-1.0))*0.6),0.1
					clone_dist_level_1[1]+=1.0
					#print "elif"
				else:
					x,y = 0.5,0.1
					clone_dist_level_1[1]+=1.0
					#print "else"
				#print "bottom   level 1:",clone_dist_level_1[1],"  level 2:",clone_dist_level_2[1]
			elif index%4 == 2: # left
				#print "-------- LEFT ---------"
				if clone_dist_level_2[2] > clone_dist_level_3[2]+2.0 and clone_total_level_3[2] > 1:
					x,y = 0.34,0.4+((clone_dist_level_3[2]/(clone_total_level_3[2]-1.0))*0.2)
					clone_dist_level_3[2]+=1.0
					#print "if"
				elif clone_dist_level_2[2] > clone_dist_level_3[2]+2.0:
					x,y = 0.34,0.5
					clone_dist_level_3[2]+=1.0
					#print "if"
				elif clone_dist_level_1[2] > clone_dist_level_2[2]+2.0 and clone_total_level_2[2] > 1:
					x,y = 0.22,0.3+((clone_dist_level_2[2]/(clone_total_level_2[2]-1.0))*0.4)
					clone_dist_level_2[2]+=1.0
					#print "if"
				elif clone_dist_level_1[2] > clone_dist_level_2[2]+2.0:
					x,y = 0.22,0.5
					clone_dist_level_2[2]+=1.0
					#print "if"
				elif clone_total_level_1[2] > 1:
					x,y = 0.1,0.2+((clone_dist_level_1[2]/(clone_total_level_1[2]-1.0))*0.6)
					clone_dist_level_1[2]+=1.0
					#print "elif"
				else:
					x,y = 0.1,0.5
					clone_dist_level_1[2]+=1.0
					#print "else"
				#print "left     level 1:",clone_dist_level_1[2],"  level 2:",clone_dist_level_2[2]
			else: # right
				#print "-------- RIGHT ---------"
				if clone_dist_level_2[3] > clone_dist_level_3[3]+2.0 and clone_total_level_3[3] > 1:
					x,y = 0.66,0.4+((clone_dist_level_3[3]/(clone_total_level_3[3]-1.0))*0.2)
					clone_dist_level_3[3]+=1.0
					#print "if"
				elif clone_dist_level_2[3] > clone_dist_level_3[3]+2.0:
					x,y = 0.66,0.5
					clone_dist_level_3[3]+=1.0
					#print "if"
				elif clone_dist_level_1[3] > clone_dist_level_2[3]+2.0 and clone_total_level_2[3] > 1:
					x,y = 0.78,0.3+((clone_dist_level_2[3]/(clone_total_level_2[3]-1.0))*0.4)
					clone_dist_level_2[3]+=1.0
					#print "if"
				elif clone_dist_level_1[3] > clone_dist_level_2[3]+2.0:
					x,y = 0.78,0.5
					clone_dist_level_2[3]+=1.0
					#print "if"
				elif clone_total_level_1[3] > 1:
					x,y = 0.9,0.2+((clone_dist_level_1[3]/(clone_total_level_1[3]-1.0))*0.6)
					clone_dist_level_1[3]+=1.0
					#print "elif"
				else:
					x,y = 0.9,0.5
					clone_dist_level_1[3]+=1.0
					#print "else"
				#print "right    level 1:",clone_dist_level_1[3],"  level 2:",clone_dist_level_2[3]
			#print index," ",x,y
			#print "index ",index,"   screentoworld at ",x,y
			#print "clone dist      level 1:",clone_dist_level_1,"of",clone_total_level_1,"     level 2:",clone_dist_level_2,"of",clone_total_level_2,"     level 3:",clone_dist_level_3,"of",clone_total_level_3
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
			#clone.parent(supermarket)
			curPos = clone.getPosition() #Save current position
			#if clone_total_level_2[0] > 2 and clone_dist_level_2[0] > clone_dist_level_3[0]:
			#	clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_3[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_3[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_3[index%4], viz.ABS_GLOBAL)
			#elif clone_total_level_1[0] > 2 and clone_dist_level_1[0] > clone_dist_level_2[0]:
			#	clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_2[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_2[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_2[index%4], viz.ABS_GLOBAL)
			#else:
			#	clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_1[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_1[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_1[index%4], viz.ABS_GLOBAL)
			object_distance = clone.getBoundingSphere(viz.ABS_GLOBAL).radius*2.155/0.04 # dependent on object size
			print object_distance
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*object_distance,(user_position[1]-obj_position[1])+dir_vector[1]*object_distance,(user_position[2]-obj_position[2])+dir_vector[2]*object_distance, viz.ABS_GLOBAL)
			gotoPos = clone.getPosition() #Get computed local pos
			clone.setPosition(curPos) #Restore position
			#clone.setScale(100,100,100)
			#clone.runAction(vizact.goto(gotoPos,.25,viz.TIME))
			clone.setPosition(gotoPos)
			#clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4])
			self.clone_list.append(clone)
			index+=1
	#'''
	
	# selectSQUADQuadrant()
	# callback for selection of quadrants, called by the real callback that checks
	# if the select button was pressed during the SELECTION self.mode or SELECTION_QUADRANTS
	def selectSQUADQuadrant(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		if len(self.clone_list) > 0:
			#print "selecting those items who are in",self.selectedQuadrant
			#print "self.clone_list had",len(self.clone_list),"items"
			new_clone_list = []
			index = 0
			for clone in self.clone_list:
				if index%4 != self.selectedQuadrant or self.objInBubble != None: 
					#print "removing index",index,"..."
					#clone.visible(viz.OFF)
					clone.endAction(viz.ALL_POOLS)
					#clone.setPosition(0,0,0,viz.ABS_GLOBAL)
					clone.setMatrix(identity,viz.ABS_GLOBAL)
					clone.depthFunc(viz.GL_LESS)
					clone.drawOrder(0)
					#print len(self.clone_list)
				else:
					new_clone_list.append(clone)
				index+=1
			
			if self.objInBubble != None:
				new_clone_list.append(self.objInBubble)
			
			#print "now self.clone_list has",len(new_clone_list),"items"
			if len(new_clone_list) > 1:
				#print "more than 1 left..."		
				
				#print new_clone_list
				self.createSQUADQuadrants(new_clone_list,1)
			else:
				if len(new_clone_list) == 1 and self.mode == InteractionMode.SELECTION_QUADRANTS:
					#print "adding",new_clone_list[0]
					for i in self.intersectingObjects:
						if new_clone_list[0] == i:
							self.selectedObject = i
							self.intersectingObjects.remove(i)
							break
					self.reset()
					self.mode = InteractionMode.SELECTION
				else:
					self.mode = InteractionMode.SELECTION
		else:
			self.mode = InteractionMode.SELECTION

	# updateSQUADQuadrants()
	# updates rendering of the quadrants and the objects in the quadrants
	def updateSQUADQuadrants(self):
		if self.bubbleQuadMenu != None:
			self.bubbleQuadMenu.remove()
		if self.bubbleQuadMenuObj != None:
			self.bubbleQuadMenuObj.remove()
		if self.menuObj2OjbLine != None:
			self.menuObj2OjbLine.remove()
		self.objInBubble = None
		self.menuObj2OjbLine = None
		
		quadHighlighted = False
		
		x,y = self.cursorPositionNormalized[0],self.cursorPositionNormalized[1]#float(self.cursorPosition[0])/float(self.windowSize[0]), float(self.cursorPosition[1])/float(self.windowSize[1])
		
		# will create bubble cursor if these conditions are not met
		if (y >= 1.0 or (y > 0.5 and y < 0.65)) and x >= (0.5-(y-0.5)) and x <= (0.5+(y-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'top')
			self.selectedQuadrant = Quadrant.TOP
			quadHighlighted = True
			if y > 1.15 and self.quadrantSelected == False:
				self.selectSQUADQuadrant()
				self.quadrantSelected = True
			elif y < 1.15:
				self.quadrantSelected = False
		else:
			self.quadrantTriangles.color([1,1,1],'top')
		if (y < 0.0 or (y < 0.5 and y > 0.35)) and x >= (0.5-((1.0-y)-0.5)) and x <= (0.5+((1.0-y)-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'bottom')
			self.selectedQuadrant = Quadrant.BOTTOM
			quadHighlighted = True
			if y < -0.15 and self.quadrantSelected == False:
				self.selectSQUADQuadrant()
				self.quadrantSelected = True
			elif y > -0.15:
				self.quadrantSelected = False
		else:
			self.quadrantTriangles.color([1,1,1],'bottom')
		if (x < 0.0 or (x < 0.5 and x > 0.35)) and y >= (0.5-((1.0-x)-0.5)) and y <= (0.5+((1.0-x)-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'left')
			self.selectedQuadrant = Quadrant.LEFT
			quadHighlighted = True
			if x < -0.15 and self.quadrantSelected == False:
				self.selectSQUADQuadrant()
				self.quadrantSelected = True
			elif x > -0.15:
				self.quadrantSelected = False
		else:
			self.quadrantTriangles.color([1,1,1],'left')
		if (x >= 1.0 or (x > 0.5 and x < 0.65)) and y >= (0.5-(x-0.5)) and y <= (0.5+(x-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'right')
			self.selectedQuadrant = Quadrant.RIGHT
			quadHighlighted = True
			if x > 1.15 and self.quadrantSelected == False:
				self.selectSQUADQuadrant()
				self.quadrantSelected = True
			elif x < 1.15:
				self.quadrantSelected = False
		else:
			self.quadrantTriangles.color([1,1,1],'right')
		
		if quadHighlighted == False:
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
			central_point = [0,0,0]
			object_point = [0,0,0]
			object_radius = 0.0
			ray_pos = None
			ray_mult = 0.0
			original_position = [0,0,0]
			
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
						original_position = oglpos
						self.objInBubble = item
			
			#print "central:",central_point
			#print "object: ",object_point
			#print "ray mult:",ray_mult
			#print "ray pos:",ray_pos
			
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
		
		if self.mode == InteractionMode.SELECTION_QUADRANTS:
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
			self.createSQUADQuadrants(self.intersectingObjects)
			self.mode = InteractionMode.SELECTION_QUADRANTS
		elif self.mode == InteractionMode.SELECTION and len(self.intersectingObjects) == 1:
			print 'selected object ',self.intersectingObjects[0]
			self.selectedObject = self.intersectingObjects[0]
		elif self.mode == InteractionMode.SELECTION_QUADRANTS:
			self.selectSQUADQuadrant()
			
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		pass
	
	def calculateSphereCastingFrustum(self, Vertex, FrustumPlane, inverted = False): # both return variables
		x,y = float(self.cursorPosition[0]),float(self.cursorPosition[1])
		
		# create box around the cursor to serve as frustum
		half_size = self.min_distance # in pixels, same as initial min_distance
		boxn = [x-half_size,y-half_size,x+half_size,y+half_size]
		if boxn[0] < 0: 
			boxn[0] = 0
		if boxn[1] < 0:
			boxn[1] = 0
		if boxn[2] >= self.windowSize[0]:
			boxn[2] = self.windowSize[0]
		if boxn[3] >= self.windowSize[1]:
			boxn[3] = self.windowSize[1]
		# create corners from box limits
		corners = [[boxn[0], boxn[1]],[boxn[0],boxn[3]],[boxn[2], boxn[1]],[boxn[2],boxn[3]]]
		
		#print "boxn: ",boxn[0],",",boxn[1]," by ",boxn[2],",",boxn[3]
		for i in range(4): # for each box corner
			# calculate vector from origin to corner
			line = viz.screentoworld(corners[i],mode = viz.WINDOW_PIXELS)
			begin = line[:3]
			end = line[3:]
		
			origin = Vector3(begin[0],begin[1],begin[2])
			direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
			direction.normalize()
			
			# add vertex for near and far planes
			Vertex.append(origin+direction*1.0)
			Vertex.append(origin+direction*1000.0)
		
		# adding frustum planes in order for rendering
		if inverted:
			normal = Vector3.Cross( Vector3(Vertex[0],Vertex[2]), Vector3(Vertex[0],Vertex[1]) )
		else:
			normal = Vector3.Cross( Vector3(Vertex[0],Vertex[1]), Vector3(Vertex[0],Vertex[2]) )
		normal.normalize()
		distance = Vector3.Dot( normal, Vertex[0] );
		FrustumPlane.append([normal,distance]) # F0 - left
		
		if inverted:
			normal = Vector3.Cross( Vector3(Vertex[2],Vertex[6]), Vector3(Vertex[2],Vertex[3]) )
		else:
			normal = Vector3.Cross( Vector3(Vertex[2],Vertex[3]), Vector3(Vertex[2],Vertex[6]) )
		normal.normalize()
		distance = Vector3.Dot( normal, Vertex[2] );
		FrustumPlane.append([normal,distance]) # F3 - top
		
		if inverted:
			normal = Vector3.Cross( Vector3(Vertex[0],Vertex[1]), Vector3(Vertex[0],Vertex[4]) )
		else:
			normal = Vector3.Cross( Vector3(Vertex[0],Vertex[4]), Vector3(Vertex[0],Vertex[1]) )
		normal.normalize()
		distance = Vector3.Dot( normal, Vertex[0] );
		FrustumPlane.append([normal,distance]) # F2 - bottom
		
		if inverted:
			normal = Vector3.Cross( Vector3(Vertex[5],Vertex[7]), Vector3(Vertex[5],Vertex[4]) )
		else:
			normal = Vector3.Cross( Vector3(Vertex[5],Vertex[4]), Vector3(Vertex[5],Vertex[7]) )
		normal.normalize()
		distance = Vector3.Dot( normal, Vertex[5] );
		FrustumPlane.append([normal,distance]) # F1 - right
		
		if inverted:
			normal = Vector3.Cross( Vector3(Vertex[4],Vertex[6]), Vector3(Vertex[4],Vertex[0]) )
		else:
			normal = Vector3.Cross( Vector3(Vertex[4],Vertex[0]), Vector3(Vertex[4],Vertex[6]) )
		normal.normalize()
		distance = Vector3.Dot( normal, Vertex[4] );
		FrustumPlane.append([normal,distance]) # F5 - front
		
		if inverted:
			normal = Vector3.Cross( Vector3(Vertex[1],Vertex[3]), Vector3(Vertex[1],Vertex[5]) )
		else:
			normal = Vector3.Cross( Vector3(Vertex[1],Vertex[5]), Vector3(Vertex[1],Vertex[3]) )
		normal.normalize()
		distance = Vector3.Dot( normal, Vertex[1] );
		FrustumPlane.append([normal,distance]) # F6 - back
	
	def sphereInFrustum(self, frustum, center, radius):
		for frustumPlane in frustum:
			if ((frustumPlane[0].x * center.x + frustumPlane[0].y * center.y + frustumPlane[0].z * center.z) < (radius + frustumPlane[1])):
				return False
		return True
		
	def nodesInFrustumOctree(self,objects_in_cone,objects_bs_in_cone):
		FrustumVertex = []
		FrustumPlanes = []
		self.calculateSphereCastingFrustum(FrustumVertex,FrustumPlanes)
		if len(self.frustumObj) > 0:
			for obj in self.frustumObj:
				obj.remove()
			self.frustumObj = []
		index = 0
		for p in FrustumVertex:
			sphere = self.createSphere(10,10)
			sphere.setPosition(p[0],p[1],p[2])
			if index % 2 == 0:
				sphere.setScale(0.025,0.025,0.025)
				sphere.color(1,0,0)
			else:
				sphere.setScale(0.4,0.4,0.4)
				sphere.color(0,1,0)
			self.frustumObj.append(sphere)
			index += 1
		#index = 0
		#for f in FrustumPlanes:
		#	print f[0],f[1]
		#print viz.MainView.getPosition()
		#	self.frustumObj.append(self.createLine(P[index*2],P[index*2]+f[0]*100))
		#	index += 1
		#self.octree.draw()
		
		#objects_in_frustum = []
		self.octree.nodesInFrustum(self.octree.root,FrustumPlanes,objects_in_cone,objects_bs_in_cone)
		
	def nodesInFrustumIterative(self,objects_in_cone,objects_positions_in_cone):
		P = []
		Frustum = []
		self.calculateSphereCastingFrustum(P,Frustum,True)
		#objects_in_frustum = []
		
		index = 0
		for obj in self.objects:
			#objects_positions.append(Vector3(self.bs[index].center[0],self.bs[index].center[1],self.bs[index].center[2]))
			#objects_sizes.append(self.bs[index].radius)
			object_position = Vector3(self.bs[index].center[0],self.bs[index].center[1],self.bs[index].center[2])
			object_size.append(self.bs[index].radius)

			#pos_in_ray = Vector3.PositionInRay(origin,direction,objects_positions[-1])
			obj_size = objects_sizes[-1]
			#if not viz.MainWindow.isCulled(obj,eye=viz.LEFT_EYE) and obj_size < 40:# and pos_in_ray > 0: # checks if the object is in front of the user and if it is a selectable object
			if self.sphereInFrustum(Frustum,object_position,self.bs[index].radius) and obj_size < 40:
				# add to auxiliary lists
				#if pos_in_ray > 0:
				#objects_in_frustum.append(obj)
				objects_in_cone.append(obj)
				#pos_in_ray = Vector3.PositionInRay(origin,direction,objects_positions[-1])
				#pos_in_ray_in_cone.append(pos_in_ray)
				objects_positions_in_cone.append(object_position)
			index += 1
		
	# update()
	# main update function for squad, needs to be called every frame/every time the cursor is updated
	def update(self):
		print "Update"
		timer = Timer()
		timer.start()
		
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		user_position = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		user_position_v3 = Vector3(user_position[12],user_position[13],user_position[14])
		#print "User Position:", user_position[12], user_position[13], user_position[14]
		#print "orientation:",viz.MainView.getEuler()

		if self.ccCone != None:
			self.ccCone.remove()
			self.ccCone = None
		
		if self.mode == InteractionMode.SELECTION:			
			if self.bubbleQuadMenu != None:
				self.bubbleQuadMenu.remove()
			if self.bubbleQuadMenuObj != None:
				self.bubbleQuadMenuObj.remove()
			if self.menuObj2OjbLine != None:
				self.menuObj2OjbLine.remove()
			self.quadrantSelected = False
			self.quadrantLines.visible(viz.OFF)
			self.quadrantTriangles.visible(viz.OFF)
			self.scSphere.visible(viz.ON)
			self.crosshair.visible(viz.OFF)
			
			self.intersecting = False
			self.intersectingObjects = []
			
			line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
			begin = line[:3]
			end = line[3:]
			
			origin = Vector3(begin[0],begin[1],begin[2])
			direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
			direction.normalize()
			#print origin, direction
			#print viz.MainView.getPosition(viz.ABS_GLOBAL)
			
			#stencilBuffer = self.stencilRenderNode.getRenderTexture(buffer = viz.RENDER_STENCIL)
			#print self.stencilTexture.getSize()
			#data = self.stencilTexture.getImageData()
			#print self.stencilTexture.getPixelSize(), len(data)
			#for pixel in data:
			#	if pixel != 0:
			#		print int(pixel)
			
			# get the objects in the frustum formed by the sphere
			objects_in_cone = []
			pos_in_ray_in_cone = []
			objects_positions_in_cone = []
			objects_bs_in_cone = []
			
			objects_positions = []
			objects_sizes = []
			
			print timer.elapsed()
			print len(self.objects)
			
			if self.useOctree:
				self.nodesInFrustumOctree(objects_in_cone,objects_bs_in_cone)
			else:
				self.nodesIn
			
			#for i in range(len(self.plFilter)):
			#	self.pppFilter[i].send(['test', 'send'])
			# since recv locks until it receives something, we need a separate loop
			#for i in range(len(self.plFilter)):
			#	print self.pppFilter[i].recv()
			
			print timer.elapsed()
			print len(objects_in_cone)
			# initialize values
			min_distance = self.min_distance
			min_distance_squared = min_distance**2
			
			# for the minimum visual size
			min_distance_to_point = 0
			min_distance_obj = None
			min_distance_point = []
			min_pos_in_ray = 0
			
			distance_to_point = 0
			'''
			index = 0
			for obj in objects_in_cone:
				point = objects_positions_in_cone[index]
				
				distance = Vector3.DistanceToLineSquared(origin,direction,point) # distance is squared
				distance_to_point = user_position_v3.distanceSquared(point)
				min_distance_adjusted = distance_to_point*min_distance_squared/160000 #
				
				if distance < min_distance_adjusted:
					min_distance_squared = distance #distance squared
					min_distance_obj = obj
					min_distance_point = point
					min_distance_to_point = distance_to_point
					min_pos_in_ray = pos_in_ray_in_cone[index]
						
				index += 1
			'''
			# SCREEN SPACE CALCULATIONS
			index = 0
			if self.useOctree:
				for obj in objects_in_cone:
					pos = objects_bs_in_cone[index].center
					point = Vector3(pos[0],pos[1],pos[2])
					screen_pos = viz.MainWindow.worldToScreen(pos,mode=viz.WINDOW_PIXELS)
					# calculate distance from line to object
					distance = math.pow(screen_pos[0]-x,2)+math.pow(screen_pos[1]-y,2) # distance is squared
					if distance < min_distance_squared and objects_bs_in_cone[index].radius < 40:
						min_distance_squared = distance #distance squared
						min_distance_obj = obj
						min_distance_point = point
						distance_to_point = user_position_v3.distanceSquared(point)
						min_distance_to_point = distance_to_point
					index += 1
			else:
				for obj in objects_in_cone:
					point = objects_positions_in_cone[index]
					screen_pos = viz.MainWindow.worldToScreen(point[0],point[1],point[2],mode=viz.WINDOW_PIXELS)
					# calculate distance from line to object
					distance = math.pow(screen_pos[0]-x,2)+math.pow(screen_pos[1]-y,2) # distance is squared
					if distance < min_distance_squared:
						min_distance_squared = distance #distance squared
						min_distance_obj = obj
						min_distance_point = point
						distance_to_point = user_position_v3.distanceSquared(point)
						min_distance_to_point = distance_to_point
					index += 1
			
			print timer.elapsed()
			# if we found an object within the minimal distance, calculate the size of the sphere
			if min_distance_obj != None:
				self.intersecting = True
				intersection = Vector3.IntersectionPoint(origin,direction,min_distance_point)
				min_distance_squared = min_distance_point.distanceSquared(intersection)
				min_distance_adjusted = min_distance_to_point*650/202500
				if min_distance_squared < min_distance_adjusted:
					min_distance_squared = min_distance_to_point*650/202500
				min_distance = min_distance_squared**0.5 # distance squared
				min_pos_in_ray = Vector3.PositionInRay(origin,direction,min_distance_point)
				self.scSphereRadius = min_distance   # this is in pixels
				self.scSphere.setScale(self.scSphereRadius,self.scSphereRadius,self.scSphereRadius)
				self.scSphere.setPosition(intersection.x,intersection.y,intersection.z,viz.ABS_GLOBAL)
				
				self.ccCone = self.createCone(-direction, origin+direction, min_pos_in_ray, min_distance, 20)
				self.ccCone.color(0.2,0.6,1.0)
				self.ccCone.alpha(0.6)
				
			if self.intersecting == True:
				#self.scSphere.visible(viz.ON)
				self.scSphere.visible(viz.OFF)
				self.ccCone.visible(viz.ON)
			else:
				self.scSphere.visible(viz.OFF)
			
			# determine which objects are in the sphere
			if self.intersecting == True:
				#print "testing intersection with objects"
				
				#print timer.elapsed()
				index = 0
				if self.useOctree:
					for obj in objects_in_cone: 
						if objects_bs_in_cone[index].radius < 40:
							pos = objects_bs_in_cone[index].center
							point = Vector3(pos[0],pos[1],pos[2])
							
							pos_in_ray = Vector3.PositionInRay(origin,direction,point)
							
							intersect_position = origin+direction*pos_in_ray
									
							radius_at_pos_in_ray = (pos_in_ray**2)*min_distance_squared/(min_pos_in_ray**2)
									
							distance = ((point.x-intersect_position.x)**2+
										(point.y-intersect_position.y)**2+
										(point.z-intersect_position.z)**2)
									
							if distance < radius_at_pos_in_ray*1.2:
								self.intersectingObjects.append(obj)
								
						index += 1
				else:
					for obj in objects_in_cone: 
						point = objects_positions_in_cone[index]
						pos_in_ray = Vector3.PositionInRay(origin,direction,point)
						
						intersect_position = origin+direction*pos_in_ray
								
						radius_at_pos_in_ray = (pos_in_ray**2)*min_distance_squared/(min_pos_in_ray**2)
								
						distance = ((point.x-intersect_position.x)**2+
									(point.y-intersect_position.y)**2+
									(point.z-intersect_position.z)**2)
								
						if distance < radius_at_pos_in_ray*1.2:
							self.intersectingObjects.append(obj)
						index += 1
				
				#self.intersectingObjects.append(min_distance_obj)
				print timer.elapsed()

			self.drawIntersectObjsBoundingBoxes()
			
			#print timer.elapsed()
		elif self.mode == InteractionMode.SELECTION_QUADRANTS:
			#self.rotQUAD += 1
			#if self.rotQUAD == 360:
			#	self.rotQUAD = 1
			
			self.quadrantLines.setMatrix(user_position, viz.ABS_GLOBAL)
			self.quadrantLines.setPosition([0,0,50], viz.REL_LOCAL)
			self.quadrantLines.setScale(self.aspectRatio,1,1)
			self.quadrantLines.visible(viz.ON)
			self.quadrantTriangles.setMatrix(user_position, viz.ABS_GLOBAL)
			self.quadrantTriangles.setPosition([0,0,50], viz.REL_LOCAL)
			self.quadrantTriangles.setScale(self.aspectRatio,1,1)
			self.quadrantTriangles.visible(viz.ON)
			
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
			
			self.updateSQUADQuadrants()
		
		#print timer.stop()
	# clean()
	# reset visual aids/quadrants
	def clean(self):	
		self.quadrantLines.visible(viz.OFF)
		self.quadrantTriangles.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
