import viz
import math
import vizmat

from PointingTechnique import PointingTechnique

class InteractionMode:
	SELECTION = 0
	SELECTION_QUADRANTS = 1
	
class Quadrant:
	TOP=0
	BOTTOM=1
	LEFT=2
	RIGHT=3
	NONE=4

#ONE_PX_IN_M          = 0.00238125
#ONE_PX_IN_DEG        = 0.000080645
#SCREEN_SPHERE_RADIUS = 2.155

#what's the meaning of these radii?
#1 is bigger than the screen, so it's not normalized, neither absolute
#absolute should be 10ft = 3.048m -> 3.048/2 = 1.524 -> diameter of the screen
#TINY_SPHERE_RADIUS   = ONE_PX_IN_M/4.0
#NORMAL_SPHERE_RADIUS = 0.6465

class SQUAD(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "SQUAD, original"
		
		# initialize quadrants
		self.quadrantLines = self.createQuadLin()
		self.quadrantLines.depthFunc(viz.GL_ALWAYS)
		self.quadrantLines.drawOrder(1)
		self.quadrantLines.color(0,0,0)
		self.quadrantLines.visible(viz.OFF)
		self.quadrantTriangles = self.createQuadTri()
		self.quadrantTriangles.color(0.8,0.8,0.8)
		self.quadrantTriangles.depthFunc(viz.GL_ALWAYS)
		self.quadrantTriangles.drawOrder(0)
		self.quadrantTriangles.visible(viz.OFF)
		
		# object clone list for the quadrants
		self.clone_list = []
		
		# determines the selected quadrant
		self.selectedQuadrant = Quadrant.NONE
		
		# SQUAD selection mode, can be SELECTION and SELECTION_QUADRANT
		self.mode = InteractionMode.SELECTION
		
		# flag that tells if there are intersecting objects
		self.intersecting = False
		
		# variable that controls the animation of the objects in the quadrants
		self.rotQUAD = 0
		
		# register button callbacks
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
	
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
		
	#-------------------------------------------------------------------------------
	# SQUAD quadrants functions
	#-------------------------------------------------------------------------------
	# createSQUADQuadrants()
	# distributes the items that were inside the sphere among the different quadrants
	def createSQUADQuadrants(self,list,centered=0):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		self.cloneList = []
		#print "selecting an object among:",list
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		#print "size of the array:",len(list)
		aspect = (viz.getWindowList())[0].getAspectRatio()
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
		for child in list:
			clone = child
			#clone.collideNone()
			clone.depthFunc(viz.GL_ALWAYS)
			clone.drawOrder(3)
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
			#print index,"  dir_vector[%.4f,"%((x*aspect)-aspect/2.0)+"%.4f"%y+"] =",dir_vector,"    length =",length
			#if index%4 == 0:
			#	print "going to",(user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4]
			clone.setMatrix(identity,viz.ABS_GLOBAL)		
			obj_position = clone.getBoundingBox(viz.ABS_GLOBAL).center
			#clone.parent(supermarket)
			curPos = clone.getPosition() #Save current position
			if clone_total_level_2[0] > 2 and clone_dist_level_2[0] > clone_dist_level_3[0]:
				clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_3[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_3[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_3[index%4], viz.ABS_GLOBAL)
			elif clone_total_level_1[0] > 2 and clone_dist_level_1[0] > clone_dist_level_2[0]:
				clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_2[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_2[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_2[index%4], viz.ABS_GLOBAL)
			else:
				clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_1[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_1[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_1[index%4], viz.ABS_GLOBAL)
			gotoPos = clone.getPosition() #Get computed local pos
			clone.setPosition(curPos) #Restore position
			#clone.runAction(vizact.goto(gotoPos,.25,viz.TIME))
			clone.setPosition(gotoPos)
			#clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4])
			self.cloneList.append(clone)
			index+=1

	# selectSQUADQuadrant()
	# callback for selection of quadrants, called by the real callback that checks
	# if the select button was pressed during the SELECTION self.mode or SELECTION_QUADRANTS
	def selectSQUADQuadrant(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		if len(self.cloneList) > 0:
			#print "selecting those items who are in",self.selectedQuadrant
			#print "self.cloneList had",len(self.cloneList),"items"
			new_clone_list = []
			index = 0
			for clone in self.cloneList:
				if index%4 != self.selectedQuadrant: 
					#print "removing index",index,"..."
					#clone.visible(viz.OFF)
					clone.endAction(viz.ALL_POOLS)
					#clone.setPosition(0,0,0,viz.ABS_GLOBAL)
					clone.setMatrix(identity,viz.ABS_GLOBAL)
					clone.depthFunc(viz.GL_LESS)
					clone.drawOrder(0)
					#print len(self.cloneList)
				else:
					new_clone_list.append(clone)
				index+=1
			#print "now self.cloneList has",len(new_clone_list),"items"
			if len(new_clone_list) > 1:
				#print "more than 1 left..."
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
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		x,y = float(self.cursorPosition[0])/float(self.windowSize[0]), float(self.cursorPosition[1])/float(self.windowSize[1])
		
		if y >= 0.5 and x >= (0.5-(y-0.5)) and x <= (0.5+(y-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'top')
			self.selectedQuadrant = Quadrant.TOP
		else:
			self.quadrantTriangles.color([1,1,1],'top')
		if y < 0.5 and x >= (0.5-((1.0-y)-0.5)) and x <= (0.5+((1.0-y)-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'bottom')
			self.selectedQuadrant = Quadrant.BOTTOM
		else:
			self.quadrantTriangles.color([1,1,1],'bottom')
		if x < 0.5 and y >= (0.5-((1.0-x)-0.5)) and y <= (0.5+((1.0-x)-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'left')
			self.selectedQuadrant = Quadrant.LEFT
		else:
			self.quadrantTriangles.color([1,1,1],'left')
		if x >= 0.5 and y >= (0.5-(x-0.5)) and y <= (0.5+(x-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'right')
			self.selectedQuadrant = Quadrant.RIGHT
		else:
			self.quadrantTriangles.color([1,1,1],'right')
		
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		
		for item in self.cloneList:
			if item.getAction() == None:
				oldposition = item.getBoundingBox(viz.ABS_GLOBAL).center
				screenposition = viz.MainWindow.worldToScreen(oldposition, eye = viz.BOTH_EYE, mode = viz.WINDOW_NORMALIZED)
				distance = math.sqrt(math.pow((user_position[0]-oldposition[0]),2)+math.pow((user_position[1]-oldposition[1]),2)+math.pow((user_position[2]-oldposition[2]),2))
				item.setMatrix(identity,viz.ABS_GLOBAL)
				item.setAxisAngle(-.5,1,0,self.rotQUAD,viz.ABS_GLOBAL)
				center = item.getBoundingBox(viz.ABS_GLOBAL).center
				#print "screen position:",screenposition
				line = viz.screentoworld(screenposition[0],screenposition[1])
				#distance = screenposition[2]
				dir_vector = line.dir
				length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
				dir_vector[0] = (dir_vector[0]/length)
				dir_vector[1] = (dir_vector[1]/length)
				dir_vector[2] = (dir_vector[2]/length)
				point = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
				item.setPosition(point[0]-center[0],point[1]-center[1],point[2]-center[2],viz.ABS_GLOBAL)

	# reset()
	# resets SQUAD quadrants
	def reset(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
		
		if self.mode == InteractionMode.SELECTION_QUADRANTS:
			for clone in self.cloneList:
				#print "removing index",index,"..."
				#clone.visible(viz.OFF)
				clone.endAction(viz.ALL_POOLS)
				clone.setMatrix(identity,viz.ABS_GLOBAL)
				clone.depthFunc(viz.GL_LESS)
				clone.drawOrder(0)
				#print len(self.cloneList)
			self.cloneList = []
		
		self.mode = InteractionMode.SELECTION

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
	
	# update()
	# main update function for squad, needs to be called every frame/every time the cursor is updated
	def update(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		user_position = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		aspect = (viz.getWindowList())[0].getAspectRatio()
		
		#print "User Position:", user_position[12], user_position[13], user_position[14]
		#print "orientation:",viz.MainView.getEuler()
		
		#print "width: ", aspect, "  height: ", 1.0
		#line = viz.screentoworld(x*aspect-(aspect-1.0)/2.0,(1.0-y))
		
		self.rotQUAD += 1
		if self.rotQUAD == 360:
			self.rotQUAD = 1
			
		if self.mode == InteractionMode.SELECTION:
			self.quadrantLines.visible(viz.OFF)
			self.quadrantTriangles.visible(viz.OFF)
			self.scSphere.visible(viz.ON)
			self.crosshair.visible(viz.OFF)
			
			line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
			begin = line[:3]
			end = line[3:]
			
			all_info = viz.intersect(begin,end,True)
			index = 0
			self.intersecting = False
			for info in all_info:
				if info.valid == True:
					#print 'Intersected with object id:', info.object.id 
					if info.object != self.scSphere:
						self.scSphere.setPosition(info.point,viz.ABS_GLOBAL)
						distance = math.sqrt(((info.point[0]-user_position[12])*(info.point[0]-user_position[12])) + ((info.point[1]-user_position[13])*(info.point[1]-user_position[13])) + ((info.point[2]-user_position[14])*(info.point[2]-user_position[14])))
						self.scSphereRadius = 5.0+distance/50.0
						self.scSphere.setScale(self.scSphereRadius,self.scSphereRadius,self.scSphereRadius)
						#print index," distance:", distance, " sphere radius:", scSphereRadius
						self.intersecting = True
						break
					#else:
					#	print index," colliding with sphere"
				index += 1
			
			if self.intersecting == True:
				self.scSphere.visible(viz.ON)
			else:
				self.scSphere.visible(viz.OFF)
			
			self.intersectingObjects = []
			
			if self.intersecting == True:
				is_position = self.scSphere.getPosition(viz.ABS_GLOBAL)
				
				index = 0
				for obj in self.objects:
					obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size#obj.getBoundingBox(viz.ABS_GLOBAL).size
					#print obj,": ",obj_size
					if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
						obj_pos = obj.getBoundingBox(viz.ABS_GLOBAL).center
						distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
											 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
											 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
						
						#if viz.MainWindow.isCulled(obj) == 0: 
						if distance < self.scSphereRadius*1.2:
							self.intersectingObjects.append(obj)
					index+=1

			self.drawIntersectObjsBoundingBoxes()
			
		elif self.mode == InteractionMode.SELECTION_QUADRANTS:
			self.quadrantLines.setMatrix(user_position, viz.ABS_GLOBAL)
			self.quadrantLines.setPosition([0,0,50], viz.REL_LOCAL)
			self.quadrantLines.setScale(aspect,1,1)
			self.quadrantLines.visible(viz.ON)
			self.quadrantTriangles.setMatrix(user_position, viz.ABS_GLOBAL)
			self.quadrantTriangles.setPosition([0,0,50], viz.REL_LOCAL)
			self.quadrantTriangles.setScale(aspect,1,1)
			self.quadrantTriangles.visible(viz.ON)
			
			self.crosshair.visible(viz.ON)
			self.scSphere.visible(viz.OFF)
			
			self.crosshair.setPosition(x/self.windowSize[0],y/self.windowSize[1],0)
			
			self.updateSQUADQuadrants()

	# clean()
	# reset visual aids/quadrants
	def clean(self):	
		self.quadrantLines.visible(viz.OFF)
		self.quadrantTriangles.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
