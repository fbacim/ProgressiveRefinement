## {{{ http://code.activestate.com/recipes/498121/ (r1)
# python Octree v.1

# UPDATED:
# Is now more like a true octree (ie: partitions space containing objects)

# Important Points to remember:
# The OctNode positions do not correspond to any object position
# rather they are seperate containers which may contain objects
# or other nodes.

# An OctNode which which holds less objects than MAX_OBJECTS_PER_CUBE
# is a LeafNode; it has no branches, but holds a list of objects contained within
# its boundaries. The list of objects is held in the leafNode's 'data' property

# If more objects are added to an OctNode, taking the object count over MAX_OBJECTS_PER_CUBE
# Then the cube has to subdivide itself, and arrange its objects in the new child nodes.
# The new octNode itself contains no objects, but its children should.

# Psyco may well speed this script up considerably, but results seem to vary.

# TODO: Add support for multi-threading for node insertion and/or searching

#### Global Variables ####

# This defines the maximum objects an LeafNode can hold, before it gets subdivided again.
MAX_OBJECTS_PER_CUBE = 20

# This dictionary is used by the findBranch function, to return the correct branch index
DIRLOOKUP = {"3":0, "2":1, "-2":2, "-1":3, "1":4, "0":5, "-4":6, "-3":7}

#### End Globals ####

import viz
import vizshape

import math

from Vector3 import Vector3

class OctNode:
	# New Octnode Class, can be appended to as well i think
	def __init__(self, position, size, data):
		# OctNode Cubes have a position and size
		# position is related to, but not the same as the objects the node contains.
		self.position = position
		self.size = size

		# All OctNodes will be leaf nodes at first
		# Then subdivided later as more objects get added
		self.isLeafNode = True

		# store our object, typically this will be one, but maybe more
		self.data = data

		# might as well give it some emtpy branches while we are here.
		self.branches = [None, None, None, None, None, None, None, None]

		# The cube's bounding coordinates -- Not currently used
		self.ldb = (position[0] - (size / 2.0), position[1] - (size / 2.0), position[2] - (size / 2.0))
		self.ruf = (position[0] + (size / 2.0), position[1] + (size / 2.0), position[2] + (size / 2.0))
		
	# returns a list with all objects 
	def allObjects(self,nodeList,bbList):
		if self.isLeafNode:
			for obj in self.data:
				nodeList.append(obj.obj)
				bbList.append(obj.bs)
		else:
			for branch in self.branches:
				if branch != None:
					branch.allObjects(nodeList,bbList)
	
class Octree:
	def __init__(self, worldSize, x=0, y=0, z=0):
		# Init the world bounding root cube
		# all world geometry is inside this
		# it will first be created as a leaf node (ie, without branches)
		# this is because it has no objects, which is less than MAX_OBJECTS_PER_CUBE
		# if we insert more objects into it than MAX_OBJECTS_PER_CUBE, then it will subdivide itself.
		self.root = self.addNode((x,y,z), worldSize, [])
		self.worldSize = worldSize
		self.bbList = []
		
		# for frustum collision checks
		self.INTERSECT = 0
		self.INSIDE = 1
		self.OUTSIDE = 2

	def addNode(self, position, size, objects):
		# This creates the actual OctNode itself.
		return OctNode(position, size, objects)

	def insertNode(self, root, size, parent, objData):
		if root == None:
			# we're inserting a single object, so if we reach an empty node, insert it here
			# Our new node will be a leaf with one object, our object
			# More may be added later, or the node maybe subdivided if too many are added
			# Find the Real Geometric centre point of our new node:
			# Found from the position of the parent node supplied in the arguments
			pos = parent.position
			# offset is halfway across the size allocated for this node
			offset = size / 2
			# find out which direction we're heading in
			branch = self.findBranch(parent, objData.position)
			# new center = parent position + (branch direction * offset)
			newCenter = (0,0,0)
			if branch == 0:
				# left down back
				newCenter = (pos[0] - offset, pos[1] - offset, pos[2] - offset )

			elif branch == 1:
				# left down forwards
				newCenter = (pos[0] - offset, pos[1] - offset, pos[2] + offset )

			elif branch == 2:
				# right down forwards
				newCenter = (pos[0] + offset, pos[1] - offset, pos[2] + offset )

			elif branch == 3:
				# right down back
				newCenter = (pos[0] + offset, pos[1] - offset, pos[2] - offset )

			elif branch == 4:
				# left up back
				newCenter = (pos[0] - offset, pos[1] + offset, pos[2] - offset )

			elif branch == 5:
				# left up forward
				newCenter = (pos[0] - offset, pos[1] + offset, pos[2] + offset )

			elif branch == 6:
				# right up forward
				newCenter = (pos[0] + offset, pos[1] + offset, pos[2] + offset )

			elif branch == 7:
				# right up back
				newCenter = (pos[0] + offset, pos[1] + offset, pos[2] - offset )
				
			# Now we know the centre point of the new node
			# we already know the size as supplied by the parent node
			# So create a new node at this position in the tree
			# print "Adding Node of size: " + str(size / 2) + " at " + str(newCenter)
			return self.addNode(newCenter, size, [objData])

		#else: are we not at our position, but not at a leaf node either
		elif root.position != objData.position and root.isLeafNode == False:

			# we're in an octNode still, we need to traverse further
			branch = self.findBranch(root, objData.position)
			# Find the new scale we working with
			newSize = root.size / 2
			# Perform the same operation on the appropriate branch recursively
			root.branches[branch] = self.insertNode(root.branches[branch], newSize, root, objData)
		# else, is this node a leaf node with objects already in it?
		elif root.isLeafNode:
			# We've reached a leaf node. This has no branches yet, but does hold
			# some objects, at the moment, this has to be less objects than MAX_OBJECTS_PER_CUBE
			# otherwise this would not be a leafNode (elementary my dear watson).
			# if we add the node to this branch will we be over the limit?
			if len(root.data) < MAX_OBJECTS_PER_CUBE:
				# No? then Add to the Node's list of objects and we're done
				root.data.append(objData)
				#return root
			elif len(root.data) == MAX_OBJECTS_PER_CUBE:
				# Adding this object to this leaf takes us over the limit
				# So we have to subdivide the leaf and redistribute the objects
				# on the new children. 
				# Add the new object to pre-existing list
				root.data.append(objData)
				# copy the list
				objList = root.data
				# Clear this node's data
				root.data = None
				# Its not a leaf node anymore
				root.isLeafNode = False
				# Calculate the size of the new children
				newSize = root.size / 2
				# distribute the objects on the new tree
				# print "Subdividing Node sized at: " + str(root.size) + " at " + str(root.position)
				for ob in objList:
					branch = self.findBranch(root, ob.position)
					root.branches[branch] = self.insertNode(root.branches[branch], newSize, root, ob)
		return root

	def findPosition(self, root, position):
		# Basic collision lookup that finds the leaf node containing the specified position
		# Returns the child objects of the leaf, or None if the leaf is empty or none
		if root == None:
			return None
		elif root.isLeafNode:
			return root.data
		else:
			branch = self.findBranch(root, position)
			return self.findPosition(root.branches[branch], position)

	def findBranch(self, root, position):
		# helper function
		# returns an index corresponding to a branch
		# pointing in the direction we want to go
		vec1 = root.position
		vec2 = position
		result = 0
		# Equation created by adding nodes with known branch directions
		# into the tree, and comparing results.
		# See DIRLOOKUP above for the corresponding return values and branch indices
		for i in range(3):
			if vec1[i] <= vec2[i]:
				result += (-4 / (i + 1) / 2)
			else:
				result += (4 / (i + 1) / 2)
		result = DIRLOOKUP[str(result)]
		return result
		
	# createBoundingBox()
	# creates a bounding box with the given size
	def createBoundingBox(self,min,max,r=0.0,g=0.0,b=0.0,width=2.0):
		viz.startlayer(viz.LINE_LOOP, 'top') 
		viz.vertexcolor(r,g,b)
		viz.linewidth(width)
		
		#top
		#viz.vertexcolor(0.0,1.0,0.0)
		#viz.normal(0,1,0)
		viz.vertex( max[0], max[1], min[2])
		viz.vertex( min[0], max[1], min[2])
		viz.vertex( min[0], max[1], max[2])
		viz.vertex( max[0], max[1], max[2])

		viz.startlayer(viz.LINE_LOOP,'bottom') 
		viz.vertexcolor(r,g,b)
		viz.linewidth(width)
		
		#bottom
		#viz.vertexcolor(1.0,0.5,0.0)
		#viz.normal(0,-1,0)
		viz.vertex( max[0], min[1], max[2])
		viz.vertex( min[0], min[1], max[2])
		viz.vertex( min[0], min[1], min[2])
		viz.vertex( max[0], min[1], min[2])

		viz.startlayer(viz.LINE_LOOP,'front') 
		viz.vertexcolor(r,g,b)
		viz.linewidth(width)
		
		#front
		#viz.vertexcolor(1.0,0.0,0.0)
		#viz.normal(0,0,1)
		viz.vertex( max[0], max[1], max[2])
		viz.vertex( min[0], max[1], max[2])
		viz.vertex( min[0], min[1], max[2])
		viz.vertex( max[0], min[1], max[2])

		viz.startlayer(viz.LINE_LOOP,'back') 
		viz.vertexcolor(r,g,b)
		viz.linewidth(width)
		
		#back
		#viz.vertexcolor(r,g,b)
		#viz.normal(0,0,-1)
		viz.vertex( max[0], min[1], min[2])
		viz.vertex( min[0], min[1], min[2])
		viz.vertex( min[0], max[1], min[2])
		viz.vertex( max[0], max[1], min[2])

		viz.startlayer(viz.LINE_LOOP,'left') 
		viz.vertexcolor(r,g,b)
		viz.linewidth(width)
		
		#left
		#viz.vertexcolor(r,g,b)		
		#viz.normal(-1,0,0)
		viz.vertex( min[0], max[1], max[2])	
		viz.vertex( min[0], max[1], min[2])	
		viz.vertex( min[0], min[1], min[2])	
		viz.vertex( min[0], min[1], max[2])	

		viz.startlayer(viz.LINE_LOOP,'right') 
		viz.vertexcolor(r,g,b)
		viz.linewidth(width)
		
		#right
		#viz.vertexcolor(1.0,0.0,1.0)
		#viz.normal(1,0,0)
		viz.vertex( max[0], max[1], min[2])	
		viz.vertex( max[0], max[1], max[2])	
		viz.vertex( max[0], min[1], max[2])	
		viz.vertex( max[0], min[1], min[2])	
		
		return viz.endlayer()	
	
	def drawNode(self, node):
		if node.isLeafNode:
			self.bbList.append(self.createBoundingBox(node.ldb,node.ruf,0.5,0.5,0.5))
		for branch in node.branches:
			if branch != None:
				self.drawNode(branch)
	
	def draw(self):
		for bb in self.bbList:
			bb.remove()
		self.drawNode(self.root)

	# receive a node and the frustum planes
	def nodesInFrustum(self, node, planes, nodeList, bbList):
		# calculate intersection
		code = self.frustumAABBIntersect(planes, node)#node.ldb, node.ruf)
		#print code
		#if node.isLeafNode and code != self.OUTSIDE:
		#	print len(node.data)
		#	print node.data

		if code == self.INSIDE:
			# add all nodes
			node.allObjects(nodeList, bbList)
		#elif code == self.OUTSIDE:
		#	# This node (and all children) are outside, skip
		#	return ret
		elif code == self.INTERSECT:
			# Add objects associated to this node
			if node.isLeafNode:
				for obj in node.data:
					nodeList.append(obj.obj)
					bbList.append(obj.bs)
			else:
				# Visit my children
				for branch in node.branches:
					if branch != None:
						self.nodesInFrustum(branch,planes,nodeList,bbList)
		
		#print nodeList

	# Returns: INTERSECT : 0 
	#          INSIDE : 1 
	#          OUTSIDE : 2 
	def frustumAABBIntersect(self, planes, node):#mins, maxs):
		p1 = Vector3(node.ldb[0],node.ldb[1],node.ldb[2])
		p2 = Vector3(node.ruf[0],node.ruf[1],node.ruf[2])
		
		index = 0
		allInForAllPlanes = True
		for planeFrustum in planes:
			allOut = True
			for c in range(8):
				pos = Vector3(p1.x if (c&4) else p2.x, p1.y if (c&2) else p2.y, p1.z if (c&1) else p2.z)
				if (Vector3.Dot(pos, planeFrustum[0]) - planeFrustum[1]) > 0.0:
					allInForAllPlanes = False
				else:
					allOut = False
			
			# The eight points are on the outside side of this plane
			if allOut:
				return self.OUTSIDE

		if allInForAllPlanes:
			return self.INSIDE

		return self.INTERSECT

	#Object class to test with
class NodeObject:
	def __init__(self, index, bs, obj):
		self.index = index # index in the original list
		self.bs = bs # bounding sphere
		self.position = bs.center
		self.obj = obj # vizard object