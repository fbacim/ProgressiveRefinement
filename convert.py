import viz

# getmodels()
# creates a node3d for each model in the loaded .ive file 
def getModels():
	nodeNames = supermarket.getNodeNames()
	for name in nodeNames:
		supermarket.getChild(name)

if __name__ == '__main__':
	global children
	
	print "Loading the supermarket model"	
	supermarket = viz.add('finalM.ive')
	
	print "Getting all the models..."
	getModels()
	children = supermarket.getChildren()
	
	index = 0
	for object in children:
		object.save('supermarket'+str(index)+'.ive')
		index += 1