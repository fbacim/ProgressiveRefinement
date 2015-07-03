#include "MyExtension.h"
#include "MySensor.h"
#include "MyNode.h"
#include "MyTexture.h"
#include <viz/python>
#include <iostream>

#include <osg/Node>
#include <osg/Texture>
#include <osg/Program>
#include <osg/Image>
#include <osg/OcclusionQueryNode>

/*
 This function is called once to create a single instance of your extension
 */
extern "C" __declspec(dllexport) viz::Extension* CreateVizardExtension(viz::Data &data);
viz::Extension* CreateVizardExtension(viz::Data &data)
{

	/*
	 You can optionally define the Python interface for you extension objects
	 within your source code here.
	 */
	const char *code =	//Define extension interface
						"class _MyExtension(viz.VizExtension):\n"

						"    def getSomeString(self):\n"
						"        return self.command(1)\n"

						"    def getSomeList(self,size):\n"
						"        return self.command(2,'',size)\n"

						"    def addMySensor(self, speed, radius, height=0.0):\n"
						"        return _MySensor(self.addSensor(1,'',speed,radius,height).id)\n"

						"    def addMyNode(self, speed):\n"
						"        return _MyNode(self.addNode(1,'',speed).id)\n"

						"    def addMyTexture(self, size):\n"
						"        return _MyTexture(self.addTexture(1,'',size[0],size[1]).id)\n"

						// Define sensor interface
						"class _MySensor(viz.VizExtensionSensor):\n"

						"    def setSpeed(self,speed):\n"
						"        self.command(1,'',speed)\n"

						"    def getSpeed(self):\n"
						"        return self.command(2)\n"

						"    def setRadius(self,radius):\n"
						"        self.command(3,'',radius)\n"

						"    def getRadius(self):\n"
						"        return self.command(4)\n"

						"    def setHeight(self,height):\n"
						"        self.command(5,'',height)\n"

						"    def getHeight(self):\n"
						"        return self.command(6)\n"

						"    def getConfigName(self):\n"
						"        return 'MySensor ' + str(self.id)\n"

						"    def createConfigUI(self):\n"
						"        '''Implement configurable interface'''\n"
						"        import vizconfig\n"
						"        ui = vizconfig.DefaultUI()\n"
						"        ui.addCommandItem('','Reset',self.reset)\n"
						"        ui.addFloatRangeItem('Speed',[0.0,360.0],fset=self.setSpeed,fget=self.getSpeed)\n"
						"        ui.addFloatRangeItem('Radius',[0.0,10.0],fset=self.setRadius,fget=self.getRadius)\n"
						"        ui.addFloatRangeItem('Height',[-5.0,5.0],fset=self.setHeight,fget=self.getHeight)\n"
						"        return ui\n"

						// Define node interface
						"class _MyNode(viz.VizExtensionNode):\n"

						"    def setSpeed(self,speed):\n"
						"        self.command(1,'',speed)\n"

						"    def getSpeed(self):\n"
						"        return self.command(2)\n"

						"    def getConfigName(self):\n"
						"        return 'MyNode ' + str(self.id)\n"

						"    def createConfigUI(self):\n"
						"        '''Implement configurable interface'''\n"
						"        import vizconfig\n"
						"        ui = vizconfig.DefaultUI()\n"
						"        ui.addFloatRangeItem('Speed',[0.0,5.0],fset=self.setSpeed,fget=self.getSpeed)\n"
						"        return ui\n"

						//Define texture interface
						"class _MyTexture(viz.VizExtensionTexture):\n"

						"    def generate(self):\n"
						"        self.command(1)\n"

						"    def getConfigName(self):\n"
						"        return 'MyTexture ' + str(self.id)\n"

						"    def createConfigUI(self):\n"
						"        '''Implement configurable interface'''\n"
						"        import vizconfig\n"
						"        ui = vizconfig.DefaultUI()\n"
						"        ui.addCommandItem('','Regenerate',self.generate)\n"
						"        return ui\n";

	Python_SetExtensionCode(code);

	return new MyExtension();
}

MyExtension::MyExtension(void)
	: viz::Extension()
{
}

MyExtension::~MyExtension(void)
{
}

/*
 Called every frame to allow extension to perform any updates.
 */
void MyExtension::update(const viz::Event &e)
{
	// Same as viz.getFrameNumber()
	int frameNumber = e.getID();

	// Same as viz.getFrameTime()
	double frameTime = e.getTime();

	// Same as viz.getFrameElapsed()
	double frameElapsed = e.getElapsed();

	// TODO: Perform any per frame updates
}

/*
 Handles a user triggered command
 */
void MyExtension::command(viz::Data &data)
{
	// Retrieve command arguments
	int command = data.getInt("command");
	const char *msg = data.getString("message");
	float x = data.getFloat("x");
	float y = data.getFloat("y");
	float z = data.getFloat("z");
	float w = data.getFloat("w");

	switch(command)
	{
		case 2: // return list of colors within distance of x, y
		{
			float distance = z;
			
			boost::unordered_map<unsigned int, float>::iterator iter;
			//boost::container::map<unsigned int, float>::iterator iter;
			
			std::vector<unsigned int> colorsList;

			for(iter = minColorDistance.begin(); iter != minColorDistance.end(); ++iter) 
				if(iter->first != 0xFFFFFF && sqrt(iter->second) <= distance)
					colorsList.push_back(iter->first);
			
			int size = colorsList.size();
			int* ret = new int[size];

			for(int i = 0; i < size; i++)
				ret[i] = (int)colorsList[i];

			data.set( PYTHON_RETURN_OBJECT , PYTHON_INT_LIST(ret, size) );
			//data.set( PYTHON_RETURN_OBJECT , PYTHON_UINT(colorsList[0]) );
		}
	}
}

/*
 Creates an extension node
 */
viz::Referenced* MyExtension::createNode(viz::Data &data)
{
	int command = data.getInt("command");

	//Create custom node object from specified arguments
	switch(command) {

		case 1:
			return new MyNode( data.getFloat("x") );
			break;

	}

	return NULL;
}

/*
 Creates an extension texture
 */
viz::Referenced* MyExtension::createTexture(viz::Data &data)
{
	int command = data.getInt("command");

	//Create custom texture object from specified arguments
	switch(command) {

		case 1:
			return new MyTexture( static_cast<int>(data.getFloat("x")) , static_cast<int>(data.getFloat("y")) );
			break;

	}

	return NULL;
}

/*
 Creates an extension sensor
 */
viz::Referenced* MyExtension::createSensor(viz::Data &data)
{
	int command = data.getInt("command");

	//Create custom sensor object from specified arguments
	switch(command) {

		case 1:
			return new MySensor( data.getFloat("x") , data.getFloat("y") , data.getFloat("z") );
			break;

	}

	return NULL;
}

int MyExtension::modifyNode(viz::Data &data)
{
	// The root transform of the node being modified
	osg::ref_ptr<osg::Node> osg_root = data.get<osg::Node*>("osg_root");

	// The actual scene graph node of the node being modified
	osg::ref_ptr<osg::Node> osg_node = data.get<osg::Node*>("osg_node");

	// Perform some modification on the node
	if(osg_node.valid()) 
	{
		//if(queryNodes.find(osg_node) == queryNodes.end())
		if(nodeColorMap.find(osg_node) == nodeColorMap.end())
		{
			/*osg::ref_ptr<osg::OcclusionQueryNode> parent = new osg::OcclusionQueryNode();
			//parent->setDebugDisplay(true);
			parent->setVisibilityThreshold(1); // One pixel
			osg_root->asTransform()->removeChild(osg_node.get());
			parent->addChild(osg_node.get());
			osg_root->asTransform()->addChild(parent.get());
			//queryNodes.push_back(parent);
			queryNodes.insert(std::pair< osg::Node*, osg::OcclusionQueryNode* >(osg_node, parent));*/

			//unsigned int r = (unsigned int)(data.getFloat("x")*255.0);
			//unsigned int g = (unsigned int)(data.getFloat("y")*255.0);
			//unsigned int b = (unsigned int)(data.getFloat("z")*255.0);
			//unsigned int a = 255;
			unsigned int composite = (unsigned int)(data.getFloat("x"));//(r << 24) + (g << 16) + (b << 8) + a;

			nodeColorMap[osg_node] = composite;
		}
		else
		{
			unsigned int composite = nodeColorMap[osg_node];

			//data.set( PYTHON_RETURN_OBJECT , PYTHON_UINT(composite) );
			if(colors.find(composite) != colors.end())
				data.set( PYTHON_RETURN_OBJECT , PYTHON_UINT(1) );
			else
				data.set( PYTHON_RETURN_OBJECT , PYTHON_UINT(0) );
		}
	}

	return 0;
}

int MyExtension::modifyTexture(viz::Data &data)
{
	// The texture object being modified
	osg::ref_ptr<osg::Texture> osg_texture = data.get<osg::Texture*>("osg_texture");

	// Retrieve command arguments
	float x = data.getFloat("x");
	float y = data.getFloat("y");

	// TODO: Perform some modification on the texture
	if(osg_texture.valid()) 
	{
		int width = osg_texture->getTextureWidth();
		int height = osg_texture->getTextureHeight();
		float radius = pow((float)(width*height),2); // return value
		
		unsigned char* buffer = new unsigned char[osg_texture->getTextureWidth()*osg_texture->getTextureHeight()*4];

		osg_texture->getTextureObject(0)->bind(); 
		glGetTexImage(osg_texture->getTextureTarget(), 0, GL_RGBA, GL_UNSIGNED_BYTE, &buffer[0]); 
	
		colors.clear();
		minColorDistance.clear();
	
		//for(int i = 0; i < osg_texture->getTextureWidth()*osg_texture->getTextureHeight()*4; i+=4)
		unsigned int pos = 0;
		for(int i = 0; i < height; i++)
		{
			for(int j = 0; j < width; j++)
			{
				//unsigned int pos = ((width * i) + j) * 4;
				unsigned int r = buffer[pos];
				unsigned int g = buffer[pos+1];
				unsigned int b = buffer[pos+2];
				//unsigned int a = 255;
				unsigned int composite = (r << 16) + (g << 8) + b;//(r << 24) + (g << 16) + (b << 8) + a;

				pos += 4;

				if(composite == 0xFFFFFF)
					continue;
				
				//colors.insert(composite);

				// calculate distance from cursor
				float distance = pow(j-x,2)+pow(i-y,2);
				if(minColorDistance.find(composite) == minColorDistance.end() || distance < minColorDistance[composite])
					minColorDistance[composite] = distance;
				if(minColorDistance[composite] < radius)
					radius = minColorDistance[composite];
			}
		}

		delete[] buffer;

		data.set( PYTHON_RETURN_OBJECT , PYTHON_FLOAT(sqrt(radius)) );
	}

	return 0;
}
