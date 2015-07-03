import viz
import math
import sys
from math import sqrt
import vizmat

from PointingTechnique import PointingTechnique
from Vector3 import Vector3

class InteractionMode:
	SELECTION = 0
	SELECTION_QUADRANTS = 1
	
class Quadrant:
	TOP=0
	BOTTOM=1
	LEFT=2
	RIGHT=3
	NONE=4

class SQUADBubblev3(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "SQUAD+bubble cursor v3"
		
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
			#print index,"  dir_vector[%.4f,"%((x*aspectRatio)-aspectRatio/2.0)+"%.4f"%y+"] =",dir_vector,"    length =",length
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
			self.clone_list.append(clone)
			index+=1
	#'''
	
	'''
	# New version; automatic definition of lists (inside->outside)
	def createSQUADQuadrants(self, list,centered=0):
		identity = vizmat.Transform()
		identity.makeIdent()
		
		self.clone_list = []
		#print "selecting an object among:",list
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		#print "size of the array:",len(list)
		clone_total_level = [0.0,0.0,0.0,0.0]
		clone_dist_level = [0.0,0.0,0.0,0.0]
		clone_total_sub_level = [0.0,0.0,0.0,0.0]
		clone_dist_sub_level = [0.0,0.0,0.0,0.0]
		clone_current_sub_level = [0.0,0.0,0.0,0.0]
		index = 0
		for child in list:
			clone_total_level[index%4]+=1.0
			index += 1
		
		for i in range(4):
			clone_total_sub_level[i] = 1.0
			clone_current_sub_level[i] = 3.0
		
		#if clone_total_level[0] == 4.0:
		#	for i in range(4):
		#		clone_total_sub_level[i] = 1.0
		#		clone_current_sub_level[i] = 3.0
		#elif clone_total_level[0] == 16.0:
		#	for i in range(4):
		#		clone_total_sub_level[i] = 1.0
		#		clone_current_sub_level[i] = 6.0
		#elif clone_total_level[0] == 64.0:
		#	for i in range(4):
		#		clone_total_sub_level[i] = 1.0
		#		clone_current_sub_level[i] = 11.0
		
		if clone_total_sub_level[0] > 0:
			clone_xy_offset = 0.25/clone_current_sub_level[0]
		else:
			clone_xy_offset = 0
		distance_level = 110 + 30*(clone_current_sub_level[0])
		index = 0
		#print "list"
		for child in list:
			clone = child
			#clone.collideNone()
			clone.depthFunc(viz.GL_ALWAYS)
			clone.drawOrder(3)
			obj_position = []
				
			#x,y = 0.5,0.5
			if index%4 == 0: # top
				#print "-------- TOP ---------"
				#print clone_dist_sub_level[0],"/",(clone_total_sub_level[0]-1.0)
				
				my_offset = (clone_xy_offset*(clone_total_sub_level[0]-1))
				if clone_total_sub_level[0] > 1:
					x = (0.5-my_offset)+((clone_dist_sub_level[0]/(clone_total_sub_level[0]-1.0))*(my_offset*2))
				else:
					x = 0.5
				y = 0.55+my_offset

				#print clone_current_sub_level[0]," - ", x
				
				#set the position of the last line to the center
				if clone_current_sub_level[0] == 1:
					if len(list) == 256:
						x += 0.045
					elif len(list) == 64 or len(list) == 16:
						x = 0.5
				

				#print "(",x,", ",y,")"
				#print "x,y: ",x,",",y
				#print "offset:",my_offset
				clone_dist_level[0] += 1.0
				clone_dist_sub_level[0] += 1.0
				if clone_dist_sub_level[0] == clone_total_sub_level[0]:
					clone_total_sub_level[0] += 1.0
					clone_dist_sub_level[0] = 0.0
					clone_current_sub_level[0] -= 1.0
				
			elif index%4 == 1: # bottom
				#print "-------- BOTTOM ---------"
				#print clone_dist_sub_level[1],"/",(clone_total_sub_level[1]-1.0)
				
				my_offset = (clone_xy_offset*(clone_total_sub_level[1]-1))
				if clone_total_sub_level[1] > 1:
					x = (0.5-my_offset)+((clone_dist_sub_level[1]/(clone_total_sub_level[1]-1.0))*(my_offset*2))
				else:
					x = 0.5
				y = 0.45-my_offset
				
				#set the position of the last line to the center
				if clone_current_sub_level[1] == 1:
					if len(list) == 256:
						x += 0.045
					elif len(list) == 64 or len(list) == 16:
						x = 0.5
				
				#print "x,y = ",x,",",y
				clone_dist_level[1] += 1.0
				clone_dist_sub_level[1] += 1.0
				if clone_dist_sub_level[1] == clone_total_sub_level[1]:
					clone_total_sub_level[1] += 1.0
					clone_dist_sub_level[1] = 0.0
					clone_current_sub_level[1] -= 1.0
					
			elif index%4 == 2: # left
				#print "-------- LEFT ---------"
				#print clone_dist_sub_level[2],"/",(clone_total_sub_level[2]-1.0)
				
				my_offset = (clone_xy_offset*(clone_total_sub_level[2]-1))
				if clone_total_sub_level[2] > 1:
					y = (0.5-my_offset)+((clone_dist_sub_level[2]/(clone_total_sub_level[2]-1.0))*(my_offset*2))
				else:
					y = 0.5
				x = 0.45-my_offset
				
				#set the position of the last line to the center
				if clone_current_sub_level[2] == 1:
					if len(list) == 256:
						y += 0.045
					elif len(list) == 64 or len(list) == 16:
						y = 0.5
				
				#print "x,y = ",x,",",y
				clone_dist_level[2] += 1.0
				clone_dist_sub_level[2] += 1.0
				if clone_dist_sub_level[2] == clone_total_sub_level[2]:
					clone_total_sub_level[2] += 1.0
					clone_dist_sub_level[2] = 0.0
					clone_current_sub_level[2] -= 1.0
				
			else: # right
				#print "-------- RIGHT ---------"
				#print clone_dist_sub_level[3],"/",(clone_total_sub_level[3]-1.0)
				
				my_offset = (clone_xy_offset*(clone_total_sub_level[3]-1))
				if clone_total_sub_level[3] > 1:
					y = (0.5-my_offset)+((clone_dist_sub_level[3]/(clone_total_sub_level[3]-1.0))*(my_offset*2))
				else:
					y = 0.5
				x = 0.55+my_offset

				#set the position of the last line to the center
				if clone_current_sub_level[3] == 1:
					if len(list) == 256:
						y += 0.045
					elif len(list) == 64 or len(list) == 16:
						y = 0.5

				#print "x,y = ",x,",",y
				clone_dist_level[3] += 1.0
				clone_dist_sub_level[3] += 1.0
				if clone_dist_sub_level[3] == clone_total_sub_level[3]:
					clone_total_sub_level[3] += 1.0
					clone_dist_sub_level[3] = 0.0
					clone_current_sub_level[3] -= 1.0
			
			line = viz.screentoworld(x,y)
			dir_vector = line.dir
			length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
			dir_vector[0] = (dir_vector[0]/length)#*1.3
			dir_vector[1] = (dir_vector[1]/length)#*1.3
			dir_vector[2] = (dir_vector[2]/length)#*1.3
			clone.setMatrix(identity,viz.ABS_GLOBAL)		
			obj_position = clone.getBoundingBox(viz.ABS_GLOBAL).center
			curPos = clone.getPosition() #Save current position
			dist = distance_level-clone_current_sub_level[index%4]*10
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*dist,(user_position[1]-obj_position[1])+dir_vector[1]*dist,(user_position[2]-obj_position[2])+dir_vector[2]*dist, viz.ABS_GLOBAL)
			self.clone_list.append(clone)
			index+=1
	'''

	'''
	# Old version (outside->inside)
	def createQuadrants(self,list,centered=0):		
		identity = vizmat.Transform()
		identity.makeIdent()
		#print "selecting an object among:",list
		user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
		#print "size of the array:",len(list)
		clone_total_level = [0.0,0.0,0.0,0.0]
		clone_dist_level = [0.0,0.0,0.0,0.0]
		clone_total_sub_level = [0.0,0.0,0.0,0.0]
		clone_dist_sub_level = [0.0,0.0,0.0,0.0]
		clone_current_sub_level = [0.0,0.0,0.0,0.0]
		index = 0
		for child in list:
			clone_total_level[index%4]+=1.0
			index += 1
			
		if clone_total_level[0] == 4.0:
			for i in range(4):
				clone_total_sub_level[i] = 3.0
				#clone_current_sub_level[i] = 2.0
		elif clone_total_level[0] == 16.0:
			for i in range(4):
				clone_total_sub_level[i] = 6.0
				#clone_current_sub_level[i] = 6.0
		elif clone_total_level[0] == 64.0:
			for i in range(4):
				clone_total_sub_level[i] = 11.0
				#clone_current_sub_level[i] = 11.0
		if clone_total_sub_level[0] > 0:
			clone_xy_offset = 0.35/clone_total_sub_level[0]
		else:
			clone_xy_offset = 0
		distance_level = 110 + 30*(clone_total_sub_level[0])
		index = 0
		#print "list"
		for child in list:
			clone = child
			#clone.collideNone()
			clone.depthFunc(viz.GL_ALWAYS)
			clone.drawOrder(3)
			obj_position = []
				
			#x,y = 0.5,0.5
			if index%4 == 0: # top
				#print "-------- TOP ---------"
				#print clone_dist_sub_level[0],"/",(clone_total_sub_level[0]-1.0)
				
				my_offset = (clone_xy_offset*clone_current_sub_level[0])
				if clone_total_level[0]-clone_dist_level[0] > 1 and clone_total_sub_level[0] > 1:
					x = (0.2+my_offset)+((clone_dist_sub_level[0]/(clone_total_sub_level[0]-1.0))*(0.6-(my_offset*2)))
				else:
					x = 0.5
				y = 0.9-my_offset
				#print "x,y = ",x,",",y
				clone_dist_level[0] += 1.0
				clone_dist_sub_level[0] += 1.0
				if clone_dist_sub_level[0] == clone_total_sub_level[0]:
					clone_total_sub_level[0] -= 1.0
					clone_dist_sub_level[0] = 0.0
					clone_current_sub_level[0] += 1.0
				
			elif index%4 == 1: # bottom
				#print "-------- BOTTOM ---------"
				#print clone_dist_sub_level[1],"/",(clone_total_sub_level[1]-1.0)
				
				my_offset = (clone_xy_offset*clone_current_sub_level[1])
				if clone_total_level[1]-clone_dist_level[1] > 1 and clone_total_sub_level[1] > 1:
					x = (0.2+my_offset)+((clone_dist_sub_level[1]/(clone_total_sub_level[1]-1.0))*(0.6-(my_offset*2)))
				else:
					x = 0.5
				y = 0.1+my_offset
				#print "x,y = ",x,",",y
				clone_dist_level[1] += 1.0
				clone_dist_sub_level[1] += 1.0
				if clone_dist_sub_level[1] == clone_total_sub_level[1]:
					clone_total_sub_level[1] -= 1.0
					clone_dist_sub_level[1] = 0.0
					clone_current_sub_level[1] += 1.0
					
			elif index%4 == 2: # left
				#print "-------- LEFT ---------"
				#print clone_dist_sub_level[2],"/",(clone_total_sub_level[2]-1.0)
				
				my_offset = (clone_xy_offset*clone_current_sub_level[2])
				if clone_total_level[2]-clone_dist_level[2] > 1 and clone_total_sub_level[2] > 1:
					y = (0.2+my_offset)+((clone_dist_sub_level[2]/(clone_total_sub_level[2]-1.0))*(0.6-(my_offset*2)))
				else:
					y = 0.5
				x = 0.1+my_offset
				#print "x,y = ",x,",",y
				clone_dist_level[2] += 1.0
				clone_dist_sub_level[2] += 1.0
				if clone_dist_sub_level[2] == clone_total_sub_level[2]:
					clone_total_sub_level[2] -= 1.0
					clone_dist_sub_level[2] = 0.0
					clone_current_sub_level[2] += 1.0
				
			else: # right
				#print "-------- RIGHT ---------"
				#print clone_dist_sub_level[3],"/",(clone_total_sub_level[3]-1.0)
				
				my_offset = (clone_xy_offset*clone_current_sub_level[3])
				if clone_total_level[3]-clone_dist_level[3] > 1 and clone_total_sub_level[3] > 1:
					y = (0.2+my_offset)+((clone_dist_sub_level[3]/(clone_total_sub_level[3]-1.0))*(0.6-(my_offset*2)))
				else:
					y = 0.5
				x = 0.9-my_offset
				#print "x,y = ",x,",",y
				clone_dist_level[3] += 1.0
				clone_dist_sub_level[3] += 1.0
				if clone_dist_sub_level[3] == clone_total_sub_level[3]:
					clone_total_sub_level[3] -= 1.0
					clone_dist_sub_level[3] = 0.0
					clone_current_sub_level[3] += 1.0
				
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
			#print index,"  dir_vector[%.4f,"%((x*self.aspectRatio)-aspectRatio/2.0)+"%.4f"%y+"] =",dir_vector,"    length =",length
			#if index%4 == 0:
			#	print "going to",(user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4]
			clone.setMatrix(identity,viz.ABS_GLOBAL)		
			obj_position = clone.getBoundingBox(viz.ABS_GLOBAL).center
			#clone.parent(supermarket)
			#object_to_place.setPosition(intersection_point[0]-center[0],intersection_point[1]-center[1],intersection_point[2]-center[2],viz.ABS_GLOBAL)
			curPos = clone.getPosition() #Save current position
			dist = distance_level-clone_current_sub_level[index%4]*10
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*dist,(user_position[1]-obj_position[1])+dir_vector[1]*dist,(user_position[2]-obj_position[2])+dir_vector[2]*dist, viz.ABS_GLOBAL)
			self.clone_list.append(clone)
			index+=1
	'''
	
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
		self.objInBubble = None
		
		quadHighlighted = False
		
		x,y = float(self.cursorPosition[0])/float(self.windowSize[0]), float(self.cursorPosition[1])/float(self.windowSize[1])
		
		# will create bubble cursor if these conditions are not met
		if y >= 0.95 and x >= (0.5-(y-0.5)) and x <= (0.5+(y-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'top')
			self.selectedQuadrant = Quadrant.TOP
			quadHighlighted = True
		else:
			self.quadrantTriangles.color([1,1,1],'top')
		if y < 0.05 and x >= (0.5-((1.0-y)-0.5)) and x <= (0.5+((1.0-y)-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'bottom')
			self.selectedQuadrant = Quadrant.BOTTOM
			quadHighlighted = True
		else:
			self.quadrantTriangles.color([1,1,1],'bottom')
		if x < 0.05 and y >= (0.5-((1.0-x)-0.5)) and y <= (0.5+((1.0-x)-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'left')
			self.selectedQuadrant = Quadrant.LEFT
			quadHighlighted = True
		else:
			self.quadrantTriangles.color([1,1,1],'left')
		if x >= 0.95 and y >= (0.5-(x-0.5)) and y <= (0.5+(x-0.5)):
			self.quadrantTriangles.color([0.2,0.6,1],'right')
			self.selectedQuadrant = Quadrant.RIGHT
			quadHighlighted = True
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
			
			for item in self.clone_list:
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
	
	# update()
	# main update function for squad, needs to be called every frame/every time the cursor is updated
	def update(self):
		x,y = self.cursorPosition[0],self.cursorPosition[1]
		
		user_position = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		user_position_v3 = Vector3(user_position[12],user_position[13],user_position[14])
		#print "User Position:", user_position[12], user_position[13], user_position[14]
		#print "orientation:",viz.MainView.getEuler()
		
		if self.mode == InteractionMode.SELECTION:			
			if self.bubbleQuadMenu != None:
				self.bubbleQuadMenu.remove()
			if self.bubbleQuadMenuObj != None:
				self.bubbleQuadMenuObj.remove()
			self.quadrantLines.visible(viz.OFF)
			self.quadrantTriangles.visible(viz.OFF)
			self.scSphere.visible(viz.ON)
			self.crosshair.visible(viz.OFF)
			
			self.intersecting = False
							
			# get the objects in the frustum formed by the sphere
			objects_in_cone = self.objects
			#objects_in_cone = self.calculateSphereCastingFrustum()
			
			line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
			begin = line[:3]
			end = line[3:]
			
			# first we check for intersections with the ray
			all_info = viz.intersect(begin,end,True)
			intersect_object = None
			for info in all_info:
				if info.valid == True:
					if info.object != self.scSphere:
						#print 'Intersected with object id:', info.object.id 
						intersect_object = info.object
						obj_size = intersect_object.getBoundingBox(viz.ABS_GLOBAL).size
						if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
							self.intersecting = True
							self.scSphereRadius = 5.0 # needs to be a function of distance and frustum settings
							self.scSphere.setScale(self.scSphereRadius,self.scSphereRadius,self.scSphereRadius)
							self.scSphere.setPosition(info.point,viz.ABS_GLOBAL)
						break
					#else:
					#	print index," colliding with sphere"
			
			if not self.intersecting:
				origin = Vector3(begin[0],begin[1],begin[2])
				direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
				direction.normalize()
				#print origin, direction
				
				# testing distance from line to objects in the scene 
				d_prime_factor = 0.0005
				min_distance = 50.0
				min_distance_squared = min_distance**2
				min_distance_to_point = 50.0
				min_distance_to_point_squared = min_distance_to_point**2
				min_d_prime = min_distance_squared+min_distance_to_point_squared*d_prime_factor
				min_distance_obj = None
				min_distance_point = []
				min_distance_function = 0
				index = 0
				for obj in objects_in_cone:#self.objects:
					#if not viz.MainWindow.isCulled(obj):
					obj_pos = obj.getBoundingBox(viz.ABS_GLOBAL).center
					point = Vector3(obj_pos[0],obj_pos[1],obj_pos[2]) 
					if Vector3.PositionInRay(origin,direction,point) > 0: # checks if the object is in front of the user
						obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
						if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
							obj_radius = obj.getBoundingSphere(viz.ABS_GLOBAL).radius
							distance = Vector3.DistanceToLineSquared(origin,direction,point)#+obj_radius # distance is squared
							distance_to_point = user_position_v3.distanceSquared(point)
							d_prime = distance+distance_to_point*d_prime_factor
							#if obj == testobject:
							#	print "if",d_prime,"<",min_d_prime
							#	print "distance to line",distance
							#	print "distance to point",distance_to_point
								
							#if distance < min_distance:
							if d_prime < min_d_prime: # distance squared
								min_d_prime = d_prime
								min_distance_squared = distance #distance squared
								min_distance_obj = obj
								min_distance_point = point
					index += 1
				
				# if we found an object within the minimal distance, calculate the size of the sphere
				if min_distance_obj != None:
					self.intersecting = True
					intersection = Vector3.IntersectionPoint(origin,direction,min_distance_point)
					min_distance = min_distance_squared**0.5 # distance squared
					if min_distance < 5.0:
						min_distance = 5.0
					self.scSphereRadius = min_distance
					self.scSphere.setScale(self.scSphereRadius,self.scSphereRadius,self.scSphereRadius)
				
					#print "intersection point:",intersection 
					self.scSphere.setPosition(intersection.x,intersection.y,intersection.z,viz.ABS_GLOBAL)
				
			if self.intersecting == True:
				self.scSphere.visible(viz.ON)
			else:
				self.scSphere.visible(viz.OFF)
			
			self.intersectingObjects = []
			
			# determine which objects are in the sphere
			if self.intersecting == True:
				#print "testing intersection with objects"
				is_position = self.scSphere.getPosition(viz.ABS_GLOBAL)
				radiusSquared = self.scSphereRadius*self.scSphereRadius*1.2
				
				index = 0
				for obj in objects_in_cone: #self.objects:
					#if not viz.MainWindow.isCulled(obj):
					obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size#obj.getBoundingBox(viz.ABS_GLOBAL).size
					#print obj,": ",obj_size
					if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
						obj_pos = obj.getBoundingBox(viz.ABS_GLOBAL).center
						distance = ((obj_pos[0]-is_position[0])**2+
									(obj_pos[1]-is_position[1])**2+
									(obj_pos[2]-is_position[2])**2)
						
						if distance < radiusSquared:
							self.intersectingObjects.append(obj)
					index+=1

			self.drawIntersectObjsBoundingBoxes()
			
		elif self.mode == InteractionMode.SELECTION_QUADRANTS:
			self.rotQUAD += 1
			if self.rotQUAD == 360:
				self.rotQUAD = 1
			
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

	# clean()
	# reset visual aids/quadrants
	def clean(self):	
		self.quadrantLines.visible(viz.OFF)
		self.quadrantTriangles.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
