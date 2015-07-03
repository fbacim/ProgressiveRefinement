import viz
viz.go()

# Add a model
logo = viz.addChild('logo.ive',pos=(0,1,5))

# Create the extension
myext = viz.add('myextension.dle')

# Perform some modification on the node
myext.modifyNode(logo)
