import viz
import math

from PointingTechnique import PointingTechnique
from Vector3 import Vector3
from Timer import Timer

# based on Regis Kopper's DyCoDiR
class DyCoDiR(PointingTechnique):
	def __init__(self,sceneObjects):
		PointingTechnique.__init__(self,sceneObjects)
		
		self.name = "DyCoDiR"
		
		self.samplingInterval = 0.1 # seconds
		# for Regis' version
		self.timer = Timer()
		self.recoveryTimer = Timer()
		self.elapsedSampling = 0.0
		self.pointBuffer = []
		self.elapsedBuffer = []
		self.pointS = 0.0
		self.minS = 0.0
		self.maxS = 643 # converting 1.4m/s to px/s -> 1.4 * 1400 / 3.05 
		self.scaleC = 643
		self.recover = False
		self.pointOffset = Vector3()
		self.CDRatio = 1
		self.previousCalculatedPoint = Vector3(-1,-1,0)
		self.calculatedPoint = Vector3()
		self.userdata = 0.0
		
		self.registerButtonCallbacks(self.selectButtonPressed,self.selectButtonReleased)
	
	def update(self):
		prev_point = Vector3(self.cursorPosition[0],self.cursorPosition[1],0)
		if len(self.pointBuffer) > 1:
			# since we only add the current point to the pointBuffer inside the calculate function, we simply get the last one from the list
			prev_point = self.pointBuffer[-1]
		
		curr_point = Vector3(self.cursorPosition[0],self.cursorPosition[1],0)
		
		# calculate distance of the device from cursor position - orthogonal distance = 1.52m, max distance = 2.153m
		distance_from_center_px = math.sqrt(math.pow(self.cursorPosition[0]-self.windowSize[0]/2.0,2)+math.pow(self.cursorPosition[1]-self.windowSize[1]/2.0,2))
		max_distance_px = math.sqrt(math.pow(self.windowSize[0]/2.0,2)+math.pow(self.windowSize[1]/2.0,2))
		distance_from_center = distance_from_center_px*0.633/max_distance_px
		distance_to_cursor = (1.52+distance_from_center)*1000.0 # calculate function uses mm
		
		if self.previousCalculatedPoint == Vector3(-1,-1,0):
			self.previousCalculatedPoint = curr_point
		
		self.calculatedPoint = self.calculate(prev_point,curr_point,self.previousCalculatedPoint,distance_to_cursor)
		self.previousCalculatedPoint = self.calculatedPoint
		
		x,y = self.calculatedPoint.x/self.windowSize[0],self.calculatedPoint.y/self.windowSize[1]
		
		self.crosshair.visible(viz.ON)
		self.scSphere.visible(viz.OFF)
		
		obj = viz.pick(pos = [x,y])
		if obj.valid():
			obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
			#print intersectObj,": ",obj_size
			if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
				self.intersectingObjects = []
				self.intersectingObjects.append(obj)
			else:
				self.intersectingObjects = []
		else:
			self.intersectingObjects = []
		self.drawIntersectObjsBoundingBoxes()
		
		self.crosshair.setPosition(x,y,0)
		

	def calculate(self,prev_point,curr_point,previous_calculated_point,distance_to_cursor):
		# initialize sampling timer
		if not self.timer.running:
			self.timer.start()
		
		# update sampling timer
		prevElapsed = self.elapsedSampling
		self.elapsedSampling = self.timer.elapsed()
		
		# add point buffers
		self.pointBuffer.append(curr_point)
		self.elapsedBuffer.append(self.elapsedSampling)
		
		# start calculating only when the interval has passed
		if self.elapsedSampling > self.samplingInterval:
			# this calculates the speed of the point, which will determine the
			# CD ratio to be applied on the distance since last frame
			self.pointS = (curr_point-Vector3(self.pointBuffer[0][0],self.pointBuffer[0][1],0)).norm()/(self.elapsedSampling-self.elapsedBuffer[0])
			del self.pointBuffer[0]
			del self.elapsedBuffer[0]
		else:
			self.pointS = 0.0;
			
		k = 1.0
		if self.pointS > self.maxS:
			self.recover = True
			self.pointOffset = curr_point - previous_calculated_point
			if not self.recoveryTimer.running:
				self.recoveryTimer.clear()
				self.recoveryTimer.start()
		else:
			if self.recoveryTimer.running:
				self.recoveryTimer.stop()
				self.recoveryTimer.clear()
			self.recover = False
			if self.pointS >= self.scaleC:
				k = 1.0
			elif self.pointS > self.minS:
				k = self.pointS / self.scaleC
			else:
				k = 0.0
		
		# if the cursor is very far (>2m) the CD ratio needs to be even smaller
		# we elevate k to the power of 1 if distance is 2m, power of 2 if distance is 4m...
		if distance_to_cursor > 2000.0:
			k = math.pow(k, distance_to_cursor / 2000.0)
	
		if k != 0:
			self.CDRatio = 1.0/k
		
		# the cd ratio also depends on the distance of the input device to
		# the cursor, up to 1 meter distant
		if distance_to_cursor > 1000.0:
			distance_to_cursor = 1000.0
		# convert to meters
		distance_to_cursor /= 1000.0
		
		# this makes the cd ratio smaller as the cursor and input device
		# are closer together - at 1 meter, there is no change from the 
		# calculated CD ratio; at 5 meters, the CD ratio is 5x higher,
		# at 0m the CD ratio is 
		self.CDRatio *= distance_to_cursor
		if self.CDRatio < 1.0:
			self.CDRatio = 1.0
			
		distance = (curr_point - prev_point) / self.CDRatio;
		
		# recover the point position, so it catches absolute when speed is
		# faster than maxS (above)
		# done according to PRISM
		if self.recover and self.CDRatio == 1:
			# first, let's determine the offset of the point position to the
			# point position - based on the last frame
			self.pointOffset = prev_point - previous_calculated_point

			# get the current time from the start of recovery
			curTime = self.recoveryTimer.elapsed()

			# if we are in the first 0.5s, we reduce the pointOffset by 20%
			# multiply by distance_to_cursor to make recovery faster when the user is 
			# near the cursor
			# we add the distance which is the absolute displacement from the previous 
			# frame
			#if curTime < .05: 
			if curTime < .5: 
				#self.pointOffset = self.pointOffset * .99 + distance # this doesn't make sense... it will take 2 frames to recover this way, since you're recovering 99% of the difference in one frame
				self.pointOffset = self.pointOffset * .8
			# if it's past 0.5s but before 1s, we reduce the pointOffset by 50%
			#elif curTime < .1:
			elif curTime < 1:
				#self.pointOffset = self.pointOffset * .9 + distance
				self.pointOffset = self.pointOffset * .5
			# after 1s we recovered, so bring the pointOffset to 0 and reset the flag
			else:
				self.pointOffset = distance
				self.recover = False
				self.recoveryTimer.stop()
				self.recoveryTimer.clear()

			# If overshoot, don't move the cursor in the 
			# direction of the over shooting
			RelToAbs = curr_point - previous_calculated_point
			AbsToPrev = curr_point - prev_point
			if RelToAbs.x * AbsToPrev.x < 0:
				# means they have opposite direction,
				# we don't move in x
				self.pointOffset.x = 0

			if RelToAbs.y * AbsToPrev.y < 0:
				# means they have opposite direction,
				# we don't move in y
				self.pointOffset.y = 0;
		else:
			self.pointOffset = distance

		'''
		print "DyCoDiR Info:"
		print "  Previous cursor:",prev_point
		print "  Current cursor: ",curr_point
		print "  Previous calc:  ",previous_calculated_point
		print "  Distance cursor:",distance_to_cursor
		print "  px Speed:       ",self.pointS
		print "  CD Ratio:       ",self.CDRatio
		print "  Recovering?     ",self.recover, self.recoveryTimer.elapsed()
		print "  New calc:       ",previous_calculated_point + self.pointOffset
		print "  New offset:     ",self.pointOffset
		'''
		
		# update userdata variable
		if self.CDRatio == 1.0:
			self.userdata += self.timer.elapsed()-prevElapsed
		
		# now, we return the previous calculated point adding the new offset
		return previous_calculated_point + self.pointOffset

	
	
	# selectButtonPressed()
	# callback for the selection button
	def selectButtonPressed(self):
		#print 'select pressed'
		if len(self.intersectingObjects) > 0:
			self.selectedObject = self.intersectingObjects[0]
		
	# selectButtonReleased()
	# callback for the selection button
	def selectButtonReleased(self):
		#print 'select released'
		pass
	
	def clean(self):
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
	
	def reset(self):
		self.calculatedPoint = Vector3(self.cursorPosition[0],self.cursorPosition[1],0)
		self.previousCalculatedPoint = self.calculatedPoint
		
		self.timer = Timer()
		self.recoveryTimer = Timer()
		self.elapsedSampling = 0.0
		self.pointBuffer = []
		self.elapsedBuffer = []
		self.pointS = 0.0
		self.recover = False
		self.pointOffset = Vector3()
		self.CDRatio = 1
		self.userdata = 0.0
		
		self.crosshair.visible(viz.OFF)
		self.scSphere.visible(viz.OFF)
	