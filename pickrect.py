import viz
import vizact


viz.go()
viz.MainView.setPosition( 6,6,-24)

#create boxes
boxes = []
for r in range(10):
	for c in range(10):
		for d in range(10):
			b =viz.add('box.wrl', pos=[r*1.5,c*1.5,d*1.5] )
			b.setScale([(10.0-float(d))/10.0*1,(10.0-float(d))/10.0*1,(10.0-float(d))/10.0*1])
			boxes.append(b)



def onKeyDown():
	for b in boxes:
		b.color( viz.RED )

	#now do a pick around the mouse
	mousePos = viz.mouse.getPosition( )
	rect = [mousePos[0]-.1, mousePos[1]-.1, mousePos[0]+.1, mousePos[1]+.1]
	selection = viz.MainWindow.pickRect( rect  )
	for b in selection:
		b.color( viz.GREEN)

vizact.onkeydown( ' ', onKeyDown)