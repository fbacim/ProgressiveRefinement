#include "MySensor.h"
#include <viz/python>

#define _USE_MATH_DEFINES
#include <math.h>

MySensor::MySensor(float speed, float radius, float height)
	: viz::ExtensionSensor()
	, m_angle(0.0f)
	, m_speed(speed)
	, m_radius(radius)
	, m_height(height)
{
	m_pos[0] = m_pos[1] = m_pos[2] = 0.0f;
	m_ori[0] = m_ori[1] = m_ori[2] = 0.0f; m_ori[3] = 1.0f;
}

MySensor::~MySensor(void)
{
}

/*
 Called every frame to allow sensor to update data.
 */
void MySensor::update(const viz::Event &e)
{
	//Update rotation angle
	double elapsed = e.getElapsed();
	m_angle += m_speed * static_cast<float>(elapsed);

	//Convert to radians
	float radians = m_angle * (static_cast<float>(M_PI) / 180.0f);

	//Update position
	m_pos[0] = sinf(radians) * m_radius;
	m_pos[1] = m_height;
	m_pos[2] = cosf(radians) * m_radius;
}

/*
 Handles a user triggered command.
 */
void MySensor::command(viz::Data &data)
{
	int command = data.getInt("command");

	switch(command) {

		case 1: // Set speed
			m_speed = data.getFloat("x");
			break;

		case 2: // Get speed
			data.set( PYTHON_RETURN_OBJECT , PYTHON_FLOAT(m_speed) );
			break;

		case 3: // Set radius
			m_radius = data.getFloat("x");
			break;

		case 4: // Get radius
			data.set( PYTHON_RETURN_OBJECT , PYTHON_FLOAT(m_radius) );
			break;

		case 5: // Set height
			m_height = data.getFloat("x");
			break;

		case 6: // Get height
			data.set( PYTHON_RETURN_OBJECT , PYTHON_FLOAT(m_height) );
			break;

	}
}

/*
 Called by the user to reset the sensor.
 */
void MySensor::reset(viz::Data &data)
{
	m_angle = 0.0f;
}

/*
 Return the current sensor position, if supported
 */
bool MySensor::getPosition(float *pos, int flag)
{
	pos[0] = m_pos[0];
	pos[1] = m_pos[1];
	pos[2] = m_pos[2];
	return true;
}

/*
 Return the current sensor quaternion orientation, if supported
 */
bool MySensor::getOrientation(float *ori, int flag)
{
	ori[0] = m_ori[0];
	ori[1] = m_ori[1];
	ori[2] = m_ori[2];
	ori[3] = m_ori[3];
	return true;
}
