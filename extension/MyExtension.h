#pragma once

#include <viz/Extension>
#include <map>
#include <set>
#include <boost/unordered_map.hpp>
#include <boost/container/map.hpp>
#include <osg/OcclusionQueryNode>

class MyExtension : public viz::Extension
{
public:
	MyExtension(void);

	//You must override this method to provide a name for your extension
	virtual const char* getName() const { return "My Extension"; }


	/******************************************************
	 ********* THE FOLLOWING METHODS ARE OPTIONAL *********
	 ******************************************************/

	virtual void update(const viz::Event &e);
	virtual void command(viz::Data &data);
	virtual viz::Referenced* createNode(viz::Data &data);
	virtual viz::Referenced* createTexture(viz::Data &data);
	virtual viz::Referenced* createSensor(viz::Data &data);
	virtual int modifyNode(viz::Data &data);
	virtual int modifyTexture(viz::Data &data);

protected:
	virtual ~MyExtension(void);

private:
	std::map< osg::Node*, osg::OcclusionQueryNode* > queryNodes;
	std::set< unsigned int > colors;
	//std::map< unsigned int, float > minColorDistance;
	boost::unordered_map< unsigned int, float > minColorDistance;
	//boost::container::map< unsigned int, float > minColorDistance;
	std::map< osg::Node*, unsigned int > nodeColorMap;
};
