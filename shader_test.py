"""
This script uses a multi-texturing shader.
Multitexturing allows you to apply multiple textures to an object.
Drag the slider to change the texture blending mix.
"""
import viz
import vizact

viz.setMultiSample(4)
viz.fov(60)
viz.go()

#import vizinfo
#vizinfo.InfoPanel()

viz.clearcolor( viz.GRAY )

#Add the geometry that we will be applying the shader to
quad1 = viz.addTexQuad()
quad1.setPosition([0, 1.8, 1])
#quad1.setScale([3,3,3])
#quad1.setPosition([1, 1, 2.5])

#Add all the textures that the tutorial will use
tex1 = viz.addTexture( 'image-test.png' )
tex1.filter(viz.MIN_FILTER,viz.NEAREST)
tex1.filter(viz.MAG_FILTER,viz.NEAREST)

#Attach these textures to the nodes as texture numbers 0 and 1
quad1.texture( tex1 )

#Create shader object and assosiate it with our texture blending frag program
tex2 = viz.addRenderTexture()
shader = viz.addShader( frag = 'occlusion.frag' )
lens = viz.addRenderNode(size=(100,100))
lens.attachTexture(tex2)
#lens.setInheritView(True,viz.POST_MULT)
quad1.renderOnlyToRenderNodes([lens], True)

#Create the shader parameter objects
#They tell the shader the texture numbers of blendable textures and blend amount
TextureUnit1Uniform = viz.addUniformInt( 'TextureUnit1', 0 )

#Make Vizard use the created shader when rendering the logo node
lens.apply( shader )
#Provide the shader with its parameters
lens.apply( TextureUnit1Uniform )

def update():
	data = tex2.saveToBuffer('<raw>')
	print len(data)
#quad2 = viz.addTexQuad()
#quad2.setPosition([0, 1.8, 1])
#quad2.texture( tex2 )


vizact.ontimer(0,update)