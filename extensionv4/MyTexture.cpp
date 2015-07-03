#include "MyTexture.h"

static unsigned char random()
{
	return (unsigned char)(((float)rand()/RAND_MAX)*255.0f);
}

MyTexture::MyTexture(int width, int height)
	: VizExtensionOSGTexture()
{
	m_image = new osg::Image;
	m_image->setImage(width,height,1,3,GL_RGB,GL_UNSIGNED_BYTE,new unsigned char[width*height*3],osg::Image::USE_NEW_DELETE);
	m_image->setDataVariance(osg::Object::DYNAMIC);

	m_texture = new osg::Texture2D;
	m_texture->setImage(m_image.get());
	m_texture->setWrap(osg::Texture::WRAP_S,osg::Texture::CLAMP_TO_EDGE);
	m_texture->setWrap(osg::Texture::WRAP_T,osg::Texture::CLAMP_TO_EDGE);
	m_texture->setDataVariance(osg::Object::DYNAMIC);

	generate();
}

MyTexture::~MyTexture(void)
{
}

void MyTexture::generate()
{
	for(int x = 0; x < m_image->s(); x++) {
		for(int y = 0; y < m_image->t(); y++) {
			unsigned char *pixel = m_image->data(x,y);
			pixel[0] = random();
			pixel[1] = random();
			pixel[2] = random();
		}
	}
	m_image->dirty();
}

/*
 Handles a user triggered command
 */
void MyTexture::command(viz::Data &data)
{
	int command = data.getInt("command");

	switch(command) {

		case 1: // Generate new random image
			generate();
			break;

	}
}
