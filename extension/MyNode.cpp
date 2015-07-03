#include "MyNode.h"
#include <viz/python>

class CustomDrawable: public osg::Drawable
{
public:
	CustomDrawable(float speed=1.0f)
		: osg::Drawable()
		, m_speed(speed)
	{
		setUseDisplayList(false);
		setStateSet(new osg::StateSet);
	}

	CustomDrawable(const CustomDrawable& drawable ,const osg::CopyOp& copyop=osg::CopyOp::SHALLOW_COPY)
		: osg::Drawable(drawable,copyop)
		, m_speed(drawable.m_speed)
	{
	}

	virtual osg::Object* cloneType() const { return new CustomDrawable(); }
	virtual osg::Object* clone(const osg::CopyOp& copyop) const { return new CustomDrawable(*this,copyop); }        
	virtual bool isSameKindAs(const osg::Object* obj) const { return dynamic_cast<const CustomDrawable*>(obj)!=NULL; }

	void setSpeed(float speed) { m_speed = speed; }
	float getSpeed() const { return m_speed; }

	virtual void drawImplementation(osg::RenderInfo& renderInfo) const
	{
		//Calculate an offset for the right vertices
		double offset = fmod(renderInfo.getState()->getFrameStamp()->getReferenceTime()*m_speed,2.0);
		if(offset > 1.0)
			offset = 2.0 - offset;

		//PLACE OPENGL CODE HERE
		glBegin(GL_QUADS);
	
		glColor3f(1,1,1);
		glNormal3f(0,0,1);

		//Upper left vertex
		glTexCoord2f(0,1);
		glVertex3f(-1, 1, 0);

		//Upper right vertex
		glTexCoord2f(1,1);
		glVertex3f( 1+offset, 1+offset, 0);

		//Lower right vertex
		glTexCoord2f(1,0);
		glVertex3f( 1+offset,-1-offset, 0);

		//Lower left vertex
		glTexCoord2f(0,0);
		glVertex3f(-1,-1, 0);

		glEnd();
	}

	osg::BoundingBox computeBound() const
	{
		osg::BoundingBox bbox;

		//YOU MUST MANUALLY SET THE BOUNDING BOX OF YOUR OPENGL CODE
		bbox.set(-2,-2,-2,2,2,2);

		return bbox;
	}

protected:
	float m_speed;
};

MyNode::MyNode(float speed)
	: viz::ExtensionOSGNode()
{
	m_drawable = new CustomDrawable(speed);

	m_geode = new osg::Geode;
	m_geode->addDrawable(m_drawable.get());
}

MyNode::~MyNode(void)
{
}

/*
 Handles a user triggered command
 */
void MyNode::command(viz::Data &data)
{
	int command = data.getInt("command");

	switch(command) {

		case 1: // Set speed
			m_drawable->setSpeed( data.getFloat("x") );
			break;

		case 2: // Get speed
			data.set( PYTHON_RETURN_OBJECT , PYTHON_FLOAT(m_drawable->getSpeed()) );
			break;

	}
}
