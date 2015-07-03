#pragma once

#include <viz/ExtensionOSGNode>
#include <osg/Geode>

class CustomDrawable;

class MyNode : public viz::ExtensionOSGNode
{
public:
	MyNode(float speed);

	/*
	 You must override this method to return a valid osg::Node pointer
	 */
	virtual osg::Node* getNode() { return m_geode.get(); }
	virtual void command(viz::Data &data);

protected:
	virtual ~MyNode(void);

	osg::ref_ptr<osg::Geode> m_geode;
	osg::ref_ptr<CustomDrawable> m_drawable;
};
