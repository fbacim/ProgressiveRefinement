import viz
viz.go()

# Create the extension
myext = viz.add('myextension.dle')

# Create custom node
mynode = myext.addMyNode(speed=1.0)
mynode.setPosition([0,1.8,7])

# Add a texture
tex = viz.add('image2.jpg')

# Apply texture to custom node
mynode.texture(tex)

# Allow configuring node
import vizconfig
vizconfig.register(mynode)
vizconfig.getConfigWindow().setWindowVisible(True)
