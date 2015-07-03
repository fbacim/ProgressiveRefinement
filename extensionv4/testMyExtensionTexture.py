import viz
viz.go()

# Create the extension
myext = viz.add('myextension.dle')

# Create custom texture
mytex = myext.addMyTexture(size=[256,256])

# Apply texture to a quad
quad = viz.addTexQuad(pos=(0,1.8,2),texture=mytex)

# Allow configuring texture
import vizconfig
vizconfig.register(mytex)
vizconfig.getConfigWindow().setWindowVisible(True)
