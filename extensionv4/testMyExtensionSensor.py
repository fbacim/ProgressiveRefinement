import viz
import vizshape
viz.go()

# Create the extension
myext = viz.add('myextension.dle')

# Create custom sensor
sensor1 = myext.addMySensor(speed=180,radius=1)
sensor2 = myext.addMySensor(speed=90,radius=3,height=1)
sensor3 = myext.addMySensor(speed=45,radius=5,height=2)

# Link sensors to objects
viz.link( sensor1 , vizshape.addSphere(0.1,color=viz.RED) )
viz.link( sensor2 , vizshape.addSphere(0.1,color=viz.GREEN) )
viz.link( sensor3 , vizshape.addSphere(0.1,color=viz.BLUE) )

# Allow configuring sensors
import vizconfig
vizconfig.register(sensor1)
vizconfig.register(sensor2)
vizconfig.register(sensor3)
vizconfig.getConfigWindow().setWindowVisible(True)

#Add environment
vizshape.addGrid(color=[0.2]*3)
viz.clearcolor(viz.GRAY)

#Setup camera navigation
import vizcam
cam = vizcam.PivotNavigate(center=[0,0,0],distance=20)
cam.rotateUp(25)
