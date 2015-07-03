#pragma once

#include <viz/ExtensionSensor>

class MySensor : public viz::ExtensionSensor
{
public:
	MySensor(float speed, float radius, float height);

	//viz::ExtensionSensor interface
	virtual const char* getName() const { return "My Sensor"; }
	virtual void update(const viz::Event &e);
	virtual void command(viz::Data &data);
	virtual void reset(viz::Data &data);

	//Linkable interface
	virtual int getSourceType() const { return VIZ_LINK_POS | VIZ_LINK_ORI; }
	virtual bool getPosition(float *pos, int flag);
	virtual bool getOrientation(float *ori, int flag);

protected:
	virtual ~MySensor(void);
	
	float m_angle;
	float m_speed;
	float m_radius;
	float m_height;

	float m_pos[3];
	float m_ori[4];
};
