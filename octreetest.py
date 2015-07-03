from Octree import Octree, NodeObject
from Vector3 import Vector3

import viz
import vizshape

## ---------------------------------------------------------------------------------------------------##
def createBoundingBox(min,max,r=0.0,g=0.0,b=0.0,width=2.0):
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


# resetBoundingBoxes()
# reset the bounding boxes
def resetBoundingBoxes():
	global boundingBoxes
	for bb in boundingBoxes:
		bb.remove()
	boundingBoxes = []

# drawIntersectObjsBoundingBoxes()
# creates the bounding boxes of all objects that are inside the sphere, independent of its size
def drawIntersectObjsBoundingBoxes(intersectingObjects):
	global boundingBoxes
	resetBoundingBoxes()
	
	for object in intersectingObjects:
		aux_bb = object.getBoundingBox(viz.ABS_GLOBAL)
		min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
		bb = createBoundingBox(min,max,1,0,0)
		boundingBoxes.append(bb)


if __name__ == "__main__":
	### Object Insertion Test ###

	# So lets test the adding:
	import random
	import time

	#Dummy object class to test with
	class TestObject:
		def __init__(self, name, position):
			self.name = name
			self.position = position

	# Create a new octree, size of world
	myTree = Octree(15.0000)

	# Number of objects we intend to add.
	NUM_TEST_OBJECTS = 200

	# Number of collisions we're going to test
	NUM_COLLISION_LOOKUPS = 200

	# Insert some random objects and time it
	Start = time.time()
	for x in range(NUM_TEST_OBJECTS):
		pos = (random.randrange(-4500, 4500)/1000.0, random.randrange(-4500, 4500)/1000.0, random.randrange(-4500, 4500)/1000.0)
		sphere = vizshape.addSphere(radius=0.1)
		sphere.setPosition(pos)
		#testOb = TestObject(name, pos)
		testOb = NodeObject(x, pos, sphere)
		myTree.insertNode(myTree.root, 15.000, myTree.root, testOb)
	End = time.time() - Start

	# print some results.
	print str(NUM_TEST_OBJECTS) + "-Node Tree Generated in " + str(End) + " Seconds"
	print "Tree Leaves contain a maximum of " + str(5) + " objects each."

	Vertex = []
	FrustumPlane = []
	
	user_pos = viz.MainView.getPosition(viz.ABS_GLOBAL)
	origin = Vector3(user_pos[0],user_pos[1],user_pos[2])
	
	Vertex.append(Vector3(-1,-1,-1000))
	Vertex.append(Vector3(-1,-1,1000))
	Vertex.append(Vector3(-1, 1,-1000))
	Vertex.append(Vector3(-1, 1,1000))
	Vertex.append(Vector3( 1,-1,-1000))
	Vertex.append(Vector3( 1,-1,1000))
	Vertex.append(Vector3( 1, 1,-1000))
	Vertex.append(Vector3( 1, 1,1000))
	
	createBoundingBox(Vertex[0],Vertex[7],0,1,0)
	
	# adding frustum planes in order for rendering
	normal = Vector3.Cross( Vector3(Vertex[0],Vertex[1]), Vector3(Vertex[0],Vertex[2]) )
	#normal = Vector3.Cross( Vector3(Vertex[0],Vertex[2]), Vector3(Vertex[0],Vertex[1]) )
	normal.normalize()
	distance = Vector3.Dot( normal, Vertex[0] );
	FrustumPlane.append([normal,distance]) # F0 - left
	
	normal = Vector3.Cross( Vector3(Vertex[2],Vertex[3]), Vector3(Vertex[2],Vertex[6]) )
	#normal = Vector3.Cross( Vector3(Vertex[2],Vertex[6]), Vector3(Vertex[2],Vertex[3]) )
	normal.normalize()
	distance = Vector3.Dot( normal, Vertex[2] );
	FrustumPlane.append([normal,distance]) # F3 - top
	
	normal = Vector3.Cross( Vector3(Vertex[0],Vertex[4]), Vector3(Vertex[0],Vertex[1]) )
	#normal = Vector3.Cross( Vector3(Vertex[0],Vertex[1]), Vector3(Vertex[0],Vertex[4]) )
	normal.normalize()
	distance = Vector3.Dot( normal, Vertex[0] );
	FrustumPlane.append([normal,distance]) # F2 - bottom
	
	normal = Vector3.Cross( Vector3(Vertex[5],Vertex[4]), Vector3(Vertex[5],Vertex[7]) )
	#normal = Vector3.Cross( Vector3(Vertex[5],Vertex[7]), Vector3(Vertex[5],Vertex[4]) )
	normal.normalize()
	distance = Vector3.Dot( normal, Vertex[5] );
	FrustumPlane.append([normal,distance]) # F1 - right
	
	normal = Vector3.Cross( Vector3(Vertex[4],Vertex[0]), Vector3(Vertex[4],Vertex[6]) )
	#normal = Vector3.Cross( Vector3(Vertex[4],Vertex[6]), Vector3(Vertex[4],Vertex[0]) )
	normal.normalize()
	distance = Vector3.Dot( normal, Vertex[4] );
	FrustumPlane.append([normal,distance]) # F5 - front
	
	normal = Vector3.Cross( Vector3(Vertex[1],Vertex[5]), Vector3(Vertex[1],Vertex[3]) )
	#normal = Vector3.Cross( Vector3(Vertex[1],Vertex[3]), Vector3(Vertex[1],Vertex[5]) )
	normal.normalize()
	distance = Vector3.Dot( normal, Vertex[1] );
	FrustumPlane.append([normal,distance]) # F6 - back
	
	objects_in_frustum = []
	myTree.nodesInFrustum(myTree.root,FrustumPlane,objects_in_frustum)
	
	global boundingBoxes
	boundingBoxes = []
	
	drawIntersectObjsBoundingBoxes(objects_in_frustum)
	
	for frustum in FrustumPlane:
		print frustum[0],frustum[1]

	'''
	### Lookup Tests ###

	# Look up some random positions and time it
	Start = time.time()
	for x in range(NUM_COLLISION_LOOKUPS):
		pos = (random.randrange(-4500, 4500)/1000.0, random.randrange(-4500, 4500)/1000.0, random.randrange(-4500, 4500)/1000.0)
		result = myTree.findPosition(myTree.root, pos)

		##################################################################################
		# This proves that results are being returned - but may result in a large printout
		# I'd just comment it out and trust me :)
		# print "Results for test at: " + str(pos)
		# if result != None:
		#    for i in result:
		#        print i.name, i.position,
		# print
		##################################################################################

	End = time.time() - Start

	# print some results.
	print str(NUM_COLLISION_LOOKUPS) + " Collision Lookups performed in " + str(End) + " Seconds"
	print "Tree Leaves contain a maximum of " + str(MAX_OBJECTS_PER_CUBE) + " objects each."
	'''
	myTree.draw()
	
	viz.go()
	#x = raw_input("Press any key (Wheres the any key?):")
	## end of http://code.activestate.com/recipes/498121/ }}}
