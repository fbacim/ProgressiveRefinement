#pragma once

#include <viz/ExtensionOSGTexture>
#include <osg/Texture2D>

class MyTexture : public viz::ExtensionOSGTexture
{
public:
	MyTexture(int width, int height);

	/*
	 You must override this method to return a valid osg::Texture pointer
	 */
	virtual osg::Texture* getTexture() { return m_texture.get(); }
	virtual void command(viz::Data &data);

protected:
	virtual ~MyTexture(void);

	void generate();

	osg::ref_ptr<osg::Image> m_image;
	osg::ref_ptr<osg::Texture2D> m_texture;
};
