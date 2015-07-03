import viz
import math
import sys
from math import sqrt
import vizmat
import vizact

from PointingTechnique import PointingTechnique
from Vector3 import Vector3

class BubbleCursor(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "BubbleCursor"
		
		# object clone list for the quadrants
		self.clone_list = []
		
		# for calculating distances between the cursor and objects in the quad menu
		self.distance_list = []
		
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
		
		# register button callbacks
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
	
	# reset()
	# resets SQUAD quadrants
	def reset(self):
		# create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()
				
		if self.menuObj2OjbLine != None:
			self.menuObj2OjbLine.remove()

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
		
		if self.bubbleQuadMenu != None:
			self.bubbleQuadMenu.remove()
		if self.bubbleQuadMenuObj != None:
			self.bubbleQuadMenuObj.remove()
		if self.menuObj2OjbLine != None:
			self.menuObj2OjbLine.remove()
		self.scSphere.visible(viz.ON)
		self.crosshair.visible(viz.OFF)
		
		# reset flag
		self.intersecting = False
		
		# get the objects in the frustum formed by the sphere
		objects_in_cone = self.objects
		#objects_in_cone = self.calculateSphereCastingFrustum()
		
		# project cusor position into the world, create vector
		line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
		begin = line[:3]
		end = line[3:]
		
		origin = Vector3(begin[0],begin[1],begin[2])
		direction = Vector3(end[0]-begin[0],end[1]-begin[1],end[2]-begin[2])
		direction.normalize()
		#print origin, direction
		#print viz.MainView.getPosition(viz.ABS_GLOBAL)
		
		# testing distance from line to objects in the scene 
		d_prime_factor = 0.0005
		min_distance = 0.0
		min_distance_squared = 500**2
		# for the minimum visual size
		min_distance_to_point = 0
		#
		min_distance_obj = None
		min_distance_point = []
		min_distance_function = 0
		min_pos_in_ray = 0
		distance_to_point = 0
		index = 0
		
		# get intersecting object
		obj_intersect = None
		all_objects = viz.intersect(begin,end,True)
		for obj in all_objects:
			if obj.object != self.scSphere:
				obj_intersect = obj.object
				break
		
		# for visual distance
		for obj in objects_in_cone:
			obj_pos = obj.getBoundingBox(viz.ABS_GLOBAL).center
			point = Vector3(obj_pos[0],obj_pos[1],obj_pos[2]) 
			pos_in_ray = Vector3.PositionInRay(origin,direction,point)
			if pos_in_ray > 0: # checks if the object is in front of the user			
				obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
				if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
					screen_pos = viz.MainWindow.worldToScreen(obj_pos,mode=viz.WINDOW_PIXELS)
					# calculate distance from line to object
					distance = math.pow(screen_pos[0]-x,2)+math.pow(screen_pos[1]-y,2) # distance is squared
					if distance < min_distance_squared or obj_intersect == obj:
						min_distance_squared = distance #distance squared
						min_distance_obj = obj
						min_distance_point = point
						min_pos_in_ray = pos_in_ray
						if obj_intersect == obj:
							break
			index += 1
		# if we found an object within the minimal distance, calculate the size of the sphere
		if min_distance_obj != None:
			self.intersecting = True
			intersection = Vector3.IntersectionPoint(origin,direction,min_distance_point)
			min_distance = min_distance_squared**0.5 # distance squared
			self.scSphereRadius = intersection.distance(min_distance_point)
			self.scSphere.setScale(self.scSphereRadius,self.scSphereRadius,self.scSphereRadius)
		
			#print "intersection point:",intersection 
			self.scSphere.setPosition(intersection.x,intersection.y,intersection.z,viz.ABS_GLOBAL)
			
			#print "min_distance:",min_distance
			
		if self.intersecting == True:
			self.scSphere.visible(viz.ON)
		else:
			self.scSphere.visible(viz.OFF)
		
		self.intersectingObjects = []
		
		# determine which objects are in the sphere
		if self.intersecting == True:
			self.intersectingObjects.append(min_distance_obj)

		self.drawIntersectObjsBoundingBoxes()

	# clean()
	# reset visual aids
	def clean(self):	
		self.scSphere.visible(viz.OFF)
