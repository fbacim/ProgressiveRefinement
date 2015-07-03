import viz
import math
import os, sys
import vizshape
import random
import time
import copy

class SelectionMode:
	NO_TRACKING = 0
	WITH_TRACKING = 1
	
class Move:
	NONE=0
	RIGHT=1
	LEFT=2
	FORWARD=3
	BACK=4
	UP=5
	DOWN=6
	
class Rotate:
	NONE=0
	CW=1
	CCW=2
	
class Navigation:
	class DDR:
		strafe = Move.NONE
		walk = Move.NONE
	class BB:
		strafe = Move.NONE
		walk = Move.NONE
	fly = Move.NONE
	yaw = Rotate.NONE
	pitch = Rotate.NONE
	roll = Rotate.NONE
	TRANSLATION_SPEED = 10
	ROTATION_SPEED = 30
	rotation_speed = ROTATION_SPEED
	translation_speed = TRANSLATION_SPEED
	walk_speed = TRANSLATION_SPEED
	strafe_speed = TRANSLATION_SPEED
	half_speed = False
	TOTAL_ANIMATION_TIME = 0.25

class InteractionMode:
	SELECTION_TRIGGER = 0
	SELECTION = 1
	SELECTION_QUADRANTS = 2

class Study:
	class InteractionTechnique:
		DiscreteZoom = 0
		ContinuousZoom = 1
		Raycasting = 2
		size = 3
	class TargetSize:
		Small = 0
		Medium = 1
		Large = 2
		size = 3
	class Mode:
		Training_Free = 0
		Training = 1
		Experiment = 2
		size = 3
		
	technique = None
	target = None
	mode = None
	
	TARGET_SIZE = 0
	OBJ_IN_SPHERE = 0
	MAX_CIRCLES = 0
	
class Trial:
	technique = None
	target = None
	mode = None
	myTarget = -1
	original = 0
	tryCount = 0
	maxZoom = -1
	id = None
	
class CircularObject:
	class Size:
		#radius
		#SMALL  = 0.01  #0.531743557deg
		SMALL  = 0.01  #sqrt(((pow(0.04,2)*pi)/16)/pi)=sqrt(0.0001)=0.01 => LOL
		#MEDIUM = 0.015 #0.797608179deg
		MEDIUM = 0.02 #sqrt(((pow(0.04,2)*pi)/4)/pi)=sqrt(0.0004)=0.02
		LARGE  = 0.04  #2.12674528deg
	
	class Quantity:
		HIGH   = 80
		MEDIUM = 40
		LOW    = 20
		
	class InSphere:
		HIGH   = 256
		MEDIUM = 64
		LOW    = 16

class Globals:
	class Application:
		EVALUATION = 0
		CROWDSIMULATION = 1
		SUPERMARKET = 2
	
	#application = Application.EVALUATION
	#application = Application.CROWDSIMULATION
	application = Application.SUPERMARKET
	
	technique = Study.InteractionTechnique.ContinuousZoom
	#technique = Study.InteractionTechnique.DiscreteZoom
	
	ONE_PX_IN_M          = 0.00238125
	ONE_PX_IN_DEG        = 0.000080645
	SCREEN_SPHERE_RADIUS = 2.155
	
	#what's the meaning of these radii?
	#1 is bigger than the screen, so it's not normalized, neither absolute
	#absolute should be 10ft = 3.048m -> 3.048/2 = 1.524 -> diameter of the screen
	TINY_SPHERE_RADIUS   = ONE_PX_IN_M/4.0
	NORMAL_SPHERE_RADIUS = 0.6465
	
	USE_FILTERING = True
	USE_DISTRACTORS = False
	
	TRIGGER_SIZE = 0.1
	
#-------------------------------------------------------------------------------
# Vector 3D class in support of low pass filter
#-------------------------------------------------------------------------------
class Vector3:
	x = 0
	y = 0
	z = 0
	
	def __init__(self, xx = None, yy = None, zz = None):
		if xx != None and yy == None and zz == None:
			#xx is a vector, we create a new vector passing
			#xx values as arguments
			self.x = xx.x
			self.y = xx.y
			self.z = xx.z
		elif xx != None and yy != None and zz != None:
			self.x = xx
			self.y = yy
			self.z = zz
		else:
			print "Vector Creation Error!"
			viz.quit()
	
	def __add__(self, vec):
		return Vector3(self.x + vec.x, self.y + vec.y, self.z + vec.z)
		
	def __sub__(self, vec):
		return Vector3(self.x - vec.x, self.y - vec.y, self.z - vec.z)
		
	def __mul__(self, val):
		return Vector3(self.x * val, self.y * val, self.z * val)
		
	def __div__(self, val):
		return Vector3(self.x / val, self.y / val, self.z / val)
		
	def abs (self):
		return Vector3(math.fabs(self.x),math.fabs(self.y), math.fabs(self.z))
		
def max (u, f):
	vec = Vector3
	if u.x > f:
		vec.x = u.x
	else:
		vec.x = f

	if u.y > f:
		vec.y = u.y
	else:
		vec.y = f

	if u.z > f:
		vec.z = u.z
	else:
		vec.z = f
	
	return vec
	
def min (u, f):
	vec = Vector3
	
	if u.x < f:
		vec.x = u.x
	else:
		vec.x = f

	if u.y < f:
		vec.y = u.y
	else:
		vec.y = f

	if u.z < f:
		vec.z = u.z
	else:
		vec.z = f
	
	return vec

#-------------------------------------------------------------------------------
# Low pass filter, used with low pass dynamic filter
#-------------------------------------------------------------------------------
class LowPassFilter:
	mFirstTime = False
	mPrevValue = Vector3
	mCutoffFrequency = 0
	mTau = 0

	def __init__(self, cutoff):
		self.mFirstTime = True
		self.mCutoffFrequency = cutoff
		#print "INIT CUTTOF: ", cutoff

	def SetCutoffFrequency(self,f): 
		self.mCutoffFrequency = f
		self.mTau = float(1.0 / (6.2831853 * self.mCutoffFrequency))	# a time constant calculated from the cut-off frequency

	def Apply(self, newValue, frequency):
		#print "freq", frequency
		'''
		  Let's say Pnf the filtered position, Pn the non filtered position and Pn-1f the previous filtered position, 
		  Te the sampling period (in second) and tau a time constant calculated from the cut-off frequency fc.

		  tau = 1 / (2 * pi * fc)
		  Pnf = ( Pn + tau/Te * Pn-1f ) * 1/(1+ tau/Te)
		 
		  Attention: tau >= 10 * Te
		'''

		if self.mFirstTime:
			self.mPrevValue = Vector3(newValue)
			self.mFirstTime = False
		

		#	float frequency = *mFrequency

		Te = float(1.0 / float(frequency))		# the sampling period (in seconds)

		filteredValue = (newValue + self.mPrevValue * (self.mTau/Te)) * (1.0 / (1.0 + self.mTau/Te))

		# filter position and velocity at the same 
		#	Vecteur3D filteredValue = ((newValue - PositionPrev) * (1.0/Te) +  mPrevValue * (Tau/Te) ) * (1.0 / (1.0 + Tau / Te))
		self.mPrevValue = Vector3(filteredValue)
		#	PositionPrev = Position
		#	if (fabs(Velocity.x) < SpeedDeadband) newValue.x = 0.0
		#	if (fabs(Velocity.y) < SpeedDeadband) newValue.y = 0.0
		#	if (fabs(Velocity.z) < speedDeadband) Velocity.z = 0.0
		return filteredValue
		#}

	def Clear(self):
		self.mFirstTime = True

#-------------------------------------------------------------------------------
#Low pass dynamic filter, used to smooth the cursor.
#-------------------------------------------------------------------------------
class LowPassDynamicFilter(LowPassFilter):
	mVelocityFilter = None
	mLastPositionForVelocity = 0.0
	mCutoffFrequencyHigh = 0.0
	mVelocityLow = 0.0
	mVelocityHigh = 0.0
	
	def __init__(self,cutoffLow=0, cutoffHigh=0, velocityLow=0, velocityHigh=0):
		#print "VelHigh",self.velocityHigh
		#print "VelLow",self.mVelocityLow
		self.mVelocityFilter = LowPassFilter(cutoffLow)
		LowPassFilter.mFirstTime = True
		LowPassFilter.mCutoffFrequency = cutoffLow
		self.mCutoffFrequencyHigh = cutoffHigh 
		self.mVelocityLow = velocityLow
		self.mVelocityHigh = velocityHigh 
		self.SetCutoffFrequencyVelocity()
		

	def SetCutoffFrequencyVelocity(self) :
		#print "chamada" ,float(LowPassFilter.mCutoffFrequency  + 0.75 * (self.mCutoffFrequencyHigh - LowPassFilter.mCutoffFrequency))
		self.mVelocityFilter.SetCutoffFrequency(float(LowPassFilter.mCutoffFrequency  + 0.75 * (self.mCutoffFrequencyHigh - LowPassFilter.mCutoffFrequency)))

	def Apply(self, NewValue, frequency):
		#print "freq ",frequency
		#std::cout << "updt: " << std::endl
		# special case if first time being used
		if LowPassFilter.mFirstTime:
			LowPassFilter.mPrevValue = Vector3(NewValue)
			self.mLastPositionForVelocity = Vector3(NewValue)
			LowPassFilter.mFirstTime = False
		

		#float updateFrequency = *mFrequency

		# first get an estimate of velocity (with filter)
		self.mPositionForVelocity = self.mVelocityFilter.Apply(NewValue, frequency)
		vel = (self.mPositionForVelocity - self.mLastPositionForVelocity) * frequency
		self.mLastPositionForVelocity = Vector3(self.mPositionForVelocity)
		vel = vel.abs()
		
		#print "%.4f    "%(vel.x),

		# interpolate between frequencies depending on velocity
		t = (vel - Vector3(self.mVelocityLow, self.mVelocityLow, self.mVelocityLow)) / (self.mVelocityHigh - self.mVelocityLow)

		t = max(t, 0.0)
		t = min(t, 1.0)

		cutoff = (Vector3(t.x,t.y,t.z) * self.mCutoffFrequencyHigh) + ((Vector3(1,1,1) - Vector3(t.x,t.y,t.z)) * LowPassFilter.mCutoffFrequency)

		#print "%.4f    "%(cutoff.x),


		Te = Vector3(1.0 / frequency, 1.0 / frequency, 1.0 / frequency)		# the sampling period (in seconds)
		Tau = Vector3(1.0 / (6.2831853 * cutoff.x), 1.0 / (6.2831853 * cutoff.y), 1.0 / (6.2831853 * cutoff.z))	# a time constant calculated from the cut-off frequency

		filteredValue = Vector3
		filteredValue.x = (NewValue.x + (Tau.x / Te.x) * self.mPrevValue.x) * (1.0 / (1.0 + Tau.x / Te.x))
		filteredValue.y = (NewValue.y + (Tau.y / Te.y) * self.mPrevValue.y) * (1.0 / (1.0 + Tau.y / Te.y))
		filteredValue.z = (NewValue.z + (Tau.z / Te.z) * self.mPrevValue.z) * (1.0 / (1.0 + Tau.z / Te.z))

		LowPassFilter.mPrevValue = Vector3(filteredValue)

		# 	cout << cutoff.x << " " << cutoff.y << " " << cutoff.z << "    " <<
		# 			NewValue.x << " " << NewValue.y << " " << NewValue.z << "    " <<
		# 			filteredValue.x << " " << filteredValue.y << " " << filteredValue.z <<
		# 			endl

		return filteredValue

## supermarket
def getModels():
	supermarket.getChild('Box01')
	supermarket.getChild('Box02')
	supermarket.getChild('Box04')
	supermarket.getChild('Box08')
	supermarket.getChild('Arch_44__039_19')
	supermarket.getChild('Arch_44__039_189')
	supermarket.getChild('Arch_44__25805521')
	supermarket.getChild('Arch_44__039_244')
	supermarket.getChild('Arch_44__727323946')
	supermarket.getChild('Arch_44__039_274')
	supermarket.getChild('Arch_44__808345238')
	supermarket.getChild('Arch_44__039_300')
	supermarket.getChild('Arch_44__015_5')
	supermarket.getChild('Arch_44__015_7')
	supermarket.getChild('Arch_44__938314247')
	supermarket.getChild('Arch_44__015_36')
	supermarket.getChild('Arch_44__015_37')
	supermarket.getChild('Arch_44__863027884')
	supermarket.getChild('Arch_44__015_63')
	supermarket.getChild('Arch_44__015_64')
	supermarket.getChild('Arch_44__922551095')
	supermarket.getChild('Arch_44__015_78')
	supermarket.getChild('Arch_44__015_203')
	supermarket.getChild('Arch_44__79656110')
	supermarket.getChild('Arch_44__015_250')
	supermarket.getChild('Arch_44__015_395')
	supermarket.getChild('Arch_44__124941062')
	supermarket.getChild('Arch_44__015_407')
	supermarket.getChild('Arch_44__91305578')
	supermarket.getChild('Arch_44__015_537')
	supermarket.getChild('Arch_44__015_629')
	supermarket.getChild('Arch_44__015_661')
	supermarket.getChild('Arch_44__113478')
	supermarket.getChild('Arch_44__015_677')
	supermarket.getChild('Box42')
	supermarket.getChild('Arch_44__015_691')
	supermarket.getChild('Arch_44__015_692')
	supermarket.getChild('Arch_44__015_693')
	supermarket.getChild('Arch_44__015_694')
	supermarket.getChild('Arch_44__015_695')
	supermarket.getChild('Arch_44__015_696')
	supermarket.getChild('Arch_44__015_697')
	supermarket.getChild('Arch_44__015_698')
	supermarket.getChild('Arch_44__015_699')
	supermarket.getChild('Arch_44__015_700')
	supermarket.getChild('Arch_44__015_701')
	supermarket.getChild('Arch_44__015_702')
	supermarket.getChild('Arch_44__015_703')
	supermarket.getChild('Arch_44__015_704')
	supermarket.getChild('Arch_44__015_705')
	supermarket.getChild('Arch_44__015_706')
	supermarket.getChild('Arch_44__015_707')
	supermarket.getChild('Arch_44__015_708')
	supermarket.getChild('Arch_44__015_709')
	supermarket.getChild('Arch_44__015_710')
	supermarket.getChild('Arch_44__015_711')
	supermarket.getChild('Arch_44__015_712')
	supermarket.getChild('Arch_44__015_713')
	supermarket.getChild('Arch_44__015_714')
	supermarket.getChild('Arch_44__015_731')
	supermarket.getChild('Arch_44__015_732')
	supermarket.getChild('Arch_44__015_733')
	supermarket.getChild('Arch_44__015_744')
	supermarket.getChild('Arch_44__015_745')
	supermarket.getChild('Arch_44__015_747')
	supermarket.getChild('Arch_44__015_748')
	supermarket.getChild('Arch_44__015_750')
	supermarket.getChild('Arch_44__015_751')
	supermarket.getChild('Arch_44__015_752')
	supermarket.getChild('Arch_44__015_753')
	supermarket.getChild('Arch_44__015_755')
	supermarket.getChild('Arch_44__015_756')
	supermarket.getChild('Arch_44__015_757')
	supermarket.getChild('Arch_44__015_759')
	supermarket.getChild('Arch_44__015_760')
	supermarket.getChild('Arch_44__015_762')
	supermarket.getChild('Arch_44__015_763')
	supermarket.getChild('Arch_44__015_765')
	supermarket.getChild('Arch_44__015_767')
	supermarket.getChild('Arch_44__015_768')
	supermarket.getChild('Arch_44__015_783')
	supermarket.getChild('Arch_44__015_785')
	supermarket.getChild('Arch_44__015_786')
	supermarket.getChild('Arch_44__015_787')
	supermarket.getChild('Arch_44__015_788')
	supermarket.getChild('Arch_44__015_789')
	supermarket.getChild('Arch_44__015_790')
	supermarket.getChild('Arch_44__015_791')
	supermarket.getChild('Arch_44__015_792')
	supermarket.getChild('Arch_44__015_793')
	supermarket.getChild('Arch_44__015_794')
	supermarket.getChild('Arch_44__015_795')
	supermarket.getChild('Arch_44__015_796')
	supermarket.getChild('Arch_44__015_797')
	supermarket.getChild('Arch_44__015_798')
	supermarket.getChild('Arch_44__015_799')
	supermarket.getChild('Arch_44__015_800')
	supermarket.getChild('Arch_44__015_801')
	supermarket.getChild('Arch_44__015_802')
	supermarket.getChild('Arch_44__015_803')
	supermarket.getChild('Arch_44__015_804')
	supermarket.getChild('Arch_44__015_805')
	supermarket.getChild('Arch_44__015_812')
	supermarket.getChild('Arch_44__015_813')
	supermarket.getChild('Arch_44__015_814')
	supermarket.getChild('Arch_44__015_815')
	supermarket.getChild('Arch_44__015_816')
	supermarket.getChild('Arch_44__015_817')
	supermarket.getChild('Arch_44__015_818')
	supermarket.getChild('Arch_44__015_819')
	supermarket.getChild('Arch_44__015_820')
	supermarket.getChild('Arch_44__015_821')
	supermarket.getChild('Arch_44__015_822')
	supermarket.getChild('Arch_44__015_823')
	supermarket.getChild('Arch_44__015_824')
	supermarket.getChild('Arch_44__015_825')
	supermarket.getChild('Arch_44__015_826')
	supermarket.getChild('Arch_44__015_827')
	supermarket.getChild('Arch_44__015_828')
	supermarket.getChild('Arch_44__015_829')
	supermarket.getChild('Arch_44__015_830')
	supermarket.getChild('Arch_44__015_831')
	supermarket.getChild('Arch_44__015_832')
	supermarket.getChild('Arch_44__015_833')
	supermarket.getChild('Arch_44__015_834')
	supermarket.getChild('Arch_44__015_835')
	supermarket.getChild('Arch_44__015_836')
	supermarket.getChild('Arch_44__015_837')
	supermarket.getChild('Arch_44__015_838')
	supermarket.getChild('Arch_44__015_839')
	supermarket.getChild('Arch_44__015_840')
	supermarket.getChild('Arch_44__015_841')
	supermarket.getChild('Arch_44__015_842')
	supermarket.getChild('Arch_44__015_843')
	supermarket.getChild('Arch_44__015_844')
	supermarket.getChild('Arch_44__015_845')
	supermarket.getChild('Arch_44__015_846')
	supermarket.getChild('Arch_44__015_847')
	supermarket.getChild('Arch_44__015_848')
	supermarket.getChild('Arch_44__015_849')
	supermarket.getChild('Arch_44__015_850')
	supermarket.getChild('Arch_44__015_851')
	supermarket.getChild('Arch_44__015_852')
	supermarket.getChild('Arch_44__015_853')
	supermarket.getChild('Arch_44__015_854')
	supermarket.getChild('Arch_44__015_855')
	supermarket.getChild('Arch_44__015_856')
	supermarket.getChild('Arch_44__015_857')
	supermarket.getChild('Arch_44__015_858')
	supermarket.getChild('Arch_44__015_859')
	supermarket.getChild('Arch_44__015_860')
	supermarket.getChild('Arch_44__015_861')
	supermarket.getChild('Arch_44__015_862')
	supermarket.getChild('Arch_44__015_865')
	supermarket.getChild('Arch_44__015_866')
	supermarket.getChild('Arch_44__015_867')
	supermarket.getChild('Arch_44__015_868')
	supermarket.getChild('Arch_44__015_870')
	supermarket.getChild('Arch_44__015_871')
	supermarket.getChild('Arch_44__015_872')
	supermarket.getChild('Arch_44__015_873')
	supermarket.getChild('Arch_44__015_874')
	supermarket.getChild('Arch_44__015_875')
	supermarket.getChild('Arch_44__015_876')
	supermarket.getChild('Arch_44__015_878')
	supermarket.getChild('Arch_44__015_879')
	supermarket.getChild('Arch_44__015_880')
	supermarket.getChild('Arch_44__015_881')
	supermarket.getChild('Arch_44__015_882')
	supermarket.getChild('Arch_44__015_883')
	supermarket.getChild('Arch_44__015_884')
	supermarket.getChild('Arch_44__015_885')
	supermarket.getChild('Arch_44__015_886')
	supermarket.getChild('Arch_44__015_887')
	supermarket.getChild('Arch_44__015_888')
	supermarket.getChild('Arch_44__015_889')
	supermarket.getChild('Arch_44__015_890')
	supermarket.getChild('Arch_44__015_891')
	supermarket.getChild('Arch_44__015_892')
	supermarket.getChild('Arch_44__015_893')
	supermarket.getChild('Arch_44__015_894')
	supermarket.getChild('Arch_44__015_895')
	supermarket.getChild('Arch_44__015_896')
	supermarket.getChild('Arch_44__015_897')
	supermarket.getChild('Arch_44__015_898')
	supermarket.getChild('Arch_44__015_899')
	supermarket.getChild('Arch_44__015_900')
	supermarket.getChild('Arch_44__015_901')
	supermarket.getChild('Arch_44__015_902')
	supermarket.getChild('Arch_44__015_903')
	supermarket.getChild('Arch_44__015_904')
	supermarket.getChild('Arch_44__015_905')
	supermarket.getChild('Arch_44__015_906')
	supermarket.getChild('Arch_44__015_907')
	supermarket.getChild('Arch_44__015_908')
	supermarket.getChild('Arch_44__015_909')
	supermarket.getChild('Arch_44__015_910')
	supermarket.getChild('Arch_44__015_911')
	supermarket.getChild('Arch_44__015_912')
	supermarket.getChild('Arch_44__015_913')
	supermarket.getChild('Arch_44__015_914')
	supermarket.getChild('Arch_44__015_915')
	supermarket.getChild('Arch_44__015_943')
	supermarket.getChild('Arch_44__015_944')
	supermarket.getChild('Arch_44__015_945')
	supermarket.getChild('Arch_44__015_946')
	supermarket.getChild('Arch_44__015_947')
	supermarket.getChild('Arch_44__015_948')
	supermarket.getChild('Arch_44__015_949')
	supermarket.getChild('Arch_44__015_950')
	supermarket.getChild('Arch_44__015_951')
	supermarket.getChild('Arch_44__015_952')
	supermarket.getChild('Arch_44__015_953')
	supermarket.getChild('Arch_44__015_954')
	supermarket.getChild('Arch_44__015_955')
	supermarket.getChild('Arch_44__015_956')
	supermarket.getChild('Arch_44__015_957')
	supermarket.getChild('Arch_44__015_958')
	supermarket.getChild('Arch_44__015_959')
	supermarket.getChild('Arch_44__015_960')
	supermarket.getChild('Arch_44__015_961')
	supermarket.getChild('Arch_44__015_962')
	supermarket.getChild('Arch_44__015_963')
	supermarket.getChild('Arch_44__015_964')
	supermarket.getChild('Arch_44__015_965')
	supermarket.getChild('Arch_44__015_966')
	supermarket.getChild('Arch_44__015_967')
	supermarket.getChild('Arch_44__015_968')
	supermarket.getChild('Arch_44__015_969')
	supermarket.getChild('Arch_44__015_970')
	supermarket.getChild('Arch_44__015_971')
	supermarket.getChild('Arch_44__015_972')
	supermarket.getChild('Arch_44__015_973')
	supermarket.getChild('Arch_44__015_974')
	supermarket.getChild('Arch_44__015_975')
	supermarket.getChild('Arch_44__015_976')
	supermarket.getChild('Arch_44__015_977')
	supermarket.getChild('Arch_44__015_978')
	supermarket.getChild('Arch_44__015_979')
	supermarket.getChild('Arch_44__015_980')
	supermarket.getChild('Arch_44__015_981')
	supermarket.getChild('Arch_44__015_982')
	supermarket.getChild('Arch_44__015_983')
	supermarket.getChild('Arch_44__015_984')
	supermarket.getChild('Arch_44__015_985')
	supermarket.getChild('Arch_44__015_986')
	supermarket.getChild('Arch_44__015_987')
	supermarket.getChild('Arch_44__015_988')
	supermarket.getChild('Arch_44__015_989')
	supermarket.getChild('Arch_44__015_990')
	supermarket.getChild('Arch_44__015_991')
	supermarket.getChild('Arch_44__015_992')
	supermarket.getChild('Arch_44__015_993')
	supermarket.getChild('Arch_44__015_994')
	supermarket.getChild('Arch_44__015_995')
	supermarket.getChild('Arch_44__015_996')
	supermarket.getChild('Arch_44__015_997')
	supermarket.getChild('Arch_44__015_998')
	supermarket.getChild('Arch_44__015_999')
	supermarket.getChild('Arch_44__015_1000')
	supermarket.getChild('Arch_44__015_1001')
	supermarket.getChild('Arch_44__015_1002')
	supermarket.getChild('Arch_44__015_1003')
	supermarket.getChild('Arch_44__015_1004')
	supermarket.getChild('Arch_44__015_1005')
	supermarket.getChild('Arch_44__015_1006')
	supermarket.getChild('Arch_44__015_1007')
	supermarket.getChild('Arch_44__015_1008')
	supermarket.getChild('Arch_44__015_1009')
	supermarket.getChild('Arch_44__015_1010')
	supermarket.getChild('Arch_44__015_1011')
	supermarket.getChild('Arch_44__015_1012')
	supermarket.getChild('Arch_44__015_1013')
	supermarket.getChild('Arch_44__015_1014')
	supermarket.getChild('Arch_44__015_1015')
	supermarket.getChild('Arch_44__015_1016')
	supermarket.getChild('Arch_44__015_1017')
	supermarket.getChild('Arch_44__015_1018')
	supermarket.getChild('Arch_44__015_1019')
	supermarket.getChild('Arch_44__015_1020')
	supermarket.getChild('Arch_44__015_1021')
	supermarket.getChild('Arch_44__015_1022')
	supermarket.getChild('Arch_44__015_1023')
	supermarket.getChild('Arch_44__015_1024')
	supermarket.getChild('Arch_44__015_1025')
	supermarket.getChild('Arch_44__015_1026')
	supermarket.getChild('Arch_44__015_1027')
	supermarket.getChild('Arch_44__015_1028')
	supermarket.getChild('Arch_44__015_1029')
	supermarket.getChild('Arch_44__015_1030')
	supermarket.getChild('Arch_44__015_1031')
	supermarket.getChild('Arch_44__015_1032')
	supermarket.getChild('Arch_44__015_1033')
	supermarket.getChild('Arch_44__015_1034')
	supermarket.getChild('Arch_44__015_1035')
	supermarket.getChild('Arch_44__015_1036')
	supermarket.getChild('Arch_44__015_1037')
	supermarket.getChild('Arch_44__015_1038')
	supermarket.getChild('Arch_44__015_1039')
	supermarket.getChild('Arch_44__015_1040')
	supermarket.getChild('Arch_44__015_1041')
	supermarket.getChild('Arch_44__015_1042')
	supermarket.getChild('Arch_44__015_1043')
	supermarket.getChild('Arch_44__015_1044')
	supermarket.getChild('Arch_44__015_1045')
	supermarket.getChild('Arch_44__015_1046')
	supermarket.getChild('Arch_44__015_1047')
	supermarket.getChild('Arch_44__015_1048')
	supermarket.getChild('Arch_44__015_1049')
	supermarket.getChild('Arch_44__015_1050')
	supermarket.getChild('Arch_44__015_1051')
	supermarket.getChild('Arch_44__015_1052')
	supermarket.getChild('Arch_44__015_1053')
	supermarket.getChild('Arch_44__015_1054')
	supermarket.getChild('Arch_44__015_1055')
	supermarket.getChild('Arch_44__015_1056')
	supermarket.getChild('Arch_44__015_1057')
	supermarket.getChild('Arch_44__015_1058')
	supermarket.getChild('Arch_44__015_1059')
	supermarket.getChild('Arch_44__015_1060')
	supermarket.getChild('Arch_44__015_1061')
	supermarket.getChild('Arch_44__015_1062')
	supermarket.getChild('Arch_44__015_1064')
	supermarket.getChild('Arch_44__015_1065')
	supermarket.getChild('Arch_44__015_1066')
	supermarket.getChild('Arch_44__015_1068')
	supermarket.getChild('Arch_44__015_1069')
	supermarket.getChild('Arch_44__015_1070')
	supermarket.getChild('Arch_44__015_1072')
	supermarket.getChild('Arch_44__015_1073')
	supermarket.getChild('Arch_44__015_1074')
	supermarket.getChild('Arch_44__015_1076')
	supermarket.getChild('Arch_44__015_1077')
	supermarket.getChild('Arch_44__015_1078')
	supermarket.getChild('Arch_44__015_1079')
	supermarket.getChild('Arch_44__015_1080')
	supermarket.getChild('Arch_44__015_1081')
	supermarket.getChild('Arch_44__015_1082')
	supermarket.getChild('Arch_44__015_1083')
	supermarket.getChild('Arch_44__015_1084')
	supermarket.getChild('Arch_44__015_1085')
	supermarket.getChild('Arch_44__015_1086')
	supermarket.getChild('Arch_44__015_1087')
	supermarket.getChild('Arch_44__015_1088')
	supermarket.getChild('Arch_44__015_1089')
	supermarket.getChild('Arch_44__015_1090')
	supermarket.getChild('Arch_44__015_1091')
	supermarket.getChild('Arch_44__015_1092')
	supermarket.getChild('Arch_44__015_1110')
	supermarket.getChild('Arch_44__015_1111')
	supermarket.getChild('Arch_44__015_1112')
	supermarket.getChild('Arch_44__015_1113')
	supermarket.getChild('Arch_44__015_1114')
	supermarket.getChild('Arch_44__015_1115')
	supermarket.getChild('Arch_44__015_1116')
	supermarket.getChild('Arch_44__015_1117')
	supermarket.getChild('Arch_44__015_1118')
	supermarket.getChild('Arch_44__015_1119')
	supermarket.getChild('Arch_44__015_1120')
	supermarket.getChild('Arch_44__015_1121')
	supermarket.getChild('Arch_44__015_1122')
	supermarket.getChild('Arch_44__015_1123')
	supermarket.getChild('Arch_44__015_1124')
	supermarket.getChild('Arch_44__015_1125')
	supermarket.getChild('Arch_44__015_1126')
	supermarket.getChild('Arch_44__015_1127')
	supermarket.getChild('Arch_44__015_1128')
	supermarket.getChild('Arch_44__015_1129')
	supermarket.getChild('Arch_44__015_1130')
	supermarket.getChild('Box43')
	supermarket.getChild('Box44')
	supermarket.getChild('Box45')
	supermarket.getChild('Arch_44__040_137')
	supermarket.getChild('Arch_44__530026195')
	supermarket.getChild('Arch_44__040_157')
	supermarket.getChild('Arch_44__166257883')
	supermarket.getChild('Arch_44__030_61')
	supermarket.getChild('Arch_44__625738632')
	supermarket.getChild('Arch_44__030_71')
	supermarket.getChild('Arch_44__030_96')
	supermarket.getChild('Arch_44__132954645')
	supermarket.getChild('Arch_44__030_97')
	supermarket.getChild('Arch_44__030_98')
	supermarket.getChild('Arch_44__030_102')
	supermarket.getChild('Arch_44__030_103')
	supermarket.getChild('Arch_44__030_107')
	supermarket.getChild('Arch_44__030_111')
	supermarket.getChild('Arch_44__030_112')
	supermarket.getChild('Arch_44__030_116')
	supermarket.getChild('Arch_44__030_117')
	supermarket.getChild('Arch_44__030_121')
	supermarket.getChild('Arch_44__030_122')
	supermarket.getChild('Arch_44__030_126')
	supermarket.getChild('Arch_44__030_130')
	supermarket.getChild('Arch_44__030_131')
	supermarket.getChild('Arch_44__030_132')
	supermarket.getChild('Arch_44__030_136')
	supermarket.getChild('Arch_44__030_137')
	supermarket.getChild('Arch_44__030_138')
	supermarket.getChild('Arch_44__030_142')
	supermarket.getChild('Arch_44__030_146')
	supermarket.getChild('Arch_44__030_147')
	supermarket.getChild('Arch_44__030_151')
	supermarket.getChild('Arch_44__030_152')
	supermarket.getChild('Arch_44__030_153')
	supermarket.getChild('Arch_44__030_156')
	supermarket.getChild('Arch_44__030_161')
	supermarket.getChild('Arch_44__030_162')
	supermarket.getChild('Arch_44__030_166')
	supermarket.getChild('Arch_44__030_167')
	supermarket.getChild('Arch_44__030_168')
	supermarket.getChild('Arch_44__030_169')
	supermarket.getChild('Arch_44__030_170')
	supermarket.getChild('Arch_44__030_171')
	supermarket.getChild('Arch_44__030_176')
	supermarket.getChild('Arch_44__030_177')
	supermarket.getChild('Arch_44__030_179')
	supermarket.getChild('Arch_44__030_180')
	supermarket.getChild('Arch_44__030_186')
	supermarket.getChild('Arch_44__030_187')
	supermarket.getChild('Arch_44__031_41')
	supermarket.getChild('Arch_44__031_101')
	supermarket.getChild('Arch_44__031_126')
	supermarket.getChild('Arch_44__635485520')
	supermarket.getChild('Arch_44__031_144')
	supermarket.getChild('Arch_44__799395050')
	supermarket.getChild('Arch_44__031_212')
	supermarket.getChild('Arch_44__113505807')
	supermarket.getChild('Arch_44__031_213')
	supermarket.getChild('Arch_44__031_217')
	supermarket.getChild('Arch_44__031_218')
	supermarket.getChild('Arch_44__031_219')
	supermarket.getChild('Arch_44__031_220')
	supermarket.getChild('Arch_44__031_221')
	supermarket.getChild('Arch_44__031_225')
	supermarket.getChild('Arch_44__031_226')
	supermarket.getChild('Arch_44__031_227')
	supermarket.getChild('Arch_44__031_228')
	supermarket.getChild('Arch_44__031_229')
	supermarket.getChild('Arch_44__031_230')
	supermarket.getChild('Arch_44__031_231')
	supermarket.getChild('Arch_44__031_232')
	supermarket.getChild('Arch_44__031_233')
	supermarket.getChild('Arch_44__031_254')
	supermarket.getChild('Arch_44__031_255')
	supermarket.getChild('Arch_44__031_256')
	supermarket.getChild('Arch_44__031_257')
	supermarket.getChild('Arch_44__031_258')
	supermarket.getChild('Arch_44__031_259')
	supermarket.getChild('Arch_44__031_260')
	supermarket.getChild('Arch_44__031_261')
	supermarket.getChild('Arch_44__031_262')
	supermarket.getChild('Arch_44__031_263')
	supermarket.getChild('Arch_44__031_264')
	supermarket.getChild('Arch_44__031_271')
	supermarket.getChild('Arch_44__031_275')
	supermarket.getChild('Arch_44__031_279')
	supermarket.getChild('Arch_44__031_302')
	supermarket.getChild('Arch_44__031_308')
	supermarket.getChild('Arch_44__031_309')
	supermarket.getChild('Arch_44__031_315')
	supermarket.getChild('Arch_44__031_316')
	supermarket.getChild('Arch_44__031_317')
	supermarket.getChild('Arch_44__031_319')
	supermarket.getChild('Arch_44__031_320')
	supermarket.getChild('Arch_44__031_321')
	supermarket.getChild('Arch_44__031_322')
	supermarket.getChild('Arch_44__031_323')
	supermarket.getChild('Arch_44__031_324')
	supermarket.getChild('Arch_44__031_328')
	supermarket.getChild('Arch_44__031_329')
	supermarket.getChild('Arch_44__031_330')
	supermarket.getChild('Arch_44__031_335')
	supermarket.getChild('Arch_44__031_336')
	supermarket.getChild('Arch_44__031_337')
	supermarket.getChild('Arch_44__031_338')
	supermarket.getChild('Arch_44__031_339')
	supermarket.getChild('Arch_44__031_340')
	supermarket.getChild('Arch_44__031_341')
	supermarket.getChild('Arch_44__031_342')
	supermarket.getChild('Arch_44__031_344')
	supermarket.getChild('Arch_44__263998131')
	supermarket.getChild('Arch_44__031_345')
	supermarket.getChild('Arch_44__031_347')
	supermarket.getChild('Arch_44__031_348')
	supermarket.getChild('Arch_44__031_350')
	supermarket.getChild('Arch_44__031_351')
	supermarket.getChild('Arch_44__031_352')
	supermarket.getChild('Arch_44__031_353')
	supermarket.getChild('Arch_44__031_354')
	supermarket.getChild('Arch_44__031_355')
	supermarket.getChild('Arch_44__031_356')
	supermarket.getChild('Arch_44__031_361')
	supermarket.getChild('Arch_44__031_362')
	supermarket.getChild('Arch_44__031_363')
	supermarket.getChild('Arch_44__031_364')
	supermarket.getChild('Arch_44__031_365')
	supermarket.getChild('Arch_44__031_366')
	supermarket.getChild('Arch_44__031_367')
	supermarket.getChild('Arch_44__031_369')
	supermarket.getChild('Arch_44__031_370')
	supermarket.getChild('Arch_44__031_374')
	supermarket.getChild('Arch_44__031_375')
	supermarket.getChild('Arch_44__031_379')
	supermarket.getChild('Arch_44__031_380')
	supermarket.getChild('Arch_44__031_381')
	supermarket.getChild('Arch_44__031_382')
	supermarket.getChild('Arch_44__031_383')
	supermarket.getChild('Arch_44__031_384')
	supermarket.getChild('Arch_44__031_385')
	supermarket.getChild('Arch_44__031_386')
	supermarket.getChild('Arch_44__031_387')
	supermarket.getChild('Arch_44__031_388')
	supermarket.getChild('Arch_44__031_393')
	supermarket.getChild('Arch_44__031_394')
	supermarket.getChild('Arch_44__031_395')
	supermarket.getChild('Arch_44__031_396')
	supermarket.getChild('Arch_44__031_397')
	supermarket.getChild('Arch_44__031_398')
	supermarket.getChild('Arch_44__031_399')
	supermarket.getChild('Arch_44__031_400')
	supermarket.getChild('Arch_44__031_401')
	supermarket.getChild('Arch_44__031_402')
	supermarket.getChild('Arch_44__031_403')
	supermarket.getChild('Arch_44__031_404')
	supermarket.getChild('Arch_44__031_405')
	supermarket.getChild('Arch_44__031_406')
	supermarket.getChild('Arch_44__031_407')
	supermarket.getChild('Arch_44__031_409')
	supermarket.getChild('Arch_44__031_410')
	supermarket.getChild('Arch_44__031_411')
	supermarket.getChild('Arch_44__031_412')
	supermarket.getChild('Arch_44__031_413')
	supermarket.getChild('Arch_44__031_414')
	supermarket.getChild('Arch_44__031_416')
	supermarket.getChild('Arch_44__031_417')
	supermarket.getChild('Arch_44__031_418')
	supermarket.getChild('Arch_44__031_420')
	supermarket.getChild('Arch_44__031_421')
	supermarket.getChild('Arch_44__031_440')
	supermarket.getChild('Arch_44__031_441')
	supermarket.getChild('Arch_44__031_442')
	supermarket.getChild('Arch_44__031_443')
	supermarket.getChild('Arch_44__031_444')
	supermarket.getChild('Arch_44__031_445')
	supermarket.getChild('Arch_44__031_446')
	supermarket.getChild('Arch_44__031_447')
	supermarket.getChild('Arch_44__031_448')
	supermarket.getChild('Arch_44__031_449')
	supermarket.getChild('Arch_44__031_450')
	supermarket.getChild('Arch_44__031_451')
	supermarket.getChild('Arch_44__031_452')
	supermarket.getChild('Arch_44__031_453')
	supermarket.getChild('Arch_44__031_454')
	supermarket.getChild('Arch_44__031_463')
	supermarket.getChild('Arch_44__031_464')
	supermarket.getChild('Arch_44__031_465')
	supermarket.getChild('Arch_44__031_466')
	supermarket.getChild('Arch_44__031_467')
	supermarket.getChild('Arch_44__031_468')
	supermarket.getChild('Arch_44__031_473')
	supermarket.getChild('Arch_44__031_490')
	supermarket.getChild('Arch_44__031_492')
	supermarket.getChild('Arch_44__030_190')
	supermarket.getChild('Arch_44__030_192')
	supermarket.getChild('Arch_44__030_193')
	supermarket.getChild('Arch_44__030_195')
	supermarket.getChild('Arch_44__030_196')
	supermarket.getChild('Arch_44__030_205')
	supermarket.getChild('Arch_44__030_210')
	supermarket.getChild('Arch_44__030_215')
	supermarket.getChild('Arch_44__030_224')
	supermarket.getChild('Arch_44__030_229')
	supermarket.getChild('Arch_44__030_230')
	supermarket.getChild('Arch_44__030_231')
	supermarket.getChild('Arch_44__030_236')
	supermarket.getChild('Arch_44__030_240')
	supermarket.getChild('Arch_44__030_245')
	supermarket.getChild('Arch_44__030_247')
	supermarket.getChild('Arch_44__030_255')
	supermarket.getChild('Arch_44__030_260')
	supermarket.getChild('Arch_44__030_262')
	supermarket.getChild('Arch_44__030_265')
	supermarket.getChild('Arch_44__030_270')
	supermarket.getChild('Arch_44__030_271')
	supermarket.getChild('Arch_44__030_274')
	supermarket.getChild('Arch_44__030_280')
	supermarket.getChild('Arch_44__032_2')
	supermarket.getChild('Arch_44__032_6')
	supermarket.getChild('Arch_44__386208186')
	supermarket.getChild('Arch_44__032_29')
	supermarket.getChild('Arch_44__340351762')
	supermarket.getChild('Arch_44__032_35')
	supermarket.getChild('Arch_44__805313931')
	supermarket.getChild('Arch_44__032_65')
	supermarket.getChild('Arch_44__834896755')
	supermarket.getChild('Arch_44__032_120')
	supermarket.getChild('Arch_44__032_148')
	supermarket.getChild('Arch_44__032_149')
	supermarket.getChild('Arch_44__032_150')
	supermarket.getChild('Arch_44__032_151')
	supermarket.getChild('Arch_44__032_152')
	supermarket.getChild('Arch_44__032_155')
	supermarket.getChild('Arch_44__032_156')
	supermarket.getChild('Arch_44__032_157')
	supermarket.getChild('Arch_44__032_158')
	supermarket.getChild('Arch_44__032_159')
	supermarket.getChild('Arch_44__032_160')
	supermarket.getChild('Arch_44__032_161')
	supermarket.getChild('Arch_44__032_162')
	supermarket.getChild('Arch_44__032_163')
	supermarket.getChild('Arch_44__032_164')
	supermarket.getChild('Arch_44__032_165')
	supermarket.getChild('Arch_44__032_166')
	supermarket.getChild('Arch_44__032_167')
	supermarket.getChild('Arch_44__032_168')
	supermarket.getChild('Arch_44__032_169')
	supermarket.getChild('Arch_44__032_170')
	supermarket.getChild('Arch_44__032_171')
	supermarket.getChild('Arch_44__032_172')
	supermarket.getChild('Arch_44__032_173')
	supermarket.getChild('Arch_44__032_174')
	supermarket.getChild('Arch_44__032_175')
	supermarket.getChild('Arch_44__032_176')
	supermarket.getChild('Arch_44__032_177')
	supermarket.getChild('Arch_44__032_178')
	supermarket.getChild('Arch_44__032_179')
	supermarket.getChild('Arch_44__032_180')
	supermarket.getChild('Arch_44__032_181')
	supermarket.getChild('Arch_44__032_182')
	supermarket.getChild('Arch_44__032_183')
	supermarket.getChild('Arch_44__032_184')
	supermarket.getChild('Arch_44__032_185')
	supermarket.getChild('Arch_44__032_186')
	supermarket.getChild('Arch_44__032_187')
	supermarket.getChild('Arch_44__032_188')
	supermarket.getChild('Arch_44__032_189')
	supermarket.getChild('Arch_44__032_190')
	supermarket.getChild('Arch_44__032_191')
	supermarket.getChild('Arch_44__032_192')
	supermarket.getChild('Arch_44__032_193')
	supermarket.getChild('Arch_44__032_194')
	supermarket.getChild('Arch_44__032_195')
	supermarket.getChild('Arch_44__032_196')
	supermarket.getChild('Arch_44__032_197')
	supermarket.getChild('Arch_44__032_198')
	supermarket.getChild('Arch_44__032_199')
	supermarket.getChild('Arch_44__032_200')
	supermarket.getChild('Arch_44__032_201')
	supermarket.getChild('Arch_44__032_202')
	supermarket.getChild('Arch_44__032_203')
	supermarket.getChild('Arch_44__032_204')
	supermarket.getChild('Arch_44__032_205')
	supermarket.getChild('Arch_44__032_206')
	supermarket.getChild('Arch_44__032_207')
	supermarket.getChild('Arch_44__033_263')
	supermarket.getChild('Arch_44__033_421')
	supermarket.getChild('Arch_44__033_422')
	supermarket.getChild('Arch_44__033_423')
	supermarket.getChild('Arch_44__033_436')
	supermarket.getChild('Arch_44__033_437')
	supermarket.getChild('Arch_44__033_438')
	supermarket.getChild('Arch_44__033_452')
	supermarket.getChild('Arch_44__033_453')
	supermarket.getChild('Arch_44__033_454')
	supermarket.getChild('Arch_44__033_471')
	supermarket.getChild('Arch_44__033_472')
	supermarket.getChild('Arch_44__033_473')
	supermarket.getChild('Arch_44__033_474')
	supermarket.getChild('Arch_44__033_490')
	supermarket.getChild('Arch_44__033_491')
	supermarket.getChild('Arch_44__033_492')
	supermarket.getChild('Arch_44__033_505')
	supermarket.getChild('Arch_44__033_506')
	supermarket.getChild('Arch_44__033_507')
	supermarket.getChild('Arch_44__033_520')
	supermarket.getChild('Arch_44__033_521')
	supermarket.getChild('Arch_44__033_522')
	supermarket.getChild('Arch_44__033_536')
	supermarket.getChild('Arch_44__033_537')
	supermarket.getChild('Arch_44__033_538')
	supermarket.getChild('Arch_44__033_552')
	supermarket.getChild('Arch_44__033_553')
	supermarket.getChild('Arch_44__033_554')
	supermarket.getChild('Arch_44__033_555')
	supermarket.getChild('Arch_44__033_587')
	supermarket.getChild('Arch_44__033_588')
	supermarket.getChild('Arch_44__033_589')
	supermarket.getChild('Arch_44__033_590')
	supermarket.getChild('Arch_44__033_591')
	supermarket.getChild('Arch_44__033_592')
	supermarket.getChild('Arch_44__033_593')
	supermarket.getChild('Arch_44__033_594')
	supermarket.getChild('Arch_44__032_210')
	supermarket.getChild('Arch_44__032_211')
	supermarket.getChild('Arch_44__032_212')
	supermarket.getChild('Arch_44__032_213')
	supermarket.getChild('Arch_44__032_214')
	supermarket.getChild('Arch_44__032_215')
	supermarket.getChild('Arch_44__032_221')
	supermarket.getChild('Arch_44__032_227')
	supermarket.getChild('Arch_44__032_228')
	supermarket.getChild('Arch_44__032_229')
	supermarket.getChild('Arch_44__032_230')
	supermarket.getChild('Arch_44__032_231')
	supermarket.getChild('Arch_44__032_233')
	supermarket.getChild('Arch_44__032_234')
	supermarket.getChild('Arch_44__032_235')
	supermarket.getChild('Arch_44__032_237')
	supermarket.getChild('Arch_44__032_245')
	supermarket.getChild('Arch_44__032_251')
	supermarket.getChild('Arch_44__032_252')
	supermarket.getChild('Arch_44__032_253')
	supermarket.getChild('Arch_44__032_258')
	supermarket.getChild('Arch_44__032_260')
	supermarket.getChild('Arch_44__032_263')
	supermarket.getChild('Arch_44__032_264')
	supermarket.getChild('Arch_44__032_268')
	supermarket.getChild('Arch_44__032_269')
	supermarket.getChild('Arch_44__032_270')
	supermarket.getChild('Arch_44__032_271')
	supermarket.getChild('Arch_44__032_272')
	supermarket.getChild('Box58')
	supermarket.getChild('Arch_44__032_273')
	supermarket.getChild('Arch_44__033_615')
	supermarket.getChild('Arch_44__033_616')
	supermarket.getChild('Arch_44__033_622')
	supermarket.getChild('Arch_44__033_623')
	supermarket.getChild('Arch_44__033_624')
	supermarket.getChild('Arch_44__033_625')
	supermarket.getChild('Arch_44__033_630')
	supermarket.getChild('Arch_44__033_631')
	supermarket.getChild('Arch_44__033_638')
	supermarket.getChild('Arch_44__033_639')
	supermarket.getChild('Arch_44__033_640')
	supermarket.getChild('Arch_44__033_641')
	supermarket.getChild('Arch_44__033_644')
	supermarket.getChild('Arch_44__033_645')
	supermarket.getChild('Arch_44__033_646')
	supermarket.getChild('Arch_44__033_647')
	supermarket.getChild('Arch_44__033_648')
	supermarket.getChild('Arch_44__033_656')
	supermarket.getChild('Arch_44__033_657')
	supermarket.getChild('Arch_44__033_658')
	supermarket.getChild('Arch_44__033_659')
	supermarket.getChild('Arch_44__033_660')
	supermarket.getChild('Arch_44__033_663')
	supermarket.getChild('Arch_44__033_664')
	supermarket.getChild('Arch_44__033_665')
	supermarket.getChild('Arch_44__033_666')
	supermarket.getChild('Arch_44__033_667')
	supermarket.getChild('Arch_44__033_668')
	supermarket.getChild('Arch_44__033_675')
	supermarket.getChild('Arch_44__033_676')
	supermarket.getChild('Arch_44__033_677')
	supermarket.getChild('Arch_44__033_678')
	supermarket.getChild('Arch_44__033_679')
	supermarket.getChild('Arch_44__033_684')
	supermarket.getChild('Arch_44__033_685')
	supermarket.getChild('Arch_44__033_691')
	supermarket.getChild('Arch_44__033_692')
	supermarket.getChild('Arch_44__033_693')
	supermarket.getChild('Arch_44__033_694')
	supermarket.getChild('Arch_44__033_699')
	supermarket.getChild('Arch_44__033_700')
	supermarket.getChild('Arch_44__033_701')
	supermarket.getChild('Arch_44__033_702')
	supermarket.getChild('Arch_44__033_703')
	supermarket.getChild('Arch_44__033_704')
	supermarket.getChild('Arch_44__033_705')
	supermarket.getChild('Arch_44__033_706')
	supermarket.getChild('Arch_44__033_707')
	supermarket.getChild('Arch_44__033_708')
	supermarket.getChild('Arch_44__033_709')
	supermarket.getChild('Arch_44__033_713')
	supermarket.getChild('Arch_44__033_714')
	supermarket.getChild('Arch_44__033_715')
	supermarket.getChild('Arch_44__033_722')
	supermarket.getChild('Arch_44__033_723')
	supermarket.getChild('Arch_44__033_724')
	supermarket.getChild('Arch_44__033_725')
	supermarket.getChild('Arch_44__033_729')
	supermarket.getChild('Arch_44__033_730')
	supermarket.getChild('Arch_44__033_731')
	supermarket.getChild('Arch_44__033_732')
	supermarket.getChild('Arch_44__033_733')
	supermarket.getChild('Arch_44__033_734')
	supermarket.getChild('Arch_44__033_735')
	supermarket.getChild('Arch_44__033_736')
	supermarket.getChild('Arch_44__033_737')
	supermarket.getChild('Arch_44__033_738')
	supermarket.getChild('Arch_44__033_739')
	supermarket.getChild('Arch_44__033_740')
	supermarket.getChild('Arch_44__033_741')
	supermarket.getChild('Arch_44__033_745')
	supermarket.getChild('Arch_44__033_746')
	supermarket.getChild('Arch_44__033_747')
	supermarket.getChild('Arch_44__033_748')
	supermarket.getChild('Arch_44__033_749')
	supermarket.getChild('Arch_44__033_757')
	supermarket.getChild('Arch_44__033_758')
	supermarket.getChild('Arch_44__033_759')
	supermarket.getChild('Arch_44__033_760')
	supermarket.getChild('Arch_44__033_761')
	supermarket.getChild('Arch_44__033_763')
	supermarket.getChild('Arch_44__033_764')
	supermarket.getChild('Arch_44__033_765')
	supermarket.getChild('Arch_44__033_766')
	supermarket.getChild('Arch_44__033_771')
	supermarket.getChild('Arch_44__033_773')
	supermarket.getChild('Arch_44__033_774')
	supermarket.getChild('Arch_44__033_775')
	supermarket.getChild('Arch_44__033_776')
	supermarket.getChild('Arch_44__033_777')
	supermarket.getChild('Arch_44__033_778')
	supermarket.getChild('Arch_44__033_780')
	supermarket.getChild('Arch_44__033_783')
	supermarket.getChild('Arch_44__033_784')
	supermarket.getChild('Arch_44__033_785')
	supermarket.getChild('Arch_44__033_786')
	supermarket.getChild('Arch_44__033_787')
	supermarket.getChild('Arch_44__033_788')
	supermarket.getChild('Arch_44__033_795')
	supermarket.getChild('Arch_44__033_796')
	supermarket.getChild('Arch_44__033_797')
	supermarket.getChild('Arch_44__033_798')
	supermarket.getChild('Arch_44__033_799')
	supermarket.getChild('Arch_44__032_275')
	supermarket.getChild('Arch_44__032_276')
	supermarket.getChild('Arch_44__032_277')
	supermarket.getChild('Arch_44__032_278')
	supermarket.getChild('Arch_44__032_279')
	supermarket.getChild('Arch_44__032_280')
	supermarket.getChild('Arch_44__032_283')
	supermarket.getChild('Arch_44__032_284')
	supermarket.getChild('Arch_44__032_285')
	supermarket.getChild('Arch_44__032_286')
	supermarket.getChild('Arch_44__032_287')
	supermarket.getChild('Arch_44__032_290')
	supermarket.getChild('Arch_44__032_291')
	supermarket.getChild('Arch_44__032_292')
	supermarket.getChild('Arch_44__032_293')
	supermarket.getChild('Arch_44__032_294')
	supermarket.getChild('Arch_44__032_295')
	supermarket.getChild('Arch_44__032_296')
	supermarket.getChild('Arch_44__032_297')
	supermarket.getChild('Arch_44__032_299')
	supermarket.getChild('Arch_44__032_300')
	supermarket.getChild('Arch_44__032_301')
	supermarket.getChild('Arch_44__032_303')
	supermarket.getChild('Arch_44__032_305')
	supermarket.getChild('Arch_44__032_306')
	supermarket.getChild('Arch_44__032_307')
	supermarket.getChild('Arch_44__032_308')
	supermarket.getChild('Arch_44__032_309')
	supermarket.getChild('Arch_44__032_310')
	supermarket.getChild('Arch_44__032_311')
	supermarket.getChild('Arch_44__032_312')
	supermarket.getChild('Arch_44__032_313')
	supermarket.getChild('Arch_44__032_314')
	supermarket.getChild('Arch_44__032_317')
	supermarket.getChild('Arch_44__032_318')
	supermarket.getChild('Arch_44__032_319')
	supermarket.getChild('Arch_44__032_320')
	supermarket.getChild('Arch_44__032_322')
	supermarket.getChild('Arch_44__032_324')
	supermarket.getChild('Arch_44__032_325')
	supermarket.getChild('Arch_44__032_326')
	supermarket.getChild('Arch_44__032_327')
	supermarket.getChild('Arch_44__032_328')
	supermarket.getChild('Arch_44__032_329')
	supermarket.getChild('Arch_44__032_330')
	supermarket.getChild('Arch_44__032_332')
	supermarket.getChild('Arch_44__032_334')
	supermarket.getChild('Arch_44__032_335')
	supermarket.getChild('Arch_44__032_336')
	supermarket.getChild('Arch_44__032_337')
	supermarket.getChild('Arch_44__032_338')
	supermarket.getChild('Arch_44__032_339')
	supermarket.getChild('Arch_44__032_340')
	supermarket.getChild('Arch_44__032_341')
	supermarket.getChild('Arch_44__032_342')
	supermarket.getChild('Arch_44__032_345')
	supermarket.getChild('Arch_44__032_346')
	supermarket.getChild('Arch_44__032_347')
	supermarket.getChild('Arch_44__032_348')
	supermarket.getChild('Arch_44__032_349')
	supermarket.getChild('Arch_44__032_350')
	supermarket.getChild('Arch_44__032_351')
	supermarket.getChild('Arch_44__032_352')
	supermarket.getChild('Arch_44__032_353')
	supermarket.getChild('Arch_44__032_354')
	supermarket.getChild('Arch_44__032_355')
	supermarket.getChild('Arch_44__032_356')
	supermarket.getChild('Arch_44__032_357')
	supermarket.getChild('Arch_44__032_358')
	supermarket.getChild('Arch_44__032_360')
	supermarket.getChild('Arch_44__032_363')
	supermarket.getChild('Arch_44__032_364')
	supermarket.getChild('Arch_44__032_367')
	supermarket.getChild('Arch_44__032_368')
	supermarket.getChild('Arch_44__032_370')
	supermarket.getChild('Arch_44__032_371')
	supermarket.getChild('Arch_44__032_372')
	supermarket.getChild('Arch_44__032_373')
	supermarket.getChild('Arch_44__032_374')
	supermarket.getChild('Arch_44__032_375')
	supermarket.getChild('Arch_44__032_376')
	supermarket.getChild('Arch_44__032_378')
	supermarket.getChild('Arch_44__032_379')
	supermarket.getChild('Arch_44__032_380')
	supermarket.getChild('Arch_44__032_381')
	supermarket.getChild('Arch_44__032_382')
	supermarket.getChild('Arch_44__032_386')
	supermarket.getChild('Arch_44__032_387')
	supermarket.getChild('Arch_44__032_388')
	supermarket.getChild('Arch_44__032_389')
	supermarket.getChild('Arch_44__032_390')
	supermarket.getChild('Arch_44__032_394')
	supermarket.getChild('Arch_44__032_397')
	supermarket.getChild('Arch_44__032_398')
	supermarket.getChild('Arch_44__031_493')
	supermarket.getChild('Arch_44__031_494')
	supermarket.getChild('Arch_44__031_495')
	supermarket.getChild('Arch_44__031_509')
	supermarket.getChild('Arch_44__031_513')
	supermarket.getChild('Arch_44__031_519')
	supermarket.getChild('Arch_44__031_520')
	supermarket.getChild('Arch_44__031_521')
	supermarket.getChild('Arch_44__031_523')
	supermarket.getChild('Arch_44__031_524')
	supermarket.getChild('Arch_44__031_525')
	supermarket.getChild('Arch_44__031_527')
	supermarket.getChild('Arch_44__031_528')
	supermarket.getChild('Arch_44__031_529')
	supermarket.getChild('Arch_44__031_540')
	supermarket.getChild('Arch_44__031_541')
	supermarket.getChild('Arch_44__031_542')
	supermarket.getChild('Arch_44__031_543')
	supermarket.getChild('Arch_44__031_544')
	supermarket.getChild('Arch_44__031_545')
	supermarket.getChild('Arch_44__031_546')
	supermarket.getChild('Arch_44__031_547')
	supermarket.getChild('Arch_44__032_406')
	supermarket.getChild('Arch_44__032_409')
	supermarket.getChild('Arch_44__032_410')
	supermarket.getChild('Arch_44__032_411')
	supermarket.getChild('Arch_44__032_412')
	supermarket.getChild('Arch_44__032_413')
	supermarket.getChild('Arch_44__032_414')
	supermarket.getChild('Arch_44__032_415')
	supermarket.getChild('Arch_44__032_416')
	supermarket.getChild('Arch_44__032_417')
	supermarket.getChild('Arch_44__032_427')
	supermarket.getChild('Arch_44__032_428')
	supermarket.getChild('Arch_44__032_429')
	supermarket.getChild('Arch_44__032_430')
	supermarket.getChild('Arch_44__032_431')
	supermarket.getChild('Arch_44__032_435')
	supermarket.getChild('Arch_44__032_437')
	supermarket.getChild('Arch_44__031_549')
	supermarket.getChild('Arch_44__031_550')
	supermarket.getChild('Arch_44__031_551')
	supermarket.getChild('Arch_44__031_552')
	supermarket.getChild('Arch_44__031_553')
	supermarket.getChild('Arch_44__031_554')
	supermarket.getChild('Arch_44__031_555')
	supermarket.getChild('Arch_44__031_556')
	supermarket.getChild('Arch_44__031_557')
	supermarket.getChild('Arch_44__031_558')
	supermarket.getChild('Arch_44__031_559')
	supermarket.getChild('Arch_44__031_560')
	supermarket.getChild('Arch_44__031_561')
	supermarket.getChild('Arch_44__031_562')
	supermarket.getChild('Arch_44__031_563')
	supermarket.getChild('Arch_44__031_564')
	supermarket.getChild('Arch_44__031_565')
	supermarket.getChild('Arch_44__031_566')
	supermarket.getChild('Arch_44__031_567')
	supermarket.getChild('Arch_44__031_568')
	supermarket.getChild('Arch_44__031_569')
	supermarket.getChild('Arch_44__031_570')
	supermarket.getChild('Arch_44__031_571')
	supermarket.getChild('Arch_44__031_572')
	supermarket.getChild('Arch_44__031_573')
	supermarket.getChild('Arch_44__031_574')
	supermarket.getChild('Arch_44__030_282')
	supermarket.getChild('Arch_44__030_283')
	supermarket.getChild('Arch_44__030_284')
	supermarket.getChild('Arch_44__030_285')
	supermarket.getChild('Arch_44__030_286')
	supermarket.getChild('Arch_44__030_287')
	supermarket.getChild('Arch_44__030_288')
	supermarket.getChild('Arch_44__030_289')
	supermarket.getChild('Arch_44__030_290')
	supermarket.getChild('Arch_44__030_291')
	supermarket.getChild('Arch_44__030_292')
	supermarket.getChild('Arch_44__030_293')
	supermarket.getChild('Arch_44__031_584')
	supermarket.getChild('Arch_44__031_585')
	supermarket.getChild('Arch_44__031_586')
	supermarket.getChild('Arch_44__031_587')
	supermarket.getChild('Arch_44__031_588')
	supermarket.getChild('Arch_44__031_589')
	supermarket.getChild('Arch_44__031_590')
	supermarket.getChild('Arch_44__031_591')
	supermarket.getChild('Arch_44__031_592')
	supermarket.getChild('Arch_44__031_593')
	supermarket.getChild('Arch_44__031_594')
	supermarket.getChild('Arch_44__031_595')
	supermarket.getChild('Arch_44__031_596')
	supermarket.getChild('Arch_44__031_597')
	supermarket.getChild('Arch_44__032_440')
	supermarket.getChild('Arch_44__032_441')
	supermarket.getChild('Arch_44__032_442')
	supermarket.getChild('Arch_44__032_443')
	supermarket.getChild('Arch_44__032_444')
	supermarket.getChild('Arch_44__032_445')
	supermarket.getChild('Arch_44__032_446')
	supermarket.getChild('Arch_44__032_447')
	supermarket.getChild('Arch_44__032_448')
	supermarket.getChild('Arch_44__032_449')
	supermarket.getChild('Arch_44__032_456')
	supermarket.getChild('Arch_44__032_457')
	supermarket.getChild('Arch_44__032_458')
	supermarket.getChild('Arch_44__032_459')
	supermarket.getChild('Arch_44__032_460')
	supermarket.getChild('Arch_44__032_464')
	supermarket.getChild('Arch_44__032_465')
	supermarket.getChild('Arch_44__032_466')
	supermarket.getChild('Arch_44__032_467')
	supermarket.getChild('Arch_44__032_468')
	supermarket.getChild('Arch_44__039_304')
	supermarket.getChild('Arch_44__039_305')
	supermarket.getChild('Arch_44__040_219')
	supermarket.getChild('Arch_44__040_220')
	supermarket.getChild('Arch_44__040_221')
	supermarket.getChild('Arch_44__040_222')
	supermarket.getChild('Arch_44__040_223')
	supermarket.getChild('Arch_44__040_224')
	supermarket.getChild('Arch_44__040_225')
	supermarket.getChild('Arch_44__19551465')
	supermarket.getChild('Arch_44__040_226')
	supermarket.getChild('Arch_44__040_227')
	supermarket.getChild('Arch_44__040_228')
	supermarket.getChild('Arch_44__039_306')
	supermarket.getChild('Arch_44__039_307')
	supermarket.getChild('Arch_44__039_308')
	supermarket.getChild('Arch_44__039_309')
	supermarket.getChild('Arch_44__039_310')
	supermarket.getChild('Arch_44__039_311')
	supermarket.getChild('Arch_44__039_312')
	supermarket.getChild('Arch_44__039_313')
	supermarket.getChild('Arch_44__039_314')
	supermarket.getChild('Arch_44__039_315')
	supermarket.getChild('Arch_44__039_316')
	supermarket.getChild('Arch_44__039_317')
	supermarket.getChild('Arch_44__039_318')
	supermarket.getChild('Arch_44__039_319')
	supermarket.getChild('Arch_44__039_320')
	supermarket.getChild('Arch_44__039_321')
	supermarket.getChild('Arch_44__039_322')
	supermarket.getChild('Arch_44__039_323')
	supermarket.getChild('Arch_44__039_324')
	supermarket.getChild('Arch_44__039_325')
	supermarket.getChild('Arch_44__039_326')
	supermarket.getChild('Arch_44__039_327')
	supermarket.getChild('Arch_44__039_328')
	supermarket.getChild('Arch_44__039_329')
	supermarket.getChild('Arch_44__039_330')
	supermarket.getChild('Arch_44__039_331')
	supermarket.getChild('Arch_44__039_332')
	supermarket.getChild('Arch_44__039_333')
	supermarket.getChild('Arch_44__039_334')
	supermarket.getChild('Arch_44__039_335')
	supermarket.getChild('Arch_44__039_336')
	supermarket.getChild('Arch_44__039_337')
	supermarket.getChild('Arch_44__039_338')
	supermarket.getChild('Arch_44__039_339')
	supermarket.getChild('Arch_44__039_340')
	supermarket.getChild('Arch_44__039_341')
	supermarket.getChild('Arch_44__039_342')
	supermarket.getChild('Arch_44__039_343')
	supermarket.getChild('Arch_44__039_344')
	supermarket.getChild('Arch_44__039_345')
	supermarket.getChild('Arch_44__039_346')
	supermarket.getChild('Arch_44__039_347')
	supermarket.getChild('Arch_44__039_348')
	supermarket.getChild('Arch_44__039_349')
	supermarket.getChild('Arch_44__039_350')
	supermarket.getChild('Arch_44__039_351')
	supermarket.getChild('Arch_44__039_352')
	supermarket.getChild('Arch_44__039_353')
	supermarket.getChild('Arch_44__039_354')
	supermarket.getChild('Arch_44__039_355')
	supermarket.getChild('Arch_44__039_356')
	supermarket.getChild('Arch_44__039_357')
	supermarket.getChild('Arch_44__039_358')
	supermarket.getChild('Arch_44__039_359')
	supermarket.getChild('Arch_44__039_360')
	supermarket.getChild('Arch_44__039_361')
	supermarket.getChild('Arch_44__039_362')
	supermarket.getChild('Arch_44__039_363')
	supermarket.getChild('Arch_44__039_364')
	supermarket.getChild('Arch_44__039_365')
	supermarket.getChild('Arch_44__039_366')
	supermarket.getChild('Arch_44__039_367')
	supermarket.getChild('Arch_44__039_368')
	supermarket.getChild('Arch_44__039_369')
	supermarket.getChild('Arch_44__039_370')
	supermarket.getChild('Arch_44__039_371')
	supermarket.getChild('Arch_44__039_372')
	supermarket.getChild('Arch_44__039_373')
	supermarket.getChild('Arch_44__039_374')
	supermarket.getChild('Arch_44__039_375')
	supermarket.getChild('Arch_44__039_376')
	supermarket.getChild('Arch_44__039_377')
	supermarket.getChild('Arch_44__039_378')
	supermarket.getChild('Arch_44__039_379')
	supermarket.getChild('Arch_44__039_380')
	supermarket.getChild('Arch_44__039_381')
	supermarket.getChild('Arch_44__039_382')
	supermarket.getChild('Arch_44__039_383')
	supermarket.getChild('Arch_44__039_384')
	supermarket.getChild('Arch_44__039_385')
	supermarket.getChild('Arch_44__039_386')
	supermarket.getChild('Arch_44__039_387')
	supermarket.getChild('Arch_44__039_388')
	supermarket.getChild('Arch_44__039_389')
	supermarket.getChild('Arch_44__039_390')
	supermarket.getChild('Arch_44__039_391')
	supermarket.getChild('Arch_44__039_392')
	supermarket.getChild('Arch_44__039_393')
	supermarket.getChild('Arch_44__039_394')
	supermarket.getChild('Arch_44__039_395')
	supermarket.getChild('Arch_44__039_396')
	supermarket.getChild('Arch_44__039_397')
	supermarket.getChild('Arch_44__039_398')
	supermarket.getChild('Arch_44__039_399')
	supermarket.getChild('Arch_44__039_400')
	supermarket.getChild('Arch_44__039_401')
	supermarket.getChild('Arch_44__039_402')
	supermarket.getChild('Arch_44__039_403')
	supermarket.getChild('Arch_44__039_404')
	supermarket.getChild('Arch_44__039_405')
	supermarket.getChild('Arch_44__039_406')
	supermarket.getChild('Arch_44__039_407')
	supermarket.getChild('Arch_44__039_408')
	supermarket.getChild('Arch_44__039_409')
	supermarket.getChild('Arch_44__039_410')
	supermarket.getChild('Arch_44__039_411')
	supermarket.getChild('Arch_44__039_412')
	supermarket.getChild('Arch_44__039_413')
	supermarket.getChild('Arch_44__039_414')
	supermarket.getChild('Arch_44__039_415')
	supermarket.getChild('Arch_44__039_416')
	supermarket.getChild('Arch_44__039_417')
	supermarket.getChild('Arch_44__039_418')
	supermarket.getChild('Arch_44__039_419')
	supermarket.getChild('Arch_44__039_420')
	supermarket.getChild('Arch_44__039_421')
	supermarket.getChild('Arch_44__039_422')
	supermarket.getChild('Arch_44__039_423')
	supermarket.getChild('Arch_44__039_424')
	supermarket.getChild('Arch_44__039_425')
	supermarket.getChild('Arch_44__039_426')
	supermarket.getChild('Arch_44__039_427')
	supermarket.getChild('Arch_44__039_428')
	supermarket.getChild('Arch_44__039_429')
	supermarket.getChild('Arch_44__039_430')
	supermarket.getChild('Arch_44__039_431')
	supermarket.getChild('Arch_44__039_432')
	supermarket.getChild('Arch_44__039_433')
	supermarket.getChild('Arch_44__039_434')
	supermarket.getChild('Arch_44__039_435')
	supermarket.getChild('Arch_44__039_436')
	supermarket.getChild('Arch_44__039_438')
	supermarket.getChild('Arch_44__039_439')
	supermarket.getChild('Arch_44__039_440')
	supermarket.getChild('Arch_44__039_441')
	supermarket.getChild('Arch_44__039_442')
	supermarket.getChild('Arch_44__039_443')
	supermarket.getChild('Arch_44__039_444')
	supermarket.getChild('Arch_44__039_445')
	supermarket.getChild('Arch_44__039_446')
	supermarket.getChild('Arch_44__039_447')
	supermarket.getChild('Arch_44__039_448')
	supermarket.getChild('Arch_44__039_449')
	supermarket.getChild('Arch_44__039_450')
	supermarket.getChild('Arch_44__039_451')
	supermarket.getChild('Arch_44__039_452')
	supermarket.getChild('Arch_44__039_453')
	supermarket.getChild('Arch_44__039_454')
	supermarket.getChild('Arch_44__039_455')
	supermarket.getChild('Arch_44__039_456')
	supermarket.getChild('Arch_44__039_457')
	supermarket.getChild('Arch_44__039_458')
	supermarket.getChild('Arch_44__039_459')
	supermarket.getChild('Arch_44__039_460')
	supermarket.getChild('Arch_44__039_461')
	supermarket.getChild('Arch_44__039_462')
	supermarket.getChild('Arch_44__039_463')
	supermarket.getChild('Arch_44__039_464')
	supermarket.getChild('Arch_44__039_465')
	supermarket.getChild('Arch_44__039_466')
	supermarket.getChild('Arch_44__039_467')
	supermarket.getChild('Arch_44__039_468')
	supermarket.getChild('Arch_44__039_469')
	supermarket.getChild('Arch_44__039_470')
	supermarket.getChild('Arch_44__039_471')
	supermarket.getChild('Arch_44__039_472')
	supermarket.getChild('Arch_44__039_473')
	supermarket.getChild('Arch_44__039_474')
	supermarket.getChild('Arch_44__039_475')
	supermarket.getChild('Arch_44__039_476')
	supermarket.getChild('Arch_44__039_477')
	supermarket.getChild('Arch_44__039_478')
	supermarket.getChild('Arch_44__039_479')
	supermarket.getChild('Arch_44__039_480')
	supermarket.getChild('Arch_44__039_481')
	supermarket.getChild('Arch_44__039_482')
	supermarket.getChild('Arch_44__039_483')
	supermarket.getChild('Arch_44__039_484')
	supermarket.getChild('Arch_44__039_485')
	supermarket.getChild('Arch_44__039_486')
	supermarket.getChild('Arch_44__039_487')
	supermarket.getChild('Arch_44__039_488')
	supermarket.getChild('Arch_44__039_489')
	supermarket.getChild('Arch_44__039_490')
	supermarket.getChild('Arch_44__039_491')
	supermarket.getChild('Arch_44__039_492')
	supermarket.getChild('Arch_44__039_493')
	supermarket.getChild('Arch_44__039_494')
	supermarket.getChild('Arch_44__039_495')
	supermarket.getChild('Arch_44__039_496')
	supermarket.getChild('Arch_44__039_497')
	supermarket.getChild('Arch_44__039_498')
	supermarket.getChild('Arch_44__039_499')
	supermarket.getChild('Arch_44__039_500')
	supermarket.getChild('Arch_44__039_501')
	supermarket.getChild('Arch_44__039_502')
	supermarket.getChild('Arch_44__039_503')
	supermarket.getChild('Arch_44__039_504')
	supermarket.getChild('Arch_44__039_505')
	supermarket.getChild('Arch_44__039_506')
	supermarket.getChild('Arch_44__039_507')
	supermarket.getChild('Arch_44__039_508')
	supermarket.getChild('Arch_44__039_509')
	supermarket.getChild('Arch_44__039_510')
	supermarket.getChild('Arch_44__039_511')
	supermarket.getChild('Arch_44__039_512')
	supermarket.getChild('Arch_44__039_513')
	supermarket.getChild('Arch_44__039_514')
	supermarket.getChild('Arch_44__039_515')
	supermarket.getChild('Arch_44__039_516')
	supermarket.getChild('Arch_44__039_517')
	supermarket.getChild('Arch_44__039_518')
	supermarket.getChild('Arch_44__039_519')
	supermarket.getChild('Arch_44__039_520')
	supermarket.getChild('Arch_44__039_521')
	supermarket.getChild('Arch_44__039_522')
	supermarket.getChild('Arch_44__039_523')
	supermarket.getChild('Arch_44__039_524')
	supermarket.getChild('Arch_44__039_525')
	supermarket.getChild('Arch_44__039_526')
	supermarket.getChild('Arch_44__039_527')
	supermarket.getChild('Arch_44__039_528')
	supermarket.getChild('Arch_44__039_529')
	supermarket.getChild('Arch_44__039_530')
	supermarket.getChild('Arch_44__039_531')
	supermarket.getChild('Arch_44__039_532')
	supermarket.getChild('Arch_44__039_533')
	supermarket.getChild('Arch_44__039_534')
	supermarket.getChild('Arch_44__039_535')
	supermarket.getChild('Arch_44__039_536')
	supermarket.getChild('Arch_44__039_537')
	supermarket.getChild('Arch_44__039_538')
	supermarket.getChild('Arch_44__039_539')
	supermarket.getChild('Arch_44__039_540')
	supermarket.getChild('Arch_44__039_541')
	supermarket.getChild('Arch_44__039_542')
	supermarket.getChild('Arch_44__039_543')
	supermarket.getChild('Arch_44__039_544')
	supermarket.getChild('Arch_44__039_545')
	supermarket.getChild('Arch_44__039_546')
	supermarket.getChild('Arch_44__039_547')
	supermarket.getChild('Arch_44__039_548')
	supermarket.getChild('Arch_44__039_549')
	supermarket.getChild('Arch_44__039_550')
	supermarket.getChild('Arch_44__039_551')
	supermarket.getChild('Arch_44__039_552')
	supermarket.getChild('Arch_44__039_553')
	supermarket.getChild('Arch_44__039_554')
	supermarket.getChild('Arch_44__039_555')
	supermarket.getChild('Arch_44__039_556')
	supermarket.getChild('Arch_44__039_557')
	supermarket.getChild('Arch_44__039_558')
	supermarket.getChild('Arch_44__039_559')
	supermarket.getChild('Arch_44__021_37')
	supermarket.getChild('Arch_44__77050487')
	supermarket.getChild('Arch_44__021_387')
	supermarket.getChild('Box77')
	supermarket.getChild('Box82')
	supermarket.getChild('Box83')
	supermarket.getChild('Box84')
	supermarket.getChild('Box85')
	supermarket.getChild('Box86')
	supermarket.getChild('Box87')
	supermarket.getChild('Box88')
	supermarket.getChild('Box89')
	supermarket.getChild('Box90')
	supermarket.getChild('Box91')
	supermarket.getChild('Box108')
	supermarket.getChild('Box110')
	supermarket.getChild('Arch_44__010_299')
	supermarket.getChild('Arch_44__351586058')
	supermarket.getChild('Arch_44__010_300')
	supermarket.getChild('Arch_44__010_301')
	supermarket.getChild('Arch_44__010_302')
	supermarket.getChild('Arch_44__010_303')
	supermarket.getChild('Arch_44__010_304')
	supermarket.getChild('Arch_44__010_305')
	supermarket.getChild('Arch_44__010_306')
	supermarket.getChild('Arch_44__010_307')
	supermarket.getChild('Arch_44__010_308')
	supermarket.getChild('Arch_44__021_459')
	supermarket.getChild('Arch_44__021_460')
	supermarket.getChild('Arch_44__021_461')
	supermarket.getChild('Arch_44__021_462')
	supermarket.getChild('Arch_44__021_463')
	supermarket.getChild('Arch_44__021_469')
	supermarket.getChild('Arch_44__021_470')
	supermarket.getChild('Arch_44__021_471')
	supermarket.getChild('Arch_44__021_472')
	supermarket.getChild('Arch_44__021_473')
	supermarket.getChild('Arch_44__021_474')
	supermarket.getChild('Arch_44__021_475')
	supermarket.getChild('Arch_44__021_476')
	supermarket.getChild('Arch_44__021_489')
	supermarket.getChild('Arch_44__954390595')
	supermarket.getChild('Arch_44__021_490')
	supermarket.getChild('Arch_44__021_491')
	supermarket.getChild('Arch_44__021_492')
	supermarket.getChild('Arch_44__021_493')
	supermarket.getChild('Arch_44__021_494')
	supermarket.getChild('Arch_44__021_495')
	supermarket.getChild('Arch_44__021_496')
	supermarket.getChild('Arch_44__021_497')
	supermarket.getChild('Arch_44__021_498')
	supermarket.getChild('Arch_44__021_499')
	supermarket.getChild('Arch_44__021_500')
	supermarket.getChild('Arch_44__011_174')
	supermarket.getChild('Arch_44__427221000')
	supermarket.getChild('Arch_44__011_175')
	supermarket.getChild('Arch_44__011_176')
	supermarket.getChild('Arch_44__011_177')
	supermarket.getChild('Arch_44__011_178')
	supermarket.getChild('Arch_44__011_179')
	supermarket.getChild('Arch_44__011_180')
	supermarket.getChild('Arch_44__011_181')
	supermarket.getChild('Arch_44__011_182')
	supermarket.getChild('Arch_44__011_183')
	supermarket.getChild('Arch_44__011_184')
	supermarket.getChild('Arch_44__011_185')
	supermarket.getChild('Arch_44__011_186')
	supermarket.getChild('Arch_44__011_187')
	supermarket.getChild('Arch_44__011_188')
	supermarket.getChild('Arch_44__012_655')
	supermarket.getChild('Arch_44__72902238')
	supermarket.getChild('Arch_44__012_656')
	supermarket.getChild('Arch_44__012_657')
	supermarket.getChild('Arch_44__012_660')
	supermarket.getChild('Arch_44__422354149')
	supermarket.getChild('Arch_44__012_661')
	supermarket.getChild('Arch_44__012_662')
	supermarket.getChild('Arch_44__012_663')
	supermarket.getChild('Arch_44__011_193')
	supermarket.getChild('Arch_44__427133318')
	supermarket.getChild('Arch_44__011_194')
	supermarket.getChild('Arch_44__011_195')
	supermarket.getChild('Arch_44__011_196')
	supermarket.getChild('Arch_44__021_506')
	supermarket.getChild('Arch_44__021_507')
	supermarket.getChild('Arch_44__021_508')
	supermarket.getChild('Arch_44__021_509')
	supermarket.getChild('Arch_44__021_510')
	supermarket.getChild('Arch_44__021_511')
	supermarket.getChild('Arch_44__021_512')
	supermarket.getChild('Arch_44__021_513')
	supermarket.getChild('Arch_44__021_514')
	supermarket.getChild('Arch_44__021_515')
	supermarket.getChild('Arch_44__021_516')
	supermarket.getChild('Arch_44__021_517')
	supermarket.getChild('Arch_44__021_518')
	supermarket.getChild('Arch_44__021_519')
	supermarket.getChild('Arch_44__021_520')
	supermarket.getChild('Arch_44__021_521')
	supermarket.getChild('Arch_44__021_522')
	supermarket.getChild('Arch_44__021_523')
	supermarket.getChild('Arch_44__021_524')
	supermarket.getChild('Arch_44__021_525')
	supermarket.getChild('Arch_44__021_526')
	supermarket.getChild('Arch_44__021_527')
	supermarket.getChild('Arch_44__021_528')
	supermarket.getChild('Arch_44__021_529')
	supermarket.getChild('Arch_44__010_309')
	supermarket.getChild('Arch_44__010_310')
	supermarket.getChild('Arch_44__010_311')
	supermarket.getChild('Arch_44__010_312')
	supermarket.getChild('Arch_44__021_530')
	supermarket.getChild('Arch_44__021_531')
	supermarket.getChild('Arch_44__021_532')
	supermarket.getChild('Arch_44__010_313')
	supermarket.getChild('Arch_44__021_533')
	supermarket.getChild('Arch_44__021_534')
	supermarket.getChild('Arch_44__021_535')
	supermarket.getChild('Arch_44__021_536')
	supermarket.getChild('Arch_44__021_537')
	supermarket.getChild('Arch_44__021_538')
	supermarket.getChild('Arch_44__010_314')
	supermarket.getChild('Arch_44__010_315')
	supermarket.getChild('Arch_44__010_316')
	supermarket.getChild('Arch_44__010_317')
	supermarket.getChild('Arch_44__010_318')
	supermarket.getChild('Arch_44__010_319')
	supermarket.getChild('Arch_44__010_320')
	supermarket.getChild('Arch_44__010_321')
	supermarket.getChild('Arch_44__010_322')
	supermarket.getChild('Arch_44__010_323')
	supermarket.getChild('Arch_44__010_324')
	supermarket.getChild('Arch_44__010_325')
	supermarket.getChild('Arch_44__010_326')
	supermarket.getChild('Arch_44__021_539')
	supermarket.getChild('Arch_44__021_540')
	supermarket.getChild('Arch_44__021_541')
	supermarket.getChild('Arch_44__010_327')
	supermarket.getChild('Arch_44__010_328')
	supermarket.getChild('Arch_44__010_329')
	supermarket.getChild('Arch_44__010_330')
	supermarket.getChild('Arch_44__010_331')
	supermarket.getChild('Arch_44__010_332')
	supermarket.getChild('Arch_44__010_333')
	supermarket.getChild('Box115')
	supermarket.getChild('Arch_44__021_542')
	supermarket.getChild('Arch_44__021_543')
	supermarket.getChild('Arch_44__021_544')
	supermarket.getChild('Arch_44__021_545')
	supermarket.getChild('Arch_44__021_546')
	supermarket.getChild('Arch_44__021_547')
	supermarket.getChild('Arch_44__021_548')
	supermarket.getChild('Arch_44__021_549')
	supermarket.getChild('Arch_44__021_550')
	supermarket.getChild('Arch_44__021_551')
	supermarket.getChild('Arch_44__021_552')
	supermarket.getChild('Arch_44__021_553')
	supermarket.getChild('Arch_44__021_554')
	supermarket.getChild('Arch_44__021_555')
	supermarket.getChild('Arch_44__021_556')
	supermarket.getChild('Arch_44__021_557')
	supermarket.getChild('Arch_44__021_563')
	supermarket.getChild('Arch_44__021_564')
	supermarket.getChild('Arch_44__021_565')
	supermarket.getChild('Arch_44__021_566')
	supermarket.getChild('Arch_44__021_567')
	supermarket.getChild('Arch_44__021_575')
	supermarket.getChild('Arch_44__021_576')
	supermarket.getChild('Arch_44__021_577')
	supermarket.getChild('Arch_44__021_578')
	supermarket.getChild('Arch_44__010_336')
	supermarket.getChild('Arch_44__010_337')
	supermarket.getChild('Arch_44__021_579')
	supermarket.getChild('Arch_44__021_584')
	supermarket.getChild('Arch_44__021_585')
	supermarket.getChild('Arch_44__021_586')
	supermarket.getChild('Arch_44__021_587')
	supermarket.getChild('Arch_44__010_349')
	supermarket.getChild('Arch_44__010_350')
	supermarket.getChild('Arch_44__010_351')
	supermarket.getChild('Arch_44__021_588')
	supermarket.getChild('Arch_44__021_589')
	supermarket.getChild('Arch_44__021_590')
	supermarket.getChild('Arch_44__010_352')
	supermarket.getChild('Arch_44__010_353')
	supermarket.getChild('Arch_44__010_354')
	supermarket.getChild('Arch_44__010_355')
	supermarket.getChild('Arch_44__010_356')
	supermarket.getChild('Arch_44__010_357')
	supermarket.getChild('Arch_44__010_358')
	supermarket.getChild('Box116')
	supermarket.getChild('Arch_44__021_592')
	supermarket.getChild('Arch_44__021_593')
	supermarket.getChild('Arch_44__021_594')
	supermarket.getChild('Arch_44__021_595')
	supermarket.getChild('Arch_44__021_601')
	supermarket.getChild('Arch_44__021_602')
	supermarket.getChild('Arch_44__021_603')
	supermarket.getChild('Arch_44__021_604')
	supermarket.getChild('Arch_44__021_605')
	supermarket.getChild('Arch_44__021_606')
	supermarket.getChild('Arch_44__021_607')
	supermarket.getChild('Arch_44__021_608')
	supermarket.getChild('Arch_44__021_609')
	supermarket.getChild('Arch_44__021_619')
	supermarket.getChild('Arch_44__021_620')
	supermarket.getChild('Arch_44__021_621')
	supermarket.getChild('Arch_44__021_622')
	supermarket.getChild('Arch_44__021_623')
	supermarket.getChild('Arch_44__021_624')
	supermarket.getChild('Arch_44__021_625')
	supermarket.getChild('Arch_44__021_626')
	supermarket.getChild('Arch_44__021_627')
	supermarket.getChild('Arch_44__010_361')
	supermarket.getChild('Arch_44__010_362')
	supermarket.getChild('Arch_44__010_364')
	supermarket.getChild('Arch_44__010_365')
	supermarket.getChild('Box117')
	supermarket.getChild('Arch_44__012_697')
	supermarket.getChild('Arch_44__011_210')
	supermarket.getChild('Arch_44__012_699')
	supermarket.getChild('Arch_44__011_217')
	supermarket.getChild('Arch_44__012_700')
	supermarket.getChild('Arch_44__011_218')
	supermarket.getChild('Arch_44__011_219')
	supermarket.getChild('Arch_44__011_220')
	supermarket.getChild('Arch_44__011_221')
	supermarket.getChild('Box118')
	supermarket.getChild('Arch_44__011_223')
	supermarket.getChild('Arch_44__011_224')
	supermarket.getChild('Arch_44__012_706')
	supermarket.getChild('Arch_44__012_707')
	supermarket.getChild('Arch_44__012_708')
	supermarket.getChild('Arch_44__012_709')
	supermarket.getChild('Arch_44__011_230')
	supermarket.getChild('Arch_44__011_231')
	supermarket.getChild('Arch_44__011_232')
	supermarket.getChild('Arch_44__011_233')
	supermarket.getChild('Arch_44__011_234')
	supermarket.getChild('Arch_44__011_235')
	supermarket.getChild('Arch_44__011_236')
	supermarket.getChild('Arch_44__011_237')
	supermarket.getChild('Arch_44__011_238')
	supermarket.getChild('Arch_44__011_239')
	supermarket.getChild('Arch_44__011_243')
	supermarket.getChild('Arch_44__012_711')
	supermarket.getChild('Arch_44__011_250')
	supermarket.getChild('Arch_44__012_712')
	supermarket.getChild('Arch_44__012_713')
	supermarket.getChild('Arch_44__012_714')
	supermarket.getChild('Arch_44__011_251')
	supermarket.getChild('Arch_44__011_252')
	supermarket.getChild('Arch_44__011_253')
	supermarket.getChild('Arch_44__011_254')
	supermarket.getChild('Box119')
	supermarket.getChild('Arch_44__011_256')
	supermarket.getChild('Arch_44__011_257')
	supermarket.getChild('Arch_44__011_258')
	supermarket.getChild('Arch_44__011_259')
	supermarket.getChild('Arch_44__011_260')
	supermarket.getChild('Arch_44__011_261')
	supermarket.getChild('Box120')
	supermarket.getChild('Arch_44__030_308')
	supermarket.getChild('Arch_44__030_309')
	supermarket.getChild('Arch_44__030_310')
	supermarket.getChild('Arch_44__030_311')
	supermarket.getChild('Arch_44__030_313')
	supermarket.getChild('Arch_44__030_314')
	supermarket.getChild('Arch_44__030_315')
	supermarket.getChild('Arch_44__030_317')
	supermarket.getChild('Arch_44__030_318')
	supermarket.getChild('Arch_44__030_319')
	supermarket.getChild('Arch_44__030_322')
	supermarket.getChild('Arch_44__030_323')
	supermarket.getChild('Arch_44__030_324')
	supermarket.getChild('Arch_44__030_327')
	supermarket.getChild('Arch_44__030_328')
	supermarket.getChild('Arch_44__030_329')
	supermarket.getChild('Arch_44__030_332')
	supermarket.getChild('Arch_44__030_333')
	supermarket.getChild('Arch_44__030_334')
	supermarket.getChild('Arch_44__030_336')
	supermarket.getChild('Arch_44__030_337')
	supermarket.getChild('Arch_44__030_338')
	supermarket.getChild('Arch_44__030_349')
	supermarket.getChild('Arch_44__030_350')
	supermarket.getChild('Arch_44__030_351')
	supermarket.getChild('Arch_44__030_380')
	supermarket.getChild('Arch_44__030_381')
	supermarket.getChild('Arch_44__030_382')
	supermarket.getChild('Arch_44__030_384')
	supermarket.getChild('Arch_44__030_385')
	supermarket.getChild('Arch_44__030_387')
	supermarket.getChild('Arch_44__030_389')
	supermarket.getChild('Arch_44__030_390')
	supermarket.getChild('Arch_44__030_391')
	supermarket.getChild('Arch_44__030_393')
	supermarket.getChild('Arch_44__030_394')
	supermarket.getChild('Arch_44__030_395')
	supermarket.getChild('Arch_44__033_800')
	supermarket.getChild('Arch_44__033_801')
	supermarket.getChild('Arch_44__033_802')
	supermarket.getChild('Arch_44__033_803')
	supermarket.getChild('Arch_44__033_804')
	supermarket.getChild('Arch_44__033_815')
	supermarket.getChild('Arch_44__033_816')
	supermarket.getChild('Arch_44__033_817')
	supermarket.getChild('Arch_44__033_818')
	supermarket.getChild('Arch_44__033_819')
	supermarket.getChild('Arch_44__033_820')
	supermarket.getChild('Arch_44__033_821')
	supermarket.getChild('Arch_44__033_841')
	supermarket.getChild('Arch_44__033_842')
	supermarket.getChild('Arch_44__033_843')
	supermarket.getChild('Arch_44__033_844')
	supermarket.getChild('Arch_44__033_845')
	supermarket.getChild('Arch_44__033_846')
	supermarket.getChild('Arch_44__033_847')
	supermarket.getChild('Arch_44__033_848')
	supermarket.getChild('Arch_44__033_849')
	supermarket.getChild('Arch_44__033_850')
	supermarket.getChild('Arch_44__033_851')
	supermarket.getChild('Arch_44__033_853')
	supermarket.getChild('Arch_44__033_854')
	supermarket.getChild('Arch_44__033_855')
	supermarket.getChild('Arch_44__033_856')
	supermarket.getChild('Arch_44__033_857')
	supermarket.getChild('Arch_44__033_858')
	supermarket.getChild('Arch_44__033_859')
	supermarket.getChild('Arch_44__033_860')
	supermarket.getChild('Arch_44__033_868')
	supermarket.getChild('Arch_44__033_869')
	supermarket.getChild('Arch_44__033_876')
	supermarket.getChild('Arch_44__033_877')
	supermarket.getChild('Arch_44__033_878')
	supermarket.getChild('Arch_44__033_879')
	supermarket.getChild('Arch_44__033_880')
	supermarket.getChild('Arch_44__033_881')
	supermarket.getChild('Arch_44__033_882')
	supermarket.getChild('Arch_44__033_883')
	supermarket.getChild('Arch_44__033_884')
	supermarket.getChild('Arch_44__033_893')
	supermarket.getChild('Arch_44__033_908')
	supermarket.getChild('Arch_44__033_909')
	supermarket.getChild('Arch_44__033_910')
	supermarket.getChild('Arch_44__033_911')
	supermarket.getChild('Arch_44__033_912')
	supermarket.getChild('Arch_44__033_913')
	supermarket.getChild('Arch_44__033_914')
	supermarket.getChild('Arch_44__033_915')
	supermarket.getChild('Arch_44__033_924')
	supermarket.getChild('Arch_44__033_925')
	supermarket.getChild('Arch_44__033_926')
	supermarket.getChild('Arch_44__033_927')
	supermarket.getChild('Arch_44__033_928')
	supermarket.getChild('Arch_44__033_929')
	supermarket.getChild('Arch_44__033_930')
	supermarket.getChild('Arch_44__033_931')
	supermarket.getChild('Arch_44__033_942')
	supermarket.getChild('Arch_44__033_943')
	supermarket.getChild('Arch_44__033_944')
	supermarket.getChild('Arch_44__033_945')
	supermarket.getChild('Arch_44__033_946')
	supermarket.getChild('Arch_44__033_947')
	supermarket.getChild('Arch_44__033_948')
	supermarket.getChild('Arch_44__033_949')
	supermarket.getChild('Arch_44__033_950')
	supermarket.getChild('Arch_44__033_951')
	supermarket.getChild('Arch_44__033_953')
	supermarket.getChild('Arch_44__033_954')
	supermarket.getChild('Arch_44__033_955')
	supermarket.getChild('Arch_44__033_956')
	supermarket.getChild('Arch_44__033_957')
	supermarket.getChild('Arch_44__033_958')
	supermarket.getChild('Arch_44__033_959')
	supermarket.getChild('Arch_44__033_961')
	supermarket.getChild('Arch_44__033_971')
	supermarket.getChild('Arch_44__033_973')
	supermarket.getChild('Arch_44__033_974')
	supermarket.getChild('Arch_44__033_975')
	supermarket.getChild('Arch_44__033_976')
	supermarket.getChild('Arch_44__033_977')
	supermarket.getChild('Arch_44__033_978')
	supermarket.getChild('Arch_44__033_979')
	supermarket.getChild('Arch_44__033_988')
	supermarket.getChild('Arch_44__033_989')
	supermarket.getChild('Box121')
	supermarket.getChild('Arch_44__031_606')
	supermarket.getChild('Arch_44__031_607')
	supermarket.getChild('Arch_44__031_608')
	supermarket.getChild('Arch_44__031_612')
	supermarket.getChild('Arch_44__031_613')
	supermarket.getChild('Arch_44__031_616')
	supermarket.getChild('Arch_44__031_617')
	supermarket.getChild('Arch_44__031_618')
	supermarket.getChild('Arch_44__031_619')
	supermarket.getChild('Arch_44__031_620')
	supermarket.getChild('Arch_44__031_621')
	supermarket.getChild('Arch_44__031_622')
	supermarket.getChild('Arch_44__031_623')
	supermarket.getChild('Arch_44__031_624')
	supermarket.getChild('Arch_44__031_625')
	supermarket.getChild('Arch_44__031_626')
	supermarket.getChild('Arch_44__031_627')
	supermarket.getChild('Arch_44__031_628')
	supermarket.getChild('Arch_44__031_629')
	supermarket.getChild('Arch_44__031_630')
	supermarket.getChild('Arch_44__031_631')
	supermarket.getChild('Arch_44__031_632')
	supermarket.getChild('Arch_44__031_633')
	supermarket.getChild('Arch_44__031_634')
	supermarket.getChild('Arch_44__031_635')
	supermarket.getChild('Arch_44__031_636')
	supermarket.getChild('Arch_44__031_637')
	supermarket.getChild('Arch_44__031_638')
	supermarket.getChild('Arch_44__031_639')
	supermarket.getChild('Arch_44__031_640')
	supermarket.getChild('Arch_44__031_641')
	supermarket.getChild('Arch_44__031_642')
	supermarket.getChild('Arch_44__031_643')
	supermarket.getChild('Arch_44__031_644')
	supermarket.getChild('Arch_44__031_645')
	supermarket.getChild('Arch_44__031_646')
	supermarket.getChild('Arch_44__031_647')
	supermarket.getChild('Arch_44__031_648')
	supermarket.getChild('Arch_44__031_649')
	supermarket.getChild('Arch_44__031_650')
	supermarket.getChild('Arch_44__031_651')
	supermarket.getChild('Arch_44__031_652')
	supermarket.getChild('Arch_44__031_653')
	supermarket.getChild('Arch_44__031_654')
	supermarket.getChild('Arch_44__031_655')
	supermarket.getChild('Arch_44__031_662')
	supermarket.getChild('Arch_44__031_666')
	supermarket.getChild('Arch_44__031_670')
	supermarket.getChild('Arch_44__031_710')
	supermarket.getChild('Arch_44__031_711')
	supermarket.getChild('Arch_44__031_712')
	supermarket.getChild('Arch_44__031_713')
	supermarket.getChild('Arch_44__031_714')
	supermarket.getChild('Arch_44__031_715')
	supermarket.getChild('Arch_44__031_716')
	supermarket.getChild('Arch_44__031_717')
	supermarket.getChild('Arch_44__031_718')
	supermarket.getChild('Arch_44__031_719')
	supermarket.getChild('Arch_44__031_720')
	supermarket.getChild('Arch_44__031_721')
	supermarket.getChild('Arch_44__031_722')
	supermarket.getChild('Arch_44__031_723')
	supermarket.getChild('Arch_44__031_724')
	supermarket.getChild('Arch_44__031_725')
	supermarket.getChild('Arch_44__031_726')
	supermarket.getChild('Arch_44__031_727')
	supermarket.getChild('Arch_44__031_728')
	supermarket.getChild('Arch_44__031_729')
	supermarket.getChild('Arch_44__031_730')
	supermarket.getChild('Arch_44__031_731')
	supermarket.getChild('Arch_44__031_732')
	supermarket.getChild('Box122')
	supermarket.getChild('Arch_44__031_740')
	supermarket.getChild('Arch_44__031_741')
	supermarket.getChild('Arch_44__031_742')
	supermarket.getChild('Arch_44__507409978')
	supermarket.getChild('Arch_44__031_743')
	supermarket.getChild('Arch_44__031_744')
	supermarket.getChild('Arch_44__031_745')
	supermarket.getChild('Arch_44__031_746')
	supermarket.getChild('Arch_44__031_747')
	supermarket.getChild('Arch_44__031_748')
	supermarket.getChild('Arch_44__031_749')
	supermarket.getChild('Arch_44__031_750')
	supermarket.getChild('Arch_44__031_751')
	supermarket.getChild('Arch_44__031_752')
	supermarket.getChild('Arch_44__031_753')
	supermarket.getChild('Arch_44__031_754')
	supermarket.getChild('Arch_44__031_755')
	supermarket.getChild('Arch_44__031_756')
	supermarket.getChild('Arch_44__031_757')
	supermarket.getChild('Arch_44__031_758')
	supermarket.getChild('Arch_44__031_759')
	supermarket.getChild('Arch_44__031_760')
	supermarket.getChild('Arch_44__031_761')
	supermarket.getChild('Arch_44__031_762')
	supermarket.getChild('Arch_44__031_763')
	supermarket.getChild('Arch_44__031_764')
	supermarket.getChild('Arch_44__031_765')
	supermarket.getChild('Arch_44__031_766')
	supermarket.getChild('Arch_44__031_767')
	supermarket.getChild('Arch_44__031_768')
	supermarket.getChild('Arch_44__031_769')
	supermarket.getChild('Arch_44__031_770')
	supermarket.getChild('Arch_44__031_771')
	supermarket.getChild('Arch_44__031_772')
	supermarket.getChild('Arch_44__031_773')
	supermarket.getChild('Arch_44__031_774')
	supermarket.getChild('Arch_44__031_775')
	supermarket.getChild('Arch_44__031_776')
	supermarket.getChild('Arch_44__031_777')
	supermarket.getChild('Arch_44__031_778')
	supermarket.getChild('Arch_44__031_779')
	supermarket.getChild('Arch_44__031_780')
	supermarket.getChild('Arch_44__031_781')
	supermarket.getChild('Arch_44__031_782')
	supermarket.getChild('Arch_44__031_783')
	supermarket.getChild('Arch_44__031_784')
	supermarket.getChild('Arch_44__031_785')
	supermarket.getChild('Arch_44__031_786')
	supermarket.getChild('Arch_44__031_787')
	supermarket.getChild('Arch_44__031_788')
	supermarket.getChild('Arch_44__031_789')
	supermarket.getChild('Arch_44__031_790')
	supermarket.getChild('Arch_44__031_791')
	supermarket.getChild('Arch_44__031_792')
	supermarket.getChild('Arch_44__031_793')
	supermarket.getChild('Arch_44__031_794')
	supermarket.getChild('Arch_44__031_795')
	supermarket.getChild('Arch_44__031_796')
	supermarket.getChild('Arch_44__031_797')
	supermarket.getChild('Arch_44__031_798')
	supermarket.getChild('Arch_44__031_799')
	supermarket.getChild('Arch_44__031_800')
	supermarket.getChild('Arch_44__031_801')
	supermarket.getChild('Arch_44__031_802')
	supermarket.getChild('Arch_44__031_803')
	supermarket.getChild('Arch_44__031_804')
	supermarket.getChild('Arch_44__031_805')
	supermarket.getChild('Arch_44__031_806')
	supermarket.getChild('Arch_44__031_807')
	supermarket.getChild('Arch_44__031_808')
	supermarket.getChild('Arch_44__031_809')
	supermarket.getChild('Arch_44__031_810')
	supermarket.getChild('Arch_44__031_811')
	supermarket.getChild('Arch_44__031_812')
	supermarket.getChild('Arch_44__031_813')
	supermarket.getChild('Arch_44__031_814')
	supermarket.getChild('Arch_44__031_815')
	supermarket.getChild('Arch_44__031_816')
	supermarket.getChild('Arch_44__031_817')
	supermarket.getChild('Arch_44__031_818')
	supermarket.getChild('Arch_44__031_819')
	supermarket.getChild('Arch_44__031_820')
	supermarket.getChild('Arch_44__031_821')
	supermarket.getChild('Arch_44__031_822')
	supermarket.getChild('Arch_44__031_823')
	supermarket.getChild('Arch_44__031_824')
	supermarket.getChild('Arch_44__031_825')
	supermarket.getChild('Arch_44__031_826')
	supermarket.getChild('Arch_44__031_827')
	supermarket.getChild('Arch_44__031_828')
	supermarket.getChild('Arch_44__031_829')
	supermarket.getChild('Arch_44__031_830')
	supermarket.getChild('Arch_44__031_831')
	supermarket.getChild('Arch_44__031_832')
	supermarket.getChild('Arch_44__031_833')
	supermarket.getChild('Arch_44__031_834')
	supermarket.getChild('Arch_44__031_835')
	supermarket.getChild('Arch_44__031_836')
	supermarket.getChild('Arch_44__031_837')
	supermarket.getChild('Arch_44__031_838')
	supermarket.getChild('Arch_44__031_839')
	supermarket.getChild('Arch_44__031_840')
	supermarket.getChild('Arch_44__031_841')
	supermarket.getChild('Arch_44__031_842')
	supermarket.getChild('Arch_44__031_843')
	supermarket.getChild('Arch_44__031_844')
	supermarket.getChild('Arch_44__031_845')
	supermarket.getChild('Arch_44__031_846')
	supermarket.getChild('Arch_44__031_847')
	supermarket.getChild('Arch_44__031_848')
	supermarket.getChild('Arch_44__031_849')
	supermarket.getChild('Arch_44__031_850')
	supermarket.getChild('Arch_44__031_851')
	supermarket.getChild('Arch_44__031_852')
	supermarket.getChild('Arch_44__031_853')
	supermarket.getChild('Arch_44__031_854')
	supermarket.getChild('Arch_44__031_855')
	supermarket.getChild('Arch_44__031_856')
	supermarket.getChild('Arch_44__031_857')
	supermarket.getChild('Arch_44__031_858')
	supermarket.getChild('Arch_44__031_859')
	supermarket.getChild('Arch_44__031_860')
	supermarket.getChild('Arch_44__031_861')
	supermarket.getChild('Arch_44__031_862')
	supermarket.getChild('Arch_44__031_863')
	supermarket.getChild('Arch_44__031_864')
	supermarket.getChild('Arch_44__031_865')
	supermarket.getChild('Arch_44__031_866')
	supermarket.getChild('Arch_44__031_867')
	supermarket.getChild('Arch_44__031_868')
	supermarket.getChild('Arch_44__031_869')
	supermarket.getChild('Arch_44__031_870')
	supermarket.getChild('Arch_44__031_871')
	supermarket.getChild('Arch_44__031_872')
	supermarket.getChild('Arch_44__031_873')
	supermarket.getChild('Arch_44__031_874')
	supermarket.getChild('Arch_44__031_875')
	supermarket.getChild('Arch_44__031_876')
	supermarket.getChild('Arch_44__031_877')
	supermarket.getChild('Arch_44__031_878')
	supermarket.getChild('Arch_44__031_879')
	supermarket.getChild('Arch_44__031_880')
	supermarket.getChild('Arch_44__031_881')
	supermarket.getChild('Box123')
	supermarket.getChild('Arch_44__031_890')
	supermarket.getChild('Arch_44__031_891')
	supermarket.getChild('Arch_44__031_892')
	supermarket.getChild('Arch_44__031_896')
	supermarket.getChild('Arch_44__031_897')
	supermarket.getChild('Arch_44__031_900')
	supermarket.getChild('Arch_44__031_901')
	supermarket.getChild('Arch_44__031_902')
	supermarket.getChild('Arch_44__031_903')
	supermarket.getChild('Arch_44__031_904')
	supermarket.getChild('Arch_44__031_905')
	supermarket.getChild('Arch_44__031_906')
	supermarket.getChild('Arch_44__031_907')
	supermarket.getChild('Arch_44__031_908')
	supermarket.getChild('Arch_44__031_909')
	supermarket.getChild('Arch_44__031_910')
	supermarket.getChild('Arch_44__031_911')
	supermarket.getChild('Arch_44__031_912')
	supermarket.getChild('Arch_44__031_913')
	supermarket.getChild('Arch_44__031_914')
	supermarket.getChild('Arch_44__031_915')
	supermarket.getChild('Arch_44__031_916')
	supermarket.getChild('Arch_44__031_917')
	supermarket.getChild('Arch_44__031_918')
	supermarket.getChild('Arch_44__031_919')
	supermarket.getChild('Arch_44__031_920')
	supermarket.getChild('Arch_44__031_921')
	supermarket.getChild('Arch_44__031_922')
	supermarket.getChild('Arch_44__031_923')
	supermarket.getChild('Arch_44__031_924')
	supermarket.getChild('Arch_44__031_925')
	supermarket.getChild('Arch_44__031_926')
	supermarket.getChild('Arch_44__031_927')
	supermarket.getChild('Arch_44__031_928')
	supermarket.getChild('Arch_44__031_939')
	supermarket.getChild('Arch_44__031_946')
	supermarket.getChild('Arch_44__031_962')
	supermarket.getChild('Arch_44__031_963')
	supermarket.getChild('Arch_44__031_964')
	supermarket.getChild('Arch_44__031_965')
	supermarket.getChild('Arch_44__031_968')
	supermarket.getChild('Arch_44__031_969')
	supermarket.getChild('Arch_44__031_970')
	supermarket.getChild('Arch_44__031_985')
	supermarket.getChild('Arch_44__031_993')
	supermarket.getChild('Arch_44__031_995')
	supermarket.getChild('Arch_44__031_996')
	supermarket.getChild('Arch_44__031_997')
	supermarket.getChild('Arch_44__031_998')
	supermarket.getChild('Arch_44__031_1000')
	supermarket.getChild('Arch_44__031_1001')
	supermarket.getChild('Arch_44__031_1002')
	supermarket.getChild('Arch_44__031_1003')
	supermarket.getChild('Box124')
	supermarket.getChild('Arch_44__032_474')
	supermarket.getChild('Arch_44__032_475')
	supermarket.getChild('Arch_44__032_476')
	supermarket.getChild('Arch_44__032_477')
	supermarket.getChild('Arch_44__032_482')
	supermarket.getChild('Arch_44__032_483')
	supermarket.getChild('Arch_44__032_484')
	supermarket.getChild('Arch_44__032_485')
	supermarket.getChild('Arch_44__032_486')
	supermarket.getChild('Arch_44__032_491')
	supermarket.getChild('Arch_44__032_492')
	supermarket.getChild('Arch_44__032_495')
	supermarket.getChild('Arch_44__032_496')
	supermarket.getChild('Arch_44__032_509')
	supermarket.getChild('Arch_44__032_510')
	supermarket.getChild('Arch_44__032_511')
	supermarket.getChild('Arch_44__032_512')
	supermarket.getChild('Arch_44__032_513')
	supermarket.getChild('Arch_44__032_524')
	supermarket.getChild('Arch_44__032_525')
	supermarket.getChild('Arch_44__032_526')
	supermarket.getChild('Arch_44__032_527')
	supermarket.getChild('Arch_44__032_536')
	supermarket.getChild('Arch_44__032_537')
	supermarket.getChild('Box125')
	supermarket.getChild('Arch_44__032_544')
	supermarket.getChild('Arch_44__032_545')
	supermarket.getChild('Arch_44__032_546')
	supermarket.getChild('Arch_44__032_554')
	supermarket.getChild('Arch_44__032_555')
	supermarket.getChild('Arch_44__032_556')
	supermarket.getChild('Arch_44__032_559')
	supermarket.getChild('Arch_44__032_560')
	supermarket.getChild('Arch_44__032_563')
	supermarket.getChild('Arch_44__032_564')
	supermarket.getChild('Arch_44__032_565')
	supermarket.getChild('Arch_44__032_566')
	supermarket.getChild('Arch_44__032_567')
	supermarket.getChild('Arch_44__032_568')
	supermarket.getChild('Arch_44__032_569')
	supermarket.getChild('Arch_44__032_570')
	supermarket.getChild('Arch_44__032_571')
	supermarket.getChild('Arch_44__032_572')
	supermarket.getChild('Arch_44__032_573')
	supermarket.getChild('Arch_44__032_582')
	supermarket.getChild('Arch_44__032_585')
	supermarket.getChild('Arch_44__032_594')
	supermarket.getChild('Arch_44__032_597')
	supermarket.getChild('Arch_44__032_601')
	supermarket.getChild('Box126')
	supermarket.getChild('Arch_44__032_605')
	supermarket.getChild('Arch_44__032_606')
	supermarket.getChild('Arch_44__032_607')
	supermarket.getChild('Arch_44__032_608')
	supermarket.getChild('Arch_44__032_609')
	supermarket.getChild('Arch_44__032_613')
	supermarket.getChild('Arch_44__032_614')
	supermarket.getChild('Arch_44__032_615')
	supermarket.getChild('Arch_44__032_616')
	supermarket.getChild('Arch_44__032_617')
	supermarket.getChild('Arch_44__032_618')
	supermarket.getChild('Arch_44__032_619')
	supermarket.getChild('Arch_44__032_623')
	supermarket.getChild('Arch_44__032_624')
	supermarket.getChild('Arch_44__032_627')
	supermarket.getChild('Arch_44__032_628')
	supermarket.getChild('Arch_44__032_629')
	supermarket.getChild('Arch_44__032_640')
	supermarket.getChild('Arch_44__032_641')
	supermarket.getChild('Arch_44__032_642')
	supermarket.getChild('Arch_44__032_643')
	supermarket.getChild('Arch_44__032_644')
	supermarket.getChild('Arch_44__032_645')
	supermarket.getChild('Arch_44__032_646')
	supermarket.getChild('Arch_44__032_647')
	supermarket.getChild('Arch_44__032_652')
	supermarket.getChild('Arch_44__032_656')
	supermarket.getChild('Arch_44__032_659')
	supermarket.getChild('Arch_44__032_668')
	supermarket.getChild('Box127')
	supermarket.getChild('Arch_44__030_399')
	supermarket.getChild('Arch_44__030_401')
	supermarket.getChild('Arch_44__030_402')
	supermarket.getChild('Arch_44__030_403')
	supermarket.getChild('Arch_44__030_407')
	supermarket.getChild('Arch_44__030_411')
	supermarket.getChild('Arch_44__030_416')
	supermarket.getChild('Arch_44__030_421')
	supermarket.getChild('Arch_44__030_425')
	supermarket.getChild('Arch_44__030_426')
	supermarket.getChild('Arch_44__030_430')
	supermarket.getChild('Arch_44__030_435')
	supermarket.getChild('Arch_44__030_436')
	supermarket.getChild('Arch_44__030_437')
	supermarket.getChild('Arch_44__030_441')
	supermarket.getChild('Arch_44__030_442')
	supermarket.getChild('Arch_44__030_443')
	supermarket.getChild('Arch_44__030_447')
	supermarket.getChild('Arch_44__030_451')
	supermarket.getChild('Arch_44__030_452')
	supermarket.getChild('Arch_44__030_456')
	supermarket.getChild('Arch_44__030_459')
	supermarket.getChild('Arch_44__030_460')
	supermarket.getChild('Arch_44__030_472')
	supermarket.getChild('Arch_44__030_473')
	supermarket.getChild('Arch_44__030_479')
	supermarket.getChild('Arch_44__030_480')
	supermarket.getChild('Arch_44__030_481')
	supermarket.getChild('Box128')
	supermarket.getChild('Arch_44__030_483')
	supermarket.getChild('Arch_44__030_484')
	supermarket.getChild('Arch_44__030_485')
	supermarket.getChild('Arch_44__031_1029')
	supermarket.getChild('Arch_44__031_1047')
	supermarket.getChild('Arch_44__031_1051')
	supermarket.getChild('Arch_44__031_1052')
	supermarket.getChild('Arch_44__031_1053')
	supermarket.getChild('Arch_44__031_1055')
	supermarket.getChild('Arch_44__031_1056')
	supermarket.getChild('Arch_44__031_1057')
	supermarket.getChild('Arch_44__031_1059')
	supermarket.getChild('Arch_44__031_1060')
	supermarket.getChild('Arch_44__031_1061')
	supermarket.getChild('Arch_44__031_1078')
	supermarket.getChild('Arch_44__032_674')
	supermarket.getChild('Arch_44__032_675')
	supermarket.getChild('Arch_44__032_676')
	supermarket.getChild('Arch_44__032_678')
	supermarket.getChild('Arch_44__032_679')
	supermarket.getChild('Arch_44__032_692')
	supermarket.getChild('Arch_44__031_1081')
	supermarket.getChild('Arch_44__031_1084')
	supermarket.getChild('Arch_44__031_1085')
	supermarket.getChild('Arch_44__031_1087')
	supermarket.getChild('Arch_44__031_1088')
	supermarket.getChild('Arch_44__031_1090')
	supermarket.getChild('Arch_44__031_1093')
	supermarket.getChild('Arch_44__031_1096')
	supermarket.getChild('Arch_44__031_1099')
	supermarket.getChild('Arch_44__031_1105')
	supermarket.getChild('Box129')
	supermarket.getChild('Arch_44__031_1112')
	supermarket.getChild('Arch_44__031_1134')
	supermarket.getChild('Arch_44__031_1138')
	supermarket.getChild('Arch_44__032_704')
	supermarket.getChild('Arch_44__032_705')
	supermarket.getChild('Arch_44__032_708')
	supermarket.getChild('Arch_44__032_709')
	supermarket.getChild('Arch_44__031_1167')
	supermarket.getChild('Arch_44__031_1176')
	supermarket.getChild('Arch_44__031_1188')
	supermarket.getChild('Box130')
	supermarket.getChild('Arch_44__031_1198')
	supermarket.getChild('Arch_44__031_1205')
	supermarket.getChild('Arch_44__031_1209')
	supermarket.getChild('Arch_44__031_1210')
	supermarket.getChild('Arch_44__031_1211')
	supermarket.getChild('Arch_44__031_1212')
	supermarket.getChild('Arch_44__031_1221')
	supermarket.getChild('Arch_44__031_1222')
	supermarket.getChild('Arch_44__031_1223')
	supermarket.getChild('Arch_44__031_1224')
	supermarket.getChild('Arch_44__031_1225')
	supermarket.getChild('Arch_44__031_1226')
	supermarket.getChild('Arch_44__031_1227')
	supermarket.getChild('Arch_44__031_1228')
	supermarket.getChild('Arch_44__031_1229')
	supermarket.getChild('Arch_44__032_740')
	supermarket.getChild('Arch_44__032_743')
	supermarket.getChild('Arch_44__032_744')
	supermarket.getChild('Arch_44__032_745')
	supermarket.getChild('Arch_44__032_747')
	supermarket.getChild('Arch_44__032_748')
	supermarket.getChild('Arch_44__032_749')
	supermarket.getChild('Arch_44__032_750')
	supermarket.getChild('Arch_44__031_1230')
	supermarket.getChild('Arch_44__032_751')
	supermarket.getChild('Arch_44__032_752')
	supermarket.getChild('Arch_44__032_753')
	supermarket.getChild('Arch_44__032_755')
	supermarket.getChild('Arch_44__032_759')
	supermarket.getChild('Arch_44__032_760')
	supermarket.getChild('Arch_44__031_1256')
	supermarket.getChild('Arch_44__031_1257')
	supermarket.getChild('Arch_44__031_1260')
	supermarket.getChild('Arch_44__031_1263')
	supermarket.getChild('Arch_44__031_1267')
	supermarket.getChild('Arch_44__031_1270')
	supermarket.getChild('Arch_44__031_1272')
	supermarket.getChild('Arch_44__031_1273')
	supermarket.getChild('Arch_44__031_1275')
	supermarket.getChild('Arch_44__031_1278')
	supermarket.getChild('Arch_44__031_1280')
	supermarket.getChild('Box131')
	supermarket.getChild('Arch_44__033_996')
	supermarket.getChild('Arch_44__033_997')
	supermarket.getChild('Arch_44__033_998')
	supermarket.getChild('Arch_44__033_999')
	supermarket.getChild('Arch_44__033_1000')
	supermarket.getChild('Arch_44__033_1001')
	supermarket.getChild('Arch_44__033_1002')
	supermarket.getChild('Arch_44__033_1003')
	supermarket.getChild('Arch_44__033_1004')
	supermarket.getChild('Arch_44__033_1013')
	supermarket.getChild('Arch_44__033_1014')
	supermarket.getChild('Arch_44__033_1015')
	supermarket.getChild('Arch_44__033_1016')
	supermarket.getChild('Arch_44__033_1017')
	supermarket.getChild('Arch_44__033_1018')
	supermarket.getChild('Arch_44__033_1019')
	supermarket.getChild('Arch_44__033_1020')
	supermarket.getChild('Arch_44__033_1021')
	supermarket.getChild('Arch_44__033_1022')
	supermarket.getChild('Arch_44__033_1023')
	supermarket.getChild('Arch_44__033_1024')
	supermarket.getChild('Arch_44__033_1025')
	supermarket.getChild('Arch_44__033_1026')
	supermarket.getChild('Arch_44__033_1027')
	supermarket.getChild('Arch_44__033_1028')
	supermarket.getChild('Arch_44__033_1029')
	supermarket.getChild('Arch_44__033_1030')
	supermarket.getChild('Arch_44__033_1031')
	supermarket.getChild('Arch_44__033_1042')
	supermarket.getChild('Arch_44__033_1049')
	supermarket.getChild('Arch_44__033_1050')
	supermarket.getChild('Arch_44__033_1051')
	supermarket.getChild('Arch_44__033_1052')
	supermarket.getChild('Arch_44__033_1053')
	supermarket.getChild('Arch_44__033_1054')
	supermarket.getChild('Arch_44__033_1055')
	supermarket.getChild('Arch_44__033_1056')
	supermarket.getChild('Arch_44__033_1057')
	supermarket.getChild('Arch_44__033_1061')
	supermarket.getChild('Arch_44__033_1062')
	supermarket.getChild('Arch_44__033_1063')
	supermarket.getChild('Arch_44__033_1064')
	supermarket.getChild('Arch_44__033_1065')
	supermarket.getChild('Arch_44__033_1066')
	supermarket.getChild('Arch_44__033_1067')
	supermarket.getChild('Arch_44__033_1068')
	supermarket.getChild('Arch_44__033_1069')
	supermarket.getChild('Arch_44__033_1070')
	supermarket.getChild('Arch_44__033_1075')
	supermarket.getChild('Arch_44__033_1079')
	supermarket.getChild('Arch_44__033_1080')
	supermarket.getChild('Arch_44__033_1081')
	supermarket.getChild('Arch_44__033_1082')
	supermarket.getChild('Arch_44__033_1083')
	supermarket.getChild('Arch_44__033_1085')
	supermarket.getChild('Arch_44__033_1090')
	supermarket.getChild('Arch_44__033_1091')
	supermarket.getChild('Arch_44__033_1092')
	supermarket.getChild('Arch_44__033_1093')
	supermarket.getChild('Arch_44__033_1094')
	supermarket.getChild('Arch_44__033_1095')
	supermarket.getChild('Arch_44__033_1096')
	supermarket.getChild('Arch_44__033_1097')
	supermarket.getChild('Arch_44__033_1098')
	supermarket.getChild('Arch_44__033_1106')
	supermarket.getChild('Arch_44__033_1107')
	supermarket.getChild('Arch_44__033_1108')
	supermarket.getChild('Arch_44__033_1109')
	supermarket.getChild('Arch_44__033_1110')
	supermarket.getChild('Arch_44__033_1111')
	supermarket.getChild('Arch_44__033_1112')
	supermarket.getChild('Arch_44__033_1113')
	supermarket.getChild('Arch_44__033_1114')
	supermarket.getChild('Arch_44__033_1122')
	supermarket.getChild('Arch_44__033_1123')
	supermarket.getChild('Arch_44__033_1124')
	supermarket.getChild('Arch_44__033_1125')
	supermarket.getChild('Arch_44__033_1126')
	supermarket.getChild('Arch_44__033_1127')
	supermarket.getChild('Arch_44__033_1128')
	supermarket.getChild('Arch_44__033_1129')
	supermarket.getChild('Arch_44__033_1130')
	supermarket.getChild('Arch_44__033_1131')
	supermarket.getChild('Arch_44__033_1132')
	supermarket.getChild('Arch_44__033_1142')
	supermarket.getChild('Arch_44__033_1152')
	supermarket.getChild('Arch_44__033_1153')
	supermarket.getChild('Arch_44__033_1154')
	supermarket.getChild('Arch_44__033_1155')
	supermarket.getChild('Arch_44__033_1156')
	supermarket.getChild('Arch_44__033_1157')
	supermarket.getChild('Arch_44__033_1158')
	supermarket.getChild('Arch_44__033_1159')
	supermarket.getChild('Arch_44__033_1160')
	supermarket.getChild('Arch_44__033_1161')
	supermarket.getChild('Arch_44__033_1162')
	supermarket.getChild('Arch_44__033_1169')
	supermarket.getChild('Arch_44__033_1170')
	supermarket.getChild('Arch_44__033_1171')
	supermarket.getChild('Arch_44__033_1172')
	supermarket.getChild('Arch_44__033_1173')
	supermarket.getChild('Arch_44__033_1174')
	supermarket.getChild('Arch_44__033_1175')
	supermarket.getChild('Arch_44__033_1176')
	supermarket.getChild('Arch_44__033_1177')
	supermarket.getChild('Arch_44__033_1178')
	supermarket.getChild('Box132')
	supermarket.getChild('Arch_44__031_1281')
	supermarket.getChild('Arch_44__031_1282')
	supermarket.getChild('Arch_44__031_1283')
	supermarket.getChild('Arch_44__031_1284')
	supermarket.getChild('Arch_44__031_1285')
	supermarket.getChild('Arch_44__031_1286')
	supermarket.getChild('Arch_44__031_1287')
	supermarket.getChild('Arch_44__031_1288')
	supermarket.getChild('Arch_44__031_1291')
	supermarket.getChild('Arch_44__031_1292')
	supermarket.getChild('Arch_44__031_1293')
	supermarket.getChild('Arch_44__031_1294')
	supermarket.getChild('Arch_44__031_1297')
	supermarket.getChild('Arch_44__031_1298')
	supermarket.getChild('Arch_44__031_1332')
	supermarket.getChild('Arch_44__031_1337')
	supermarket.getChild('Arch_44__031_1339')
	supermarket.getChild('Arch_44__031_1340')
	supermarket.getChild('Arch_44__031_1341')
	supermarket.getChild('Arch_44__031_1353')
	supermarket.getChild('Arch_44__031_1354')
	supermarket.getChild('Arch_44__031_1355')
	supermarket.getChild('Arch_44__031_1356')
	supermarket.getChild('Arch_44__031_1357')
	supermarket.getChild('Arch_44__031_1361')
	supermarket.getChild('Arch_44__031_1365')
	supermarket.getChild('Arch_44__031_1369')
	supermarket.getChild('Arch_44__031_1385')
	supermarket.getChild('Arch_44__031_1386')
	supermarket.getChild('Arch_44__031_1387')
	supermarket.getChild('Arch_44__031_1388')
	supermarket.getChild('Arch_44__031_1389')
	supermarket.getChild('Arch_44__031_1390')
	supermarket.getChild('Arch_44__031_1391')
	supermarket.getChild('Arch_44__031_1392')
	supermarket.getChild('Arch_44__031_1398')
	supermarket.getChild('Arch_44__031_1403')
	supermarket.getChild('Arch_44__031_1404')
	supermarket.getChild('Arch_44__031_1416')
	supermarket.getChild('Arch_44__031_1417')
	supermarket.getChild('Arch_44__031_1418')
	supermarket.getChild('Arch_44__031_1419')
	supermarket.getChild('Arch_44__031_1421')
	supermarket.getChild('Arch_44__031_1422')
	supermarket.getChild('Box133')
	supermarket.getChild('Arch_44__031_1423')
	supermarket.getChild('Arch_44__031_1427')
	supermarket.getChild('Arch_44__031_1430')
	supermarket.getChild('Arch_44__031_1437')
	supermarket.getChild('Arch_44__031_1438')
	supermarket.getChild('Arch_44__031_1439')
	supermarket.getChild('Arch_44__031_1440')
	supermarket.getChild('Arch_44__031_1441')
	supermarket.getChild('Arch_44__031_1442')
	supermarket.getChild('Arch_44__031_1444')
	supermarket.getChild('Arch_44__031_1449')
	supermarket.getChild('Arch_44__031_1454')
	supermarket.getChild('Arch_44__031_1456')
	supermarket.getChild('Arch_44__031_1457')
	supermarket.getChild('Arch_44__031_1458')
	supermarket.getChild('Arch_44__031_1459')
	supermarket.getChild('Arch_44__031_1460')
	supermarket.getChild('Arch_44__031_1461')
	supermarket.getChild('Arch_44__031_1462')
	supermarket.getChild('Arch_44__031_1463')
	supermarket.getChild('Arch_44__031_1464')
	supermarket.getChild('Arch_44__031_1465')
	supermarket.getChild('Arch_44__031_1467')
	supermarket.getChild('Arch_44__032_761')
	supermarket.getChild('Arch_44__032_768')
	supermarket.getChild('Arch_44__032_769')
	supermarket.getChild('Arch_44__032_770')
	supermarket.getChild('Arch_44__032_776')
	supermarket.getChild('Arch_44__032_777')
	supermarket.getChild('Arch_44__032_778')
	supermarket.getChild('Arch_44__032_779')
	supermarket.getChild('Arch_44__031_1479')
	supermarket.getChild('Arch_44__031_1480')
	supermarket.getChild('Arch_44__032_780')
	supermarket.getChild('Arch_44__031_1481')
	supermarket.getChild('Arch_44__031_1482')
	supermarket.getChild('Arch_44__032_782')
	supermarket.getChild('Arch_44__031_1483')
	supermarket.getChild('Arch_44__031_1484')
	supermarket.getChild('Arch_44__031_1485')
	supermarket.getChild('Arch_44__031_1486')
	supermarket.getChild('Arch_44__031_1489')
	supermarket.getChild('Arch_44__031_1490')
	supermarket.getChild('Arch_44__031_1491')
	supermarket.getChild('Arch_44__031_1492')
	supermarket.getChild('Arch_44__031_1493')
	supermarket.getChild('Arch_44__031_1494')
	supermarket.getChild('Arch_44__031_1496')
	supermarket.getChild('Arch_44__032_792')
	supermarket.getChild('Arch_44__031_1505')
	supermarket.getChild('Arch_44__031_1507')
	supermarket.getChild('Arch_44__031_1512')
	supermarket.getChild('Arch_44__031_1513')
	supermarket.getChild('Arch_44__031_1515')
	supermarket.getChild('Arch_44__031_1517')
	supermarket.getChild('Arch_44__031_1518')
	supermarket.getChild('Arch_44__031_1519')
	supermarket.getChild('Arch_44__031_1520')
	supermarket.getChild('Arch_44__031_1521')
	supermarket.getChild('Arch_44__030_491')
	supermarket.getChild('Arch_44__030_492')
	supermarket.getChild('Arch_44__030_493')
	supermarket.getChild('Arch_44__030_494')
	supermarket.getChild('Arch_44__031_1522')
	supermarket.getChild('Arch_44__031_1523')
	supermarket.getChild('Arch_44__031_1525')
	supermarket.getChild('Arch_44__031_1527')
	supermarket.getChild('Arch_44__031_1528')
	supermarket.getChild('Arch_44__031_1529')
	supermarket.getChild('Arch_44__031_1530')
	supermarket.getChild('Arch_44__031_1531')
	supermarket.getChild('Arch_44__031_1532')
	supermarket.getChild('Arch_44__031_1533')
	supermarket.getChild('Arch_44__031_1534')
	supermarket.getChild('Arch_44__031_1535')
	supermarket.getChild('Arch_44__031_1536')
	supermarket.getChild('Arch_44__031_1537')
	supermarket.getChild('Arch_44__031_1538')
	supermarket.getChild('Arch_44__031_1539')
	supermarket.getChild('Arch_44__031_1540')
	supermarket.getChild('Arch_44__031_1541')
	supermarket.getChild('Arch_44__031_1545')
	supermarket.getChild('Arch_44__031_1546')
	supermarket.getChild('Arch_44__031_1553')
	supermarket.getChild('Arch_44__031_1554')
	supermarket.getChild('Arch_44__031_1555')
	supermarket.getChild('Arch_44__031_1556')
	supermarket.getChild('Arch_44__031_1557')
	supermarket.getChild('Arch_44__031_1558')
	supermarket.getChild('Arch_44__031_1560')
	supermarket.getChild('Arch_44__031_1562')
	supermarket.getChild('Arch_44__031_1564')
	supermarket.getChild('Arch_44__031_1565')
	supermarket.getChild('Box134')
	supermarket.getChild('Box135')
	supermarket.getChild('Arch_44__031_1594')
	supermarket.getChild('Arch_44__031_1595')
	supermarket.getChild('Arch_44__031_1596')
	supermarket.getChild('Arch_44__031_1597')
	supermarket.getChild('Arch_44__031_1607')
	supermarket.getChild('Arch_44__031_1608')
	supermarket.getChild('Arch_44__031_1609')
	supermarket.getChild('Arch_44__031_1610')
	supermarket.getChild('Arch_44__031_1611')
	supermarket.getChild('Arch_44__031_1612')
	supermarket.getChild('Arch_44__031_1613')
	supermarket.getChild('Arch_44__031_1614')
	supermarket.getChild('Arch_44__031_1615')
	supermarket.getChild('Arch_44__031_1635')
	supermarket.getChild('Arch_44__031_1637')
	supermarket.getChild('Arch_44__031_1639')
	supermarket.getChild('Arch_44__031_1662')
	supermarket.getChild('Arch_44__031_1663')
	supermarket.getChild('Arch_44__031_1664')
	supermarket.getChild('Arch_44__031_1665')
	supermarket.getChild('Arch_44__031_1666')
	supermarket.getChild('Arch_44__031_1670')
	supermarket.getChild('Arch_44__031_1671')
	supermarket.getChild('Arch_44__031_1672')
	supermarket.getChild('Arch_44__031_1673')
	supermarket.getChild('Arch_44__031_1674')
	supermarket.getChild('Arch_44__031_1675')
	supermarket.getChild('Arch_44__031_1676')
	supermarket.getChild('Arch_44__031_1677')
	supermarket.getChild('Arch_44__031_1678')
	supermarket.getChild('Arch_44__031_1679')
	supermarket.getChild('Arch_44__031_1680')
	supermarket.getChild('Arch_44__031_1681')
	supermarket.getChild('Arch_44__031_1682')
	supermarket.getChild('Arch_44__031_1688')
	supermarket.getChild('Arch_44__031_1689')
	supermarket.getChild('Arch_44__031_1690')
	supermarket.getChild('Arch_44__031_1691')
	supermarket.getChild('Arch_44__031_1692')
	supermarket.getChild('Arch_44__031_1693')
	supermarket.getChild('Arch_44__031_1694')
	supermarket.getChild('Arch_44__031_1702')
	supermarket.getChild('Arch_44__031_1704')
	supermarket.getChild('Arch_44__031_1706')
	supermarket.getChild('Arch_44__031_1709')
	supermarket.getChild('Arch_44__031_1710')
	supermarket.getChild('Arch_44__031_1711')
	supermarket.getChild('Arch_44__031_1712')
	supermarket.getChild('Arch_44__031_1714')
	supermarket.getChild('Arch_44__031_1717')
	supermarket.getChild('Arch_44__031_1723')
	supermarket.getChild('Arch_44__031_1724')
	supermarket.getChild('Arch_44__031_1725')
	supermarket.getChild('Arch_44__031_1726')
	supermarket.getChild('Arch_44__031_1727')
	supermarket.getChild('Arch_44__031_1728')
	supermarket.getChild('Box136')
	supermarket.getChild('Box137')
	supermarket.getChild('Arch_44__030_511')
	supermarket.getChild('Arch_44__030_512')
	supermarket.getChild('Arch_44__030_513')
	supermarket.getChild('Arch_44__030_514')
	supermarket.getChild('Arch_44__030_515')
	supermarket.getChild('Arch_44__030_523')
	supermarket.getChild('Arch_44__030_524')
	supermarket.getChild('Arch_44__030_525')
	supermarket.getChild('Arch_44__030_526')
	supermarket.getChild('Arch_44__033_1182')
	supermarket.getChild('Arch_44__033_1183')
	supermarket.getChild('Arch_44__033_1184')
	supermarket.getChild('Arch_44__033_1185')
	supermarket.getChild('Arch_44__033_1186')
	supermarket.getChild('Arch_44__033_1187')
	supermarket.getChild('Arch_44__033_1188')
	supermarket.getChild('Arch_44__033_1189')
	supermarket.getChild('Arch_44__033_1190')
	supermarket.getChild('Arch_44__033_1197')
	supermarket.getChild('Arch_44__031_1737')
	supermarket.getChild('Arch_44__031_1738')
	supermarket.getChild('Arch_44__031_1739')
	supermarket.getChild('Arch_44__031_1740')
	supermarket.getChild('Arch_44__031_1741')
	supermarket.getChild('Arch_44__031_1742')
	supermarket.getChild('Arch_44__031_1743')
	supermarket.getChild('Arch_44__031_1744')
	supermarket.getChild('Arch_44__021_653')
	supermarket.getChild('Arch_44__021_654')
	supermarket.getChild('Arch_44__021_655')
	supermarket.getChild('Arch_44__021_656')
	supermarket.getChild('Arch_44__021_657')
	supermarket.getChild('Arch_44__021_658')
	supermarket.getChild('Arch_44__021_659')
	supermarket.getChild('Arch_44__021_660')
	supermarket.getChild('Arch_44__021_661')
	supermarket.getChild('Arch_44__021_662')
	supermarket.getChild('Arch_44__021_663')
	supermarket.getChild('Arch_44__021_664')
	supermarket.getChild('Arch_44__021_665')
	supermarket.getChild('Arch_44__021_666')
	supermarket.getChild('Arch_44__021_667')
	supermarket.getChild('Arch_44__021_668')
	supermarket.getChild('Arch_44__021_669')
	supermarket.getChild('Arch_44__021_670')
	supermarket.getChild('Arch_44__021_671')
	supermarket.getChild('Arch_44__021_672')
	supermarket.getChild('Arch_44__021_673')
	supermarket.getChild('Arch_44__021_674')
	supermarket.getChild('Arch_44__021_675')
	supermarket.getChild('Arch_44__021_676')
	supermarket.getChild('Arch_44__021_677')
	supermarket.getChild('Arch_44__021_678')
	supermarket.getChild('Arch_44__032_793')
	supermarket.getChild('Arch_44__031_1745')
	supermarket.getChild('Arch_44__011_263')
	supermarket.getChild('Arch_44__011_264')
	supermarket.getChild('Arch_44__011_265')
	supermarket.getChild('Arch_44__011_266')
	supermarket.getChild('Arch_44__011_267')
	supermarket.getChild('Arch_44__011_268')
	supermarket.getChild('Arch_44__011_269')
	supermarket.getChild('Arch_44__011_270')
	supermarket.getChild('Arch_44__011_271')
	supermarket.getChild('Arch_44__011_272')
	supermarket.getChild('Arch_44__011_273')
	supermarket.getChild('Arch_44__011_274')
	supermarket.getChild('Arch_44__011_275')
	supermarket.getChild('Arch_44__011_276')
	supermarket.getChild('Arch_44__011_277')
	supermarket.getChild('Arch_44__011_278')
	supermarket.getChild('Arch_44__011_279')
	supermarket.getChild('Arch_44__011_280')
	supermarket.getChild('Arch_44__011_281')
	supermarket.getChild('Arch_44__011_282')
	supermarket.getChild('Arch_44__011_283')
	supermarket.getChild('Arch_44__011_284')
	supermarket.getChild('Arch_44__011_285')
	supermarket.getChild('Arch_44__011_286')
	supermarket.getChild('Arch_44__011_287')
	supermarket.getChild('Arch_44__011_289')
	supermarket.getChild('Arch_44__011_290')
	supermarket.getChild('Arch_44__011_292')
	supermarket.getChild('Arch_44__011_293')
	supermarket.getChild('Arch_44__011_295')
	supermarket.getChild('Arch_44__011_296')
	supermarket.getChild('Arch_44__011_298')
	supermarket.getChild('Arch_44__011_299')
	supermarket.getChild('Arch_44__011_302')
	supermarket.getChild('Arch_44__011_305')
	supermarket.getChild('Arch_44__011_308')
	supermarket.getChild('Arch_44__011_311')
	supermarket.getChild('Arch_44__011_314')
	supermarket.getChild('Arch_44__011_315')
	supermarket.getChild('Arch_44__011_318')
	supermarket.getChild('Arch_44__011_319')
	supermarket.getChild('Arch_44__011_320')
	supermarket.getChild('Arch_44__011_321')
	supermarket.getChild('Arch_44__011_322')
	supermarket.getChild('Arch_44__011_323')
	supermarket.getChild('Arch_44__011_324')
	supermarket.getChild('Arch_44__011_325')
	supermarket.getChild('Arch_44__011_326')
	supermarket.getChild('Arch_44__011_327')
	supermarket.getChild('Arch_44__011_328')
	supermarket.getChild('Arch_44__011_329')
	supermarket.getChild('Arch_44__011_330')
	supermarket.getChild('Arch_44__011_331')
	supermarket.getChild('Arch_44__011_334')
	supermarket.getChild('Arch_44__011_335')
	supermarket.getChild('Arch_44__011_336')
	supermarket.getChild('Arch_44__011_337')
	supermarket.getChild('Arch_44__011_340')
	supermarket.getChild('Arch_44__011_342')
	supermarket.getChild('Arch_44__011_343')
	supermarket.getChild('Arch_44__011_349')
	supermarket.getChild('Arch_44__011_362')
	supermarket.getChild('Arch_44__011_363')
	supermarket.getChild('Arch_44__011_364')
	supermarket.getChild('Arch_44__011_365')
	supermarket.getChild('Arch_44__011_366')
	supermarket.getChild('Arch_44__011_367')
	supermarket.getChild('Arch_44__011_368')
	supermarket.getChild('Arch_44__011_369')
	supermarket.getChild('Arch_44__011_370')
	supermarket.getChild('Arch_44__011_371')
	supermarket.getChild('Arch_44__011_372')
	supermarket.getChild('Arch_44__011_373')
	supermarket.getChild('Arch_44__011_374')
	supermarket.getChild('Arch_44__011_375')
	supermarket.getChild('Arch_44__011_376')
	supermarket.getChild('Arch_44__011_377')
	supermarket.getChild('Arch_44__011_378')
	supermarket.getChild('Arch_44__011_379')
	supermarket.getChild('Arch_44__011_380')
	supermarket.getChild('Arch_44__011_381')
	supermarket.getChild('Arch_44__011_382')
	supermarket.getChild('Arch_44__011_383')
	supermarket.getChild('Arch_44__011_384')
	supermarket.getChild('Arch_44__011_385')
	supermarket.getChild('Arch_44__011_386')
	supermarket.getChild('Arch_44__011_387')
	supermarket.getChild('Arch_44__011_388')
	supermarket.getChild('Arch_44__011_389')
	supermarket.getChild('Arch_44__011_390')
	supermarket.getChild('Arch_44__011_391')
	supermarket.getChild('Arch_44__011_392')
	supermarket.getChild('Arch_44__011_393')
	supermarket.getChild('Arch_44__011_394')
	supermarket.getChild('Arch_44__011_395')
	supermarket.getChild('Arch_44__011_396')
	supermarket.getChild('Arch_44__011_397')
	supermarket.getChild('Arch_44__011_398')
	supermarket.getChild('Arch_44__011_399')
	supermarket.getChild('Arch_44__011_400')
	supermarket.getChild('Arch_44__011_401')
	supermarket.getChild('Arch_44__011_402')
	supermarket.getChild('Arch_44__011_403')
	supermarket.getChild('Arch_44__011_404')
	supermarket.getChild('Arch_44__011_405')
	supermarket.getChild('Arch_44__011_406')
	supermarket.getChild('Arch_44__011_407')
	supermarket.getChild('Arch_44__011_408')
	supermarket.getChild('Arch_44__011_409')
	supermarket.getChild('Arch_44__011_410')
	supermarket.getChild('Arch_44__011_411')
	supermarket.getChild('Arch_44__011_412')
	supermarket.getChild('Arch_44__011_413')
	supermarket.getChild('Arch_44__011_414')
	supermarket.getChild('Arch_44__011_415')
	supermarket.getChild('Arch_44__032_794')
	supermarket.getChild('Arch_44__032_795')
	supermarket.getChild('Arch_44__032_796')
	supermarket.getChild('Arch_44__032_797')
	supermarket.getChild('Arch_44__032_804')
	supermarket.getChild('Arch_44__032_805')
	supermarket.getChild('Arch_44__032_806')
	supermarket.getChild('Arch_44__032_807')
	supermarket.getChild('Arch_44__032_808')
	supermarket.getChild('Arch_44__011_416')
	supermarket.getChild('Arch_44__011_417')
	supermarket.getChild('Arch_44__011_418')
	supermarket.getChild('Arch_44__011_419')
	supermarket.getChild('Arch_44__011_420')
	supermarket.getChild('Arch_44__011_421')
	supermarket.getChild('Arch_44__011_422')
	supermarket.getChild('Arch_44__011_423')
	supermarket.getChild('Arch_44__011_424')
	supermarket.getChild('Arch_44__011_425')
	supermarket.getChild('Arch_44__011_426')
	supermarket.getChild('Arch_44__011_427')
	supermarket.getChild('Arch_44__011_428')
	supermarket.getChild('Arch_44__011_429')
	supermarket.getChild('Arch_44__011_430')
	supermarket.getChild('Arch_44__011_431')
	supermarket.getChild('Arch_44__011_432')
	supermarket.getChild('Arch_44__011_433')
	supermarket.getChild('Arch_44__011_434')
	supermarket.getChild('Arch_44__011_435')
	supermarket.getChild('Arch_44__011_436')
	supermarket.getChild('Arch_44__011_437')
	supermarket.getChild('Arch_44__011_438')
	supermarket.getChild('Arch_44__011_439')
	supermarket.getChild('Arch_44__011_440')
	supermarket.getChild('Arch_44__011_441')
	supermarket.getChild('Arch_44__011_442')
	supermarket.getChild('Arch_44__011_443')
	supermarket.getChild('Arch_44__011_444')
	supermarket.getChild('Arch_44__011_445')
	supermarket.getChild('Arch_44__011_446')
	supermarket.getChild('Arch_44__011_447')
	supermarket.getChild('Arch_44__011_448')
	supermarket.getChild('Arch_44__011_449')
	supermarket.getChild('Arch_44__011_450')
	supermarket.getChild('Arch_44__011_451')
	supermarket.getChild('Arch_44__011_452')
	supermarket.getChild('Arch_44__011_453')
	supermarket.getChild('Arch_44__011_454')
	supermarket.getChild('Arch_44__011_455')
	supermarket.getChild('Arch_44__011_456')
	supermarket.getChild('Arch_44__011_457')
	supermarket.getChild('Arch_44__011_458')
	supermarket.getChild('Arch_44__011_459')
	supermarket.getChild('Arch_44__011_460')
	supermarket.getChild('Arch_44__011_461')
	supermarket.getChild('Arch_44__011_462')
	supermarket.getChild('Arch_44__011_463')
	supermarket.getChild('Arch_44__011_464')
	supermarket.getChild('Arch_44__011_465')
	supermarket.getChild('Arch_44__011_466')
	supermarket.getChild('Arch_44__031_1746')
	supermarket.getChild('Arch_44__031_1747')
	supermarket.getChild('Arch_44__031_1748')
	supermarket.getChild('Arch_44__031_1749')
	supermarket.getChild('Arch_44__031_1750')
	supermarket.getChild('Arch_44__031_1751')
	supermarket.getChild('Arch_44__031_1752')
	supermarket.getChild('Arch_44__031_1753')
	supermarket.getChild('Arch_44__031_1754')
	supermarket.getChild('Arch_44__031_1755')
	supermarket.getChild('Arch_44__031_1756')
	supermarket.getChild('Arch_44__031_1757')
	supermarket.getChild('Arch_44__031_1758')
	supermarket.getChild('Arch_44__031_1759')
	supermarket.getChild('Arch_44__031_1760')
	supermarket.getChild('Arch_44__031_1761')
	supermarket.getChild('Arch_44__033_1198')
	supermarket.getChild('Arch_44__033_1199')
	supermarket.getChild('Arch_44__033_1208')
	supermarket.getChild('Arch_44__033_1209')
	supermarket.getChild('Arch_44__033_1210')
	supermarket.getChild('Arch_44__033_1211')
	supermarket.getChild('Arch_44__033_1212')
	supermarket.getChild('Arch_44__033_1213')
	supermarket.getChild('Arch_44__033_1214')
	supermarket.getChild('Arch_44__033_1215')
	supermarket.getChild('Arch_44__033_1216')
	supermarket.getChild('Arch_44__033_1217')
	supermarket.getChild('Arch_44__033_1218')
	supermarket.getChild('Arch_44__033_1219')
	supermarket.getChild('Arch_44__033_1220')
	supermarket.getChild('Arch_44__033_1221')
	supermarket.getChild('Arch_44__033_1222')
	supermarket.getChild('Arch_44__033_1223')
	supermarket.getChild('Arch_44__033_1224')
	supermarket.getChild('Arch_44__033_1225')
	supermarket.getChild('Arch_44__032_809')
	supermarket.getChild('Arch_44__021_679')
	supermarket.getChild('Arch_44__032_810')
	supermarket.getChild('Arch_44__032_811')
	supermarket.getChild('Arch_44__032_812')
	supermarket.getChild('Arch_44__032_813')
	supermarket.getChild('Arch_44__032_814')
	supermarket.getChild('Arch_44__032_815')
	supermarket.getChild('Arch_44__032_816')
	supermarket.getChild('Arch_44__032_817')
	supermarket.getChild('Arch_44__032_818')
	supermarket.getChild('Arch_44__032_819')
	supermarket.getChild('Arch_44__032_827')
	supermarket.getChild('Arch_44__032_828')
	supermarket.getChild('Arch_44__032_829')
	supermarket.getChild('Arch_44__021_680')
	supermarket.getChild('Arch_44__021_681')
	supermarket.getChild('Arch_44__021_682')
	supermarket.getChild('Arch_44__021_684')
	supermarket.getChild('Arch_44__021_706')
	supermarket.getChild('Arch_44__021_708')
	supermarket.getChild('Arch_44__021_709')
	supermarket.getChild('Arch_44__021_710')
	supermarket.getChild('Arch_44__021_711')
	supermarket.getChild('Arch_44__021_712')
	supermarket.getChild('Arch_44__021_713')
	supermarket.getChild('Arch_44__021_714')
	supermarket.getChild('Arch_44__021_715')
	supermarket.getChild('Arch_44__021_716')
	supermarket.getChild('Arch_44__021_717')
	supermarket.getChild('Arch_44__021_718')
	supermarket.getChild('Arch_44__031_1768')
	supermarket.getChild('Arch_44__031_1769')
	supermarket.getChild('Arch_44__031_1770')
	supermarket.getChild('Arch_44__031_1779')
	supermarket.getChild('Arch_44__031_1780')
	supermarket.getChild('Arch_44__031_1781')
	supermarket.getChild('Arch_44__031_1782')
	supermarket.getChild('Arch_44__031_1783')
	supermarket.getChild('Arch_44__031_1784')
	supermarket.getChild('Arch_44__031_1785')
	supermarket.getChild('Arch_44__031_1786')
	supermarket.getChild('Arch_44__031_1787')
	supermarket.getChild('Arch_44__032_832')
	supermarket.getChild('Arch_44__032_833')
	supermarket.getChild('Arch_44__032_851')
	supermarket.getChild('Arch_44__032_852')
	supermarket.getChild('Arch_44__032_853')
	supermarket.getChild('Arch_44__032_854')
	supermarket.getChild('Arch_44__032_855')
	supermarket.getChild('Arch_44__032_856')
	supermarket.getChild('Arch_44__032_857')
	supermarket.getChild('Arch_44__032_858')
	supermarket.getChild('Arch_44__032_859')
	supermarket.getChild('Arch_44__032_860')
	supermarket.getChild('Arch_44__032_861')
	supermarket.getChild('Arch_44__032_862')
	supermarket.getChild('Arch_44__032_863')
	supermarket.getChild('Arch_44__032_864')
	supermarket.getChild('Arch_44__032_865')
	supermarket.getChild('Arch_44__030_527')
	supermarket.getChild('Arch_44__030_528')
	supermarket.getChild('Arch_44__030_529')
	supermarket.getChild('Arch_44__030_530')
	supermarket.getChild('Box138')
	supermarket.getChild('Arch_44__015_1572')
	supermarket.getChild('Arch_44__015_1573')
	supermarket.getChild('Arch_44__015_1574')
	supermarket.getChild('Arch_44__015_1575')
	supermarket.getChild('Arch_44__015_1576')
	supermarket.getChild('Arch_44__015_1577')
	supermarket.getChild('Arch_44__015_1578')
	supermarket.getChild('Arch_44__015_1579')
	supermarket.getChild('Arch_44__015_1581')
	supermarket.getChild('Arch_44__015_1582')
	supermarket.getChild('Arch_44__015_1584')
	supermarket.getChild('Arch_44__015_1585')
	supermarket.getChild('Arch_44__015_1586')
	supermarket.getChild('Arch_44__015_1587')
	supermarket.getChild('Arch_44__015_1588')
	supermarket.getChild('Box144')
	supermarket.getChild('Arch_44__015_1589')
	supermarket.getChild('Arch_44__015_1590')
	supermarket.getChild('Arch_44__015_1591')
	supermarket.getChild('Arch_44__015_1592')
	supermarket.getChild('Arch_44__015_1593')
	supermarket.getChild('Arch_44__015_1594')
	supermarket.getChild('Arch_44__015_1595')
	supermarket.getChild('Arch_44__015_1596')
	supermarket.getChild('Arch_44__015_1597')
	supermarket.getChild('Arch_44__015_1598')
	supermarket.getChild('Arch_44__015_1627')
	supermarket.getChild('Arch_44__015_1628')
	supermarket.getChild('Arch_44__015_1629')
	supermarket.getChild('Arch_44__015_1630')
	supermarket.getChild('Arch_44__015_1631')
	supermarket.getChild('Arch_44__015_1632')
	supermarket.getChild('Arch_44__015_1633')
	supermarket.getChild('Arch_44__015_1634')
	supermarket.getChild('Arch_44__015_1635')
	supermarket.getChild('Arch_44__015_1636')
	supermarket.getChild('Arch_44__015_1637')
	supermarket.getChild('Arch_44__015_1638')
	supermarket.getChild('Arch_44__015_1639')
	supermarket.getChild('Arch_44__015_1640')
	supermarket.getChild('Arch_44__015_1641')
	supermarket.getChild('Arch_44__015_1642')
	supermarket.getChild('Arch_44__015_1643')
	supermarket.getChild('Arch_44__015_1644')
	supermarket.getChild('Arch_44__015_1645')
	supermarket.getChild('Arch_44__015_1646')
	supermarket.getChild('Arch_44__015_1647')
	supermarket.getChild('Arch_44__015_1648')
	supermarket.getChild('Arch_44__015_1669')
	supermarket.getChild('Arch_44__015_1670')
	supermarket.getChild('Arch_44__015_1671')
	supermarket.getChild('Arch_44__015_1672')
	supermarket.getChild('Arch_44__015_1673')
	supermarket.getChild('Arch_44__015_1674')
	supermarket.getChild('Arch_44__015_1675')
	supermarket.getChild('Arch_44__015_1676')
	supermarket.getChild('Arch_44__015_1677')
	supermarket.getChild('Arch_44__015_1678')
	supermarket.getChild('Arch_44__015_1679')
	supermarket.getChild('Arch_44__015_1680')
	supermarket.getChild('Arch_44__015_1681')
	supermarket.getChild('Arch_44__015_1682')
	supermarket.getChild('Arch_44__015_1683')
	supermarket.getChild('Arch_44__015_1695')
	supermarket.getChild('Arch_44__015_1696')
	supermarket.getChild('Arch_44__015_1697')
	supermarket.getChild('Arch_44__015_1702')
	supermarket.getChild('Arch_44__015_1703')
	supermarket.getChild('Arch_44__015_1705')
	supermarket.getChild('Arch_44__015_1706')
	supermarket.getChild('Arch_44__015_1707')
	supermarket.getChild('Arch_44__015_1708')
	supermarket.getChild('Arch_44__015_1709')
	supermarket.getChild('Arch_44__015_1710')
	supermarket.getChild('Arch_44__015_1711')
	supermarket.getChild('Arch_44__015_1712')
	supermarket.getChild('Arch_44__015_1713')
	supermarket.getChild('Arch_44__015_1714')
	supermarket.getChild('Arch_44__015_1715')
	supermarket.getChild('Arch_44__015_1716')
	supermarket.getChild('Arch_44__015_1717')
	supermarket.getChild('Arch_44__015_1718')
	supermarket.getChild('Arch_44__015_1719')
	supermarket.getChild('Arch_44__015_1720')
	supermarket.getChild('Arch_44__015_1721')
	supermarket.getChild('Arch_44__015_1722')
	supermarket.getChild('Arch_44__015_1723')
	supermarket.getChild('Arch_44__015_1724')
	supermarket.getChild('Arch_44__015_1725')
	supermarket.getChild('Arch_44__015_1726')
	supermarket.getChild('Arch_44__015_1727')
	supermarket.getChild('Arch_44__015_1728')
	supermarket.getChild('Arch_44__015_1729')
	supermarket.getChild('Arch_44__015_1730')
	supermarket.getChild('Arch_44__015_1731')
	supermarket.getChild('Arch_44__015_1732')
	supermarket.getChild('Arch_44__015_1733')
	supermarket.getChild('Arch_44__015_1734')
	supermarket.getChild('Arch_44__015_1735')
	supermarket.getChild('Arch_44__015_1736')
	supermarket.getChild('Arch_44__015_1737')
	supermarket.getChild('Arch_44__015_1738')
	supermarket.getChild('Arch_44__015_1739')
	supermarket.getChild('Arch_44__015_1740')
	supermarket.getChild('Arch_44__015_1741')
	supermarket.getChild('Arch_44__015_1742')
	supermarket.getChild('Arch_44__015_1743')
	supermarket.getChild('Arch_44__015_1744')
	supermarket.getChild('Arch_44__015_1745')
	supermarket.getChild('Arch_44__015_1746')
	supermarket.getChild('Arch_44__015_1747')
	supermarket.getChild('Arch_44__015_1748')
	supermarket.getChild('Arch_44__015_1749')
	supermarket.getChild('Arch_44__015_1750')
	supermarket.getChild('Arch_44__015_1751')
	supermarket.getChild('Arch_44__015_1752')
	supermarket.getChild('Arch_44__015_1753')
	supermarket.getChild('Arch_44__015_1754')
	supermarket.getChild('Arch_44__015_1755')
	supermarket.getChild('Arch_44__015_1756')
	supermarket.getChild('Arch_44__015_1757')
	supermarket.getChild('Arch_44__015_1758')
	supermarket.getChild('Arch_44__015_1759')
	supermarket.getChild('Arch_44__015_1760')
	supermarket.getChild('Arch_44__015_1761')
	supermarket.getChild('Arch_44__015_1762')
	supermarket.getChild('Arch_44__015_1763')
	supermarket.getChild('Arch_44__015_1764')
	supermarket.getChild('Arch_44__015_1765')
	supermarket.getChild('Arch_44__015_1766')
	supermarket.getChild('Arch_44__015_1767')
	supermarket.getChild('Arch_44__015_1768')
	supermarket.getChild('Arch_44__015_1769')
	supermarket.getChild('Arch_44__015_1770')
	supermarket.getChild('Arch_44__015_1771')
	supermarket.getChild('Arch_44__015_1772')
	supermarket.getChild('Arch_44__015_1773')
	supermarket.getChild('Arch_44__015_1774')
	supermarket.getChild('Arch_44__015_1775')
	supermarket.getChild('Arch_44__015_1776')
	supermarket.getChild('Arch_44__015_1777')
	supermarket.getChild('Arch_44__015_1778')
	supermarket.getChild('Arch_44__015_1779')
	supermarket.getChild('Arch_44__015_1780')
	supermarket.getChild('Arch_44__015_1781')
	supermarket.getChild('Arch_44__015_1782')
	supermarket.getChild('Arch_44__015_1783')
	supermarket.getChild('Arch_44__015_1784')
	supermarket.getChild('Arch_44__015_1785')
	supermarket.getChild('Arch_44__015_1786')
	supermarket.getChild('Arch_44__015_1788')
	supermarket.getChild('Arch_44__015_1789')
	supermarket.getChild('Arch_44__015_1790')
	supermarket.getChild('Arch_44__015_1791')
	supermarket.getChild('Arch_44__015_1792')
	supermarket.getChild('Arch_44__015_1793')
	supermarket.getChild('Arch_44__015_1794')
	supermarket.getChild('Arch_44__015_1795')
	supermarket.getChild('Arch_44__015_1796')
	supermarket.getChild('Arch_44__015_1797')
	supermarket.getChild('Arch_44__015_1798')
	supermarket.getChild('Arch_44__015_1799')
	supermarket.getChild('Arch_44__015_1800')
	supermarket.getChild('Arch_44__015_1801')
	supermarket.getChild('Arch_44__015_1802')
	supermarket.getChild('Arch_44__015_1803')
	supermarket.getChild('Arch_44__015_1804')
	supermarket.getChild('Arch_44__015_1805')
	supermarket.getChild('Arch_44__015_1806')
	supermarket.getChild('Arch_44__015_1807')
	supermarket.getChild('Arch_44__015_1808')
	supermarket.getChild('Arch_44__015_1809')
	supermarket.getChild('Arch_44__015_1810')
	supermarket.getChild('Arch_44__015_1811')
	supermarket.getChild('Arch_44__015_1812')
	supermarket.getChild('Arch_44__015_1813')
	supermarket.getChild('Arch_44__015_1814')
	supermarket.getChild('Arch_44__015_1815')
	supermarket.getChild('Arch_44__015_1816')
	supermarket.getChild('Arch_44__015_1817')
	supermarket.getChild('Arch_44__015_1818')
	supermarket.getChild('Arch_44__015_1819')
	supermarket.getChild('Arch_44__015_1820')
	supermarket.getChild('Arch_44__015_1821')
	supermarket.getChild('Arch_44__015_1822')
	supermarket.getChild('Arch_44__015_1823')
	supermarket.getChild('Arch_44__015_1824')
	supermarket.getChild('Arch_44__015_1825')
	supermarket.getChild('Arch_44__015_1826')
	supermarket.getChild('Arch_44__015_1827')
	supermarket.getChild('Arch_44__015_1828')
	supermarket.getChild('Arch_44__015_1829')
	supermarket.getChild('Arch_44__015_1852')
	supermarket.getChild('Arch_44__015_1853')
	supermarket.getChild('Arch_44__015_1854')
	supermarket.getChild('Arch_44__015_1855')
	supermarket.getChild('Arch_44__015_1856')
	supermarket.getChild('Arch_44__015_1857')
	supermarket.getChild('Arch_44__015_1858')
	supermarket.getChild('Arch_44__015_1859')
	supermarket.getChild('Arch_44__015_1860')
	supermarket.getChild('Arch_44__015_1861')
	supermarket.getChild('Arch_44__015_1862')
	supermarket.getChild('Arch_44__015_1863')
	supermarket.getChild('Arch_44__015_1864')
	supermarket.getChild('Arch_44__015_1865')
	supermarket.getChild('Arch_44__015_1866')
	supermarket.getChild('Arch_44__015_1867')
	supermarket.getChild('Arch_44__015_1868')
	supermarket.getChild('Arch_44__015_1869')
	supermarket.getChild('Arch_44__015_1870')
	supermarket.getChild('Arch_44__015_1871')
	supermarket.getChild('Arch_44__015_1872')
	supermarket.getChild('Arch_44__015_1873')
	supermarket.getChild('Arch_44__015_1874')
	supermarket.getChild('Arch_44__015_1875')
	supermarket.getChild('Arch_44__015_1876')
	supermarket.getChild('Arch_44__015_1889')
	supermarket.getChild('Arch_44__015_1891')
	supermarket.getChild('Arch_44__015_1892')
	supermarket.getChild('Arch_44__015_1893')
	supermarket.getChild('Arch_44__015_1894')
	supermarket.getChild('Arch_44__015_1895')
	supermarket.getChild('Arch_44__015_1896')
	supermarket.getChild('Arch_44__015_1897')
	supermarket.getChild('Arch_44__015_1898')
	supermarket.getChild('Arch_44__015_1899')
	supermarket.getChild('Arch_44__015_1900')
	supermarket.getChild('Arch_44__015_1901')
	supermarket.getChild('Arch_44__015_1902')
	supermarket.getChild('Arch_44__015_1903')
	supermarket.getChild('Arch_44__015_1904')
	supermarket.getChild('Arch_44__015_1905')
	supermarket.getChild('Arch_44__015_1906')
	supermarket.getChild('Arch_44__015_1907')
	supermarket.getChild('Arch_44__015_1908')
	supermarket.getChild('Arch_44__015_1909')
	supermarket.getChild('Arch_44__015_1910')
	supermarket.getChild('Arch_44__015_1911')
	supermarket.getChild('Arch_44__015_1912')
	supermarket.getChild('Arch_44__015_1913')
	supermarket.getChild('Arch_44__015_1914')
	supermarket.getChild('Arch_44__015_1915')
	supermarket.getChild('Arch_44__015_1916')
	supermarket.getChild('Arch_44__015_1917')
	supermarket.getChild('Arch_44__015_1918')
	supermarket.getChild('Arch_44__015_1919')
	supermarket.getChild('Arch_44__015_1920')
	supermarket.getChild('Arch_44__015_1921')
	supermarket.getChild('Arch_44__015_1922')
	supermarket.getChild('Arch_44__015_1923')
	supermarket.getChild('Arch_44__015_1924')
	supermarket.getChild('Arch_44__015_1925')
	supermarket.getChild('Arch_44__015_1926')
	supermarket.getChild('Arch_44__015_1927')
	supermarket.getChild('Arch_44__015_1928')
	supermarket.getChild('Arch_44__015_1929')
	supermarket.getChild('Arch_44__015_1930')
	supermarket.getChild('Arch_44__015_1931')
	supermarket.getChild('Arch_44__015_1932')
	supermarket.getChild('Arch_44__015_1933')
	supermarket.getChild('Arch_44__015_1934')
	supermarket.getChild('Arch_44__015_1935')
	supermarket.getChild('Arch_44__015_1936')
	supermarket.getChild('Arch_44__015_1937')
	supermarket.getChild('Arch_44__015_1938')
	supermarket.getChild('Arch_44__015_1939')
	supermarket.getChild('Arch_44__015_1940')
	supermarket.getChild('Arch_44__015_1941')
	supermarket.getChild('Arch_44__015_1942')
	supermarket.getChild('Arch_44__015_1943')
	supermarket.getChild('Arch_44__015_1944')
	supermarket.getChild('Arch_44__015_1945')
	supermarket.getChild('Arch_44__015_1946')
	supermarket.getChild('Arch_44__015_1947')
	supermarket.getChild('Arch_44__015_1948')
	supermarket.getChild('Arch_44__015_1949')
	supermarket.getChild('Arch_44__015_1950')
	supermarket.getChild('Arch_44__015_1951')
	supermarket.getChild('Arch_44__015_1952')
	supermarket.getChild('Arch_44__015_1953')
	supermarket.getChild('Arch_44__015_1954')
	supermarket.getChild('Arch_44__015_1955')
	supermarket.getChild('Arch_44__015_1956')
	supermarket.getChild('Arch_44__015_1957')
	supermarket.getChild('Arch_44__015_1958')
	supermarket.getChild('Arch_44__015_1959')
	supermarket.getChild('Arch_44__015_1960')
	supermarket.getChild('Arch_44__015_1961')
	supermarket.getChild('Arch_44__015_1962')
	supermarket.getChild('Arch_44__015_1963')
	supermarket.getChild('Arch_44__015_1964')
	supermarket.getChild('Arch_44__015_1965')
	supermarket.getChild('Arch_44__015_1966')
	supermarket.getChild('Arch_44__015_1967')
	supermarket.getChild('Arch_44__015_1968')
	supermarket.getChild('Arch_44__015_1969')
	supermarket.getChild('Arch_44__015_1970')
	supermarket.getChild('Arch_44__015_1971')
	supermarket.getChild('Arch_44__015_1972')
	supermarket.getChild('Arch_44__015_1973')
	supermarket.getChild('Arch_44__015_1974')
	supermarket.getChild('Arch_44__015_1975')
	supermarket.getChild('Arch_44__015_1976')
	supermarket.getChild('Arch_44__015_1977')
	supermarket.getChild('Arch_44__015_1978')
	supermarket.getChild('Arch_44__015_1979')
	supermarket.getChild('Arch_44__015_1980')
	supermarket.getChild('Arch_44__015_1981')
	supermarket.getChild('Arch_44__015_1982')
	supermarket.getChild('Arch_44__015_1983')
	supermarket.getChild('Arch_44__015_1984')
	supermarket.getChild('Arch_44__015_1985')
	supermarket.getChild('Arch_44__015_1986')
	supermarket.getChild('Arch_44__015_1987')
	supermarket.getChild('Arch_44__015_1988')
	supermarket.getChild('Arch_44__015_1989')
	supermarket.getChild('Arch_44__015_1990')
	supermarket.getChild('Arch_44__015_1991')
	supermarket.getChild('Arch_44__015_1992')
	supermarket.getChild('Arch_44__015_1993')
	supermarket.getChild('Arch_44__015_1994')
	supermarket.getChild('Arch_44__015_1995')
	supermarket.getChild('Arch_44__015_1996')
	supermarket.getChild('Arch_44__015_1997')
	supermarket.getChild('Arch_44__015_1998')
	supermarket.getChild('Arch_44__015_1999')
	supermarket.getChild('Arch_44__015_2000')
	supermarket.getChild('Arch_44__015_2001')
	supermarket.getChild('Arch_44__015_2002')
	supermarket.getChild('Arch_44__015_2003')
	supermarket.getChild('Arch_44__015_2004')
	supermarket.getChild('Arch_44__015_2005')
	supermarket.getChild('Arch_44__015_2006')
	supermarket.getChild('Arch_44__015_2007')
	supermarket.getChild('Arch_44__015_2008')
	supermarket.getChild('Arch_44__015_2009')
	supermarket.getChild('Arch_44__015_2010')
	supermarket.getChild('Box145')
	supermarket.getChild('Box146')
	supermarket.getChild('Box147')
	supermarket.getChild('Box148')
	supermarket.getChild('Arch_44__012_717')
	supermarket.getChild('Arch_44__617342459')
	supermarket.getChild('Arch_44__012_718')
	supermarket.getChild('Arch_44__954843802')
	supermarket.getChild('Arch_44__012_719')
	supermarket.getChild('Arch_44__012_720')
	supermarket.getChild('Arch_44__693008009')
	supermarket.getChild('Arch_44__012_721')
	supermarket.getChild('Arch_44__857966382')
	supermarket.getChild('Arch_44__012_722')
	supermarket.getChild('Arch_44__012_723')
	supermarket.getChild('Arch_44__012_724')
	supermarket.getChild('Arch_44__012_725')
	supermarket.getChild('Arch_44__012_726')
	supermarket.getChild('Arch_44__012_727')
	supermarket.getChild('Arch_44__012_728')
	supermarket.getChild('Arch_44__012_729')
	supermarket.getChild('Arch_44__012_730')
	supermarket.getChild('Arch_44__012_731')
	supermarket.getChild('Arch_44__012_732')
	supermarket.getChild('Arch_44__012_733')
	supermarket.getChild('Arch_44__012_734')
	supermarket.getChild('Arch_44__012_735')
	supermarket.getChild('Arch_44__012_736')
	supermarket.getChild('Arch_44__012_737')
	supermarket.getChild('Arch_44__012_738')
	supermarket.getChild('Arch_44__012_739')
	supermarket.getChild('Arch_44__012_740')
	supermarket.getChild('Arch_44__012_741')
	supermarket.getChild('Arch_44__012_742')
	supermarket.getChild('Arch_44__012_743')
	supermarket.getChild('Arch_44__012_744')
	supermarket.getChild('Arch_44__012_745')
	supermarket.getChild('Arch_44__012_746')
	supermarket.getChild('Arch_44__012_747')
	supermarket.getChild('Arch_44__012_748')
	supermarket.getChild('Arch_44__012_749')
	supermarket.getChild('Arch_44__012_750')
	supermarket.getChild('Arch_44__012_751')
	supermarket.getChild('Arch_44__012_752')
	supermarket.getChild('Arch_44__012_753')
	supermarket.getChild('Arch_44__012_754')
	supermarket.getChild('Arch_44__012_755')
	supermarket.getChild('Arch_44__012_756')
	supermarket.getChild('Arch_44__012_757')
	supermarket.getChild('Arch_44__012_758')
	supermarket.getChild('Arch_44__012_759')
	supermarket.getChild('Arch_44__012_760')
	supermarket.getChild('Arch_44__012_761')
	supermarket.getChild('Arch_44__012_762')
	supermarket.getChild('Arch_44__012_763')
	supermarket.getChild('Arch_44__012_764')
	supermarket.getChild('Arch_44__012_765')
	supermarket.getChild('Arch_44__012_766')
	supermarket.getChild('Arch_44__012_767')
	supermarket.getChild('Arch_44__012_768')
	supermarket.getChild('Arch_44__012_769')
	supermarket.getChild('Arch_44__012_770')
	supermarket.getChild('Arch_44__012_771')
	supermarket.getChild('Arch_44__012_772')
	supermarket.getChild('Arch_44__012_773')
	supermarket.getChild('Arch_44__012_774')
	supermarket.getChild('Arch_44__012_775')
	supermarket.getChild('Arch_44__012_776')
	supermarket.getChild('Arch_44__012_777')
	supermarket.getChild('Arch_44__012_778')
	supermarket.getChild('Arch_44__012_779')
	supermarket.getChild('Arch_44__012_780')
	supermarket.getChild('Arch_44__012_781')
	supermarket.getChild('Arch_44__012_782')
	supermarket.getChild('Arch_44__012_783')
	supermarket.getChild('Arch_44__012_784')
	supermarket.getChild('Arch_44__012_785')
	supermarket.getChild('Arch_44__012_786')
	supermarket.getChild('Arch_44__012_787')
	supermarket.getChild('Arch_44__012_788')
	supermarket.getChild('Arch_44__012_789')
	supermarket.getChild('Arch_44__012_790')
	supermarket.getChild('Arch_44__012_791')
	supermarket.getChild('Arch_44__012_792')
	supermarket.getChild('Arch_44__012_793')
	supermarket.getChild('Arch_44__012_794')
	supermarket.getChild('Arch_44__012_795')
	supermarket.getChild('Arch_44__012_796')
	supermarket.getChild('Arch_44__012_797')
	supermarket.getChild('Arch_44__012_798')
	supermarket.getChild('Arch_44__012_799')
	supermarket.getChild('Arch_44__012_800')
	supermarket.getChild('Arch_44__012_801')
	supermarket.getChild('Arch_44__012_802')
	supermarket.getChild('Arch_44__012_803')
	supermarket.getChild('Arch_44__012_804')
	supermarket.getChild('Arch_44__012_805')
	supermarket.getChild('Arch_44__012_806')
	supermarket.getChild('Arch_44__012_807')
	supermarket.getChild('Arch_44__012_808')
	supermarket.getChild('Arch_44__012_809')
	supermarket.getChild('Arch_44__012_810')
	supermarket.getChild('Arch_44__012_811')
	supermarket.getChild('Arch_44__012_812')
	supermarket.getChild('Arch_44__012_813')
	supermarket.getChild('Arch_44__012_814')
	supermarket.getChild('Arch_44__012_815')
	supermarket.getChild('Arch_44__012_816')
	supermarket.getChild('Arch_44__012_817')
	supermarket.getChild('Arch_44__012_818')
	supermarket.getChild('Arch_44__012_819')
	supermarket.getChild('Arch_44__012_820')
	supermarket.getChild('Arch_44__012_821')
	supermarket.getChild('Arch_44__012_822')
	supermarket.getChild('Arch_44__012_823')
	supermarket.getChild('Arch_44__012_824')
	supermarket.getChild('Arch_44__012_825')
	supermarket.getChild('Arch_44__012_826')
	supermarket.getChild('Arch_44__012_827')
	supermarket.getChild('Arch_44__012_828')
	supermarket.getChild('Arch_44__012_829')
	supermarket.getChild('Arch_44__012_830')
	supermarket.getChild('Arch_44__012_831')
	supermarket.getChild('Arch_44__012_832')
	supermarket.getChild('Arch_44__012_833')
	supermarket.getChild('Arch_44__012_834')
	supermarket.getChild('Arch_44__012_835')
	supermarket.getChild('Arch_44__012_836')
	supermarket.getChild('Arch_44__012_837')
	supermarket.getChild('Arch_44__012_838')
	supermarket.getChild('Arch_44__012_839')
	supermarket.getChild('Arch_44__012_840')
	supermarket.getChild('Arch_44__012_841')
	supermarket.getChild('Arch_44__012_842')
	supermarket.getChild('Arch_44__012_843')
	supermarket.getChild('Arch_44__012_844')
	supermarket.getChild('Arch_44__012_845')
	supermarket.getChild('Arch_44__012_846')
	supermarket.getChild('Arch_44__012_847')
	supermarket.getChild('Arch_44__012_848')
	supermarket.getChild('Arch_44__012_849')
	supermarket.getChild('Arch_44__012_850')
	supermarket.getChild('Arch_44__012_851')
	supermarket.getChild('Arch_44__012_852')
	supermarket.getChild('Arch_44__012_853')
	supermarket.getChild('Arch_44__012_854')
	supermarket.getChild('Arch_44__012_855')
	supermarket.getChild('Arch_44__012_856')
	supermarket.getChild('Arch_44__012_857')
	supermarket.getChild('Arch_44__012_858')
	supermarket.getChild('Arch_44__012_859')
	supermarket.getChild('Arch_44__012_860')
	supermarket.getChild('Arch_44__012_861')
	supermarket.getChild('Arch_44__012_862')
	supermarket.getChild('Arch_44__012_863')
	supermarket.getChild('Arch_44__012_864')
	supermarket.getChild('Arch_44__012_865')
	supermarket.getChild('Arch_44__012_866')
	supermarket.getChild('Arch_44__012_867')
	supermarket.getChild('Arch_44__012_868')
	supermarket.getChild('Arch_44__012_869')
	supermarket.getChild('Arch_44__012_870')
	supermarket.getChild('Arch_44__012_871')
	supermarket.getChild('Arch_44__012_872')
	supermarket.getChild('Arch_44__012_873')
	supermarket.getChild('Arch_44__012_874')
	supermarket.getChild('Arch_44__012_875')
	supermarket.getChild('Arch_44__012_876')
	supermarket.getChild('Arch_44__012_877')
	supermarket.getChild('Arch_44__012_878')
	supermarket.getChild('Arch_44__012_879')
	supermarket.getChild('Arch_44__012_880')
	supermarket.getChild('Arch_44__012_882')
	supermarket.getChild('Arch_44__012_883')
	supermarket.getChild('Arch_44__012_884')
	supermarket.getChild('Arch_44__012_885')
	supermarket.getChild('Arch_44__012_886')
	supermarket.getChild('Arch_44__012_887')
	supermarket.getChild('Arch_44__012_888')
	supermarket.getChild('Arch_44__012_889')
	supermarket.getChild('Arch_44__012_890')
	supermarket.getChild('Arch_44__012_891')
	supermarket.getChild('Arch_44__012_892')
	supermarket.getChild('Arch_44__012_893')
	supermarket.getChild('Arch_44__012_894')
	supermarket.getChild('Arch_44__012_895')
	supermarket.getChild('Arch_44__012_896')
	supermarket.getChild('Arch_44__012_897')
	supermarket.getChild('Arch_44__012_898')
	supermarket.getChild('Arch_44__012_899')
	supermarket.getChild('Arch_44__012_900')
	supermarket.getChild('Arch_44__012_901')
	supermarket.getChild('Arch_44__012_902')
	supermarket.getChild('Arch_44__012_903')
	supermarket.getChild('Arch_44__012_904')
	supermarket.getChild('Arch_44__012_905')
	supermarket.getChild('Arch_44__926076132')
	supermarket.getChild('Arch_44__012_906')
	supermarket.getChild('Arch_44__012_907')
	supermarket.getChild('Arch_44__012_908')
	supermarket.getChild('Arch_44__012_909')
	supermarket.getChild('Arch_44__012_910')
	supermarket.getChild('Arch_44__012_911')
	supermarket.getChild('Arch_44__012_912')
	supermarket.getChild('Arch_44__012_913')
	supermarket.getChild('Arch_44__012_914')
	supermarket.getChild('Arch_44__012_915')
	supermarket.getChild('Arch_44__012_916')
	supermarket.getChild('Arch_44__012_917')
	supermarket.getChild('Arch_44__012_918')
	supermarket.getChild('Arch_44__012_919')
	supermarket.getChild('Arch_44__012_920')
	supermarket.getChild('Arch_44__012_921')
	supermarket.getChild('Arch_44__012_922')
	supermarket.getChild('Arch_44__012_923')
	supermarket.getChild('Arch_44__012_924')
	supermarket.getChild('Arch_44__012_925')
	supermarket.getChild('Arch_44__012_926')
	supermarket.getChild('Arch_44__012_927')
	supermarket.getChild('Arch_44__012_928')
	supermarket.getChild('Arch_44__012_929')
	supermarket.getChild('Arch_44__012_930')
	supermarket.getChild('Arch_44__012_931')
	supermarket.getChild('Arch_44__012_932')
	supermarket.getChild('Arch_44__012_933')
	supermarket.getChild('Arch_44__012_934')
	supermarket.getChild('Arch_44__012_935')
	supermarket.getChild('Arch_44__012_936')
	supermarket.getChild('Arch_44__012_937')
	supermarket.getChild('Arch_44__012_938')
	supermarket.getChild('Arch_44__012_939')
	supermarket.getChild('Arch_44__32326601')
	supermarket.getChild('Arch_44__012_940')
	supermarket.getChild('Arch_44__012_941')
	supermarket.getChild('Arch_44__012_942')
	supermarket.getChild('Arch_44__012_943')
	supermarket.getChild('Arch_44__012_944')
	supermarket.getChild('Arch_44__012_945')
	supermarket.getChild('Arch_44__012_946')
	supermarket.getChild('Arch_44__012_947')
	supermarket.getChild('Arch_44__012_948')
	supermarket.getChild('Arch_44__012_949')
	supermarket.getChild('Arch_44__012_950')
	supermarket.getChild('Arch_44__012_951')
	supermarket.getChild('Arch_44__012_952')
	supermarket.getChild('Arch_44__012_953')
	supermarket.getChild('Arch_44__012_954')
	supermarket.getChild('Arch_44__012_955')
	supermarket.getChild('Arch_44__012_956')
	supermarket.getChild('Arch_44__012_957')
	supermarket.getChild('Arch_44__012_958')
	supermarket.getChild('Arch_44__012_959')
	supermarket.getChild('Arch_44__012_960')
	supermarket.getChild('Arch_44__012_961')
	supermarket.getChild('Arch_44__012_962')
	supermarket.getChild('Arch_44__012_963')
	supermarket.getChild('Arch_44__012_964')
	supermarket.getChild('Arch_44__012_965')
	supermarket.getChild('Arch_44__012_966')
	supermarket.getChild('Arch_44__012_967')
	supermarket.getChild('Arch_44__012_968')
	supermarket.getChild('Arch_44__012_969')
	supermarket.getChild('Arch_44__012_970')
	supermarket.getChild('Arch_44__012_971')
	supermarket.getChild('Arch_44__012_972')
	supermarket.getChild('Arch_44__012_973')
	supermarket.getChild('Arch_44__012_974')
	supermarket.getChild('Arch_44__012_975')
	supermarket.getChild('Arch_44__012_976')
	supermarket.getChild('Arch_44__012_977')
	supermarket.getChild('Arch_44__012_978')
	supermarket.getChild('Arch_44__012_979')
	supermarket.getChild('Arch_44__012_980')
	supermarket.getChild('Arch_44__012_981')
	supermarket.getChild('Arch_44__012_982')
	supermarket.getChild('Arch_44__012_983')
	supermarket.getChild('Arch_44__012_984')
	supermarket.getChild('Arch_44__012_985')
	supermarket.getChild('Arch_44__012_986')
	supermarket.getChild('Arch_44__012_987')
	supermarket.getChild('Arch_44__012_988')
	supermarket.getChild('Arch_44__012_989')
	supermarket.getChild('Arch_44__012_990')
	supermarket.getChild('Arch_44__012_991')
	supermarket.getChild('Arch_44__012_992')
	supermarket.getChild('Arch_44__012_993')
	supermarket.getChild('Arch_44__012_994')
	supermarket.getChild('Arch_44__012_995')
	supermarket.getChild('Arch_44__012_996')
	supermarket.getChild('Arch_44__012_997')
	supermarket.getChild('Arch_44__012_998')
	supermarket.getChild('Arch_44__012_999')
	supermarket.getChild('Arch_44__012_1000')
	supermarket.getChild('Arch_44__012_1001')
	supermarket.getChild('Arch_44__012_1002')
	supermarket.getChild('Arch_44__012_1003')
	supermarket.getChild('Arch_44__012_1004')
	supermarket.getChild('Arch_44__012_1005')
	supermarket.getChild('Arch_44__012_1006')
	supermarket.getChild('Arch_44__012_1007')
	supermarket.getChild('Arch_44__012_1008')
	supermarket.getChild('Arch_44__012_1009')
	supermarket.getChild('Arch_44__012_1010')
	supermarket.getChild('Arch_44__012_1011')
	supermarket.getChild('Arch_44__012_1012')
	supermarket.getChild('Arch_44__012_1013')
	supermarket.getChild('Arch_44__012_1014')
	supermarket.getChild('Arch_44__012_1015')
	supermarket.getChild('Arch_44__012_1016')
	supermarket.getChild('Arch_44__012_1017')
	supermarket.getChild('Arch_44__012_1018')
	supermarket.getChild('Arch_44__012_1019')
	supermarket.getChild('Arch_44__012_1020')
	supermarket.getChild('Arch_44__012_1021')
	supermarket.getChild('Arch_44__012_1022')
	supermarket.getChild('Arch_44__012_1023')
	supermarket.getChild('Arch_44__012_1024')
	supermarket.getChild('Arch_44__012_1025')
	supermarket.getChild('Arch_44__012_1026')
	supermarket.getChild('Arch_44__012_1027')
	supermarket.getChild('Arch_44__012_1028')
	supermarket.getChild('Arch_44__012_1029')
	supermarket.getChild('Arch_44__012_1030')
	supermarket.getChild('Arch_44__012_1031')
	supermarket.getChild('Arch_44__012_1032')
	supermarket.getChild('Arch_44__012_1033')
	supermarket.getChild('Arch_44__012_1034')
	supermarket.getChild('Arch_44__012_1035')
	supermarket.getChild('Arch_44__012_1036')
	supermarket.getChild('Arch_44__012_1037')
	supermarket.getChild('Arch_44__012_1038')
	supermarket.getChild('Arch_44__012_1039')
	supermarket.getChild('Arch_44__012_1040')
	supermarket.getChild('Arch_44__012_1041')
	supermarket.getChild('Arch_44__012_1042')
	supermarket.getChild('Arch_44__012_1043')
	supermarket.getChild('Arch_44__012_1044')
	supermarket.getChild('Arch_44__012_1045')
	supermarket.getChild('Arch_44__012_1046')
	supermarket.getChild('Arch_44__012_1047')
	supermarket.getChild('Arch_44__012_1048')
	supermarket.getChild('Arch_44__012_1049')
	supermarket.getChild('Arch_44__012_1050')
	supermarket.getChild('Arch_44__012_1051')
	supermarket.getChild('Arch_44__012_1052')
	supermarket.getChild('Arch_44__012_1053')
	supermarket.getChild('Arch_44__012_1054')
	supermarket.getChild('Arch_44__012_1055')
	supermarket.getChild('Arch_44__012_1056')
	supermarket.getChild('Arch_44__012_1057')
	supermarket.getChild('Arch_44__012_1058')
	supermarket.getChild('Arch_44__012_1059')
	supermarket.getChild('Arch_44__012_1060')
	supermarket.getChild('Arch_44__012_1061')
	supermarket.getChild('Arch_44__012_1062')
	supermarket.getChild('Arch_44__012_1063')
	supermarket.getChild('Arch_44__012_1064')
	supermarket.getChild('Arch_44__012_1065')
	supermarket.getChild('Arch_44__012_1066')
	supermarket.getChild('Arch_44__012_1067')
	supermarket.getChild('Arch_44__012_1068')
	supermarket.getChild('Arch_44__012_1069')
	supermarket.getChild('Arch_44__012_1070')
	supermarket.getChild('Arch_44__012_1071')
	supermarket.getChild('Arch_44__012_1072')
	supermarket.getChild('Arch_44__012_1073')
	supermarket.getChild('Arch_44__012_1074')
	supermarket.getChild('Arch_44__012_1075')
	supermarket.getChild('Arch_44__012_1076')
	supermarket.getChild('Arch_44__012_1077')
	supermarket.getChild('Arch_44__012_1078')
	supermarket.getChild('Arch_44__012_1079')
	supermarket.getChild('Arch_44__012_1080')
	supermarket.getChild('Arch_44__012_1081')
	supermarket.getChild('Arch_44__012_1082')
	supermarket.getChild('Arch_44__012_1083')
	supermarket.getChild('Arch_44__012_1084')
	supermarket.getChild('Arch_44__012_1085')
	supermarket.getChild('Arch_44__012_1086')
	supermarket.getChild('Arch_44__012_1087')
	supermarket.getChild('Arch_44__012_1088')
	supermarket.getChild('Arch_44__012_1089')
	supermarket.getChild('Arch_44__012_1090')
	supermarket.getChild('Arch_44__012_1091')
	supermarket.getChild('Arch_44__012_1092')
	supermarket.getChild('Arch_44__012_1093')
	supermarket.getChild('Arch_44__012_1094')
	supermarket.getChild('Arch_44__012_1095')
	supermarket.getChild('Arch_44__012_1096')
	supermarket.getChild('Arch_44__012_1097')
	supermarket.getChild('Arch_44__012_1098')
	supermarket.getChild('Arch_44__012_1099')
	supermarket.getChild('Arch_44__012_1100')
	supermarket.getChild('Arch_44__012_1101')
	supermarket.getChild('Arch_44__012_1102')
	supermarket.getChild('Arch_44__012_1103')
	supermarket.getChild('Arch_44__012_1104')
	supermarket.getChild('Arch_44__012_1105')
	supermarket.getChild('Arch_44__012_1106')
	supermarket.getChild('Arch_44__012_1107')
	supermarket.getChild('Arch_44__012_1108')
	supermarket.getChild('Arch_44__012_1109')
	supermarket.getChild('Arch_44__012_1110')
	supermarket.getChild('Arch_44__012_1111')
	supermarket.getChild('Arch_44__012_1112')
	supermarket.getChild('Arch_44__012_1113')
	supermarket.getChild('Arch_44__012_1114')
	supermarket.getChild('Arch_44__012_1115')
	supermarket.getChild('Arch_44__012_1116')
	supermarket.getChild('Arch_44__012_1117')
	supermarket.getChild('Arch_44__012_1118')
	supermarket.getChild('Arch_44__012_1119')
	supermarket.getChild('Arch_44__012_1120')
	supermarket.getChild('Arch_44__012_1121')
	supermarket.getChild('Arch_44__012_1122')
	supermarket.getChild('Arch_44__012_1123')
	supermarket.getChild('Arch_44__012_1124')
	supermarket.getChild('Arch_44__012_1125')
	supermarket.getChild('Arch_44__012_1126')
	supermarket.getChild('Arch_44__012_1127')
	supermarket.getChild('Arch_44__012_1128')
	supermarket.getChild('Arch_44__012_1129')
	supermarket.getChild('Arch_44__012_1130')
	supermarket.getChild('Arch_44__012_1131')
	supermarket.getChild('Arch_44__012_1132')
	supermarket.getChild('Arch_44__012_1133')
	supermarket.getChild('Arch_44__012_1134')
	supermarket.getChild('Arch_44__012_1135')
	supermarket.getChild('Arch_44__012_1136')
	supermarket.getChild('Arch_44__012_1137')
	supermarket.getChild('Arch_44__012_1138')
	supermarket.getChild('Arch_44__012_1139')
	supermarket.getChild('Arch_44__012_1140')
	supermarket.getChild('Arch_44__012_1141')
	supermarket.getChild('Arch_44__012_1142')
	supermarket.getChild('Arch_44__012_1143')
	supermarket.getChild('Arch_44__319257644')
	supermarket.getChild('Arch_44__012_1144')
	supermarket.getChild('Arch_44__012_1145')
	supermarket.getChild('Arch_44__012_1146')
	supermarket.getChild('Arch_44__012_1147')
	supermarket.getChild('Arch_44__012_1148')
	supermarket.getChild('Arch_44__012_1149')
	supermarket.getChild('Arch_44__012_1150')
	supermarket.getChild('Arch_44__012_1151')
	supermarket.getChild('Arch_44__012_1152')
	supermarket.getChild('Arch_44__012_1153')
	supermarket.getChild('Arch_44__012_1154')
	supermarket.getChild('Arch_44__012_1155')
	supermarket.getChild('Arch_44__012_1156')
	supermarket.getChild('Arch_44__012_1157')
	supermarket.getChild('Arch_44__012_1158')
	supermarket.getChild('Arch_44__012_1159')
	supermarket.getChild('Arch_44__012_1160')
	supermarket.getChild('Arch_44__012_1161')
	supermarket.getChild('Arch_44__012_1162')
	supermarket.getChild('Arch_44__012_1163')
	supermarket.getChild('Arch_44__012_1164')
	supermarket.getChild('Arch_44__012_1165')
	supermarket.getChild('Arch_44__012_1166')
	supermarket.getChild('Arch_44__012_1167')
	supermarket.getChild('Arch_44__012_1168')
	supermarket.getChild('Arch_44__012_1169')
	supermarket.getChild('Arch_44__012_1170')
	supermarket.getChild('Arch_44__012_1171')
	supermarket.getChild('Arch_44__012_1172')
	supermarket.getChild('Arch_44__012_1173')
	supermarket.getChild('Arch_44__012_1174')
	supermarket.getChild('Arch_44__012_1175')
	supermarket.getChild('Arch_44__012_1176')
	supermarket.getChild('Arch_44__012_1177')
	supermarket.getChild('Arch_44__012_1178')
	supermarket.getChild('Arch_44__012_1179')
	supermarket.getChild('Arch_44__012_1180')
	supermarket.getChild('Arch_44__012_1181')
	supermarket.getChild('Arch_44__012_1182')
	supermarket.getChild('Arch_44__012_1183')
	supermarket.getChild('Arch_44__012_1184')
	supermarket.getChild('Arch_44__012_1185')
	supermarket.getChild('Arch_44__012_1186')
	supermarket.getChild('Arch_44__012_1187')
	supermarket.getChild('Arch_44__012_1188')
	supermarket.getChild('Arch_44__012_1189')
	supermarket.getChild('Arch_44__012_1190')
	supermarket.getChild('Arch_44__012_1191')
	supermarket.getChild('Arch_44__012_1192')
	supermarket.getChild('Arch_44__012_1193')
	supermarket.getChild('Arch_44__012_1194')
	supermarket.getChild('Arch_44__012_1195')
	supermarket.getChild('Arch_44__012_1196')
	supermarket.getChild('Arch_44__012_1197')
	supermarket.getChild('Arch_44__012_1198')
	supermarket.getChild('Arch_44__012_1199')
	supermarket.getChild('Arch_44__012_1200')
	supermarket.getChild('Arch_44__012_1201')
	supermarket.getChild('Arch_44__012_1202')
	supermarket.getChild('Arch_44__012_1203')
	supermarket.getChild('Arch_44__012_1204')
	supermarket.getChild('Arch_44__012_1205')
	supermarket.getChild('Arch_44__012_1206')
	supermarket.getChild('Arch_44__012_1207')
	supermarket.getChild('Arch_44__012_1208')
	supermarket.getChild('Arch_44__012_1209')
	supermarket.getChild('Arch_44__012_1210')
	supermarket.getChild('Arch_44__012_1211')
	supermarket.getChild('Arch_44__012_1212')
	supermarket.getChild('Arch_44__012_1213')
	supermarket.getChild('Arch_44__012_1214')
	supermarket.getChild('Arch_44__012_1215')
	supermarket.getChild('Arch_44__012_1216')
	supermarket.getChild('Box152')
	supermarket.getChild('Arch_44__012_1217')
	supermarket.getChild('Arch_44__012_1218')
	supermarket.getChild('Arch_44__012_1219')
	supermarket.getChild('Arch_44__012_1220')
	supermarket.getChild('Arch_44__012_1221')
	supermarket.getChild('Arch_44__012_1222')
	supermarket.getChild('Arch_44__012_1223')
	supermarket.getChild('Arch_44__012_1224')
	supermarket.getChild('Arch_44__012_1225')
	supermarket.getChild('Arch_44__012_1226')
	supermarket.getChild('Arch_44__012_1227')
	supermarket.getChild('Arch_44__012_1228')
	supermarket.getChild('Arch_44__012_1229')
	supermarket.getChild('Arch_44__012_1230')
	supermarket.getChild('Arch_44__012_1231')
	supermarket.getChild('Arch_44__012_1232')
	supermarket.getChild('Arch_44__012_1233')
	supermarket.getChild('Arch_44__012_1234')
	supermarket.getChild('Arch_44__012_1235')
	supermarket.getChild('Arch_44__012_1236')
	supermarket.getChild('Arch_44__012_1237')
	supermarket.getChild('Arch_44__012_1238')
	supermarket.getChild('Arch_44__012_1239')
	supermarket.getChild('Arch_44__012_1240')
	supermarket.getChild('Arch_44__012_1241')
	supermarket.getChild('Arch_44__012_1242')
	supermarket.getChild('Arch_44__012_1243')
	supermarket.getChild('Arch_44__012_1244')
	supermarket.getChild('Arch_44__012_1245')
	supermarket.getChild('Arch_44__012_1246')
	supermarket.getChild('Arch_44__012_1247')
	supermarket.getChild('Arch_44__012_1248')
	supermarket.getChild('Arch_44__012_1249')
	supermarket.getChild('Arch_44__012_1250')
	supermarket.getChild('Arch_44__012_1251')
	supermarket.getChild('Arch_44__012_1252')
	supermarket.getChild('Arch_44__012_1253')
	supermarket.getChild('Arch_44__012_1254')
	supermarket.getChild('Arch_44__012_1255')
	supermarket.getChild('Arch_44__012_1256')
	supermarket.getChild('Arch_44__012_1257')
	supermarket.getChild('Arch_44__012_1258')
	supermarket.getChild('Arch_44__012_1259')
	supermarket.getChild('Arch_44__012_1260')
	supermarket.getChild('Arch_44__012_1261')
	supermarket.getChild('Arch_44__012_1262')
	supermarket.getChild('Arch_44__012_1263')
	supermarket.getChild('Arch_44__012_1264')
	supermarket.getChild('Arch_44__012_1265')
	supermarket.getChild('Arch_44__012_1266')
	supermarket.getChild('Arch_44__012_1267')
	supermarket.getChild('Arch_44__012_1268')
	supermarket.getChild('Arch_44__012_1269')
	supermarket.getChild('Arch_44__012_1270')
	supermarket.getChild('Arch_44__012_1271')
	supermarket.getChild('Arch_44__012_1272')
	supermarket.getChild('Arch_44__012_1273')
	supermarket.getChild('Arch_44__012_1274')
	supermarket.getChild('Arch_44__012_1275')
	supermarket.getChild('Arch_44__012_1276')
	supermarket.getChild('Arch_44__012_1277')
	supermarket.getChild('Arch_44__012_1278')
	supermarket.getChild('Arch_44__012_1279')
	supermarket.getChild('Arch_44__012_1280')
	supermarket.getChild('Arch_44__012_1281')
	supermarket.getChild('Arch_44__012_1282')
	supermarket.getChild('Arch_44__012_1283')
	supermarket.getChild('Arch_44__012_1284')
	supermarket.getChild('Arch_44__012_1285')
	supermarket.getChild('Arch_44__012_1286')
	supermarket.getChild('Arch_44__012_1287')
	supermarket.getChild('Arch_44__012_1288')
	supermarket.getChild('Arch_44__012_1289')
	supermarket.getChild('Arch_44__012_1290')
	supermarket.getChild('Arch_44__012_1291')
	supermarket.getChild('Arch_44__012_1292')
	supermarket.getChild('Arch_44__012_1293')
	supermarket.getChild('Arch_44__012_1294')
	supermarket.getChild('Arch_44__012_1295')
	supermarket.getChild('Arch_44__012_1296')
	supermarket.getChild('Arch_44__012_1297')
	supermarket.getChild('Arch_44__012_1298')
	supermarket.getChild('Arch_44__012_1299')
	supermarket.getChild('Arch_44__012_1300')
	supermarket.getChild('Arch_44__012_1301')
	supermarket.getChild('Arch_44__012_1302')
	supermarket.getChild('Arch_44__012_1303')
	supermarket.getChild('Arch_44__012_1304')
	supermarket.getChild('Arch_44__012_1305')
	supermarket.getChild('Arch_44__012_1306')
	supermarket.getChild('Arch_44__012_1307')
	supermarket.getChild('Arch_44__012_1308')
	supermarket.getChild('Arch_44__012_1309')
	supermarket.getChild('Arch_44__012_1310')
	supermarket.getChild('Arch_44__012_1311')
	supermarket.getChild('Arch_44__012_1312')
	supermarket.getChild('Arch_44__012_1313')
	supermarket.getChild('Arch_44__012_1314')
	supermarket.getChild('Arch_44__012_1315')
	supermarket.getChild('Arch_44__012_1316')
	supermarket.getChild('Arch_44__012_1317')
	supermarket.getChild('Arch_44__012_1318')
	supermarket.getChild('Arch_44__012_1319')
	supermarket.getChild('Arch_44__012_1320')
	supermarket.getChild('Arch_44__012_1321')
	supermarket.getChild('Arch_44__012_1322')
	supermarket.getChild('Arch_44__012_1323')
	supermarket.getChild('Arch_44__012_1324')
	supermarket.getChild('Arch_44__012_1325')
	supermarket.getChild('Arch_44__012_1326')
	supermarket.getChild('Arch_44__012_1327')
	supermarket.getChild('Arch_44__012_1328')
	supermarket.getChild('Arch_44__012_1329')
	supermarket.getChild('Arch_44__012_1330')
	supermarket.getChild('Arch_44__012_1331')
	supermarket.getChild('Arch_44__012_1332')
	supermarket.getChild('Arch_44__012_1333')
	supermarket.getChild('Arch_44__012_1334')
	supermarket.getChild('Arch_44__012_1335')
	supermarket.getChild('Arch_44__012_1336')
	supermarket.getChild('Arch_44__012_1337')
	supermarket.getChild('Arch_44__012_1338')
	supermarket.getChild('Arch_44__012_1339')
	supermarket.getChild('Arch_44__012_1340')
	supermarket.getChild('Arch_44__012_1341')
	supermarket.getChild('Arch_44__012_1342')
	supermarket.getChild('Arch_44__012_1343')
	supermarket.getChild('Arch_44__012_1344')
	supermarket.getChild('Arch_44__012_1345')
	supermarket.getChild('Arch_44__012_1346')
	supermarket.getChild('Arch_44__012_1347')
	supermarket.getChild('Arch_44__012_1348')
	supermarket.getChild('Arch_44__012_1349')
	supermarket.getChild('Arch_44__012_1350')
	supermarket.getChild('Arch_44__012_1351')
	supermarket.getChild('Arch_44__012_1352')
	supermarket.getChild('Arch_44__012_1353')
	supermarket.getChild('Arch_44__012_1354')
	supermarket.getChild('Arch_44__012_1355')
	supermarket.getChild('Arch_44__012_1356')
	supermarket.getChild('Arch_44__012_1357')
	supermarket.getChild('Arch_44__012_1358')
	supermarket.getChild('Arch_44__012_1359')
	supermarket.getChild('Arch_44__012_1360')
	supermarket.getChild('Arch_44__012_1361')
	supermarket.getChild('Arch_44__012_1362')
	supermarket.getChild('Arch_44__012_1363')
	supermarket.getChild('Arch_44__012_1364')
	supermarket.getChild('Arch_44__012_1365')
	supermarket.getChild('Arch_44__012_1366')
	supermarket.getChild('Arch_44__012_1367')
	supermarket.getChild('Arch_44__012_1368')
	supermarket.getChild('Arch_44__012_1369')
	supermarket.getChild('Arch_44__012_1370')
	supermarket.getChild('Arch_44__012_1371')
	supermarket.getChild('Arch_44__012_1372')
	supermarket.getChild('Arch_44__012_1373')
	supermarket.getChild('Arch_44__012_1374')
	supermarket.getChild('Arch_44__012_1375')
	supermarket.getChild('Arch_44__012_1376')
	supermarket.getChild('Arch_44__012_1377')
	supermarket.getChild('Arch_44__012_1378')
	supermarket.getChild('Arch_44__012_1379')
	supermarket.getChild('Arch_44__012_1380')
	supermarket.getChild('Arch_44__012_1381')
	supermarket.getChild('Arch_44__012_1382')
	supermarket.getChild('Arch_44__012_1383')
	supermarket.getChild('Arch_44__012_1384')
	supermarket.getChild('Arch_44__012_1385')
	supermarket.getChild('Arch_44__012_1386')
	supermarket.getChild('Arch_44__012_1387')
	supermarket.getChild('Arch_44__012_1388')
	supermarket.getChild('Arch_44__012_1389')
	supermarket.getChild('Arch_44__012_1390')
	supermarket.getChild('Arch_44__012_1391')
	supermarket.getChild('Arch_44__012_1392')
	supermarket.getChild('Arch_44__012_1393')
	supermarket.getChild('Arch_44__012_1394')
	supermarket.getChild('Arch_44__012_1395')
	supermarket.getChild('Arch_44__012_1396')
	supermarket.getChild('Arch_44__012_1397')
	supermarket.getChild('Arch_44__012_1398')
	supermarket.getChild('Arch_44__012_1399')
	supermarket.getChild('Arch_44__012_1400')
	supermarket.getChild('Arch_44__012_1401')
	supermarket.getChild('Arch_44__012_1402')
	supermarket.getChild('Arch_44__012_1403')
	supermarket.getChild('Arch_44__012_1404')
	supermarket.getChild('Arch_44__012_1405')
	supermarket.getChild('Arch_44__012_1406')
	supermarket.getChild('Arch_44__012_1407')
	supermarket.getChild('Arch_44__012_1408')
	supermarket.getChild('Arch_44__012_1409')
	supermarket.getChild('Arch_44__012_1410')
	supermarket.getChild('Arch_44__012_1411')
	supermarket.getChild('Arch_44__012_1412')
	supermarket.getChild('Arch_44__012_1413')
	supermarket.getChild('Arch_44__012_1414')
	supermarket.getChild('Arch_44__012_1415')
	supermarket.getChild('Arch_44__012_1416')
	supermarket.getChild('Arch_44__012_1417')
	supermarket.getChild('Arch_44__012_1418')
	supermarket.getChild('Arch_44__012_1419')
	supermarket.getChild('Arch_44__012_1420')
	supermarket.getChild('Arch_44__012_1421')
	supermarket.getChild('Arch_44__012_1422')
	supermarket.getChild('Arch_44__012_1423')
	supermarket.getChild('Arch_44__012_1424')
	supermarket.getChild('Arch_44__012_1425')
	supermarket.getChild('Arch_44__012_1426')
	supermarket.getChild('Arch_44__012_1427')
	supermarket.getChild('Arch_44__012_1428')
	supermarket.getChild('Arch_44__012_1429')
	supermarket.getChild('Arch_44__012_1430')
	supermarket.getChild('Arch_44__012_1431')
	supermarket.getChild('Arch_44__012_1432')
	supermarket.getChild('Arch_44__012_1433')
	supermarket.getChild('Arch_44__012_1434')
	supermarket.getChild('Arch_44__012_1435')
	supermarket.getChild('Arch_44__012_1436')
	supermarket.getChild('Arch_44__012_1437')
	supermarket.getChild('Arch_44__012_1438')
	supermarket.getChild('Arch_44__012_1439')
	supermarket.getChild('Arch_44__012_1440')
	supermarket.getChild('Arch_44__012_1441')
	supermarket.getChild('Arch_44__012_1442')
	supermarket.getChild('Arch_44__012_1443')
	supermarket.getChild('Arch_44__012_1444')
	supermarket.getChild('Arch_44__012_1445')
	supermarket.getChild('Arch_44__012_1446')
	supermarket.getChild('Arch_44__012_1447')
	supermarket.getChild('Arch_44__012_1448')
	supermarket.getChild('Arch_44__012_1449')
	supermarket.getChild('Arch_44__012_1450')
	supermarket.getChild('Arch_44__012_1451')
	supermarket.getChild('Arch_44__012_1452')
	supermarket.getChild('Arch_44__012_1453')
	supermarket.getChild('Arch_44__012_1454')
	supermarket.getChild('Arch_44__012_1455')
	supermarket.getChild('Arch_44__012_1456')
	supermarket.getChild('Arch_44__012_1457')
	supermarket.getChild('Arch_44__012_1458')
	supermarket.getChild('Arch_44__012_1459')
	supermarket.getChild('Arch_44__012_1460')
	supermarket.getChild('Arch_44__012_1461')
	supermarket.getChild('Arch_44__012_1462')
	supermarket.getChild('Arch_44__012_1463')
	supermarket.getChild('Arch_44__012_1464')
	supermarket.getChild('Arch_44__012_1465')
	supermarket.getChild('Arch_44__012_1466')
	supermarket.getChild('Arch_44__012_1467')
	supermarket.getChild('Arch_44__012_1468')
	supermarket.getChild('Arch_44__012_1469')
	supermarket.getChild('Arch_44__012_1470')
	supermarket.getChild('Arch_44__012_1471')
	supermarket.getChild('Arch_44__012_1472')
	supermarket.getChild('Arch_44__012_1473')
	supermarket.getChild('Arch_44__012_1474')
	supermarket.getChild('Arch_44__012_1475')
	supermarket.getChild('Arch_44__012_1476')
	supermarket.getChild('Arch_44__012_1477')
	supermarket.getChild('Arch_44__012_1478')
	supermarket.getChild('Arch_44__012_1479')
	supermarket.getChild('Arch_44__012_1480')
	supermarket.getChild('Arch_44__012_1481')
	supermarket.getChild('Arch_44__012_1482')
	supermarket.getChild('Arch_44__012_1483')
	supermarket.getChild('Arch_44__012_1484')
	supermarket.getChild('Arch_44__012_1485')
	supermarket.getChild('Arch_44__012_1486')
	supermarket.getChild('Arch_44__012_1487')
	supermarket.getChild('Arch_44__012_1488')
	supermarket.getChild('Arch_44__012_1489')
	supermarket.getChild('Arch_44__012_1490')
	supermarket.getChild('Arch_44__012_1491')
	supermarket.getChild('Arch_44__012_1492')
	supermarket.getChild('Arch_44__012_1493')
	supermarket.getChild('Arch_44__012_1494')
	supermarket.getChild('Arch_44__012_1495')
	supermarket.getChild('Arch_44__012_1496')
	supermarket.getChild('Arch_44__012_1497')
	supermarket.getChild('Arch_44__012_1498')
	supermarket.getChild('Arch_44__012_1499')
	supermarket.getChild('Arch_44__012_1500')
	supermarket.getChild('Arch_44__012_1501')
	supermarket.getChild('Arch_44__012_1502')
	supermarket.getChild('Arch_44__012_1503')
	supermarket.getChild('Arch_44__012_1504')
	supermarket.getChild('Arch_44__012_1505')
	supermarket.getChild('Arch_44__012_1506')
	supermarket.getChild('Arch_44__012_1507')
	supermarket.getChild('Arch_44__012_1508')
	supermarket.getChild('Arch_44__012_1509')
	supermarket.getChild('Arch_44__012_1510')
	supermarket.getChild('Arch_44__012_1511')
	supermarket.getChild('Arch_44__012_1512')
	supermarket.getChild('Arch_44__012_1513')
	supermarket.getChild('Arch_44__012_1514')
	supermarket.getChild('Arch_44__012_1515')
	supermarket.getChild('Arch_44__012_1516')
	supermarket.getChild('Arch_44__012_1517')
	supermarket.getChild('Arch_44__012_1518')
	supermarket.getChild('Arch_44__012_1519')
	supermarket.getChild('Arch_44__012_1520')
	supermarket.getChild('Arch_44__012_1521')
	supermarket.getChild('Arch_44__012_1522')
	supermarket.getChild('Arch_44__012_1523')
	supermarket.getChild('Arch_44__012_1524')
	supermarket.getChild('Arch_44__012_1525')
	supermarket.getChild('Arch_44__012_1526')
	supermarket.getChild('Arch_44__012_1527')
	supermarket.getChild('Arch_44__012_1528')
	supermarket.getChild('Arch_44__012_1529')
	supermarket.getChild('Arch_44__012_1530')
	supermarket.getChild('Arch_44__012_1531')
	supermarket.getChild('Arch_44__012_1532')
	supermarket.getChild('Arch_44__012_1533')
	supermarket.getChild('Arch_44__012_1534')
	supermarket.getChild('Arch_44__012_1535')
	supermarket.getChild('Arch_44__012_1536')
	supermarket.getChild('Arch_44__012_1537')
	supermarket.getChild('Arch_44__012_1538')
	supermarket.getChild('Arch_44__012_1539')
	supermarket.getChild('Arch_44__012_1540')
	supermarket.getChild('Arch_44__012_1541')
	supermarket.getChild('Arch_44__012_1542')
	supermarket.getChild('Arch_44__012_1543')
	supermarket.getChild('Arch_44__012_1544')
	supermarket.getChild('Arch_44__012_1545')
	supermarket.getChild('Arch_44__012_1546')
	supermarket.getChild('Arch_44__012_1547')
	supermarket.getChild('Arch_44__012_1548')
	supermarket.getChild('Arch_44__012_1549')
	supermarket.getChild('Arch_44__012_1550')
	supermarket.getChild('Arch_44__012_1551')
	supermarket.getChild('Arch_44__012_1552')
	supermarket.getChild('Arch_44__012_1553')
	supermarket.getChild('Arch_44__012_1554')
	supermarket.getChild('Arch_44__012_1555')
	supermarket.getChild('Arch_44__012_1556')
	supermarket.getChild('Arch_44__012_1557')
	supermarket.getChild('Arch_44__012_1558')
	supermarket.getChild('Arch_44__012_1559')
	supermarket.getChild('Arch_44__012_1560')
	supermarket.getChild('Arch_44__012_1561')
	supermarket.getChild('Arch_44__012_1562')
	supermarket.getChild('Arch_44__012_1563')
	supermarket.getChild('Arch_44__012_1564')
	supermarket.getChild('Arch_44__012_1565')
	supermarket.getChild('Arch_44__012_1566')
	supermarket.getChild('Arch_44__012_1567')
	supermarket.getChild('Arch_44__012_1568')
	supermarket.getChild('Arch_44__012_1569')
	supermarket.getChild('Arch_44__012_1570')
	supermarket.getChild('Arch_44__012_1571')
	supermarket.getChild('Arch_44__012_1572')
	supermarket.getChild('Arch_44__012_1573')
	supermarket.getChild('Arch_44__012_1574')
	supermarket.getChild('Arch_44__012_1575')
	supermarket.getChild('Arch_44__012_1576')
	supermarket.getChild('Arch_44__012_1577')
	supermarket.getChild('Arch_44__012_1578')
	supermarket.getChild('Arch_44__012_1579')
	supermarket.getChild('Arch_44__012_1580')
	supermarket.getChild('Arch_44__012_1581')
	supermarket.getChild('Arch_44__012_1582')
	supermarket.getChild('Arch_44__012_1583')
	supermarket.getChild('Arch_44__012_1584')
	supermarket.getChild('Arch_44__012_1585')
	supermarket.getChild('Arch_44__012_1586')
	supermarket.getChild('Arch_44__012_1587')
	supermarket.getChild('Arch_44__012_1588')
	supermarket.getChild('Arch_44__012_1589')
	supermarket.getChild('Arch_44__012_1590')
	supermarket.getChild('Arch_44__012_1591')
	supermarket.getChild('Arch_44__012_1592')
	supermarket.getChild('Arch_44__012_1593')
	supermarket.getChild('Arch_44__012_1594')
	supermarket.getChild('Arch_44__012_1595')
	supermarket.getChild('Arch_44__012_1596')
	supermarket.getChild('Arch_44__012_1597')
	supermarket.getChild('Arch_44__012_1598')
	supermarket.getChild('Arch_44__012_1599')
	supermarket.getChild('Arch_44__012_1600')
	supermarket.getChild('Arch_44__012_1601')
	supermarket.getChild('Arch_44__012_1602')
	supermarket.getChild('Arch_44__012_1603')
	supermarket.getChild('Arch_44__012_1604')
	supermarket.getChild('Arch_44__012_1605')
	supermarket.getChild('Arch_44__012_1606')
	supermarket.getChild('Arch_44__012_1607')
	supermarket.getChild('Arch_44__012_1608')
	supermarket.getChild('Arch_44__012_1609')
	supermarket.getChild('Arch_44__012_1610')
	supermarket.getChild('Arch_44__012_1611')
	supermarket.getChild('Arch_44__012_1612')
	supermarket.getChild('Arch_44__012_1613')
	supermarket.getChild('Arch_44__012_1614')
	supermarket.getChild('Arch_44__012_1615')
	supermarket.getChild('Arch_44__012_1616')
	supermarket.getChild('Arch_44__012_1617')
	supermarket.getChild('Arch_44__012_1618')
	supermarket.getChild('Arch_44__012_1619')
	supermarket.getChild('Arch_44__012_1620')
	supermarket.getChild('Arch_44__012_1621')
	supermarket.getChild('Arch_44__012_1622')
	supermarket.getChild('Arch_44__012_1623')
	supermarket.getChild('Arch_44__012_1624')
	supermarket.getChild('Arch_44__012_1625')
	supermarket.getChild('Arch_44__012_1626')
	supermarket.getChild('Arch_44__012_1627')
	supermarket.getChild('Arch_44__012_1628')
	supermarket.getChild('Arch_44__012_1629')
	supermarket.getChild('Arch_44__012_1630')
	supermarket.getChild('Arch_44__012_1631')
	supermarket.getChild('Arch_44__012_1632')
	supermarket.getChild('Arch_44__012_1633')
	supermarket.getChild('Arch_44__012_1634')
	supermarket.getChild('Arch_44__012_1635')
	supermarket.getChild('Arch_44__012_1636')
	supermarket.getChild('Arch_44__012_1637')
	supermarket.getChild('Arch_44__012_1638')
	supermarket.getChild('Arch_44__012_1639')
	supermarket.getChild('Arch_44__012_1640')
	supermarket.getChild('Arch_44__012_1641')
	supermarket.getChild('Arch_44__012_1642')
	supermarket.getChild('Arch_44__012_1643')
	supermarket.getChild('Arch_44__012_1644')
	supermarket.getChild('Arch_44__012_1645')
	supermarket.getChild('Arch_44__012_1646')
	supermarket.getChild('Arch_44__012_1647')
	supermarket.getChild('Arch_44__012_1648')
	supermarket.getChild('Arch_44__012_1649')
	supermarket.getChild('Arch_44__012_1650')
	supermarket.getChild('Arch_44__012_1651')
	supermarket.getChild('Arch_44__012_1652')
	supermarket.getChild('Arch_44__012_1653')
	supermarket.getChild('Arch_44__012_1654')
	supermarket.getChild('Arch_44__012_1655')
	supermarket.getChild('Arch_44__012_1656')
	supermarket.getChild('Arch_44__012_1657')
	supermarket.getChild('Arch_44__012_1658')
	supermarket.getChild('Arch_44__012_1659')
	supermarket.getChild('Arch_44__012_1660')
	supermarket.getChild('Arch_44__012_1661')
	supermarket.getChild('Arch_44__012_1662')
	supermarket.getChild('Arch_44__012_1663')
	supermarket.getChild('Arch_44__012_1664')
	supermarket.getChild('Arch_44__012_1665')
	supermarket.getChild('Arch_44__012_1666')
	supermarket.getChild('Arch_44__012_1667')
	supermarket.getChild('Arch_44__012_1668')
	supermarket.getChild('Arch_44__012_1669')
	supermarket.getChild('Arch_44__012_1670')
	supermarket.getChild('Arch_44__012_1671')
	supermarket.getChild('Arch_44__012_1672')
	supermarket.getChild('Arch_44__012_1673')
	supermarket.getChild('Arch_44__012_1674')
	supermarket.getChild('Arch_44__012_1675')
	supermarket.getChild('Arch_44__012_1676')
	supermarket.getChild('Arch_44__012_1677')
	supermarket.getChild('Arch_44__012_1678')
	supermarket.getChild('Arch_44__012_1679')
	supermarket.getChild('Arch_44__012_1680')
	supermarket.getChild('Arch_44__012_1681')
	supermarket.getChild('Arch_44__012_1682')
	supermarket.getChild('Arch_44__012_1683')
	supermarket.getChild('Arch_44__012_1684')
	supermarket.getChild('Arch_44__012_1685')
	supermarket.getChild('Arch_44__012_1686')
	supermarket.getChild('Arch_44__012_1687')
	supermarket.getChild('Arch_44__012_1688')
	supermarket.getChild('Arch_44__012_1689')
	supermarket.getChild('Arch_44__012_1690')
	supermarket.getChild('Arch_44__012_1691')
	supermarket.getChild('Arch_44__012_1692')
	supermarket.getChild('Arch_44__012_1693')
	supermarket.getChild('Arch_44__012_1694')
	supermarket.getChild('Arch_44__012_1695')
	supermarket.getChild('Arch_44__012_1696')
	supermarket.getChild('Arch_44__012_1697')
	supermarket.getChild('Arch_44__012_1698')
	supermarket.getChild('Arch_44__012_1699')
	supermarket.getChild('Arch_44__012_1700')
	supermarket.getChild('Arch_44__012_1701')
	supermarket.getChild('Arch_44__012_1702')
	supermarket.getChild('Arch_44__012_1703')
	supermarket.getChild('Arch_44__012_1704')
	supermarket.getChild('Arch_44__012_1705')
	supermarket.getChild('Arch_44__012_1706')
	supermarket.getChild('Arch_44__012_1707')
	supermarket.getChild('Arch_44__012_1708')
	supermarket.getChild('Arch_44__012_1709')
	supermarket.getChild('Arch_44__012_1710')
	supermarket.getChild('Arch_44__012_1711')
	supermarket.getChild('Arch_44__012_1712')
	supermarket.getChild('Arch_44__012_1713')
	supermarket.getChild('Arch_44__012_1714')
	supermarket.getChild('Arch_44__012_1715')
	supermarket.getChild('Arch_44__012_1716')
	supermarket.getChild('Box153')
	supermarket.getChild('Box154')
	supermarket.getChild('Box07')
	supermarket.getChild('glass_mug')
	supermarket.getChild('Arch_44__483706705')
	supermarket.getChild('glass_mug01')
	supermarket.getChild('glass_mug02')
	supermarket.getChild('glass_mug03')
	supermarket.getChild('glass_mug04')
	supermarket.getChild('glass_mug05')
	supermarket.getChild('glass_mug06')
	supermarket.getChild('Arch_44__911720116')
	supermarket.getChild('glass_mug07')
	supermarket.getChild('glass_mug08')
	supermarket.getChild('glass_mug09')
	supermarket.getChild('glass_mug10')
	supermarket.getChild('glass_mug11')
	supermarket.getChild('glass_mug12')
	supermarket.getChild('glass_mug13')
	supermarket.getChild('glass_mug14')
	supermarket.getChild('glass_mug15')
	supermarket.getChild('glass_mug16')
	supermarket.getChild('glass_mug17')
	supermarket.getChild('glass_mug18')
	supermarket.getChild('glass_mug19')
	supermarket.getChild('glass_mug20')
	supermarket.getChild('glass_mug21')
	supermarket.getChild('glass_mug22')
	supermarket.getChild('glass_mug23')
	supermarket.getChild('glass_mug24')
	supermarket.getChild('glass_mug25')
	supermarket.getChild('glass_mug26')
	supermarket.getChild('glass_mug27')
	supermarket.getChild('glass_mug28')
	supermarket.getChild('glass_mug29')
	supermarket.getChild('glass_mug30')
	supermarket.getChild('glass_mug31')
	supermarket.getChild('glass_mug32')
	supermarket.getChild('glass_mug33')
	supermarket.getChild('glass_mug34')
	supermarket.getChild('glass_mug35')
	supermarket.getChild('glass_mug36')
	supermarket.getChild('glass_mug37')
	supermarket.getChild('glass_mug38')
	supermarket.getChild('glass_mug39')
	supermarket.getChild('glass_mug40')
	supermarket.getChild('glass_mug41')
	supermarket.getChild('glass_mug42')
	supermarket.getChild('Box10')
	supermarket.getChild('glass_mug43')
	supermarket.getChild('Arch_44__031_1788')
	supermarket.getChild('Arch_44__012_1717')
	supermarket.getChild('Box03')
	supermarket.getChild('Box155')
	supermarket.getChild('Box156')
	supermarket.getChild('Box157')
	#'''

#-------------------------------------------------------------------------------
# <node3d:on-the-fly> objects functions
#-------------------------------------------------------------------------------
def createQuad(size_x,size_y,x=0.0,y=0.0,z=0.0):
	viz.startlayer(viz.QUADS) 
	viz.vertexcolor(0,0,0)
	viz.vertex(x-0.5*size_x,y-0.5*size_y,z)
	viz.vertex(x+0.5*size_x,y-0.5*size_y,z)
	viz.vertex(x+0.5*size_x,y+0.5*size_y,z)
	viz.vertex(x-0.5*size_x,y+0.5*size_y,z)
	return viz.endlayer()

#create sphere of distractors - only for the evaluation application
def createLowDensityDistractors():
	global children_low
	
	if children_low != None:
		for child in children_low:
			child.remove()

	children_low = []
	childpos = [[0.08472345769405365, -1.4815624952316284, 1.5626322031021118] ,
				[0.25317707657814026, -1.4815624952316284, 1.544311761856079] ,
				[0.33641311526298523, -1.4815624952316284, 1.528340220451355] ,
				[0.4186623990535736, -1.4815624952316284, 1.5078856945037842] ,
				[0.499683678150177, -1.4815624952316284, 1.4830083847045898] ,
				[-0.499683678150177, -1.4815624952316284, 1.4830083847045898] ,
				[-0.4186623990535736, -1.4815624952316284, 1.5078856945037842] ,
				[-0.33641311526298523, -1.4815624952316284, 1.528340220451355] ,
				[-0.25317707657814026, -1.4815624952316284, 1.544311761856079] ,
				[-0.08472345769405365, -1.4815624952316284, 1.5626322031021118] ,
				[0.08510042726993561, -1.414218783378601, 1.6238129138946533] ,
				[0.2543689012527466, -1.414218783378601, 1.6060220003128052] ,
				[0.3380729854106903, -1.414218783378601, 1.5905084609985352] ,
				[0.5024743676185608, -1.414218783378601, 1.5464571714401245] ,
				[0.661370575428009, -1.414218783378601, 1.4854626655578613] ,
				[0.813020646572113, -1.414218783378601, 1.4081931114196777] ,
				[-0.813020646572113, -1.414218783378601, 1.4081931114196777] ,
				[-0.661370575428009, -1.414218783378601, 1.4854626655578613] ,
				[-0.5024743676185608, -1.414218783378601, 1.5464571714401245] ,
				[-0.3380729854106903, -1.414218783378601, 1.5905084609985352] ,
				[-0.2543689012527466, -1.414218783378601, 1.6060220003128052] ,
				[-0.08510042726993561, -1.414218783378601, 1.6238129138946533] ,
				[0.08520437777042389, -1.3468749523162842, 1.6800872087478638] ,
				[0.25473883748054504, -1.3468749523162842, 1.6628471612930298] ,
				[0.3386336863040924, -1.3468749523162842, 1.647810697555542] ,
				[0.5036025047302246, -1.3468749523162842, 1.6050972938537598] ,
				[0.6634036898612976, -1.3468749523162842, 1.5459134578704834] ,
				[0.8163974285125732, -1.3468749523162842, 1.4708664417266846] ,
				[0.9610138535499573, -1.3468749523162842, 1.3807263374328613] ,
				[-0.9610138535499573, -1.3468749523162842, 1.3807263374328613] ,
				[-0.8163974285125732, -1.3468749523162842, 1.4708664417266846] ,
				[-0.6634036898612976, -1.3468749523162842, 1.5459134578704834] ,
				[-0.5036025047302246, -1.3468749523162842, 1.6050972938537598] ,
				[-0.3386336863040924, -1.3468749523162842, 1.647810697555542] ,
				[-0.25473883748054504, -1.3468749523162842, 1.6628471612930298] ,
				[-0.08520437777042389, -1.3468749523162842, 1.6800872087478638] ,
				[0.08508431911468506, -1.2795312404632568, 1.7319310903549194] ,
				[0.16996365785598755, -1.2795312404632568, 1.7256700992584229] ,
				[0.3382904827594757, -1.2795312404632568, 1.700701117515564] ,
				[0.5033593773841858, -1.2795312404632568, 1.659353494644165] ,
				[0.6635806560516357, -1.2795312404632568, 1.6020253896713257] ,
				[0.8174113035202026, -1.2795312404632568, 1.5292689800262451] ,
				[0.9633697867393494, -1.2795312404632568, 1.4417847394943237] ,
				[1.1000505685806274, -1.2795312404632568, 1.3404154777526855] ,
				[-1.1000505685806274, -1.2795312404632568, 1.3404154777526855] ,
				[-0.9633697867393494, -1.2795312404632568, 1.4417847394943237] ,
				[-0.8174113035202026, -1.2795312404632568, 1.5292689800262451] ,
				[-0.6635806560516357, -1.2795312404632568, 1.6020253896713257] ,
				[-0.5033593773841858, -1.2795312404632568, 1.659353494644165] ,
				[-0.3382904827594757, -1.2795312404632568, 1.700701117515564] ,
				[-0.16996365785598755, -1.2795312404632568, 1.7256700992584229] ,
				[-0.08508431911468506, -1.2795312404632568, 1.7319310903549194] ,
				[0.16936592757701874, -1.2121875286102295, 1.7736802101135254] ,
				[0.33719804883003235, -1.2121875286102295, 1.7495496273040771] ,
				[0.501976490020752, -1.2121875286102295, 1.709574818611145] ,
				[0.5827527642250061, -1.2121875286102295, 1.683753490447998] ,
				[0.7401649355888367, -1.2121875286102295, 1.6207351684570312] ,
				[0.8908740878105164, -1.2121875286102295, 1.5430392026901245] ,
				[1.0335153341293335, -1.2121875286102295, 1.4513691663742065] ,
				[1.1014035940170288, -1.2121875286102295, 1.4005486965179443] ,
				[1.2295470237731934, -1.2121875286102295, 1.289511799812317] ,
				[1.289511799812317, -1.2121875286102295, 1.2295470237731934] ,
				[-1.289511799812317, -1.2121875286102295, 1.2295470237731934] ,
				[-1.2295470237731934, -1.2121875286102295, 1.289511799812317] ,
				[-1.1014035940170288, -1.2121875286102295, 1.4005486965179443] ,
				[-1.0335153341293335, -1.2121875286102295, 1.4513691663742065] ,
				[-0.8908740878105164, -1.2121875286102295, 1.5430392026901245] ,
				[-0.7401649355888367, -1.2121875286102295, 1.6207351684570312] ,
				[-0.5827527642250061, -1.2121875286102295, 1.683753490447998] ,
				[-0.501976490020752, -1.2121875286102295, 1.709574818611145] ,
				[-0.33719804883003235, -1.2121875286102295, 1.7495496273040771] ,
				[-0.16936592757701874, -1.2121875286102295, 1.7736802101135254] ,
				[0.08494351804256439, -1.1448436975479126, 1.8237714767456055] ,
				[0.16970308125019073, -1.1448436975479126, 1.8178445100784302] ,
				[0.742598831653595, -1.1448436975479126, 1.667904257774353] ,
				[0.8944154381752014, -1.1448436975479126, 1.5916591882705688] ,
				[1.0384877920150757, -1.1448436975479126, 1.5016326904296875] ,
				[1.2373682260513306, -1.1448436975479126, 1.3424893617630005] ,
				[1.2984880208969116, -1.1448436975479126, 1.2834666967391968] ,
				[1.3567955493927002, -1.1448436975479126, 1.2216641902923584] ,
				[1.4121646881103516, -1.1448436975479126, 1.15721595287323] ,
				[-1.4121646881103516, -1.1448436975479126, 1.15721595287323] ,
				[-1.3567955493927002, -1.1448436975479126, 1.2216641902923584] ,
				[-1.2984880208969116, -1.1448436975479126, 1.2834666967391968] ,
				[-1.2373682260513306, -1.1448436975479126, 1.3424893617630005] ,
				[-1.0384877920150757, -1.1448436975479126, 1.5016326904296875] ,
				[-0.8944154381752014, -1.1448436975479126, 1.5916591882705688] ,
				[-0.742598831653595, -1.1448436975479126, 1.667904257774353] ,
				[-0.16970308125019073, -1.1448436975479126, 1.8178445100784302] ,
				[-0.08494351804256439, -1.1448436975479126, 1.8237714767456055] ,
				[0.5035176277160645, -1.0774999856948853, 1.7970778942108154] ,
				[0.5847890377044678, -1.0774999856948853, 1.7722980976104736] ,
				[1.0412638187408447, -1.0774999856948853, 1.5488022565841675] ,
				[1.1777898073196411, -1.0774999856948853, 1.4476981163024902] ,
				[1.3045562505722046, -1.0774999856948853, 1.3345979452133179] ,
				[1.3639479875564575, -1.0774999856948853, 1.2738385200500488] ,
				[1.4205127954483032, -1.0774999856948853, 1.210438847541809] ,
				[1.4741332530975342, -1.0774999856948853, 1.1445304155349731] ,
				[-1.4741332530975342, -1.0774999856948853, 1.1445304155349731] ,
				[-1.4205127954483032, -1.0774999856948853, 1.210438847541809] ,
				[-1.3639479875564575, -1.0774999856948853, 1.2738385200500488] ,
				[-1.3045562505722046, -1.0774999856948853, 1.3345979452133179] ,
				[-1.1777898073196411, -1.0774999856948853, 1.4476981163024902] ,
				[-1.0412638187408447, -1.0774999856948853, 1.5488022565841675] ,
				[-0.5847890377044678, -1.0774999856948853, 1.7722980976104736] ,
				[-0.5035176277160645, -1.0774999856948853, 1.7970778942108154] ,
				[0.0847984105348587, -1.010156273841858, 1.9016883373260498] ,
				[0.16942845284938812, -1.010156273841858, 1.8960230350494385] ,
				[0.8961713314056396, -1.010156273841858, 1.679430365562439] ,
				[0.9700950384140015, -1.010156273841858, 1.6378415822982788] ,
				[1.3080273866653442, -1.010156273841858, 1.3829944133758545] ,
				[1.3683370351791382, -1.010156273841858, 1.3233530521392822] ,
				[1.4259297847747803, -1.010156273841858, 1.2610841989517212] ,
				[1.48069167137146, -1.010156273841858, 1.1963117122650146] ,
				[-1.48069167137146, -1.010156273841858, 1.1963117122650146] ,
				[-1.4259297847747803, -1.010156273841858, 1.2610841989517212] ,
				[-1.3683370351791382, -1.010156273841858, 1.3233530521392822] ,
				[-1.3080273866653442, -1.010156273841858, 1.3829944133758545] ,
				[-0.9700950384140015, -1.010156273841858, 1.6378415822982788] ,
				[-0.8961713314056396, -1.010156273841858, 1.679430365562439] ,
				[-0.16942845284938812, -1.010156273841858, 1.8960230350494385] ,
				[-0.0847984105348587, -1.010156273841858, 1.9016883373260498] ,
				[0.33882710337638855, -0.9428125023841858, 1.907963752746582] ,
				[0.4223059117794037, -0.9428125023841858, 1.8912396430969238] ,
				[0.5866584777832031, -0.9428125023841858, 1.8468788862228394] ,
				[0.7464836239814758, -0.9428125023841858, 1.7882649898529053] ,
				[1.1182560920715332, -0.9428125023841858, 1.5826032161712646] ,
				[1.377747654914856, -0.9428125023841858, 1.3626961708068848] ,
				[1.4362733364105225, -0.9428125023841858, 1.300864577293396] ,
				[1.4920265674591064, -0.9428125023841858, 1.23652184009552] ,
				[1.544899821281433, -0.9428125023841858, 1.1697922945022583] ,
				[-1.544899821281433, -0.9428125023841858, 1.1697922945022583] ,
				[-1.4920265674591064, -0.9428125023841858, 1.23652184009552] ,
				[-1.4362733364105225, -0.9428125023841858, 1.300864577293396] ,
				[-1.377747654914856, -0.9428125023841858, 1.3626961708068848] ,
				[-1.1182560920715332, -0.9428125023841858, 1.5826032161712646] ,
				[-0.7464836239814758, -0.9428125023841858, 1.7882649898529053] ,
				[-0.5866584777832031, -0.9428125023841858, 1.8468788862228394] ,
				[-0.4223059117794037, -0.9428125023841858, 1.8912396430969238] ,
				[-0.33882710337638855, -0.9428125023841858, 1.907963752746582] ,
				[0.0847175344824791, -0.8754687309265137, 1.9673337936401367] ,
				[0.972321629524231, -0.8754687309265137, 1.7123581171035767] ,
				[1.3773432970046997, -0.8754687309265137, 1.4073041677474976] ,
				[1.5470679998397827, -0.8754687309265137, 1.2182611227035522] ,
				[-1.5470679998397827, -0.8754687309265137, 1.2182611227035522] ,
				[-1.3773432970046997, -0.8754687309265137, 1.4073041677474976] ,
				[-0.972321629524231, -0.8754687309265137, 1.7123581171035767] ,
				[-0.0847175344824791, -0.8754687309265137, 1.9673337936401367] ,
				[0.08478642255067825, -0.8081250190734863, 1.9959384202957153] ,
				[0.169420063495636, -0.8081250190734863, 1.9905415773391724] ,
				[0.33761945366859436, -0.8081250190734863, 1.9690028429031372] ,
				[0.42088207602500916, -0.8081250190734863, 1.952899694442749] ,
				[0.5849832892417908, -0.8081250190734863, 1.9101710319519043] ,
				[0.7448697090148926, -0.8081250190734863, 1.8536796569824219] ,
				[0.8228709697723389, -0.8081250190734863, 1.8203961849212646] ,
				[1.2550193071365356, -0.8081250190734863, 1.554311990737915] ,
				[1.4996469020843506, -0.8081250190734863, 1.3198553323745728] ,
				[-1.4996469020843506, -0.8081250190734863, 1.3198553323745728] ,
				[-1.2550193071365356, -0.8081250190734863, 1.554311990737915] ,
				[-0.8228709697723389, -0.8081250190734863, 1.8203961849212646] ,
				[-0.7448697090148926, -0.8081250190734863, 1.8536796569824219] ,
				[-0.5849832892417908, -0.8081250190734863, 1.9101710319519043] ,
				[-0.42088207602500916, -0.8081250190734863, 1.952899694442749] ,
				[-0.33761945366859436, -0.8081250190734863, 1.9690028429031372] ,
				[-0.169420063495636, -0.8081250190734863, 1.9905415773391724] ,
				[-0.08478642255067825, -0.8081250190734863, 1.9959384202957153] ,
				[0.8231035470962524, -0.7407812476158142, 1.8487207889556885] ,
				[0.9749137759208679, -0.7407812476158142, 1.7733615636825562] ,
				[1.1198856830596924, -0.7407812476158142, 1.6855634450912476] ,
				[1.385302186012268, -0.7407812476158142, 1.4751969575881958] ,
				[1.44586181640625, -0.7407812476158142, 1.415892481803894] ,
				[1.6119191646575928, -0.7407812476158142, 1.2235132455825806] ,
				[-1.6119191646575928, -0.7407812476158142, 1.2235132455825806] ,
				[-1.44586181640625, -0.7407812476158142, 1.415892481803894] ,
				[-1.385302186012268, -0.7407812476158142, 1.4751969575881958] ,
				[-1.1198856830596924, -0.7407812476158142, 1.6855634450912476] ,
				[-0.9749137759208679, -0.7407812476158142, 1.7733615636825562] ,
				[-0.8231035470962524, -0.7407812476158142, 1.8487207889556885] ,
				[0.08515513688325882, -0.6734374761581421, 2.0453009605407715] ,
				[0.1701628565788269, -0.6734374761581421, 2.0399880409240723] ,
				[0.3391478955745697, -0.6734374761581421, 2.0187830924987793] ,
				[0.4228326678276062, -0.6734374761581421, 2.002927780151367] ,
				[0.5878626108169556, -0.6734374761581421, 1.9608478546142578] ,
				[0.6689220666885376, -0.6734374761581421, 1.9346964359283447] ,
				[1.2644016742706299, -0.6734374761581421, 1.6099053621292114] ,
				[1.5696685314178467, -0.6734374761581421, 1.3140195608139038] ,
				[-1.5696685314178467, -0.6734374761581421, 1.3140195608139038] ,
				[-1.2644016742706299, -0.6734374761581421, 1.6099053621292114] ,
				[-0.6689220666885376, -0.6734374761581421, 1.9346964359283447] ,
				[-0.5878626108169556, -0.6734374761581421, 1.9608478546142578] ,
				[-0.4228326678276062, -0.6734374761581421, 2.002927780151367] ,
				[-0.3391478955745697, -0.6734374761581421, 2.0187830924987793] ,
				[-0.1701628565788269, -0.6734374761581421, 2.0399880409240723] ,
				[-0.08515513688325882, -0.6734374761581421, 2.0453009605407715] ,
				[0.5863293409347534, -0.6060937643051147, 1.9831523895263672] ,
				[0.6672533750534058, -0.6060937643051147, 1.9574085474014282] ,
				[0.8255914449691772, -0.6060937643051147, 1.8960680961608887] ,
				[0.9783633351325989, -0.6060937643051147, 1.8219441175460815] ,
				[1.0523384809494019, -0.6060937643051147, 1.7802413702011108] ,
				[1.454779863357544, -0.6060937643051147, 1.4697928428649902] ,
				[1.5138957500457764, -0.6060937643051147, 1.408827543258667] ,
				[-1.5138957500457764, -0.6060937643051147, 1.408827543258667] ,
				[-1.454779863357544, -0.6060937643051147, 1.4697928428649902] ,
				[-1.0523384809494019, -0.6060937643051147, 1.7802413702011108] ,
				[-0.9783633351325989, -0.6060937643051147, 1.8219441175460815] ,
				[-0.8255914449691772, -0.6060937643051147, 1.8960680961608887] ,
				[-0.6672533750534058, -0.6060937643051147, 1.9574085474014282] ,
				[-0.5863293409347534, -0.6060937643051147, 1.9831523895263672] ,
				[0.08510822802782059, -0.5387499928474426, 2.0848333835601807] ,
				[0.17007480561733246, -0.5387499928474426, 2.0796267986297607] ,
				[1.1987435817718506, -0.5387499928474426, 1.7078604698181152] ,
				[1.3339613676071167, -0.5387499928474426, 1.6044689416885376] ,
				[1.6313459873199463, -0.5387499928474426, 1.3009549379348755] ,
				[-1.6313459873199463, -0.5387499928474426, 1.3009549379348755] ,
				[-1.3339613676071167, -0.5387499928474426, 1.6044689416885376] ,
				[-1.1987435817718506, -0.5387499928474426, 1.7078604698181152] ,
				[-0.17007480561733246, -0.5387499928474426, 2.0796267986297607] ,
				[-0.08510822802782059, -0.5387499928474426, 2.0848333835601807] ,
				[0.08467153459787369, -0.4714062511920929, 2.101102590560913] ,
				[0.16920574009418488, -0.4714062511920929, 2.095989227294922] ,
				[0.33731409907341003, -0.4714062511920929, 2.0755770206451416] ,
				[0.42061561346054077, -0.4714062511920929, 2.0603115558624268] ,
				[0.585037887096405, -0.4714062511920929, 2.019785165786743] ,
				[0.6658919453620911, -0.4714062511920929, 1.994589924812317] ,
				[0.8242304921150208, -0.4714062511920929, 1.934540033340454] ,
				[0.9014580845832825, -0.4714062511920929, 1.8997827768325806] ,
				[0.9772235751152039, -0.4714062511920929, 1.8619439601898193] ,
				[1.4566662311553955, -0.4714062511920929, 1.5165501832962036] ,
				[1.5165501832962036, -0.4714062511920929, 1.4566662311553955] ,
				[1.573974370956421, -0.4714062511920929, 1.394419550895691] ,
				[-1.573974370956421, -0.4714062511920929, 1.394419550895691] ,
				[-1.5165501832962036, -0.4714062511920929, 1.4566662311553955] ,
				[-1.4566662311553955, -0.4714062511920929, 1.5165501832962036] ,
				[-0.9772235751152039, -0.4714062511920929, 1.8619439601898193] ,
				[-0.9014580845832825, -0.4714062511920929, 1.8997827768325806] ,
				[-0.8242304921150208, -0.4714062511920929, 1.934540033340454] ,
				[-0.6658919453620911, -0.4714062511920929, 1.994589924812317] ,
				[-0.585037887096405, -0.4714062511920929, 2.019785165786743] ,
				[-0.42061561346054077, -0.4714062511920929, 2.0603115558624268] ,
				[-0.33731409907341003, -0.4714062511920929, 2.0755770206451416] ,
				[-0.16920574009418488, -0.4714062511920929, 2.095989227294922] ,
				[-0.08467153459787369, -0.4714062511920929, 2.101102590560913] ,
				[0.9020476341247559, -0.40406250953674316, 1.914959192276001] ,
				[1.052270531654358, -0.40406250953674316, 1.836704969406128] ,
				[1.1957556009292603, -0.40406250953674316, 1.746690273284912] ,
				[1.3315842151641846, -0.40406250953674316, 1.645491361618042] ,
				[1.6847120523452759, -0.40406250953674316, 1.281602144241333] ,
				[-1.6847120523452759, -0.40406250953674316, 1.281602144241333] ,
				[-1.3315842151641846, -0.40406250953674316, 1.645491361618042] ,
				[-1.1957556009292603, -0.40406250953674316, 1.746690273284912] ,
				[-1.052270531654358, -0.40406250953674316, 1.836704969406128] ,
				[-0.9020476341247559, -0.40406250953674316, 1.914959192276001] ,
				[0.08462298661470413, -0.33671873807907104, 2.1268484592437744] ,
				[0.1691121608018875, -0.33671873807907104, 2.121802568435669] ,
				[0.33715516328811646, -0.33671873807907104, 2.1016592979431152] ,
				[0.42044323682785034, -0.33671873807907104, 2.0865936279296875] ,
				[0.5848943591117859, -0.33671873807907104, 2.046593189239502] ,
				[0.6657973527908325, -0.33671873807907104, 2.021721839904785] ,
				[1.4595462083816528, -0.33671873807907104, 1.5493128299713135] ,
				[1.5199875831604004, -0.33671873807907104, 1.4900615215301514] ,
				[1.5780255794525146, -0.33671873807907104, 1.428454041481018] ,
				[1.633568286895752, -0.33671873807907104, 1.3645879030227661] ,
				[-1.633568286895752, -0.33671873807907104, 1.3645879030227661] ,
				[-1.5780255794525146, -0.33671873807907104, 1.428454041481018] ,
				[-1.5199875831604004, -0.33671873807907104, 1.4900615215301514] ,
				[-1.4595462083816528, -0.33671873807907104, 1.5493128299713135] ,
				[-0.6657973527908325, -0.33671873807907104, 2.021721839904785] ,
				[-0.5848943591117859, -0.33671873807907104, 2.046593189239502] ,
				[-0.42044323682785034, -0.33671873807907104, 2.0865936279296875] ,
				[-0.33715516328811646, -0.33671873807907104, 2.1016592979431152] ,
				[-0.1691121608018875, -0.33671873807907104, 2.121802568435669] ,
				[-0.08462298661470413, -0.33671873807907104, 2.1268484592437744] ,
				[0.0850033164024353, -0.2693749964237213, 2.1364073753356934] ,
				[0.1698722243309021, -0.2693749964237213, 2.1313388347625732] ,
				[0.3386704623699188, -0.2693749964237213, 2.111104965209961] ,
				[0.42233288288116455, -0.2693749964237213, 2.0959715843200684] ,
				[0.5875231027603149, -0.2693749964237213, 2.0557916164398193] ,
				[0.6687897443771362, -0.2693749964237213, 2.030808210372925] ,
				[0.8280236124992371, -0.2693749964237213, 1.9712531566619873] ,
				[0.9057391285896301, -0.2693749964237213, 1.9367753267288208] ,
				[1.0567530393600464, -0.2693749964237213, 1.858691692352295] ,
				[1.2010859251022339, -0.2693749964237213, 1.7688568830490112] ,
				[1.337825059890747, -0.2693749964237213, 1.6678388118743896] ,
				[-1.337825059890747, -0.2693749964237213, 1.6678388118743896] ,
				[-1.2010859251022339, -0.2693749964237213, 1.7688568830490112] ,
				[-1.0567530393600464, -0.2693749964237213, 1.858691692352295] ,
				[-0.9057391285896301, -0.2693749964237213, 1.9367753267288208] ,
				[-0.8280236124992371, -0.2693749964237213, 1.9712531566619873] ,
				[-0.6687897443771362, -0.2693749964237213, 2.030808210372925] ,
				[-0.5875231027603149, -0.2693749964237213, 2.0557916164398193] ,
				[-0.42233288288116455, -0.2693749964237213, 2.0959715843200684] ,
				[-0.3386704623699188, -0.2693749964237213, 2.111104965209961] ,
				[-0.1698722243309021, -0.2693749964237213, 2.1313388347625732] ,
				[-0.0850033164024353, -0.2693749964237213, 2.1364073753356934] ,
				[1.3353341817855835, -0.20203125476837158, 1.6793125867843628] ,
				[1.4637502431869507, -0.20203125476837158, 1.5686439275741577] ,
				[1.5245792865753174, -0.20203125476837158, 1.5095914602279663] ,
				[1.5830278396606445, -0.20203125476837158, 1.4481819868087769] ,
				[1.6390047073364258, -0.20203125476837158, 1.3845113515853882] ,
				[1.6924225091934204, -0.20203125476837158, 1.3186789751052856] ,
				[-1.6924225091934204, -0.20203125476837158, 1.3186789751052856] ,
				[-1.6390047073364258, -0.20203125476837158, 1.3845113515853882] ,
				[-1.5830278396606445, -0.20203125476837158, 1.4481819868087769] ,
				[-1.5245792865753174, -0.20203125476837158, 1.5095914602279663] ,
				[-1.4637502431869507, -0.20203125476837158, 1.5686439275741577] ,
				[-1.3353341817855835, -0.20203125476837158, 1.6793125867843628] ,
				[0.08497028797864914, -0.13468749821186066, 2.1491076946258545] ,
				[0.16980791091918945, -0.13468749821186066, 2.144073009490967] ,
				[0.3385556936264038, -0.13468749821186066, 2.1239736080169678] ,
				[0.42220237851142883, -0.13468749821186066, 2.108940362930298] ,
				[0.5873885154724121, -0.13468749821186066, 2.069023609161377] ,
				[0.6686700582504272, -0.13468749821186066, 2.0442028045654297] ,
				[0.8279756903648376, -0.13468749821186066, 1.9850291013717651] ,
				[0.9057510495185852, -0.13468749821186066, 1.9507689476013184] ,
				[1.0569398403167725, -0.13468749821186066, 1.8731690645217896] ,
				[-1.0569398403167725, -0.13468749821186066, 1.8731690645217896] ,
				[-0.9057510495185852, -0.13468749821186066, 1.9507689476013184] ,
				[-0.8279756903648376, -0.13468749821186066, 1.9850291013717651] ,
				[-0.6686700582504272, -0.13468749821186066, 2.0442028045654297] ,
				[-0.5873885154724121, -0.13468749821186066, 2.069023609161377] ,
				[-0.42220237851142883, -0.13468749821186066, 2.108940362930298] ,
				[-0.3385556936264038, -0.13468749821186066, 2.1239736080169678] ,
				[-0.16980791091918945, -0.13468749821186066, 2.144073009490967] ,
				[-0.08497028797864914, -0.13468749821186066, 2.1491076946258545] ,
				[0.08509515225887299, -0.06734374910593033, 2.152266025543213] ,
				[0.17005744576454163, -0.06734374910593033, 2.147223949432373] ,
				[0.3390531837940216, -0.06734374910593033, 2.1270949840545654] ,
				[0.4228228032588959, -0.06734374910593033, 2.112039566040039] ,
				[0.5882516503334045, -0.06734374910593033, 2.072064161300659] ,
				[0.6696526408195496, -0.06734374910593033, 2.0472066402435303] ,
				[0.8291923999786377, -0.06734374910593033, 1.9879461526870728] ,
				[0.9070820212364197, -0.06734374910593033, 1.953635573387146] ,
				[1.0584930181503296, -0.06734374910593033, 1.8759217262268066] ,
				[1.2032958269119263, -0.06734374910593033, 1.7864962816238403] ,
				[1.3405863046646118, -0.06734374910593033, 1.685917615890503] ,
				[1.4695073366165161, -0.06734374910593033, 1.5748136043548584] ,
				[1.5305756330490112, -0.06734374910593033, 1.515528917312622] ,
				[1.5892541408538818, -0.06734374910593033, 1.4538779258728027] ,
				[1.6454511880874634, -0.06734374910593033, 1.3899568319320679] ,
				[1.699079155921936, -0.06734374910593033, 1.323865532875061] ,
				[-1.699079155921936, -0.06734374910593033, 1.323865532875061] ,
				[-1.6454511880874634, -0.06734374910593033, 1.3899568319320679] ,
				[-1.5892541408538818, -0.06734374910593033, 1.4538779258728027] ,
				[-1.5305756330490112, -0.06734374910593033, 1.515528917312622] ,
				[-1.4695073366165161, -0.06734374910593033, 1.5748136043548584] ,
				[-1.3405863046646118, -0.06734374910593033, 1.685917615890503] ,
				[-1.2032958269119263, -0.06734374910593033, 1.7864962816238403] ,
				[-1.0584930181503296, -0.06734374910593033, 1.8759217262268066] ,
				[-0.9070820212364197, -0.06734374910593033, 1.953635573387146] ,
				[-0.8291923999786377, -0.06734374910593033, 1.9879461526870728] ,
				[-0.6696526408195496, -0.06734374910593033, 2.0472066402435303] ,
				[-0.5882516503334045, -0.06734374910593033, 2.072064161300659] ,
				[-0.4228228032588959, -0.06734374910593033, 2.112039566040039] ,
				[-0.3390531837940216, -0.06734374910593033, 2.1270949840545654] ,
				[-0.17005744576454163, -0.06734374910593033, 2.147223949432373] ,
				[-0.08509515225887299, -0.06734374910593033, 2.152266025543213] ,
				[0.08509515225887299, 0.06734374910593033, 2.152266025543213] ,
				[0.17005744576454163, 0.06734374910593033, 2.147223949432373] ,
				[0.3390531837940216, 0.06734374910593033, 2.1270949840545654] ,
				[0.4228228032588959, 0.06734374910593033, 2.112039566040039] ,
				[0.5882516503334045, 0.06734374910593033, 2.072064161300659] ,
				[0.6696526408195496, 0.06734374910593033, 2.0472066402435303] ,
				[0.8291923999786377, 0.06734374910593033, 1.9879461526870728] ,
				[0.9070820212364197, 0.06734374910593033, 1.953635573387146] ,
				[1.0584930181503296, 0.06734374910593033, 1.8759217262268066] ,
				[1.2032958269119263, 0.06734374910593033, 1.7864962816238403] ,
				[1.3405863046646118, 0.06734374910593033, 1.685917615890503] ,
				[1.4695073366165161, 0.06734374910593033, 1.5748136043548584] ,
				[1.5305756330490112, 0.06734374910593033, 1.515528917312622] ,
				[1.5892541408538818, 0.06734374910593033, 1.4538779258728027] ,
				[1.6454511880874634, 0.06734374910593033, 1.3899568319320679] ,
				[1.699079155921936, 0.06734374910593033, 1.323865532875061] ,
				[-1.699079155921936, 0.06734374910593033, 1.323865532875061] ,
				[-1.6454511880874634, 0.06734374910593033, 1.3899568319320679] ,
				[-1.5892541408538818, 0.06734374910593033, 1.4538779258728027] ,
				[-1.5305756330490112, 0.06734374910593033, 1.515528917312622] ,
				[-1.4695073366165161, 0.06734374910593033, 1.5748136043548584] ,
				[-1.3405863046646118, 0.06734374910593033, 1.685917615890503] ,
				[-1.2032958269119263, 0.06734374910593033, 1.7864962816238403] ,
				[-1.0584930181503296, 0.06734374910593033, 1.8759217262268066] ,
				[-0.9070820212364197, 0.06734374910593033, 1.953635573387146] ,
				[-0.8291923999786377, 0.06734374910593033, 1.9879461526870728] ,
				[-0.6696526408195496, 0.06734374910593033, 2.0472066402435303] ,
				[-0.5882516503334045, 0.06734374910593033, 2.072064161300659] ,
				[-0.4228228032588959, 0.06734374910593033, 2.112039566040039] ,
				[-0.3390531837940216, 0.06734374910593033, 2.1270949840545654] ,
				[-0.17005744576454163, 0.06734374910593033, 2.147223949432373] ,
				[-0.08509515225887299, 0.06734374910593033, 2.152266025543213] ,
				[0.08497028797864914, 0.13468749821186066, 2.1491076946258545] ,
				[0.16980791091918945, 0.13468749821186066, 2.144073009490967] ,
				[0.3385556936264038, 0.13468749821186066, 2.1239736080169678] ,
				[0.42220237851142883, 0.13468749821186066, 2.108940362930298] ,
				[0.5873885154724121, 0.13468749821186066, 2.069023609161377] ,
				[0.6686700582504272, 0.13468749821186066, 2.0442028045654297] ,
				[0.8279756903648376, 0.13468749821186066, 1.9850291013717651] ,
				[0.9057510495185852, 0.13468749821186066, 1.9507689476013184] ,
				[1.0569398403167725, 0.13468749821186066, 1.8731690645217896] ,
				[-1.0569398403167725, 0.13468749821186066, 1.8731690645217896] ,
				[-0.9057510495185852, 0.13468749821186066, 1.9507689476013184] ,
				[-0.8279756903648376, 0.13468749821186066, 1.9850291013717651] ,
				[-0.6686700582504272, 0.13468749821186066, 2.0442028045654297] ,
				[-0.5873885154724121, 0.13468749821186066, 2.069023609161377] ,
				[-0.42220237851142883, 0.13468749821186066, 2.108940362930298] ,
				[-0.3385556936264038, 0.13468749821186066, 2.1239736080169678] ,
				[-0.16980791091918945, 0.13468749821186066, 2.144073009490967] ,
				[-0.08497028797864914, 0.13468749821186066, 2.1491076946258545] ,
				[1.3353341817855835, 0.20203125476837158, 1.6793125867843628] ,
				[1.4637502431869507, 0.20203125476837158, 1.5686439275741577] ,
				[1.5245792865753174, 0.20203125476837158, 1.5095914602279663] ,
				[1.5830278396606445, 0.20203125476837158, 1.4481819868087769] ,
				[1.6390047073364258, 0.20203125476837158, 1.3845113515853882] ,
				[1.6924225091934204, 0.20203125476837158, 1.3186789751052856] ,
				[-1.6924225091934204, 0.20203125476837158, 1.3186789751052856] ,
				[-1.6390047073364258, 0.20203125476837158, 1.3845113515853882] ,
				[-1.5830278396606445, 0.20203125476837158, 1.4481819868087769] ,
				[-1.5245792865753174, 0.20203125476837158, 1.5095914602279663] ,
				[-1.4637502431869507, 0.20203125476837158, 1.5686439275741577] ,
				[-1.3353341817855835, 0.20203125476837158, 1.6793125867843628] ,
				[0.0850033164024353, 0.2693749964237213, 2.1364073753356934] ,
				[0.1698722243309021, 0.2693749964237213, 2.1313388347625732] ,
				[0.3386704623699188, 0.2693749964237213, 2.111104965209961] ,
				[0.42233288288116455, 0.2693749964237213, 2.0959715843200684] ,
				[0.5875231027603149, 0.2693749964237213, 2.0557916164398193] ,
				[0.6687897443771362, 0.2693749964237213, 2.030808210372925] ,
				[0.8280236124992371, 0.2693749964237213, 1.9712531566619873] ,
				[0.9057391285896301, 0.2693749964237213, 1.9367753267288208] ,
				[1.0567530393600464, 0.2693749964237213, 1.858691692352295] ,
				[1.2010859251022339, 0.2693749964237213, 1.7688568830490112] ,
				[1.337825059890747, 0.2693749964237213, 1.6678388118743896] ,
				[-1.337825059890747, 0.2693749964237213, 1.6678388118743896] ,
				[-1.2010859251022339, 0.2693749964237213, 1.7688568830490112] ,
				[-1.0567530393600464, 0.2693749964237213, 1.858691692352295] ,
				[-0.9057391285896301, 0.2693749964237213, 1.9367753267288208] ,
				[-0.8280236124992371, 0.2693749964237213, 1.9712531566619873] ,
				[-0.6687897443771362, 0.2693749964237213, 2.030808210372925] ,
				[-0.5875231027603149, 0.2693749964237213, 2.0557916164398193] ,
				[-0.42233288288116455, 0.2693749964237213, 2.0959715843200684] ,
				[-0.3386704623699188, 0.2693749964237213, 2.111104965209961] ,
				[-0.1698722243309021, 0.2693749964237213, 2.1313388347625732] ,
				[-0.0850033164024353, 0.2693749964237213, 2.1364073753356934] ,
				[0.08462298661470413, 0.33671873807907104, 2.1268484592437744] ,
				[0.1691121608018875, 0.33671873807907104, 2.121802568435669] ,
				[0.33715516328811646, 0.33671873807907104, 2.1016592979431152] ,
				[0.42044323682785034, 0.33671873807907104, 2.0865936279296875] ,
				[0.5848943591117859, 0.33671873807907104, 2.046593189239502] ,
				[0.6657973527908325, 0.33671873807907104, 2.021721839904785] ,
				[1.4595462083816528, 0.33671873807907104, 1.5493128299713135] ,
				[1.5199875831604004, 0.33671873807907104, 1.4900615215301514] ,
				[1.5780255794525146, 0.33671873807907104, 1.428454041481018] ,
				[1.633568286895752, 0.33671873807907104, 1.3645879030227661] ,
				[-1.633568286895752, 0.33671873807907104, 1.3645879030227661] ,
				[-1.5780255794525146, 0.33671873807907104, 1.428454041481018] ,
				[-1.5199875831604004, 0.33671873807907104, 1.4900615215301514] ,
				[-1.4595462083816528, 0.33671873807907104, 1.5493128299713135] ,
				[-0.6657973527908325, 0.33671873807907104, 2.021721839904785] ,
				[-0.5848943591117859, 0.33671873807907104, 2.046593189239502] ,
				[-0.42044323682785034, 0.33671873807907104, 2.0865936279296875] ,
				[-0.33715516328811646, 0.33671873807907104, 2.1016592979431152] ,
				[-0.1691121608018875, 0.33671873807907104, 2.121802568435669] ,
				[-0.08462298661470413, 0.33671873807907104, 2.1268484592437744] ,
				[0.9020476341247559, 0.40406250953674316, 1.914959192276001] ,
				[1.052270531654358, 0.40406250953674316, 1.836704969406128] ,
				[1.1957556009292603, 0.40406250953674316, 1.746690273284912] ,
				[1.3315842151641846, 0.40406250953674316, 1.645491361618042] ,
				[1.6847120523452759, 0.40406250953674316, 1.281602144241333] ,
				[-1.6847120523452759, 0.40406250953674316, 1.281602144241333] ,
				[-1.3315842151641846, 0.40406250953674316, 1.645491361618042] ,
				[-1.1957556009292603, 0.40406250953674316, 1.746690273284912] ,
				[-1.052270531654358, 0.40406250953674316, 1.836704969406128] ,
				[-0.9020476341247559, 0.40406250953674316, 1.914959192276001] ,
				[0.08467153459787369, 0.4714062511920929, 2.101102590560913] ,
				[0.16920574009418488, 0.4714062511920929, 2.095989227294922] ,
				[0.33731409907341003, 0.4714062511920929, 2.0755770206451416] ,
				[0.42061561346054077, 0.4714062511920929, 2.0603115558624268] ,
				[0.585037887096405, 0.4714062511920929, 2.019785165786743] ,
				[0.6658919453620911, 0.4714062511920929, 1.994589924812317] ,
				[0.8242304921150208, 0.4714062511920929, 1.934540033340454] ,
				[0.9014580845832825, 0.4714062511920929, 1.8997827768325806] ,
				[0.9772235751152039, 0.4714062511920929, 1.8619439601898193] ,
				[1.4566662311553955, 0.4714062511920929, 1.5165501832962036] ,
				[1.5165501832962036, 0.4714062511920929, 1.4566662311553955] ,
				[1.573974370956421, 0.4714062511920929, 1.394419550895691] ,
				[-1.573974370956421, 0.4714062511920929, 1.394419550895691] ,
				[-1.5165501832962036, 0.4714062511920929, 1.4566662311553955] ,
				[-1.4566662311553955, 0.4714062511920929, 1.5165501832962036] ,
				[-0.9772235751152039, 0.4714062511920929, 1.8619439601898193] ,
				[-0.9014580845832825, 0.4714062511920929, 1.8997827768325806] ,
				[-0.8242304921150208, 0.4714062511920929, 1.934540033340454] ,
				[-0.6658919453620911, 0.4714062511920929, 1.994589924812317] ,
				[-0.585037887096405, 0.4714062511920929, 2.019785165786743] ,
				[-0.42061561346054077, 0.4714062511920929, 2.0603115558624268] ,
				[-0.33731409907341003, 0.4714062511920929, 2.0755770206451416] ,
				[-0.16920574009418488, 0.4714062511920929, 2.095989227294922] ,
				[-0.08467153459787369, 0.4714062511920929, 2.101102590560913] ,
				[0.08510822802782059, 0.5387499928474426, 2.0848333835601807] ,
				[0.17007480561733246, 0.5387499928474426, 2.0796267986297607] ,
				[1.1987435817718506, 0.5387499928474426, 1.7078604698181152] ,
				[1.3339613676071167, 0.5387499928474426, 1.6044689416885376] ,
				[1.6313459873199463, 0.5387499928474426, 1.3009549379348755] ,
				[-1.6313459873199463, 0.5387499928474426, 1.3009549379348755] ,
				[-1.3339613676071167, 0.5387499928474426, 1.6044689416885376] ,
				[-1.1987435817718506, 0.5387499928474426, 1.7078604698181152] ,
				[-0.17007480561733246, 0.5387499928474426, 2.0796267986297607] ,
				[-0.08510822802782059, 0.5387499928474426, 2.0848333835601807] ,
				[0.5863293409347534, 0.6060937643051147, 1.9831523895263672] ,
				[0.6672533750534058, 0.6060937643051147, 1.9574085474014282] ,
				[0.8255914449691772, 0.6060937643051147, 1.8960680961608887] ,
				[0.9783633351325989, 0.6060937643051147, 1.8219441175460815] ,
				[1.0523384809494019, 0.6060937643051147, 1.7802413702011108] ,
				[1.454779863357544, 0.6060937643051147, 1.4697928428649902] ,
				[1.5138957500457764, 0.6060937643051147, 1.408827543258667] ,
				[-1.5138957500457764, 0.6060937643051147, 1.408827543258667] ,
				[-1.454779863357544, 0.6060937643051147, 1.4697928428649902] ,
				[-1.0523384809494019, 0.6060937643051147, 1.7802413702011108] ,
				[-0.9783633351325989, 0.6060937643051147, 1.8219441175460815] ,
				[-0.8255914449691772, 0.6060937643051147, 1.8960680961608887] ,
				[-0.6672533750534058, 0.6060937643051147, 1.9574085474014282] ,
				[-0.5863293409347534, 0.6060937643051147, 1.9831523895263672] ,
				[0.08515513688325882, 0.6734374761581421, 2.0453009605407715] ,
				[0.1701628565788269, 0.6734374761581421, 2.0399880409240723] ,
				[0.3391478955745697, 0.6734374761581421, 2.0187830924987793] ,
				[0.4228326678276062, 0.6734374761581421, 2.002927780151367] ,
				[0.5878626108169556, 0.6734374761581421, 1.9608478546142578] ,
				[0.6689220666885376, 0.6734374761581421, 1.9346964359283447] ,
				[1.2644016742706299, 0.6734374761581421, 1.6099053621292114] ,
				[1.5696685314178467, 0.6734374761581421, 1.3140195608139038] ,
				[-1.5696685314178467, 0.6734374761581421, 1.3140195608139038] ,
				[-1.2644016742706299, 0.6734374761581421, 1.6099053621292114] ,
				[-0.6689220666885376, 0.6734374761581421, 1.9346964359283447] ,
				[-0.5878626108169556, 0.6734374761581421, 1.9608478546142578] ,
				[-0.4228326678276062, 0.6734374761581421, 2.002927780151367] ,
				[-0.3391478955745697, 0.6734374761581421, 2.0187830924987793] ,
				[-0.1701628565788269, 0.6734374761581421, 2.0399880409240723] ,
				[-0.08515513688325882, 0.6734374761581421, 2.0453009605407715] ,
				[0.8231035470962524, 0.7407812476158142, 1.8487207889556885] ,
				[0.9749137759208679, 0.7407812476158142, 1.7733615636825562] ,
				[1.1198856830596924, 0.7407812476158142, 1.6855634450912476] ,
				[1.385302186012268, 0.7407812476158142, 1.4751969575881958] ,
				[1.44586181640625, 0.7407812476158142, 1.415892481803894] ,
				[1.6119191646575928, 0.7407812476158142, 1.2235132455825806] ,
				[-1.6119191646575928, 0.7407812476158142, 1.2235132455825806] ,
				[-1.44586181640625, 0.7407812476158142, 1.415892481803894] ,
				[-1.385302186012268, 0.7407812476158142, 1.4751969575881958] ,
				[-1.1198856830596924, 0.7407812476158142, 1.6855634450912476] ,
				[-0.9749137759208679, 0.7407812476158142, 1.7733615636825562] ,
				[-0.8231035470962524, 0.7407812476158142, 1.8487207889556885] ,
				[0.08478642255067825, 0.8081250190734863, 1.9959384202957153] ,
				[0.169420063495636, 0.8081250190734863, 1.9905415773391724] ,
				[0.33761945366859436, 0.8081250190734863, 1.9690028429031372] ,
				[0.42088207602500916, 0.8081250190734863, 1.952899694442749] ,
				[0.5849832892417908, 0.8081250190734863, 1.9101710319519043] ,
				[0.7448697090148926, 0.8081250190734863, 1.8536796569824219] ,
				[0.8228709697723389, 0.8081250190734863, 1.8203961849212646] ,
				[1.2550193071365356, 0.8081250190734863, 1.554311990737915] ,
				[1.4996469020843506, 0.8081250190734863, 1.3198553323745728] ,
				[-1.4996469020843506, 0.8081250190734863, 1.3198553323745728] ,
				[-1.2550193071365356, 0.8081250190734863, 1.554311990737915] ,
				[-0.8228709697723389, 0.8081250190734863, 1.8203961849212646] ,
				[-0.7448697090148926, 0.8081250190734863, 1.8536796569824219] ,
				[-0.5849832892417908, 0.8081250190734863, 1.9101710319519043] ,
				[-0.42088207602500916, 0.8081250190734863, 1.952899694442749] ,
				[-0.33761945366859436, 0.8081250190734863, 1.9690028429031372] ,
				[-0.169420063495636, 0.8081250190734863, 1.9905415773391724] ,
				[-0.08478642255067825, 0.8081250190734863, 1.9959384202957153] ,
				[0.0847175344824791, 0.8754687309265137, 1.9673337936401367] ,
				[0.972321629524231, 0.8754687309265137, 1.7123581171035767] ,
				[1.3773432970046997, 0.8754687309265137, 1.4073041677474976] ,
				[1.5470679998397827, 0.8754687309265137, 1.2182611227035522] ,
				[-1.5470679998397827, 0.8754687309265137, 1.2182611227035522] ,
				[-1.3773432970046997, 0.8754687309265137, 1.4073041677474976] ,
				[-0.972321629524231, 0.8754687309265137, 1.7123581171035767] ,
				[-0.0847175344824791, 0.8754687309265137, 1.9673337936401367] ,
				[0.33882710337638855, 0.9428125023841858, 1.907963752746582] ,
				[0.4223059117794037, 0.9428125023841858, 1.8912396430969238] ,
				[0.5866584777832031, 0.9428125023841858, 1.8468788862228394] ,
				[0.7464836239814758, 0.9428125023841858, 1.7882649898529053] ,
				[1.1182560920715332, 0.9428125023841858, 1.5826032161712646] ,
				[1.377747654914856, 0.9428125023841858, 1.3626961708068848] ,
				[1.4362733364105225, 0.9428125023841858, 1.300864577293396] ,
				[1.4920265674591064, 0.9428125023841858, 1.23652184009552] ,
				[1.544899821281433, 0.9428125023841858, 1.1697922945022583] ,
				[-1.544899821281433, 0.9428125023841858, 1.1697922945022583] ,
				[-1.4920265674591064, 0.9428125023841858, 1.23652184009552] ,
				[-1.4362733364105225, 0.9428125023841858, 1.300864577293396] ,
				[-1.377747654914856, 0.9428125023841858, 1.3626961708068848] ,
				[-1.1182560920715332, 0.9428125023841858, 1.5826032161712646] ,
				[-0.7464836239814758, 0.9428125023841858, 1.7882649898529053] ,
				[-0.5866584777832031, 0.9428125023841858, 1.8468788862228394] ,
				[-0.4223059117794037, 0.9428125023841858, 1.8912396430969238] ,
				[-0.33882710337638855, 0.9428125023841858, 1.907963752746582] ,
				[0.0847984105348587, 1.010156273841858, 1.9016883373260498] ,
				[0.16942845284938812, 1.010156273841858, 1.8960230350494385] ,
				[0.8961713314056396, 1.010156273841858, 1.679430365562439] ,
				[0.9700950384140015, 1.010156273841858, 1.6378415822982788] ,
				[1.3080273866653442, 1.010156273841858, 1.3829944133758545] ,
				[1.3683370351791382, 1.010156273841858, 1.3233530521392822] ,
				[1.4259297847747803, 1.010156273841858, 1.2610841989517212] ,
				[1.48069167137146, 1.010156273841858, 1.1963117122650146] ,
				[-1.48069167137146, 1.010156273841858, 1.1963117122650146] ,
				[-1.4259297847747803, 1.010156273841858, 1.2610841989517212] ,
				[-1.3683370351791382, 1.010156273841858, 1.3233530521392822] ,
				[-1.3080273866653442, 1.010156273841858, 1.3829944133758545] ,
				[-0.9700950384140015, 1.010156273841858, 1.6378415822982788] ,
				[-0.8961713314056396, 1.010156273841858, 1.679430365562439] ,
				[-0.16942845284938812, 1.010156273841858, 1.8960230350494385] ,
				[-0.0847984105348587, 1.010156273841858, 1.9016883373260498] ,
				[0.5035176277160645, 1.0774999856948853, 1.7970778942108154] ,
				[0.5847890377044678, 1.0774999856948853, 1.7722980976104736] ,
				[1.0412638187408447, 1.0774999856948853, 1.5488022565841675] ,
				[1.1777898073196411, 1.0774999856948853, 1.4476981163024902] ,
				[1.3045562505722046, 1.0774999856948853, 1.3345979452133179] ,
				[1.3639479875564575, 1.0774999856948853, 1.2738385200500488] ,
				[1.4205127954483032, 1.0774999856948853, 1.210438847541809] ,
				[1.4741332530975342, 1.0774999856948853, 1.1445304155349731] ,
				[-1.4741332530975342, 1.0774999856948853, 1.1445304155349731] ,
				[-1.4205127954483032, 1.0774999856948853, 1.210438847541809] ,
				[-1.3639479875564575, 1.0774999856948853, 1.2738385200500488] ,
				[-1.3045562505722046, 1.0774999856948853, 1.3345979452133179] ,
				[-1.1777898073196411, 1.0774999856948853, 1.4476981163024902] ,
				[-1.0412638187408447, 1.0774999856948853, 1.5488022565841675] ,
				[-0.5847890377044678, 1.0774999856948853, 1.7722980976104736] ,
				[-0.5035176277160645, 1.0774999856948853, 1.7970778942108154] ,
				[0.08494351804256439, 1.1448436975479126, 1.8237714767456055] ,
				[0.16970308125019073, 1.1448436975479126, 1.8178445100784302] ,
				[0.742598831653595, 1.1448436975479126, 1.667904257774353] ,
				[0.8944154381752014, 1.1448436975479126, 1.5916591882705688] ,
				[1.0384877920150757, 1.1448436975479126, 1.5016326904296875] ,
				[1.2373682260513306, 1.1448436975479126, 1.3424893617630005] ,
				[1.2984880208969116, 1.1448436975479126, 1.2834666967391968] ,
				[1.3567955493927002, 1.1448436975479126, 1.2216641902923584] ,
				[1.4121646881103516, 1.1448436975479126, 1.15721595287323] ,
				[-1.4121646881103516, 1.1448436975479126, 1.15721595287323] ,
				[-1.3567955493927002, 1.1448436975479126, 1.2216641902923584] ,
				[-1.2984880208969116, 1.1448436975479126, 1.2834666967391968] ,
				[-1.2373682260513306, 1.1448436975479126, 1.3424893617630005] ,
				[-1.0384877920150757, 1.1448436975479126, 1.5016326904296875] ,
				[-0.8944154381752014, 1.1448436975479126, 1.5916591882705688] ,
				[-0.742598831653595, 1.1448436975479126, 1.667904257774353] ,
				[-0.16970308125019073, 1.1448436975479126, 1.8178445100784302] ,
				[-0.08494351804256439, 1.1448436975479126, 1.8237714767456055] ,
				[0.16936592757701874, 1.2121875286102295, 1.7736802101135254] ,
				[0.33719804883003235, 1.2121875286102295, 1.7495496273040771] ,
				[0.33719804883003235, 1.2121875286102295, 1.7495496273040771] ,
				[0.501976490020752, 1.2121875286102295, 1.709574818611145] ,
				[0.5827527642250061, 1.2121875286102295, 1.683753490447998] ,
				[0.7401649355888367, 1.2121875286102295, 1.6207351684570312] ,
				[0.8908740878105164, 1.2121875286102295, 1.5430392026901245] ,
				[1.0335153341293335, 1.2121875286102295, 1.4513691663742065] ,
				[1.1014035940170288, 1.2121875286102295, 1.4005486965179443] ,
				[1.2295470237731934, 1.2121875286102295, 1.289511799812317] ,
				[1.289511799812317, 1.2121875286102295, 1.2295470237731934] ,
				[-1.289511799812317, 1.2121875286102295, 1.2295470237731934] ,
				[-1.2295470237731934, 1.2121875286102295, 1.289511799812317] ,
				[-1.1014035940170288, 1.2121875286102295, 1.4005486965179443] ,
				[-1.0335153341293335, 1.2121875286102295, 1.4513691663742065] ,
				[-0.8908740878105164, 1.2121875286102295, 1.5430392026901245] ,
				[-0.7401649355888367, 1.2121875286102295, 1.6207351684570312] ,
				[-0.5827527642250061, 1.2121875286102295, 1.683753490447998] ,
				[-0.501976490020752, 1.2121875286102295, 1.709574818611145] ,
				[-0.33719804883003235, 1.2121875286102295, 1.7495496273040771] ,
				[-0.16936592757701874, 1.2121875286102295, 1.7736802101135254] ,
				[0.08508431911468506, 1.2795312404632568, 1.7319310903549194] ,
				[0.16996365785598755, 1.2795312404632568, 1.7256700992584229] ,
				[0.3382904827594757, 1.2795312404632568, 1.700701117515564] ,
				[0.5033593773841858, 1.2795312404632568, 1.659353494644165] ,
				[0.6635806560516357, 1.2795312404632568, 1.6020253896713257] ,
				[0.8174113035202026, 1.2795312404632568, 1.5292689800262451] ,
				[0.9633697867393494, 1.2795312404632568, 1.4417847394943237] ,
				[1.1000505685806274, 1.2795312404632568, 1.3404154777526855] ,
				[-1.1000505685806274, 1.2795312404632568, 1.3404154777526855] ,
				[-0.9633697867393494, 1.2795312404632568, 1.4417847394943237] ,
				[-0.8174113035202026, 1.2795312404632568, 1.5292689800262451] ,
				[-0.6635806560516357, 1.2795312404632568, 1.6020253896713257] ,
				[-0.5033593773841858, 1.2795312404632568, 1.659353494644165] ,
				[-0.3382904827594757, 1.2795312404632568, 1.700701117515564] ,
				[-0.16996365785598755, 1.2795312404632568, 1.7256700992584229] ,
				[-0.08508431911468506, 1.2795312404632568, 1.7319310903549194] ,
				[0.08520437777042389, 1.3468749523162842, 1.6800872087478638] ,
				[0.25473883748054504, 1.3468749523162842, 1.6628471612930298] ,
				[0.3386336863040924, 1.3468749523162842, 1.647810697555542] ,
				[0.5036025047302246, 1.3468749523162842, 1.6050972938537598] ,
				[0.6634036898612976, 1.3468749523162842, 1.5459134578704834] ,
				[0.8163974285125732, 1.3468749523162842, 1.4708664417266846] ,
				[0.9610138535499573, 1.3468749523162842, 1.3807263374328613] ,
				[-0.9610138535499573, 1.3468749523162842, 1.3807263374328613] ,
				[-0.8163974285125732, 1.3468749523162842, 1.4708664417266846] ,
				[-0.6634036898612976, 1.3468749523162842, 1.5459134578704834] ,
				[-0.5036025047302246, 1.3468749523162842, 1.6050972938537598] ,
				[-0.3386336863040924, 1.3468749523162842, 1.647810697555542] ,
				[-0.25473883748054504, 1.3468749523162842, 1.6628471612930298] ,
				[-0.08520437777042389, 1.3468749523162842, 1.6800872087478638] ,
				[0.08510042726993561, 1.414218783378601, 1.6238129138946533] ,
				[0.2543689012527466, 1.414218783378601, 1.6060220003128052] ,
				[0.3380729854106903, 1.414218783378601, 1.5905084609985352] ,
				[0.5024743676185608, 1.414218783378601, 1.5464571714401245] ,
				[0.661370575428009, 1.414218783378601, 1.4854626655578613] ,
				[0.813020646572113, 1.414218783378601, 1.4081931114196777] ,
				[-0.813020646572113, 1.414218783378601, 1.4081931114196777] ,
				[-0.661370575428009, 1.414218783378601, 1.4854626655578613] ,
				[-0.5024743676185608, 1.414218783378601, 1.5464571714401245] ,
				[-0.3380729854106903, 1.414218783378601, 1.5905084609985352] ,
				[-0.2543689012527466, 1.414218783378601, 1.6060220003128052] ,
				[-0.08510042726993561, 1.414218783378601, 1.6238129138946533] ,
				[0.08472345769405365, 1.4815624952316284, 1.5626322031021118] ,
				[0.25317707657814026, 1.4815624952316284, 1.544311761856079] ,
				[0.33641311526298523, 1.4815624952316284, 1.528340220451355] ,
				[0.4186623990535736, 1.4815624952316284, 1.5078856945037842] ,
				[0.499683678150177, 1.4815624952316284, 1.4830083847045898] ,
				[-0.499683678150177, 1.4815624952316284, 1.4830083847045898] ,
				[-0.4186623990535736, 1.4815624952316284, 1.5078856945037842] ,
				[-0.33641311526298523, 1.4815624952316284, 1.528340220451355] ,
				[-0.25317707657814026, 1.4815624952316284, 1.544311761856079] ,
				[-0.08472345769405365, 1.4815624952316284, 1.5626322031021118]]

	# SCREEN_SPHERE_RADIUS = 2.155
	#print viz.MainWindow.getSize()
	showLines = False
	
	lines = []
	
	for row in range(1,16):
		line = viz.MainWindow.screentoworld(x=0.5,y=row/16.0)
		if showLines:
			line.setLength(Globals.SCREEN_SPHERE_RADIUS)
			viz.startlayer(viz.LINES) 
			viz.linewidth(2)
			viz.vertex(-1000,0,0) #Vertices are split into pairs.
			viz.vertex( 1000,0,0)
			obj = viz.endlayer()
			obj.setPosition(line.getDir(),viz.ABS_GLOBAL)
		line.setLength(1.0)
		vec1 = line.getDir()
		vec2 = [1,0,0]
		lines.append([vec1[1]*vec2[2] - vec1[2]*vec2[1], vec1[2]*vec2[0] - vec1[0]*vec2[2], vec1[0]*vec2[1] - vec1[1]*vec2[0]])
	
	
	for col in range(1,16):
		line = viz.MainWindow.screentoworld(x=col/16.0,y=0.5)
		if showLines:
			line.setLength(Globals.SCREEN_SPHERE_RADIUS)
			viz.startlayer(viz.LINES) 
			viz.linewidth(2)
			viz.vertex(0,-1000,0) #Vertices are split into pairs.
			viz.vertex(0, 1000,0)
			obj = viz.endlayer()
			obj.setPosition(line.getDir(),viz.ABS_GLOBAL)
		line.setLength(1.0)
		vec1 = line.getDir()
		vec2 = [0,1,0]
		lines.append([vec1[1]*vec2[2] - vec1[2]*vec2[1], vec1[2]*vec2[0] - vec1[0]*vec2[2], vec1[0]*vec2[1] - vec1[1]*vec2[0]])
	
	base = [0,0,0]

	for pos in childpos:
		valid = True
		#for line in lines:
		#	if distancePointPlane(pos,line,base) < CircularObject.Size.LARGE:
		#		valid = False
		#		break
				
		if valid:
			#print distancePointPlane(pos,ABC,base)
			tmp1 = viz.add(viz.GROUP,viz.WORLD)
			tmp1.setPosition(pos,viz.ABS_GLOBAL)
			#obj = createQuad(0.2, 0.2)
			obj = createCircle(CircularObject.Size.LARGE)
			#obj.parent(tmp1)
			obj.setMatrix(tmp1.getMatrix(viz.ABS_GLOBAL),viz.ABS_GLOBAL)	
			tmp1.remove()
			obj.color(0.2,0.2,0.2)
			obj.depthFunc(viz.GL_ALWAYS)
			obj.drawOrder(0)
			obj.visible(viz.OFF)
			children_low.append(obj)
	
	#print 'childpos = [',
	#for child in children_low:
	#	print child.getPosition(viz.ABS_GLOBAL),','
	#print ']'

# dot product (3D) which allows vector operations in arguments
def dot(u,v):
	return (u[0] * v[0] + u[1] * v[1] + u[2] * v[2])
	
def norm(v):
	return math.sqrt(dot(v,v))
	
def distance(u,v):
	return norm([u[0]-v[0],u[1]-v[1],u[2]-v[2]])

# pbase_Plane(): get base of perpendicular from point to a plane
#    Input:  P = a 3D point
#            PL = a plane with point V0 and normal n
#    Output: *B = base point on PL of perpendicular from P
#    Return: the distance from P to the plane PL
def distancePointPlane( P, PL, B ):
	sn = -dot( PL, P)
	sd = dot(PL, PL)
	sb = sn / sd
	
	B = [P[0] + sb * PL[0],P[1] + sb * PL[1],P[2] + sb * PL[2]]
	return distance(P, B)

#-------------------------------------------------------------------------------
#  Create the quadrants of the SQUAD technique
#-------------------------------------------------------------------------------
def createQuad(left_bot,left_top,right_bot,right_top):
	viz.startlayer(viz.QUADS) 
	viz.vertexcolor(0,0,0)
	viz.vertex(left_bot)
	viz.vertex(left_top)
	viz.vertex(right_top)
	viz.vertex(right_bot)
	return viz.endlayer()

def createQuadLin():
	viz.startlayer(viz.LINES) 
	viz.linewidth(2)
	viz.vertex(-1000,-1000,0) #Vertices are split into pairs.
	viz.vertex( 1000, 1000,0)
	viz.vertex(-1000, 1000,0)
	viz.vertex( 1000,-1000,0)
	return viz.endlayer()

def createQuadTri():
	viz.startlayer(viz.TRIANGLES,'bottom') 
	viz.vertex(-1000,-1000,0) #Vertices are split into pairs.
	viz.vertex( 1000,-1000,0)
	viz.vertex(    0,    0,0) 
	viz.startlayer(viz.TRIANGLES,'top') 
	viz.vertex(-1000, 1000,0)
	viz.vertex(    0,    0,0)
	viz.vertex( 1000, 1000,0)
	viz.startlayer(viz.TRIANGLES,'left') 
	viz.vertex(-1000, 1000,0)
	viz.vertex(-1000,-1000,0)
	viz.vertex(    0,    0,0)
	viz.startlayer(viz.TRIANGLES,'right') 
	viz.vertex(    0,    0,0)
	viz.vertex( 1000,-1000,0)
	viz.vertex( 1000, 1000,0)
	return viz.endlayer()


#-------------------------------------------------------------------------------
#  Create the quadrants of the discrete zoom technique
#-------------------------------------------------------------------------------
def createQuadrantsZoom():
	global aspectRatio
	
	quadrants = []
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	texQuad.setPosition(0.25,0.75)
	texQuad.setScale(5.115*1.25,5.115,1)
	#texQuad.setPosition(0.5,0.5)
	#texQuad.setScale(10.23*1.255,10.23,1)
	quadrants.append(texQuad)
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	texQuad.setPosition(0.75,0.75)
	texQuad.setScale(5.115*1.25,5.115,1)
	quadrants.append(texQuad)
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	texQuad.setPosition(0.25,0.25)
	texQuad.setScale(5.115*1.25,5.115,1)
	quadrants.append(texQuad)
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	texQuad.setPosition(0.75,0.25)
	texQuad.setScale(5.115*1.25,5.115,1)
	quadrants.append(texQuad)
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	texQuad.setPosition(0.5,0.5)
	texQuad.setScale(10.23*1.255,0.025,1)
	texQuad.color(0,0,0)
	quadrants.append(texQuad)
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	texQuad.setPosition(0.5,0.5)
	texQuad.setScale(0.025,10.23,1)
	texQuad.color(0,0,0)
	quadrants.append(texQuad)
	
	return quadrants

#-------------------------------------------------------------------------------
#  Create a bounding box with the given size
#-------------------------------------------------------------------------------
def createBoundingBox(min,max):
	viz.startlayer(viz.LINE_LOOP, 'top') 
	viz.vertexcolor(1.0,1.0,0.0)
	viz.linewidth(2.0)
	
	#top
	#viz.vertexcolor(0.0,1.0,0.0)
	#viz.normal(0,1,0)
	viz.vertex( max[0], max[1], min[2])
	viz.vertex( min[0], max[1], min[2])
	viz.vertex( min[0], max[1], max[2])
	viz.vertex( max[0], max[1], max[2])

	viz.startlayer(viz.LINE_LOOP,'bottom') 
	viz.vertexcolor(.5,.5,0.0)
	viz.linewidth(2.0)
	
	#bottom
	#viz.vertexcolor(1.0,0.5,0.0)
	#viz.normal(0,-1,0)
	viz.vertex( max[0], min[1], max[2])
	viz.vertex( min[0], min[1], max[2])
	viz.vertex( min[0], min[1], min[2])
	viz.vertex( max[0], min[1], min[2])

	viz.startlayer(viz.LINE_LOOP,'front') 
	viz.vertexcolor(.5,.5,0.0)
	viz.linewidth(2.0)
	
	#front
	#viz.vertexcolor(1.0,0.0,0.0)
	#viz.normal(0,0,1)
	viz.vertex( max[0], max[1], max[2])
	viz.vertex( min[0], max[1], max[2])
	viz.vertex( min[0], min[1], max[2])
	viz.vertex( max[0], min[1], max[2])

	viz.startlayer(viz.LINE_LOOP,'back') 
	viz.vertexcolor(.5,.5,0.0)
	viz.linewidth(2.0)
	
	#back
	#viz.vertexcolor(1.0,1.0,0.0)
	#viz.normal(0,0,-1)
	viz.vertex( max[0], min[1], min[2])
	viz.vertex( min[0], min[1], min[2])
	viz.vertex( min[0], max[1], min[2])
	viz.vertex( max[0], max[1], min[2])

	viz.startlayer(viz.LINE_LOOP,'left') 
	viz.vertexcolor(.5,.5,0.0)
	viz.linewidth(2.0)
	
	#left
	#viz.vertexcolor(0.0,0.0,1.0)		
	#viz.normal(-1,0,0)
	viz.vertex( min[0], max[1], max[2])	
	viz.vertex( min[0], max[1], min[2])	
	viz.vertex( min[0], min[1], min[2])	
	viz.vertex( min[0], min[1], max[2])	

	viz.startlayer(viz.LINE_LOOP,'right') 
	viz.vertexcolor(.5,.5,0.0)
	viz.linewidth(2.0)
	
	#right
	#viz.vertexcolor(1.0,0.0,1.0)
	#viz.normal(1,0,0)
	viz.vertex( max[0], max[1], min[2])	
	viz.vertex( max[0], max[1], max[2])	
	viz.vertex( max[0], min[1], max[2])	
	viz.vertex( max[0], min[1], min[2])	
	
	return viz.endlayer()

#-------------------------------------------------------------------------------
#  Create a disk (filled 2D circle)
#-------------------------------------------------------------------------------
def createCircle(radius,x=0.0,y=0.0,z=0.0):
	viz.startlayer(viz.TRIANGLE_FAN) 
	viz.vertexcolor(0,0,0)
	viz.vertex(x,y,z)
	detail = 20
	for i in range(int(360.0/detail)+1):
		viz.vertex(x+radius*math.sin(float(i)*detail*math.pi/180.0),y+radius*math.cos(float(i)*detail*math.pi/180.0),z)
		#print "[",(x+radius*math.sin(float(i)*detail*math.pi/180.0)),",",(y+radius*math.cos(float(i)*detail*math.pi/180.0)),"]"
	return viz.endlayer()

#-------------------------------------------------------------------------------
#  Create a sphere
#-------------------------------------------------------------------------------
def createSphere(lats,longs):
	for i in range(lats+1):
		lat0 = math.pi * (-0.5 + (float(i) - 1.0) / lats)
		z0  = math.sin(lat0)
		zr0 = math.cos(lat0)
		
		lat1 = math.pi * (-0.5 + float(i) / lats)
		z1 = math.sin(lat1)
		zr1 = math.cos(lat1)
		
		viz.startlayer(viz.QUAD_STRIP) 
		for j in range(longs+1):
			lng = 2 * math.pi * (float(j) - 1.0) / longs
			x = math.cos(lng)
			y = math.sin(lng)
				
			viz.normal(x * zr0, y * zr0, z0)
			viz.vertex(x * zr0, y * zr0, z0)
			viz.normal(x * zr1, y * zr1, z1)
			viz.vertex(x * zr1, y * zr1, z1)
	
	return viz.endlayer()

def createBackgroundGrid(min,max):
	viz.startlayer(viz.LINES, 'background') 
	viz.vertexcolor(0.2,0.2,0.2)
	viz.linewidth(2.0)
	
	for i in range(min,max):
		# \ - lower left
		viz.vertex( i, min, 0)
		viz.vertex( min, i, 0)
		# \ - upper left
		viz.vertex( max, i, 0)
		viz.vertex( i, max, 0)
		# / - lower left
		viz.vertex( i+1, min, 0)
		viz.vertex( max, min+max-i-1, 0)
		# / - upper left
		viz.vertex( i+1, max, 0)
		viz.vertex( min, min+max-i-1, 0)
	
	return viz.endlayer()

#-------------------------------------------------------------------------------
# Color the quadrants based on the cursor position
#-------------------------------------------------------------------------------
def colorQuadrants():
	global centroid
	global windowSize
	global quadrants
	
	x,y = centroid[0],centroid[1]
	if x < windowSize[0]/2.0 and y >= windowSize[1]/2.0:
		quadrants[0].color([0.2,0.6,1])
		quadrants[0].alpha(0.3)
	else:
		quadrants[0].color([0,0,0])
		quadrants[0].alpha(0.0)
	if x >= windowSize[0]/2.0 and y >= windowSize[1]/2.0:
		quadrants[1].color([0.2,0.6,1])
		quadrants[1].alpha(0.3)
	else:
		quadrants[1].color([0,0,0])
		quadrants[1].alpha(0.0)
	if x < windowSize[0]/2.0 and y < windowSize[1]/2.0:
		quadrants[2].color([0.2,0.6,1])
		quadrants[2].alpha(0.3)
	else:
		quadrants[2].color([0,0,0])
		quadrants[2].alpha(0.0)
	if x >= windowSize[0]/2.0 and y < windowSize[1]/2.0:
		quadrants[3].color([0.2,0.6,1])
		quadrants[3].alpha(0.3)
	else:
		quadrants[3].color([0,0,0])
		quadrants[3].alpha(0.0)

#-------------------------------------------------------------------------------
# trial-related functions
#-------------------------------------------------------------------------------
# make the target acquisition different to not be near the edges AND NOT NEAR THE CENTER
def targetAcquisition():
	global children
	#global highlight_children
	global object_position
	global start_time
	global setting_up_trial
	global targetPos

	#print "attempting to acquire random target..."
	targetNotAlreadyCreated = False
	if trials[current_it][current_iteration].myTarget == -1:
		#print "...my target does not exist..."
		targetNotAlreadyCreated = True
		while 1:
			is_position = [0,0,Globals.SCREEN_SPHERE_RADIUS]
			trials[current_it][current_iteration].myTarget = random.randint(0,len(children)-1)
			#print "...randomizing target (between 0 and ",len(children)-1,"):",trials[current_it][current_iteration].myTarget,"  ", 
			obj_pos = children[trials[current_it][current_iteration].myTarget].getBoundingBox(viz.ABS_GLOBAL).center
			#print obj_pos
			distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
								 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
								 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
			#print "distance: ", distance
			if distance > Globals.SCREEN_SPHERE_RADIUS * .4 and distance < Globals.SCREEN_SPHERE_RADIUS * .6:
				#print "...target acquired!"
				children[trials[current_it][current_iteration].myTarget].color(0.8,0.0,0.8)
				break
		trials[current_it][current_iteration].original = trials[current_it][current_iteration].myTarget
	
	#print "setting up target size and removing occluded distractors..."
	#print "original:",trials[current_it][current_iteration].original
	#print "target:  ",trials[current_it][current_iteration].myTarget

	#Set the actual target the correct scale
	scale = Study.TARGET_SIZE/Study.DISTRACTORS_SIZE
	children[trials[current_it][current_iteration].original].setScale(scale,scale,scale)

	# saving target to update myTarget index after removing occluded distractors
	target = children[trials[current_it][current_iteration].original]
	
	to_be_removed = []
	for child in children:
		child.drawOrder(0)
		child.depthFunc(viz.GL_ALWAYS)
		if child != target:
			if Globals.USE_DISTRACTORS:
				is_position = [0,0,Globals.SCREEN_SPHERE_RADIUS]
				obj_pos = child.getBoundingBox(viz.ABS_GLOBAL).center
				distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
									 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
									 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
				#print "distance: ", distance
				if distance > Globals.SCREEN_SPHERE_RADIUS * .4 and distance < Globals.SCREEN_SPHERE_RADIUS * .6:
					child.color(0.0,0.0,0.8)
				else:
					child.color(0.2,0.2,0.2)
					
				is_position = target.getBoundingBox(viz.ABS_GLOBAL).center
				obj_pos = child.getBoundingBox(viz.ABS_GLOBAL).center
				distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
									 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
									 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
				if distance-Study.TARGET_SIZE-Study.DISTRACTORS_SIZE < 0:
					child.remove()
			else:
				to_be_removed.append(child)
				
	for child in to_be_removed:
		children.remove(child)
		child.remove()
	
	#print "updating object position list..."
	object_position = []
	for child in children:
		object_position.append(child.getBoundingBox(viz.ABS_GLOBAL).center)
	
	#print "updating target index..."
	if targetNotAlreadyCreated == True:
		trials[current_it][current_iteration].myTarget = children.index(target)
	targetPos = trials[current_it][current_iteration].myTarget
		
	#print "target acquired! painting target red...",trials[current_it][current_iteration].myTarget
	children[trials[current_it][current_iteration].myTarget].color(1.0,0.0,0.0)
	
	#print "setting up object visibility..."
	for child in children:
		child.visible(viz.OFF)
	trigger.visible(viz.ON)
	target.visible(viz.ON)
	target.billboard(viz.BILLBOARD_VIEW_POS)

	
	#print "  target:",trials[current_it][current_iteration].myTarget
	
	'''
	print "creating bounding boxes..."
	for child in highlight_children: 
		child.remove()
	highlight_children = []
	
	for child in children:
		aux_bb = child.getBoundingBox(viz.ABS_GLOBAL)
		if child == children[trials[current_it][current_iteration].myTarget]:
			center = [(aux_bb.xmax+aux_bb.xmin)/2.0,(aux_bb.ymax+aux_bb.ymin)/2.0,(aux_bb.zmax+aux_bb.zmin)/2.0]
			desloc = [(aux_bb.xmax-aux_bb.xmin)/2.0,(aux_bb.ymax-aux_bb.ymin)/2.0,(aux_bb.zmax-aux_bb.zmin)/2.0]
			min,max = [center[0]-desloc[0]*scale,center[1]-desloc[1]*scale,center[2]-desloc[2]*scale],[center[0]+desloc[0]*scale,center[1]+desloc[1]*scale,center[2]+desloc[2]*scale]
		else:
			min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
		bb = createBoundingBox(min,max)
		bb.visible(viz.OFF)
		highlight_children.append(bb)
	'''
	#highlight_children[trials[current_it][current_iteration].myTarget].setScale([10,10,10],viz.ABS_LOCAL)
		
	#here is the point where the task actually starts, but it will change to after clicking the 
	#center
	#start_time = viz.tick()
	if in_training == False:
		data_file.write('\n\nTrial '+str(current_iteration)+':\n')
		data_file.write('Id '+str(trials[current_it][current_iteration].id)+':\n')
		data_file.write('Try '+str(trials[current_it][current_iteration].tryCount+1)+'/5:\n')
		data_file.write('Technique='+str(trials[current_it][current_iteration].technique)+'\n')
		data_file.write('Target='+str(trials[current_it][current_iteration].target)+'\n')
		if trials[current_it][current_iteration].maxZoom != -1:
			data_file.write('MaxZoom='+str(math.pow(2,trials[current_it][current_iteration].maxZoom))+'\n')
		else:
			data_file.write('MaxZoom=0 or no limit\n')
		target_pos = viz.MainWindow.worldToScreen(target.getPosition())
		#Y grows downward
		target_pos[1] = 1 - target_pos[1]
		data_file.write('Target Position='+str(target_pos[:2])+'\n')
	
	if errorMessage.getVisible() == False:
		setting_up_trial = False

def setupTrial():
	global children
	#global highlight_children
	global intersection_sphere
	global intersection_sphere_radius
	global setting_up_trial
	global in_training
	global current_it
	global current_iteration
	global start_training
	global training_timer
	global stop_training
	#global intersecting
	global children_high
	global children_medium
	global children_low
	global target
	global targetPos
	
	updateFrustum()
	
	print "Setting up trial ",current_iteration,
	if current_it >= len(trials):
		return
	
	setting_up_trial = True
	
	#'''
	#print targetPos,len(children)
	#if Study.TARGET_SIZE != 0 and targetPos != -1:
	#	scale = Study.DISTRACTORS_SIZE/Study.TARGET_SIZE
	#	children[targetPos].setScale(scale,scale,scale,viz.ABS_LOCAL)
	#	print oldScale,children[targetPos].getScale(viz.ABS_GLOBAL)
	
	#print children
	
	for child in children:
		child.visible(viz.OFF)
		child.remove()
	children = []
	
	#print children

	#set condition parameters
	Study.technique = trials[current_it][current_iteration].technique
	Study.target    = trials[current_it][current_iteration].target
	Study.mode      = trials[current_it][current_iteration].mode

	#sets up scene depending on the distractors density
	Study.MAX_CIRCLES      = CircularObject.Quantity.LOW
	Study.DISTRACTORS_SIZE = CircularObject.Size.LARGE
	Study.OBJ_IN_SPHERE    = CircularObject.InSphere.LOW

	#sets up target size
	if Study.target == Study.TargetSize.Small:
		#log_2(3.375)^2 more difficult than next target, 36 times more difficult than largest
		Study.TARGET_SIZE = CircularObject.Size.SMALL
	elif Study.target == Study.TargetSize.Medium:
		Study.TARGET_SIZE = CircularObject.Size.MEDIUM
	elif Study.target == Study.TargetSize.Large:
		Study.TARGET_SIZE = CircularObject.Size.LARGE

	#make sure that sphere cast does not exist
	if intersection_sphere != None:
		intersection_sphere.remove()

	#'''
	createDistractorObjects()
	#print children
	#children = []
	children = copy.deepcopy(children_low)
	#print children
	#'''

	#create sphere ALWAYS -- make it tiny and invisible to simulate raycasting
	
	#the tiny sphere (rc) is always active when trial is set up - to click on the trigger button
	#we never use the actual sphere, only after
	intersection_sphere_radius = Globals.TINY_SPHERE_RADIUS
	intersection_sphere = createSphere(20,20)
	intersection_sphere.color(0.2,0.6,1.0)
	intersection_sphere.alpha(0.0)
	#intersecting = False
		
	if Study.mode == Study.Mode.Training_Free:
		in_training = True
		stop_training = False
		training_timer = None
		print " - Free Training"
	elif Study.mode == Study.Mode.Training:
		in_training = True
		if training_timer == None:
			start_training = True
		print " - Training"
	elif Study.mode == Study.Mode.Experiment:
		print " - Experiment - ",
		in_training = False
		start_training = False
		
	trigger.visible(viz.OFF)
	#vizact.ontimer2(.1,0,targetAcquisition)
	#print "acquiring target" 
	targetAcquisition()
	#print "target acquired" 
	
	if in_training == False:
		print "Trial ",trials[current_it][current_iteration].id
		print "Try ",(trials[current_it][current_iteration].tryCount+1),"/ 5" 
	print (len(trials[current_it])-current_iteration),"trials left for this tracking condition."

	print "  technique:",trials[current_it][current_iteration].technique
	print "  target:",trials[current_it][current_iteration].target
	if trials[current_it][current_iteration].maxZoom != -1:
		print "  zoom:",math.pow(2,trials[current_it][current_iteration].maxZoom)
	else:
		print "  zoom: 0 or no max"
	print "Done!"

def turnOffErrorMessage():
	global setting_up_trial
	
	crosshair.visible(viz.ON)
	errorMessage.visible(viz.OFF)
	black_quad.visible(viz.OFF)
	setting_up_trial = False

def turnOnErrorMessage(timeout = 0):
	crosshair.visible(viz.OFF)
	errorMessage.visible(viz.ON)
	black_quad.visible(viz.ON)
	if timeout > 0.0:
		vizact.ontimer2(timeout,0,turnOffErrorMessage)

#-------------------------------------------------------------------------------
# parser for experimental conditions
#-------------------------------------------------------------------------------
def stripLine(line):
	#strip trailing spaces and remove everything after a comment
	comment_pos = line.find('#')
	if comment_pos >= 0:
		line = line.replace(line, line[0:comment_pos])
	
	return line.strip().rstrip()

def parseInputFile(input_file):
	global user_id
	global sortedIT
	global maxZoom
	global total_trial_iterations
	
	global interleave_tracking

	line = input_file.readline()

	while line != "":
		line = stripLine(line)
		
		#if not between Begin and End Trial, could be user_id
		if line != "Begin Trial":
			if len(line) > 0:
				lhs = (line[0:line.find('=')].strip()).rstrip()
				if lhs == "UserID":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					user_id = rhs
				if lhs == "IT1":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					sortedIT[0] = rhs-1
				if lhs == "IT2":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					sortedIT[1] = rhs-1
				if lhs == "IT3":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					sortedIT[2] = rhs-1
				if lhs == "MaxZoomContinuous1":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					maxZoom[0] = rhs
				if lhs == "MaxZoomContinuous2":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					maxZoom[1] = rhs
				if lhs == "MaxZoomDiscrete1":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					maxZoom[2] = rhs
				if lhs == "MaxZoomDiscrete2":
					rhs = int(line[line.find('=')+1:len(line)].strip().rstrip())
					maxZoom[3] = rhs

			line = input_file.readline()

	print "End of Trials\n"

def initializeTrials():
	global trials
	global total_trial_iterations
	global total_trial_iterations_training
	
	'''
	initialize a serial unique id for each trial - trial being condition
	'''
	id = 0
	
	'''
	this populate the trials array, with all conditions in random order
	'''
	for i in range(Study.InteractionTechnique.size): # technique is RC or SCQM
		if i == Study.InteractionTechnique.Raycasting: 
			maxRange = 1
		else:
			maxRange = 3
		for j in range(maxRange):
			#myTrials = [] #local array to keep the current set of conditions
			for n in range(Study.Mode.size): # each mode is experiment, training or initial training (training_free)
				if n == Study.Mode.Experiment: #different number of iterations if in training or experiment
					trial_iterations = total_trial_iterations
				else:
					trial_iterations = total_trial_iterations_training
				
				if n == Study.Mode.Training_Free: #initial training
					print "training free"
					randomTrials = []
					for m in range(trial_iterations*Study.TargetSize.size): #number of total iterations for all conditions
						trial = Trial()
						trial.technique = i
						trial.target    = Study.TargetSize.Medium
						trial.mode      = n
						trial.myTarget  = -1
						if j < 2 and i != Study.InteractionTechnique.Raycasting: 
							if i == Study.InteractionTechnique.ContinuousZoom:
								trial.maxZoom   = maxZoom[j]-1
							elif i == Study.InteractionTechnique.DiscreteZoom:
								trial.maxZoom   = maxZoom[j+2]-1
						else:
							trial.maxZoom   = -1
						randomTrials.append(trial)
					#myTrials.append(randomTrials) #append to the set of trials for both tracking conditions
					trials.append(randomTrials) #append to the set of trials for both tracking conditions
				else: 
					#for j in range(Study.Tracking.size): # for each type of tracking (good, bad)
					randomTrials = []
					#	for k in range(Study.DistractorsDensity.size):
					for l in range(Study.TargetSize.size):
						for m in range(trial_iterations):
							trial = Trial()
							trial.technique = i
							trial.target    = l
							trial.mode      = n
							trial.myTarget  = -1
							if j < 2 and i != Study.InteractionTechnique.Raycasting: 
								if i == Study.InteractionTechnique.ContinuousZoom:
									if trial.target == Study.TargetSize.Small:
										trial.maxZoom   = maxZoom[j]
									elif trial.target == Study.TargetSize.Medium:
										trial.maxZoom   = maxZoom[j]-1
									elif trial.target == Study.TargetSize.Large:
										trial.maxZoom   = maxZoom[j]-2
								elif i == Study.InteractionTechnique.DiscreteZoom:
									if trial.target == Study.TargetSize.Small:
										trial.maxZoom   = maxZoom[j+2]
									elif trial.target == Study.TargetSize.Medium:
										trial.maxZoom   = maxZoom[j+2]-1
									elif trial.target == Study.TargetSize.Large:
										trial.maxZoom   = maxZoom[j+2]-2
							else:
								trial.maxZoom   = -1
							trial.id        = id
							randomTrials.append(trial)
							id += 1
					random.shuffle(randomTrials)
					#myTrials.append(randomTrials) #append to the set of trials for both tracking conditions
					trials.append(randomTrials) #append to the set of trials for both tracking conditions
			#trials.append(myTrials) #append to the complete set of trials, for both interaction techniques
	
	print "List of trials:"
	for it in range(len(trials)):
		for iteration in range(len(trials[it])):
			
			print it,iteration,
			trial = trials[it][iteration]
			if trial.mode == Study.Mode.Training_Free:
				print "- training free",
			elif trial.mode == Study.Mode.Training:
				print "- training",
			elif trial.mode == Study.Mode.Experiment:
				print "- experiment",
			
			if trial.technique == Study.InteractionTechnique.ContinuousZoom:
				print "- continuous zoom -",trial.maxZoom
			elif trial.technique == Study.InteractionTechnique.DiscreteZoom:
				print "- discrete zoom   -",trial.maxZoom
			elif trial.technique == Study.InteractionTechnique.Raycasting:
				print "- ray casting     -",trial.maxZoom

#-------------------------------------------------------------------------------
# quadrants functions
#-------------------------------------------------------------------------------
def sphereHit():
	global elapsed_time
	global centroid
	global zoomingLevel
	global currentWindow
	global animationCurrentWindow
	
	data_file.write('Sphere HIT: ' + str(elapsed_time) + 's\n')
	data_file.write('Clicked at: ' + str(centroid) + '\n')
	data_file.write('Final zoom level: ' + str(zoomingLevel) + '\n')
	if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
		data_file.write('Final zoom window: ' + str(animationCurrentWindow) + '\n')
	elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
		data_file.write('Final zoom window: ' + str(currentWindow) + '\n')

def sphereMiss():
	global num_iterations
	global max_iterations
	global current_it
	global current_iteration
	global data_file
	global elapsed_time
	global centroid
	global zoomingLevel
	global currentWindow
	global animationCurrentWindow
	
	if trials[current_it][current_iteration].tryCount < 4:
		num_iterations = num_iterations+1
		
		trial = Trial()
		trial.technique = trials[current_it][current_iteration].technique
		trial.target    = trials[current_it][current_iteration].target
		trial.mode      = trials[current_it][current_iteration].mode
		trial.myTarget  = trials[current_it][current_iteration].myTarget
		trial.original  = trials[current_it][current_iteration].original
		trial.maxZoom   = trials[current_it][current_iteration].maxZoom
		trial.tryCount  = trials[current_it][current_iteration].tryCount+1
		trial.id        = trials[current_it][current_iteration].id
		
		for i in range(trials[current_it][current_iteration].tryCount,4):
			max_iterations[i] += 1
		
		randInsert = random.randint(0,max_iterations[trials[current_it][current_iteration].tryCount]-max_iterations[trials[current_it][current_iteration].tryCount-1]-1)
		#print "rand from 0 to",(max_iterations[trials[current_it][current_iteration].tryCount]-max_iterations[trials[current_it][current_iteration].tryCount-1]-1),":",randInsert
		trials[current_it].insert(max_iterations[trials[current_it][current_iteration].tryCount-1]+randInsert,trial)
	
	data_file.write('Sphere MISS: ' + str(elapsed_time) + 's\n')
	data_file.write('Clicked at: ' + str(centroid) + '\n')
	data_file.write('Final zoom level: ' + str(zoomingLevel) + '\n')
	if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
		data_file.write('Final zoom window: ' + str(animationCurrentWindow) + '\n')
	elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
		data_file.write('Final zoom window: ' + str(currentWindow) + '\n')

def targetHit():
	global elapsed_time
	global centroid
	global zoomingLevel
	global currentWindow
	global animationCurrentWindow
	
	data_file.write('Target HIT: ' + str(elapsed_time) + 's\n')
	data_file.write('Clicked at: ' + str(centroid) + '\n')
	data_file.write('Final zoom level: ' + str(zoomingLevel) + '\n')
	if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
		data_file.write('Final zoom window: ' + str(animationCurrentWindow) + '\n')
	elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
		data_file.write('Final zoom window: ' + str(currentWindow) + '\n')

def targetMiss():
	global num_iterations
	global max_iterations
	global current_it
	global current_iteration
	global data_file
	global elapsed_time
	global centroid
	global zoomingLevel
	global currentWindow
	global animationCurrentWindow
	
	if trials[current_it][current_iteration].tryCount < 4:
		num_iterations = num_iterations+1
		
		trial = Trial()
		trial.technique = trials[current_it][current_iteration].technique
		trial.target    = trials[current_it][current_iteration].target
		trial.mode      = trials[current_it][current_iteration].mode
		trial.myTarget  = trials[current_it][current_iteration].myTarget
		trial.original  = trials[current_it][current_iteration].original
		trial.maxZoom   = trials[current_it][current_iteration].maxZoom
		trial.tryCount  = trials[current_it][current_iteration].tryCount+1
		trial.id        = trials[current_it][current_iteration].id
		
		for i in range(trials[current_it][current_iteration].tryCount,4):
			max_iterations[i] += 1
		
		randInsert = random.randint(0,max_iterations[trials[current_it][current_iteration].tryCount]-max_iterations[trials[current_it][current_iteration].tryCount-1]-1)
		#print "rand from 0 to",(max_iterations[trials[current_it][current_iteration].tryCount]-max_iterations[trials[current_it][current_iteration].tryCount-1]-1),":",randInsert
		trials[current_it].insert(max_iterations[trials[current_it][current_iteration].tryCount-1]+randInsert,trial)

	data_file.write('Target MISS: ' + str(elapsed_time) + 's\n')
	data_file.write('Clicked at: ' + str(centroid) + '\n')
	data_file.write('Final zoom level: ' + str(zoomingLevel) + '\n')
	if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
		data_file.write('Final zoom window: ' + str(animationCurrentWindow) + '\n')
	elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
		data_file.write('Final zoom window: ' + str(currentWindow) + '\n')

def createDistractorObjects():
	global targetPos
	
	#show "Wait for instructions"
	#black_quad.visible(viz.ON)
	#interruptMessage.visible(viz.ON)
	
	#create the lists again to avoid bugs
	#print "Creating distractor lists..."
	now = viz.tick()
	targetPos = -1
	
	createLowDensityDistractors()
	#print "Distractor lists created!",(viz.tick()-now),"s"
	
def nextTrial():
	global current_it
	global current_iteration
	global num_iterations
	global max_iterations
	global original_max_iterations
	global in_training
	global input_needed
	
	global start_training
	global stop_training
	global training_timer
	
	global targetPos
	
	global sortedIT
	global currentSortedIT
	global maxZoom
	
	global previousWindow
	global currentWindow
	
	previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
	currentWindow = [[0,0],[windowSize[0],windowSize[1]]]
	
	current_iteration = current_iteration+1
	if in_training == False:
		#print current_iteration,num_iterations
		if current_iteration == num_iterations:
			createDistractorObjects()

			input_needed = True
			num_iterations = original_max_iterations
			current_iteration = 0
			
			current_it += 1
			print "current it:",current_it
			if current_it >= (sortedIT[currentSortedIT]+1)*9 or current_it > 20:
				currentSortedIT += 1
				if currentSortedIT > 2:
					print "quit"
					viz.quit()
				current_it = sortedIT[currentSortedIT]*9
				print "current sorted IT:",currentSortedIT
				print "current it:",current_it
				
			if current_it/9 == Study.InteractionTechnique.ContinuousZoom:
				print "changing IT to continuous zoom"
			elif current_it/9 == Study.InteractionTechnique.DiscreteZoom:
				print "changing IT to discrete zoom"
			elif current_it/9 == Study.InteractionTechnique.Raycasting:
				print "changing IT to raycasting"
			else:
				print "mode change"
	else:
		#print current_iteration,num_iterations_training,stop_training,training_timer
		if current_iteration == num_iterations_training or stop_training == True:
			createDistractorObjects()
			
			input_needed = True
			
			start_training = False
			stop_training = False
			training_timer = None
			
			current_iteration = 0

			num_iterations = original_max_iterations
			
			current_it += 1
			print "current it:",current_it
			if current_it >= (sortedIT[currentSortedIT]+1)*9 or current_it > 20:
				currentSortedIT += 1
				current_it = sortedIT[currentSortedIT]*9
				print "current sorted IT:",currentSortedIT
				print "current it:",current_it
				
			if current_it/9 == Study.InteractionTechnique.ContinuousZoom:
				print "changing IT to continuous zoom"
			elif current_it/9 == Study.InteractionTechnique.DiscreteZoom:
				print "changing IT to discrete zoom"
			elif current_it/9 == Study.InteractionTechnique.Raycasting:
				print "changing IT to raycasting"
			else:
				print "mode change"
				
			if currentSortedIT > 2:
				print "quit"
				viz.quit()
			
def selectTrigger():
	global mode
	global start_time
	
	global start_training
	global training_timer
	
	global intersection_sphere
	global intersection_sphere_radius
	
	if len(collision_test) > 0:
		for child in children:
			child.visible(viz.ON)
			#set billboard here because object needs to be visible...
			child.billboard(viz.BILLBOARD_VIEW_POS)
		trigger.visible(viz.OFF)

		mode = InteractionMode.SELECTION
		start_time = viz.tick()
		
		#print "(before) start training =",start_training
		if start_training == True:
			training_timer = viz.tick()
			start_training = False
			print "start timer = ", training_timer
		#print "(after) start training =",start_training
		
		#make sure sphere cast does not exist
		if intersection_sphere != None:
			intersection_sphere.remove()
		
		intersection_sphere_radius = Globals.TINY_SPHERE_RADIUS
		intersection_sphere = createSphere(intersection_sphere_radius,20,20)
		intersection_sphere.color(0.2,0.6,1.0)
		intersection_sphere.alpha(0.0)
		
		if trials[current_it][current_iteration].maxZoom == 0:
			#print "BUUUUUUUUUUUUUUUUUUUUUUUUUZZZZZZZZZZZZ"
			viz.playSound("BUZZER.WAV")

def selectTarget():
	global mode
	global current_it
	global current_iteration
	global num_iterations
	global max_iterations
	global elapsed_time
	
	global input_needed
	global interleave_tracking

	elapsed_time = viz.tick() - start_time
	if len(collision_test) > 0:
		new_list = []
	
		targetAcquired = False
		
		for obj in collision_test:
			if obj == children[trials[current_it][current_iteration].myTarget]:
				targetAcquired = True
				
		if targetAcquired == True:	
			print "Target HIT!"
			if in_training == False:
				targetHit()

			nextTrial()

			setupTrial()
			mode = InteractionMode.SELECTION_TRIGGER
		else:
			print "Target MISS!"

			if in_training == False:
				targetMiss()
					
			nextTrial()
			
			setupTrial()
			
			turnOnErrorMessage(errorMessageTimeOut)
			
			mode = InteractionMode.SELECTION_TRIGGER
	else:
		print "Target MISS!"

		if in_training == False:
			targetMiss()
				
		nextTrial()

		setupTrial()
		turnOnErrorMessage(errorMessageTimeOut)
		mode = InteractionMode.SELECTION_TRIGGER

#-------------------------------------------------------------------------------
# pointer functions
#-------------------------------------------------------------------------------
def sphereInclusionTest():
	global mode
	global collision_test
	global intersection_sphere_radius
	global object_position

	#print "Sphere radius: ", intersection_sphere_radius
	#print "Intersection sphere: ", intersection_sphere
	#global highlight_children
	global trigger
	
	global centroid

	x,y = centroid[0],centroid[1]
	#print x,y
	
	line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
	
	begin = line[:3]
	end = line[3:]
	#print line
	
	all_info = viz.intersect(begin,end,True)
	index = 0
	
	#intersecting = False
	for info in all_info:
		#print info
		if info.valid == True:
			#print 'Intersected with object id:', info.object.id 
			if info.object != intersection_sphere:
				intersection_sphere.setPosition(info.point,viz.ABS_GLOBAL)
				intersection_sphere.setScale(300,300,300,viz.ABS_GLOBAL)
				distance = math.sqrt(((info.point[0])*(info.point[0])) + ((info.point[1])*(info.point[1])) + ((info.point[2])*(info.point[2])))
				#print index," distance:", distance, " sphere radius:", intersection_sphere_radius
				#intersecting = True
				break
			#else:
			#	print index," colliding with sphere"
		index += 1
	
	collision_test = []
	if mode == InteractionMode.SELECTION:
		if len(object_position) == len(children):
			is_position = intersection_sphere.getPosition(viz.ABS_GLOBAL)
			
			index = 0
			#print "objects in sphere:",
			for child in children:
				#if viz.MainWindow.isCulled(child) == 0: 
				#obj_pos = child.getBoundingBox(viz.ABS_GLOBAL).center
				obj_pos = object_position[index]
				distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
									 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
									 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
				#print current_it, current_iteration
				if index == trials[current_it][current_iteration].myTarget:
					if distance < intersection_sphere_radius+Study.TARGET_SIZE:
						collision_test.append(child)
				else:
					if distance < intersection_sphere_radius+Study.DISTRACTORS_SIZE:
						collision_test.append(child)
					#if children.index(child) == trials[current_it][current_iteration].myTarget:
					#	print "["+str(children.index(child))+"]",
					#else:
					#	print children.index(child),
				index+=1
			#print " "
		#for child in highlight_children:
		#	child.visible(viz.OFF)
		#for obj in collision_test:
		#	highlight_children[children.index(obj)].visible(viz.ON)
				
		#print "Objects in the sphere:",len(collision_test)
	elif mode == InteractionMode.SELECTION_TRIGGER:
		is_position = intersection_sphere.getPosition(viz.ABS_GLOBAL)
		obj_pos = [0,0,Globals.SCREEN_SPHERE_RADIUS]
		distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
							 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
							 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
		if distance < intersection_sphere_radius+Globals.TRIGGER_SIZE:
			collision_test.append(trigger)

def drawIntersectObjBoundingDisk():
	global boundingBox
	global current_it
	global current_iteration
	global trials
		
	if current_it >= len(trials):
		return
	
	if not setting_up_trial:
		if boundingBox != None:
			boundingBox.remove()
			boundingBox = None
		
		scale_factor = 0.003*Globals.SCREEN_SPHERE_RADIUS
		for object in collision_test:
			#aux_bb = object.getBoundingBox(viz.ABS_GLOBAL)
			#if object == children[trials[current_it][current_iteration].myTarget]:
			#	center = [(aux_bb.xmax+aux_bb.xmin)/2.0,(aux_bb.ymax+aux_bb.ymin)/2.0,(aux_bb.zmax+aux_bb.zmin)/2.0]
			#	desloc = [(aux_bb.xmax-aux_bb.xmin)/2.0,(aux_bb.ymax-aux_bb.ymin)/2.0,(aux_bb.zmax-aux_bb.zmin)/2.0]
			#	min,max = [center[0]-desloc[0]*scale,center[1]-desloc[1]*scale,center[2]-desloc[2]*scale],[center[0]+desloc[0]*scale,center[1]+desloc[1]*scale,center[2]+desloc[2]*scale]
			#else:
			#	min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
			#bb = createBoundingBox(min,max)
			
			center = object.getBoundingBox(viz.ABS_GLOBAL).center 
			aux_bb = [center[0]*1.01,center[1]*1.01,center[2]*1.01]
			if object == children[trials[current_it][current_iteration].myTarget]:
				bb = createCircle(Study.TARGET_SIZE+scale_factor)
			elif object == trigger:
				bb = createCircle(Globals.TRIGGER_SIZE+scale_factor*2)
			else:
				bb = createCircle(Study.DISTRACTORS_SIZE+scale_factor*2)
			bb.setPosition(aux_bb)
			bb.color(1,1,0)
			bb.billboard(viz.BILLBOARD_VIEW_POS)
			boundingBox = bb
			break

def drawIntersectObjBoundingBox():
	global intersectObj
	global boundingBox
	
	if boundingBox != None:
		boundingBox.remove()
	
	aux_bb = intersectObj.getBoundingBox(viz.ABS_GLOBAL)
	min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
	boundingBox = createBoundingBox(min,max)

def placeTotem():
	global totem
	
	x,z = random.randint(0,99),random.randint(0,99)
	
	totem = viz.add("totem/models/model.dae")
	totem.setPosition(x,0,z)
	totem.setScale(0.2,0.2,0.2)
	totem.color(1,0,0)
	totem.disable(viz.LIGHTING)

#this function will return an array of strings, which can be used directly to load the name of a specific function
# if "DEF " shows up, note the next string
def loadSimulation(fileName):
	global totalFrames
	
	listFrames = []
	file = open(fileName, 'r')
	
	buildingCharList = True
	character = 0
	totalFrames = 0
	
	#for each line in the file, get the character simulation data
	for line in file:
		line = line.replace("\n","")
		#print "line >>"+line+"<<"
		if line == "":
			buildingCharList = False
			character = 0
			totalFrames += 1
			print "loaded frame",totalFrames
		elif character < 200:
			tokens = line.split(" ")
			frame = [float(tokens[0])*0.5,float(tokens[1])*0.5,-float(tokens[2])*180.0/3.14159265+90.0] #each line of the file contains posX,posZ,oriY
		
			if buildingCharList: #if character is not in the list yet
				listFrames.append([frame])
			else:
				listFrames[character].append(frame)
			
			character += 1
	
	return listFrames
	
def updateCharacters():
	global listFrames
	global children
	global totalFrames
	global currentFrame
	global previousFrame
	global zooming
	
	if currentFrame != previousFrame:
		index = 0
		for avatar in children:
			frame = listFrames[index][currentFrame]
			if zooming == True:
				#Pause the execution of animation 5
				avatar.setAnimationSpeed(0,0)
			else:
				#Pause the execution of animation 5
				avatar.setAnimationSpeed(0,2)
				#Pause the execution of animation 2
				avatar.state(2)
				avatar.setPosition([frame[0],0,frame[1]])
				avatar.setEuler(frame[2],0,0)
			index += 1
	else:
		for avatar in children:
			#Pause the execution of animation 5
			avatar.setAnimationSpeed(0,0)
			avatar.setAnimationTime(0,0)
			avatar.state(1)
	
	previousFrame = currentFrame
	
	#if zooming == False:
	#	currentFrame += 1
	#	if currentFrame == totalFrames:
	#		currentFrame = 0

def updateWindowDimensionsDiscrete(animationState):
	global zoomingLevel
	global zoomingAnimation
	global centroid
	global newCenterOffset
	global previousCenterOffset
	global currentWindow
	global previousWindow
	global offset
	global buttonState
	global previousZoomingLevel
	
	if zoomingLevel > 1:
		if zoomingAnimation == 2.0: # zooming out
			previousWindow = [previousCenterOffset,[previousCenterOffset[0]+windowSize[0]/(zoomingLevel*2.0),previousCenterOffset[1]+windowSize[1]/(zoomingLevel*2.0)]]
		else: # zooming in
			previousWindow = [previousCenterOffset,[previousCenterOffset[0]+windowSize[0]/(zoomingLevel/2.0),previousCenterOffset[1]+windowSize[1]/(zoomingLevel/2.0)]]
		currentWindow  = [newCenterOffset,[newCenterOffset[0]+windowSize[0]/zoomingLevel,newCenterOffset[1]+windowSize[1]/zoomingLevel]]
	else:
		if animationState == 0.0 or animationState == 1.0:
			previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
		elif zoomingAnimation == 1.0:
			previousWindow = [previousCenterOffset,[previousCenterOffset[0]+windowSize[0]/(zoomingLevel/2.0),previousCenterOffset[1]+windowSize[1]/(zoomingLevel/2.0)]]
		else:
			previousWindow = [previousCenterOffset,[previousCenterOffset[0]+windowSize[0]/(zoomingLevel*2.0),previousCenterOffset[1]+windowSize[1]/(zoomingLevel*2.0)]]
		currentWindow  = [[0,0],[windowSize[0],windowSize[1]]]
		
	#print animationState,"  ",previousWindow," -> ",currentWindow
	
def updateWindowDimensionsContinuous(animationState):
	global zoomingLevel
	global zoomingAnimation
	global centroid
	global newCenterOffset
	global previousCenterOffset
	global currentWindow
	global previousWindow
	global offset
	global buttonState
	global animationCurrentWindow
	#global previousZoomingLevel
	
	if zoomingLevel > 1:
		if buttonState[0] == True and ((Globals.application != Globals.Application.EVALUATION and zoomingLevel < 128.0) or (Globals.application == Globals.Application.EVALUATION and ((trials[current_it][current_iteration].maxZoom != -1 and zoomingLevel < math.pow(2,trials[current_it][current_iteration].maxZoom)) or (trials[current_it][current_iteration].maxZoom == -1 and zoomingLevel < 128.0)))):
			if Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].maxZoom != -1:
				currentWindow  = [[newCenterOffset[0]-((centroid[0]/windowSize[0]) * (windowSize[0]/(math.pow(2,trials[current_it][current_iteration].maxZoom)))),
								   newCenterOffset[1]-((centroid[1]/windowSize[1]) * (windowSize[1]/(math.pow(2,trials[current_it][current_iteration].maxZoom))))],
								  [newCenterOffset[0]+((1.0 - (centroid[0]/windowSize[0])) * (windowSize[0]/(math.pow(2,trials[current_it][current_iteration].maxZoom)))),
								   newCenterOffset[1]+((1.0 - (centroid[1]/windowSize[1])) * (windowSize[1]/(math.pow(2,trials[current_it][current_iteration].maxZoom))))]]
			else:
				currentWindow  = [[newCenterOffset[0]-((centroid[0]/windowSize[0]) * (windowSize[0]/128.0)),
								   newCenterOffset[1]-((centroid[1]/windowSize[1]) * (windowSize[1]/128.0))],
								  [newCenterOffset[0]+((1.0 - (centroid[0]/windowSize[0])) * (windowSize[0]/128.0)),
								   newCenterOffset[1]+((1.0 - (centroid[1]/windowSize[1])) * (windowSize[1]/128.0))]]
	else:
		previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
		currentWindow  = [[0,0],[windowSize[0],windowSize[1]]]
	
	animationCurrentWindow = [[(1 - animationState) * previousWindow[0][0] + animationState * currentWindow[0][0],
							   (1 - animationState) * previousWindow[0][1] + animationState * currentWindow[0][1]],
							  [(1 - animationState) * previousWindow[1][0] + animationState * currentWindow[1][0],
							   (1 - animationState) * previousWindow[1][1] + animationState * currentWindow[1][1]]]
	
	#if animationState > 0.0 and animationState < 1.0:
	#	#print animationState, previousWindow," -> ",currentWindow," = ",animationCurrentWindow
	#	print currentWindow

def updateFrustum(animationState = 1.0):
	global windowSize
	global VFOV
	global currentWindow
	global previousWindow
	
	if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
		updateWindowDimensionsContinuous(animationState)
	elif (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.DiscreteZoom):
		updateWindowDimensionsDiscrete(animationState)
	
	# calculate frustum
	#print "  FRUSTUM:"
	cameraNear = viz.MainWindow.getNearClip()
	cameraFar    = viz.MainWindow.getFarClip()
	ratio = windowSize[0]/windowSize[1]
	yfov = 2.0 * math.atan( math.tan( (defaultHFOV/57.2957795) / 2.0 ) / aspectRatio ) * 57.2957795;
	ymax = cameraNear*math.tan(yfov*math.pi/360.0)
	ymin = -ymax
	xmax = ymax*ratio
	xmin = ymin*ratio
	#print "  1)         xmin: ",xmin,"  xmax: ", xmax, "  ymin: ", ymin, "  ymax: ",ymax, "  near: ",cameraNear
	
	# previous window frustm
	pxmin = -((previousWindow[0][0]/windowSize[0]) * (xmin * 2.0) - xmin)
	pxmax = (previousWindow[1][0]/windowSize[0]) * (xmax * 2.0) - xmax
	pymin = -((previousWindow[0][1]/windowSize[1]) * (ymin * 2.0) - ymin)
	pymax = (previousWindow[1][1]/windowSize[1]) * (ymax * 2.0) - ymax
	#print "  previous)  xmin: ",pxmin,"  xmax: ", pxmax, "  ymin: ", pymin, "  ymax: ",pymax, "  near: ",cameraNear
	
	# current window frustum
	cxmin = -((currentWindow[0][0]/windowSize[0]) * (xmin * 2.0) - xmin)
	cxmax = (currentWindow[1][0]/windowSize[0]) * (xmax * 2.0) - xmax
	cymin = -((currentWindow[0][1]/windowSize[1]) * (ymin * 2.0) - ymin)
	cymax = (currentWindow[1][1]/windowSize[1]) * (ymax * 2.0) - ymax
	#print "  current )  xmin: ",cxmin,"  xmax: ", cxmax, "  ymin: ", cymin, "  ymax: ",cymax, "  near: ",cameraNear
	
	# final (desired) frustum - linear interpolation
	xmin = (1 - animationState) * pxmin + animationState * cxmin
	xmax = (1 - animationState) * pxmax + animationState * cxmax
	ymin = (1 - animationState) * pymin + animationState * cymin
	ymax = (1 - animationState) * pymax + animationState * cymax
	#print "  2)         xmin: ",xmin,"  xmax: ", xmax, "  ymin: ", ymin, "  ymax: ",ymax, "  near: ",cameraNear
	viz.MainWindow.frustum(xmin,xmax,ymin,ymax,cameraNear,cameraFar)

def cursorOverQuadrant():
	global windowSize
	global zoomingLevel
	
	x,y = centroid[0],centroid[1]
	
	if x < windowSize[0]/2.0 and y >= windowSize[1]/2.0:
		cursor = [(windowSize[0]/4.0)/zoomingLevel,(3.0*windowSize[1]/4.0)/zoomingLevel] 
	elif x >= windowSize[0]/2.0 and y >= windowSize[1]/2.0:
		cursor = [(3.0*windowSize[0]/4.0)/zoomingLevel,(3.0*windowSize[1]/4.0)/zoomingLevel] 
	elif x < windowSize[0]/2.0 and y < windowSize[1]/2.0:
		cursor = [(windowSize[0]/4.0)/zoomingLevel,(windowSize[1]/4.0)/zoomingLevel] 
	elif x >= windowSize[0]/2.0 and y < windowSize[1]/2.0:
		cursor = [(3.0*windowSize[0]/4.0)/zoomingLevel,(windowSize[1]/4.0)/zoomingLevel] 
		
	return cursor

def calculateCursorOffset(level):
	global windowSize
	global previousCenterOffset
	
	x,y = centroid[0],centroid[1]
	
	if x < windowSize[0]/2.0 and y >= windowSize[1]/2.0:
		cursor = [0,(windowSize[1]/2.0)/level] 
	elif x >= windowSize[0]/2.0 and y >= windowSize[1]/2.0:
		cursor = [(windowSize[0]/2.0)/level,(windowSize[1]/2.0)/level] 
	elif x < windowSize[0]/2.0 and y < windowSize[1]/2.0:
		cursor = [0,0] 
	elif x >= windowSize[0]/2.0 and y < windowSize[1]/2.0:
		cursor = [(windowSize[0]/2.0)/level,0] 
	
	cursor = [previousCenterOffset[0]+cursor[0],previousCenterOffset[1]+cursor[1]]
	return cursor

def zoomInButton():
	global centroid
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global lastZoomingLevel
	global zoomingStack
	global buttonState
	global windowSize
	global selectedQuadrant
	global previousCenterOffset
	global newCenterOffset
	global showMenu
	global totalAnimationFrames
	
	zooming = True
	if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.DiscreteZoom):
		#print "discrete zoom"
		if (Globals.application != Globals.Application.EVALUATION or trials[current_it][current_iteration].maxZoom == -1) and zoomingLevel*2 > 128.0:
			lastZoomingLevel = zoomingLevel
			zoomingLevel = 128.0
			zoomingAnimation = 0
		elif Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].maxZoom != -1 and zoomingLevel*2 > math.pow(2,trials[current_it][current_iteration].maxZoom):
			lastZoomingLevel = zoomingLevel
			zoomingLevel = math.pow(2,trials[current_it][current_iteration].maxZoom)
			zoomingAnimation = 0
		else:
			totalAnimationFrames = (fps*Navigation.TOTAL_ANIMATION_TIME)
			if zoomingLevel == 1:
				previousCenterOffset = [0,0]
			selectedQuadrant = cursorOverQuadrant()
			zoomingStack.append(newCenterOffset)
			newCenterOffset = calculateCursorOffset(zoomingLevel)
			zooming = True
			zoomingAnimation = 1 # zoom in
			zoomingCount = 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel *= 2
	elif (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
		#print "continuous zoom - iteration",zoomingCount
		if Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].maxZoom != -1:
			if zoomingLevel <= math.pow(2,trials[current_it][current_iteration].maxZoom):
				lastZoomingLevel = zoomingLevel
				if (VFOV-minFOV) == 0:
					zoomingLevel = 1.0
				else:
					if zoomingCount > 0.0:
						zoomingCount += 1.0 - math.sqrt(zoomingCount*0.01)
					else:
						zoomingCount += 1.0
					zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * (math.pow(2,trials[current_it][current_iteration].maxZoom)-1)
			#else:
			#	viz.playSound("BUZZER.WAV")
		else:
			if zoomingLevel < 128.0:
				if zoomingCount > 0.0:
					zoomingCount += 1.0 - math.sqrt(zoomingCount*0.01)
				else:
					zoomingCount += 1.0
				lastZoomingLevel = zoomingLevel
				zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * 127.0
				#zoomingLevel = 1.0 + zoomingCount
			#else:
			#	viz.playSound("BUZZER.WAV")
		#print "zooming level :",zoomingLevel

def zoomOutButton():
	global centroid
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global buttonState
	global windowSize
	global selectedQuadrant
	global previousCenterOffset
	global newCenterOffset
	global showMenu
	global totalAnimationFrames
	global zoomingStack
	
	zooming = True
	if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.DiscreteZoom):
		#print "discrete zoom cancel"
		if zoomingLevel > 1:
			totalAnimationFrames = (fps*Navigation.TOTAL_ANIMATION_TIME)
			zoomingLevel /= 2
			zooming = True
			zoomingAnimation = 2 # zoom out
			zoomingCount = 1.0
			previousCenterOffset = newCenterOffset
			newCenterOffset = zoomingStack.pop()
	elif (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
		#print "continuous zoom - iteration",zoomingCount
		#if zoomingCount > 0.0:
		#	zoomingCount -= .5
		#	zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * 127.0
		
		#print "continuous zoom - iteration",zoomingCount
		if zoomingCount > 0.0:
			zoomingCount -= .5
			lastZoomingLevel = zoomingLevel
			if Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].maxZoom != -1:
				zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * (math.pow(2,trials[current_it][current_iteration].maxZoom)-1)
			else:
				zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * 127.0
		
def selectButton():
	global zooming
	global zoomingCount
	global zoomingLevel
	global buttonState
	global totem
	global errorMessageTimeOut
	global zoomingStack
	global lastZoomingCount
	
	lastZoomingCount = 0
	
	if Globals.application == Globals.Application.CROWDSIMULATION:
		if boundingBox == None:
			turnOnErrorMessage(errorMessageTimeOut)
		if Globals.application == Globals.Application.CROWDSIMULATION:
			totem.remove()
			placeTotem()
		zooming = False
		zoomingLevel = 1
	elif Globals.application == Globals.Application.EVALUATION:
		#print "eval button"
		if mode == InteractionMode.SELECTION_TRIGGER:
			selectTrigger()
		elif mode == InteractionMode.SELECTION:
			selectTarget()			
			zooming = False
			zoomingLevel = 1.0
			zoomingCount = 0.0
			zoomingStack = []

def resetZoom():
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global lastZoomingCount
	global lastZoomingLevel
	global previousCenterOffset
	global previousZoomingLevel
	global newCenterOffset
	global zoomingStack
	global previousWindow
	global currentWindow
	global animationCurrentWindow
	
	zooming = False
	zoomingAnimation = 0
	zoomingCount = 0
	zoomingLevel = 1
	lastZoomingLevel = zoomingLevel
	previousZoomingLevel = 1
	previousCenterOffset = [0,0]
	newCenterOffset = [0,0]
	lastZoomingCount = 0
	
	zoomingStack = []
	
	previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
	currentWindow = [[0,0],[windowSize[0],windowSize[1]]]
	animationCurrentWindow = [[0,0],[windowSize[0],windowSize[1]]]

def cycleTechniqueBackward():
	Globals.technique += 1
	if Globals.technique == Study.InteractionTechnique.size:
		Globals.technique = 0
		
	resetZoom()
		
def cycleTechniqueForward():
	Globals.technique -= 1
	if Globals.technique < 0:
		Globals.technique = Study.InteractionTechnique.size-1
		
	resetZoom()

def keyDown(whichKey):
	global mode
	global clone_list
	global current_it
	global current_iteration
	global num_iterations
	global setting_up_trial
	global input_needed
	global stop_training
		
	if whichKey == 'i' or whichKey == 'I':
		input_needed = False
	if (whichKey == 'n' or whichKey == 'N'):
		stop_training = True
		nextTrial()
		setupTrial()
		mode = InteractionMode.SELECTION_TRIGGER

	#print 'The following key was pressed: ', whichKey
	if whichKey == viz.KEY_UP:
		viz.MainView.move(0,0,Navigation.translation_speed*viz.elapsed(),viz.BODY_ORI)
	elif whichKey == viz.KEY_DOWN:
		viz.MainView.move(0,0,-Navigation.translation_speed*viz.elapsed(),viz.BODY_ORI)
	if whichKey == viz.KEY_LEFT:
		Navigation.yaw = Rotate.CCW
	elif whichKey == viz.KEY_RIGHT:
		Navigation.yaw = Rotate.CW
	if whichKey == ']':
		Navigation.pitch = Rotate.CCW
	elif whichKey == '[':
		Navigation.pitch = Rotate.CW
	if whichKey == '}':
		Navigation.roll = Rotate.CCW
	elif whichKey == '{':
		Navigation.roll = Rotate.CW
	
	if Globals.application != Globals.Application.EVALUATION or setting_up_trial == False:
		if whichKey == 'e' and input_needed == False: 
			if mode == InteractionMode.SELECTION_TRIGGER:
				selectTrigger()
			elif mode == InteractionMode.SELECTION and trials[current_it][current_iteration].myTarget != -1 and setting_up_trial == False:
				selectTarget()
			elif mode == InteractionMode.SELECTION_QUADRANTS and setting_up_trial == False:
				selectQuadrant()
		elif whichKey == 'q' and (mode == InteractionMode.SELECTION_QUADRANTS):
			#print "trying to cancel"
			for clone in clone_list:
				#print "removing index",index,"..."
				#clone.visible(viz.OFF)
				clone.endAction(viz.ALL_POOLS)
				clone.remove()
				#print len(clone_list)
			clone_list = []
			
			if in_training == False:
				if Study.technique == Study.InteractionTechnique.Raycasting:
					targetMiss()
				else:
					sphereMiss()
					
			current_iteration = current_iteration+1
			setupTrial()
			mode = InteractionMode.SELECTION_TRIGGER
			
	if whichKey == 'r' or whichKey == 'R':
		if not in_training:
			data_file.write('INVALID TRIAL - TRACKING ERROR\n')
			print 'INVALID TRIAL - TRACKING ERROR'
	if whichKey == 'w':
		centroid[1]-=0.01
	elif whichKey == 'W':
		centroid[1]-=0.001
	elif whichKey == 's':
		centroid[1]+=0.01
	elif whichKey == 'S':
		centroid[1]+=0.001
	if whichKey == 'd':
		centroid[0]+=0.01
	elif whichKey == 'D':
		centroid[0]+=0.001
	elif whichKey == 'a':
		centroid[0]-=0.01
	elif whichKey == 'A':
		centroid[0]-=0.001
		
	if whichKey == 't' or whichKey == 't':
		cycleTechniqueForward()

def keyUp(whichKey):
	#print 'The following key was released: ', whichKey
	if whichKey == viz.KEY_UP or whichKey == viz.KEY_DOWN:
		Navigation.DDR.walk = Move.NONE
	if whichKey == viz.KEY_LEFT or whichKey == viz.KEY_RIGHT:
		Navigation.yaw = Rotate.NONE
	if whichKey == ']' or whichKey == '[':
		Navigation.pitch = Rotate.NONE
	if whichKey == '}' or whichKey == '{':
		Navigation.roll = Rotate.NONE
	if whichKey == 'i' or whichKey == 'k':
		Navigation.fly = Move.NONE

def updateIS900Data():
	global old_data
	global all_data
	global current_it
	global previous_centroid
	global is900Euler
	global total_frames
	global centroid
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global buttonState
	global windowSize
	global selectedQuadrant
	global previousCenterOffset
	global newCenterOffset
	global showMenu
	global mouseState
	global oldMouseState
	global previousWindow
	global currentWindow
	global animationCurrentWindow
	global lastZoomingCount
	global start_time
	
	old_data = all_data
	joystick = is900Sensor.getData()
	all_data = [is900Sensor.buttonState(),joystick[0],joystick[1]]
	
	if is900Sensor:
		#if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
		#	zooming = False
		
		old_state = int(old_data[0])
		state = int(all_data[0])
		if state & 0:
			print 'Button 0 is down'
		if state & 1:
			print 'Button 1 is down'
		if state & 2 and not(old_state & 2):
			print 'Button 2 is down'
			cycleTechniqueForward()
		if state & 4:
			print 'Button 3 is down'
		if state & 8 and not(old_state & 8):
			print 'Button 4 is down'
			cycleTechniqueBackward()
		if state & 16:
			print 'Button 5 is down'	
		if state & 32 and not(old_state & 32):
			#print 'Trigger Button is down'
			if mode == InteractionMode.SELECTION_TRIGGER or Globals.application != Globals.Application.EVALUATION or (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].maxZoom == -1 or (trials[current_it][current_iteration].maxZoom != -1 and zoomingLevel >= math.pow(2,trials[current_it][current_iteration].maxZoom))):
				selectButton()
			buttonState[2] = True
		elif old_state & 32 and not(state & 32):
			buttonState[2] = False
		
		if mode != InteractionMode.SELECTION_TRIGGER:
			if Globals.application == Globals.Application.EVALUATION:
				time_elapsed = str(viz.tick() - start_time)
				#print all_data[1], all_data[2]
				if (old_data[2] <= 230 and all_data[2] > 230) or (all_data[2] > 230 and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom):
					#print 'joystick up pressed'
					if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
						zoomInButton()
					if not in_training and (old_data[2] <= 230 and all_data[2] > 230):
						data_file.write(time_elapsed + ' zoom level increasing from: ' + str(zoomingLevel) + '\n')
						if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
							data_file.write(time_elapsed + ' zoom window increasing from: ' + str(animationCurrentWindow) + '\n')
						elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
							data_file.write(time_elapsed + ' zoom window increasing from: ' + str(currentWindow) + '\n')
					buttonState[0] = True		
				elif old_data[2] > 230 and all_data[2] <= 230:
					#print 'joystick up released'
					if trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
						zoomInButton()
					buttonState[0] = False
					if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
						previousWindow = animationCurrentWindow
						#print animationCurrentWindow,"==",previousWindow
					if not in_training:
						data_file.write(time_elapsed + ' new zoom level: ' + str(zoomingLevel) + '\n')
						if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
							data_file.write(time_elapsed + ' new zoom window: ' + str(animationCurrentWindow) + '\n')
						elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
							updateWindowDimensionsDiscrete(0.0)
							data_file.write(time_elapsed + ' new zoom window: ' + str(currentWindow) + '\n')
						
				
				elif (old_data[2] > 25 and all_data[2] <= 25) or (all_data[2] <= 25 and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom):
					#print 'joystick down pressed'
					if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
						if old_data[2] > 25 and all_data[2] <= 25:
							currentWindow = animationCurrentWindow
						previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
						zoomOutButton()	
					if not in_training and (old_data[2] <= 230 and all_data[2] > 230):
						data_file.write(time_elapsed + ' zoom level decreasing from: ' + str(zoomingLevel) + '\n')
						if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
							data_file.write(time_elapsed + ' zoom window decreasing from: ' + str(animationCurrentWindow) + '\n')
						elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
							data_file.write(time_elapsed + ' zoom window decreasing from: ' + str(currentWindow) + '\n')
					buttonState[1] = True
				elif old_data[2] <= 25 and all_data[2] > 25:
					#print 'joystick down released'
					zoomOutButton()
					buttonState[1] = False
					if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
						previousWindow = animationCurrentWindow
						#print animationCurrentWindow,"==",previousWindow
					if not in_training:
						data_file.write(time_elapsed + ' new zoom level: ' + str(zoomingLevel) + '\n')
						if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
							data_file.write(time_elapsed + ' new zoom window: ' + str(animationCurrentWindow) + '\n')
						elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
							updateWindowDimensionsDiscrete(0.0)
							data_file.write(time_elapsed + ' new zoom window: ' + str(currentWindow) + '\n')
			else:
				if (old_data[2] <= 230 and all_data[2] > 230) or (all_data[2] > 230 and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
					#print 'joystick up pressed'
					if Globals.technique == Study.InteractionTechnique.ContinuousZoom:
						zoomInButton()
					buttonState[0] = True		
				elif old_data[2] > 230 and all_data[2] <= 230:
					#print 'joystick up released'
					if Globals.technique == Study.InteractionTechnique.DiscreteZoom:
						zoomInButton()
					buttonState[0] = False
					if Globals.technique == Study.InteractionTechnique.ContinuousZoom:
						previousWindow = animationCurrentWindow
						#print animationCurrentWindow,"==",previousWindow	
				elif (old_data[2] > 25 and all_data[2] <= 25) or (all_data[2] <= 25 and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
					#print 'joystick down pressed'
					if Globals.technique == Study.InteractionTechnique.ContinuousZoom:
						if old_data[2] > 25 and all_data[2] <= 25:
							currentWindow = animationCurrentWindow
						previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
						zoomOutButton()	
					buttonState[1] = True
				elif old_data[2] <= 25 and all_data[2] > 25:
					#print 'joystick down released'
					zoomOutButton()
					buttonState[1] = False
					if Globals.technique == Study.InteractionTechnique.ContinuousZoom:
						previousWindow = animationCurrentWindow
						#print animationCurrentWindow,"==",previousWindow
			
		#The pointing with the wand is absolute when the user is at the center of the 
		#VisWalls area, at 5ft from the display, in its center, holding the wand at
		#3.5ft height. That gives a horizontal FOV of 90 and vertical of 70.
		#Since the wall is not square, the only way to match the vertical and horizontal FOV
		#is by software, which may be important, taking into account the nature of the 
		#circles distributed in a sphere
		
		#Pointing straight at the wall is +/- 180deg yaw, 0deg pitch.
		#this means that horizontally, 135deg corresponds to 0 and -135 corresponds to 1 in the 
		#normalized coordinates -- (0.5,0.5) is the center of the display
		
		previous_yaw = is900Euler[0]
		is900Euler = is900Sensor.getEuler()
		
		if Globals.USE_FILTERING:
			# we should convert to mm the values passed to the filter 3048mm x 2286mm
			#print "X: ", (centroid[0]-previous_centroid[0])*3048.0/fps, "\tY: ", (centroid[1]-previous_centroid[1])*2286.0/fps
			#print centroid, "\t", previous_centroid
			if is900Euler[0] < 0:
				is900Euler[0] += 360
			newEuler = filter.Apply(Vector3(is900Euler[0],is900Euler[1],is900Euler[2]),fps)
			is900Euler[0] = newEuler.x
			is900Euler[1] = newEuler.y
			is900Euler[2] = newEuler.z
			#print Euler
		
		previous_centroid = []
		previous_centroid.append(centroid[0])
		previous_centroid.append(centroid[1])
		#print centroid," - ",

		if is900Euler[0] > 0:
			centroid[0] = (is900Euler[0] - 135) / 90
		else:
			centroid[0] = ((is900Euler[0] + 135) / 90) + 1

		#-15 seems to be a confortable pitch for pointing at the center
		centroid[1] = 1.0 - (((is900Euler[1] +15) + 35) / 70)
		
		centroid[0] *= windowSize[0]
		if centroid[0] > windowSize[0]:
			centroid[0] = windowSize[0]-1
		elif centroid[0] < 0:
			centroid[0] = 0
		centroid[1] *= windowSize[1]
		if centroid[1] > windowSize[1]:
			centroid[1] = windowSize[1]-1
		elif centroid[1] < 0:
			centroid[1] = 0

# if not using the IS900, use this
def updateMouseData():
	global centroid
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global buttonState
	global windowSize
	global selectedQuadrant
	global previousCenterOffset
	global newCenterOffset
	global showMenu
	global mouseState
	global oldMouseState
	global previousWindow
	global currentWindow
	global animationCurrentWindow
	global lastZoomingCount
	global start_time
	
	# Get current mouse button state
	
	state = viz.mouse.getState()
	oldMouseState = mouseState
	mouseState = state

	#if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
	#	zooming = False
	
	# Check which buttons are currently pressed
	if mode != InteractionMode.SELECTION_TRIGGER:
		if Globals.application == Globals.Application.EVALUATION:
			time_elapsed = str(viz.tick() - start_time)
		if (not (oldMouseState & viz.MOUSEBUTTON_LEFT) and mouseState & viz.MOUSEBUTTON_LEFT) or (mouseState & viz.MOUSEBUTTON_LEFT and ((Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom))):
			#print 'left button down'
			if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
				zoomInButton()
			if Globals.application == Globals.Application.EVALUATION and not in_training and (not (oldMouseState & viz.MOUSEBUTTON_LEFT) and mouseState & viz.MOUSEBUTTON_LEFT):
				data_file.write(time_elapsed + ' zoom level increasing from: ' + str(zoomingLevel) + '\n')
				if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
					data_file.write(time_elapsed + ' zoom window increasing from: ' + str(animationCurrentWindow) + '\n')
				elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
					data_file.write(time_elapsed + ' zoom window increasing from: ' + str(currentWindow) + '\n')
			buttonState[0] = True
		elif oldMouseState & viz.MOUSEBUTTON_LEFT and not (mouseState & viz.MOUSEBUTTON_LEFT):
			#print 'left button up'
			if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.DiscreteZoom):
				zoomInButton()
			buttonState[0] = False
			if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
				previousWindow = animationCurrentWindow
				#print animationCurrentWindow,"==",previousWindow			
			if Globals.application == Globals.Application.EVALUATION and not in_training:
				data_file.write(time_elapsed + ' new zoom level: ' + str(zoomingLevel) + '\n')
				if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
					data_file.write(time_elapsed + ' new zoom window: ' + str(animationCurrentWindow) + '\n')
				elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
					updateWindowDimensionsDiscrete(0.0)
					data_file.write(time_elapsed + ' new zoom window: ' + str(currentWindow) + '\n')
			
		elif (not (oldMouseState & viz.MOUSEBUTTON_MIDDLE) and mouseState & viz.MOUSEBUTTON_MIDDLE) or (mouseState & viz.MOUSEBUTTON_MIDDLE and ((Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom))):
			#print 'middle button down'	
			if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
				if not (oldMouseState & viz.MOUSEBUTTON_MIDDLE) and mouseState & viz.MOUSEBUTTON_MIDDLE:
					currentWindow = animationCurrentWindow
				previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
				zoomOutButton()	
			if Globals.application == Globals.Application.EVALUATION and not in_training and (not (oldMouseState & viz.MOUSEBUTTON_MIDDLE) and mouseState & viz.MOUSEBUTTON_MIDDLE):
				data_file.write(time_elapsed + ' zoom level decreasing from: ' + str(zoomingLevel) + '\n')
				if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
					data_file.write(time_elapsed + ' zoom window decreasing from: ' + str(animationCurrentWindow) + '\n')
				elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
					data_file.write(time_elapsed + ' zoom window decreasing from: ' + str(currentWindow) + '\n')
			buttonState[1] = True
		elif oldMouseState & viz.MOUSEBUTTON_MIDDLE and not (mouseState & viz.MOUSEBUTTON_MIDDLE):
			#print 'middle button up'	
			zoomOutButton()
			buttonState[1] = False
			if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
				previousWindow = animationCurrentWindow
				#print animationCurrentWindow,"==",previousWindow			
			if Globals.application == Globals.Application.EVALUATION and not in_training:
				data_file.write(time_elapsed + ' new zoom level: ' + str(zoomingLevel) + '\n')
				if trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom:
					data_file.write(time_elapsed + ' new zoom window: ' + str(animationCurrentWindow) + '\n')
				elif trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
					updateWindowDimensionsDiscrete(0.0)
					data_file.write(time_elapsed + ' new zoom window: ' + str(currentWindow) + '\n')
		
	if not (oldMouseState & viz.MOUSEBUTTON_RIGHT) and mouseState & viz.MOUSEBUTTON_RIGHT:
		#print 'right button down' 
		if mode == InteractionMode.SELECTION_TRIGGER or (Globals.application == Globals.Application.EVALUATION) or (trials[current_it][current_iteration].maxZoom == -1 or (trials[current_it][current_iteration].maxZoom != -1 and zoomingLevel >= math.pow(2,trials[current_it][current_iteration].maxZoom))):
			selectButton()
		buttonState[2] = True
	elif oldMouseState & viz.MOUSEBUTTON_RIGHT and not (mouseState & viz.MOUSEBUTTON_RIGHT):
		#print 'right button up' 	
		buttonState[2] = False
		
	# Get mouse position in pixel coordinates
	centroid = viz.mouse.getPosition(viz.WINDOW_PIXELS) 

def updateCursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
	#global sphere
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global lastZoomingLevel
	global minFOV
	global selectedQuadrant
	global previousCenterOffset
	global newCenterOffset
	global quadrants
	global showMenu
	global intersectObj
	global boundingBox
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	
	x,y = centroid[0],centroid[1]
	#print x,y
	#print viz.mouse.getPosition(viz.WINDOW_PIXELS) 
	print "level:",zoomingLevel
	print "count:",zoomingCount
	
	if Globals.application == Globals.Application.CROWDSIMULATION:
		intersectObj = viz.pick(pos = [x/windowSize[0],y/windowSize[1]])
		
		if intersectObj.valid() and intersectObj != quad1 and intersectObj != quad2 and intersectObj != quad3:
			drawIntersectObjBoundingBox()
		elif boundingBox != None:
			boundingBox.remove()
			boundingBox = None
	elif Globals.application == Globals.Application.SUPERMARKET:
		intersectObj = viz.pick(pos = [x/windowSize[0],y/windowSize[1]])
		
		if intersectObj.valid():
			drawIntersectObjBoundingBox()
		elif boundingBox != None:
			boundingBox.remove()
			boundingBox = None
	elif Globals.application == Globals.Application.EVALUATION:
		#print "EVALUATION"
		sphereInclusionTest()
		drawIntersectObjBoundingDisk()
	#print intersect.point
	
	if Globals.application == Globals.Application.EVALUATION:
		if boundingBox != None and mode != InteractionMode.SELECTION_TRIGGER:
			if trials[current_it][current_iteration].maxZoom != -1 and zoomingLevel < math.pow(2,trials[current_it][current_iteration].maxZoom):
				boundingBox.visible(viz.OFF)
			else:
				boundingBox.visible(viz.ON)
	
	crosshair.setPosition(x/windowSize[0],y/windowSize[1],0)
	
	if (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.ContinuousZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.ContinuousZoom):
		showMenu = False
		if zooming == True:
			previousCenterOffset = [0,0]
			if buttonState[0]:
				print "zoom in button pressed"
				if (Globals.application != Globals.Application.EVALUATION and zoomingLevel < 128.0) or (Globals.application == Globals.Application.EVALUATION and ((trials[current_it][current_iteration].maxZoom != -1 and zoomingLevel < math.pow(2,trials[current_it][current_iteration].maxZoom)) or (trials[current_it][current_iteration].maxZoom == -1 and zoomingLevel < 128.0))):
					#print "setting new center offset"
					#newCenterOffset = [(newCenterOffset[0]+((previousWindow[0][0]+x * ((previousWindow[1][0]-previousWindow[0][0]) / windowSize[0]))-newCenterOffset[0])*(1.0 - (zoomingCount/(VFOV-minFOV)))), 
					#				   (newCenterOffset[1]+((previousWindow[0][1]+y * ((previousWindow[1][1]-previousWindow[0][1]) / windowSize[1]))-newCenterOffset[1])*(1.0 - (zoomingCount/(VFOV-minFOV))))]
					#newCenterOffset = [(previousWindow[0][0]+x * ((previousWindow[1][0]-previousWindow[0][0]) / windowSize[0])), 
					#				   (previousWindow[0][1]+y * ((previousWindow[1][1]-previousWindow[0][1]) / windowSize[1]))]
					newCenterOffset = [(animationCurrentWindow[0][0]+x * ((animationCurrentWindow[1][0]-animationCurrentWindow[0][0]) / windowSize[0])), 
									   (animationCurrentWindow[0][1]+y * ((animationCurrentWindow[1][1]-animationCurrentWindow[0][1]) / windowSize[1]))]
					#print " ",newCenterOffset
					#print " ",zoomingLevel
				if VFOV-minFOV-lastZoomingCount == 0:
					updateFrustum(0.0)
				else:
					updateFrustum((zoomingCount-lastZoomingCount)/(VFOV-minFOV-lastZoomingCount))
				
			elif buttonState[1]:
				#print "zooming count:",zoomingCount
				#print "last zooming count:",lastZoomingCount
				print "zoom out button pressed"#,(zoomingCount/lastZoomingCount)#((lastZoomingCount-zoomingCount)/(VFOV-minFOV-lastZoomingCount))
				#newCenterOffset = [newCenterOffset[0]+(x-newCenterOffset[0])*(1.0 - (zoomingCount/(VFOV-minFOV))), 
				#				   newCenterOffset[1]+(y-newCenterOffset[1])*(1.0 - (zoomingCount/(VFOV-minFOV)))]
				#updateFrustum((zoomingCount)/(VFOV-minFOV))
				if lastZoomingCount != 0:
					updateFrustum(zoomingCount/lastZoomingCount)
				else:
					updateFrustum(0.0)
			else:
				print "zoom button released"
				updateFrustum(0.0)
				lastZoomingCount = zoomingCount
	elif (Globals.application == Globals.Application.EVALUATION and trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom) or (Globals.application != Globals.Application.EVALUATION and Globals.technique == Study.InteractionTechnique.DiscreteZoom):
		if zoomingAnimation == 0 and mode == InteractionMode.SELECTION:
			showMenu = True
		else:
			showMenu = False
		
		# quadrants calculation
		cursor = cursorOverQuadrant()
		#print cursor
		#print newCenterOffset
		
		matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
		
		#quadrants.setMatrix(matrix, viz.ABS_GLOBAL)
		#quadrants.setPosition([0,0,50], viz.REL_LOCAL)
		
		if zoomingAnimation != 0:
			#calculate the direction vector based on the selected quadrant
			x,y = previousCenterOffset[0]+selectedQuadrant[0],previousCenterOffset[1]+selectedQuadrant[1]
			print x,y
			
			updateFrustum(zoomingCount/totalAnimationFrames)
			
			if zoomingCount+1 < totalAnimationFrames:
				#print zoomingCount
				zoomingCount += 1
			else:
				print "done!"
				zoomingCount = 0
				zoomingAnimation = 0
				previousCenterOffset = newCenterOffset
		else:
			#fov = (VFOV/zoomingLevel)
			updateFrustum()
	else:
		showMenu = False
	
	if showMenu == True:
		for quad in quadrants:
			quad.visible(viz.ON)
		#quadrants.visible(viz.ON)	
		colorQuadrants()
	else:
		for quad in quadrants:
			quad.visible(viz.OFF)			
		#quadrants.visible(viz.OFF)			
	
	#if buttonState[0] == True:
	#print "previous: ",previousCenterOffset
	#print "new:      ",newCenterOffset
	
	#print "last zooming level:",lastZoomingLevel
	if Globals.application == Globals.Application.EVALUATION:
		if (trials[current_it][current_iteration].maxZoom != -1 and lastZoomingLevel < math.pow(2,trials[current_it][current_iteration].maxZoom) and zoomingLevel >= math.pow(2,trials[current_it][current_iteration].maxZoom)) or (trials[current_it][current_iteration].maxZoom == -1 and lastZoomingLevel < 128.0 and zoomingLevel >= 128.0):
			#print "BUUUUUUUUUUUUUUUUUUUUUUUUUZZZZZZZZZZZZ"
			viz.playSound("BUZZER.WAV")
			lastZoomingLevel = zoomingLevel
		
	if zooming == False:
		#viz.fov(VFOV)
		#fov = VFOV
		updateFrustum()

def updateView():
	if Navigation.yaw == Rotate.CW: #right
		viz.MainView.setEuler([Navigation.rotation_speed*viz.elapsed()*2.0,0,0],viz.BODY_ORI,viz.REL_PARENT)
	elif Navigation.yaw == Rotate.CCW: #left
		viz.MainView.setEuler([-Navigation.rotation_speed*viz.elapsed()*2.0,0,0],viz.BODY_ORI,viz.REL_PARENT)
		
	if Navigation.pitch == Rotate.CW: #down
		viz.MainView.setEuler([0,Navigation.rotation_speed*viz.elapsed(),0],viz.HEAD_ORI,viz.REL_LOCAL)
	elif Navigation.pitch == Rotate.CCW: #up
		viz.MainView.setEuler([0,-Navigation.rotation_speed*viz.elapsed(),0],viz.HEAD_ORI,viz.REL_LOCAL)
	
	if Navigation.roll == Rotate.CW: #down
		viz.MainView.setEuler([0,0,Navigation.rotation_speed*viz.elapsed()],viz.HEAD_ORI,viz.REL_LOCAL)
	elif Navigation.roll == Rotate.CCW: #up
		viz.MainView.setEuler([0,0,-Navigation.rotation_speed*viz.elapsed()],viz.HEAD_ORI,viz.REL_LOCAL)

	if Navigation.fly == Move.UP:
		viz.MainView.move(0,Navigation.TRANSLATION_SPEED/2*viz.elapsed(),0,viz.BODY_ORI)
	elif Navigation.fly == Move.DOWN:
		viz.MainView.move(0,-Navigation.TRANSLATION_SPEED/2*viz.elapsed(),0,viz.BODY_ORI)

def update():
	global windowSize
	global aspectRatio
	global VFOV
	global minFOV
	global previousFrameTick
	global fps
	global totalAnimationFrame
	global input_needed
	
	windowSize = viz.MainWindow.getSize(viz.WINDOW_PIXELS)
	aspectRatio = windowSize[0]/windowSize[1]
	VFOV = 2.0 * math.atan( math.tan( (defaultHFOV/57.2957795) / 2.0 ) / aspectRatio ) * 57.2957795
	if Globals.application == Globals.Application.EVALUATION:
		if trials[current_it][current_iteration].maxZoom != -1:
			minFOV = VFOV / math.pow(2,trials[current_it][current_iteration].maxZoom)
		else:
			minFOV = VFOV / 128.0
	else:
		minFOV = VFOV / 128.0
	currentFrameTick = viz.tick()
	fps = 1/(currentFrameTick-previousFrameTick)
	previousFrameTick = currentFrameTick
	#print "minFOV: ",minFOV 
	
	if Globals.application == Globals.Application.EVALUATION:
		if input_needed == True:
			black_quad.visible(viz.ON)
			interruptMessage.visible(viz.ON)
		else:
			if errorMessage.getVisible() == viz.OFF:
				black_quad.visible(viz.OFF)
			interruptMessage.visible(viz.OFF)
	
	updateView()
	#updateCharacters()
	if Globals.application == Globals.Application.EVALUATION:
		if input_needed == False:
			updateIS900Data()
			#updateMouseData()
	else:
		updateIS900Data()
		#updateMouseData()
	updateCursor()

# main
if __name__ == '__main__':
	global defaultPosition
	global defaultOrientation
	global defaultFOV
	global VFOV
	global minFOV
	global listFrames
	global children
	global currentFrame
	global previousFrame
	global windowSize
	global aspectRatio
	global centroid
	#global sphere
	global buttonState
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global quadrants
	global showMenu
	global boundingBox
	global is900Sensor
	global old_data
	global all_data
	global is900Euler
	global crosshair
	global settingUpTrial
	global errorMessageTimeOut
	global previousCenterOffset
	global newCenterOffset
	global previousFrameTick
	global fps
	global quad1
	global quad2
	global quad3
	global children_low
	global in_training
	
	global application_mode
	global selection_mode
	global user_id
	global starting_it
	global intersection_sphere
	global intersection_sphere_radius
	global children
	global mode
	global collision_test
	global identity
	global trigger
	global data_file
	global num_trials
	global total_trial_iterations
	global total_trial_iterations_training
	global max_iterations
	global original_max_iterations
	global num_iterations
	global num_iterations_training
	global max_tracking
	global trials
	global current_iteration
	global start_timestamp
	global formatted_time
	global current_it
	global setting_up_trial
	global filter
	global error_message_timeout
	global mouseState
	global oldMouseState
	global zoomingStack
	
	global input_needed
	
	global training_timer
	global stop_training
	global start_training
	
	global bg_sphere
	
	global previousZoomingLevel
	global lastZoomingCount
	
	global sortedIT
	global currentSortedIT
	global maxZoom
	
	global currentWindow
	global previousWindow
	global animationCurrentWindow
	
	global lastZoomingLevel
	
	############################
	# setup vizard
	viz.collision(viz.OFF)
	viz.clearcolor(viz.BLACK)
	viz.setOption('viz.fullscreen.monitor',1)
	#viz.go(viz.FULLSCREEN)
	viz.go()
	
	############################
	# user position	
	aspectRatio = viz.MainWindow.getAspectRatio()
	defaultHFOV = 90.0 # vertical -> horizontal = vertical * aspect 
	#VFOV = defaultHFOV / aspectRatio
	VFOV = 2.0 * math.atan( math.tan( (defaultHFOV/57.2957795) / 2.0 ) / aspectRatio ) * 57.2957795
	minFOV = VFOV / 128.0
	#fov = VFOV
	#updateFrustum(fov)
	viz.MainWindow.fov(VFOV)
	print viz.MainWindow.getVerticalFOV()
	print viz.MainWindow.getHorizontalFOV()
	
	#if trials[current_it][current_iteration].technique == Study.InteractionTechnique.DiscreteZoom:
	quadrants = createQuadrantsZoom()
	for quad in quadrants:
		quad.alpha(.3)
	#quadrants.alpha(.5)
	#quadrants.depthFunc(viz.GL_ALWAYS)
	#quadrants.drawOrder(0)
	showMenu = False
	
	############################
	# get the window size
	windowSize = viz.MainWindow.getSize(viz.WINDOW_PIXELS)
	print windowSize
	
	############################
	# cursor
	viz.mouse.setOverride(viz.ON)
	buttonState = [False, False, False]
	centroid = [0,0]
	#sphere = vizshape.addSphere(radius=3)
	#sphere.disable(viz.PICKING)
	zooming = False
	zoomingAnimation = 0
	zoomingCount = 0
	zoomingLevel = 1
	lastZoomingLevel = zoomingLevel
	previousZoomingLevel = 1
	crosshair = viz.addTexQuad(viz.SCREEN,texture=viz.add('bline.png'))
	previousCenterOffset = [0,0]
	newCenterOffset = [0,0]
	lastZoomingCount = 0
	
	############################
	# Add the intersense tracker
	isense = viz.add('intersense.dle')
	is900Sensor = isense.addTracker(port=1,station=2)
	
	is900Sensor.setEnhancement(0)
	is900Sensor.setPrediction(0)
	#is900Sensor.setSensitivity(4)
	print "Wand Enhancement: "+str(is900Sensor.getEnhancement())
	print "Wand Prediction: "+str(is900Sensor.getPrediction())
	print "Wand Sensitivity: "+str(is900Sensor.getSensitivity())
	
	all_data = [0,0,0,0,0,0,0,0,0,0]
	old_data = [0,0,0,0,0,0,0,0,0,0]
	is900Euler = [0,0,0]
	
	previousFrameTick = 0.0
	fps = 0.0
	
	boundingBox = None
	
	mouseState = 0
	oldMouseState = 0
	
	errorMessage.visible(viz.OFF)
	interruptMessage.visible(viz.OFF)
	
	zoomingStack = []
	
	previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
	currentWindow = [[0,0],[windowSize[0],windowSize[1]]]
	animationCurrentWindow = [[0,0],[windowSize[0],windowSize[1]]]
	
	# Low pass filter initialization
	# the screen coordinates are [0,0] to [1,1]
	# 10' x 7.5' in the screen size -> 3048mm x 2286mm, avg 2667
	# according to Vogel & Balakrishnan freehand pointing paper,
	# the velocities low and high should be 10mm/s and 200mm/s
	# mapping that onto the 0,1 coords, we get 10/2667 = 0.0037 & 200/2667 = 0.075
	# we do the conversion in the application of the filter, passing mm values, rather than normalized units
	#filter = LowPassDynamicFilter(0.25, 5, 10.0, 200.0)
	
	#converting to degrees, which is how the filter is now being applied
	filter = LowPassDynamicFilter(.25, 5, 0.33745, 6.7492)
	
	#used to calculate fps, used for filter
	previousFrameTick = viz.tick()
	
	###########################
	# if the application is set to crowd simulation
	if Globals.application == Globals.Application.CROWDSIMULATION:
		#Set mode to disable interaction while the trigger is shown
		mode = InteractionMode.SELECTION
		
		viz.enable(viz.CULL_FACE)
	
		defaultPosition = [0.0,40.0,0.0]
		defaultOrientation = [45.0,37.0,0.0]
		viz.MainView.setPosition(defaultPosition,viz.ABS_GLOBAL)
		viz.MainView.setEuler(defaultOrientation,viz.BODY_ORI,viz.ABS_GLOBAL)
		
		# add quad/ground for picking
		quad1 = vizshape.addPlane(size=(5000.0,5000.0),axis=vizshape.AXIS_Y,cullFace=False)
		quad2 = vizshape.addPlane(size=(5000.0,5000.0),axis=vizshape.AXIS_Y,cullFace=False)
		quad2.setPosition(0,-0.0002,0)
		quad3 = vizshape.addPlane(size=(5000.0,5000.0),axis=vizshape.AXIS_Y,cullFace=False)
		quad3.setPosition(0,-0.0004,0)
		
		print "running character loader"
		#a string that contains file name. 
		fileName = 'simulation_output.txt'
		listFrames = loadSimulation(fileName)
		children = []

		for character in listFrames:
			#Add the avatar
			avatar = viz.add('male.cfg')

			#Have the avatar walk in a circle in front of the viewers
			avatar.setPosition([character[0][0],0,character[0][1]])
			avatar.setEuler(character[0][2],0,0)
			avatar.state(1)
			
			children.append(avatar)
			#print "character('",character,"')"
		
		currentFrame = 0
		previousFrame = -1
		
		placeTotem()
		
	elif Globals.application == Globals.Application.SUPERMARKET:
		#Set mode to disable interaction while the trigger is shown
		mode = InteractionMode.SELECTION
		
		defaultPosition = [-80,57,-420]
		defaultOrientation = [45.0,37.0,0.0]
		viz.MainView.setPosition(defaultPosition,viz.ABS_GLOBAL)
		viz.MainView.setEuler([0,0,0],viz.BODY_ORI,viz.ABS_GLOBAL)
		viz.MainView.setEuler(defaultOrientation,viz.BODY_ORI,viz.REL_PARENT)
		
		print "Loading the supermarket model"
		#a string that contains file name. 
		fileName = 'simulation_output.txt'
		
		currentFrame = 0
		previousFrame = -1
		
		#supermarket = viz.add('finalM.wrl')
		supermarket = viz.add('finalM.ive')
		#supermarket.appearance(viz.TEXMODULATE)
		supermarket.ambient(.6,.6,.6)

		#IMPORTANT: Need to add a joystick. This will return the first detected joystick
		#joy = vizjoy.add()

		#Make the objects in supermarket.wrl accessible
		getModels()
		children = supermarket.getChildren()
		
		#supermarket.save('finalM.ive')
		
		errorMessage.visible(viz.OFF)
		interruptMessage.visible(viz.OFF)
	
	###############################################
	# if the application is set to evaluation...
	#loads the distractors
	elif Globals.application == Globals.Application.EVALUATION:
		defaultPosition = [0.0,0.0,0.0]
		defaultOrientation = [0.0,0.0,0.0]
		viz.MainView.setPosition(defaultPosition,viz.ABS_GLOBAL)
		viz.MainView.setEuler(defaultOrientation,viz.BODY_ORI,viz.ABS_GLOBAL)
		
		children_low = None
		
		#create sphere of distractors
		createLowDensityDistractors()
		
		#flag to determine if state is training
		in_training = False
		
		user_id = None
		starting_it = None

		#variable to hold the sphere that is cast onto the environment
		intersection_sphere = None
		intersection_sphere_radius = None
		
		#list of objects
		children = []	
		
		'''
		this is needed in order to cast the sphere independently of where you're pointing to (quad or "space")
		intersection_sphere needs to always intersect something
		'''
		bg_sphere = createSphere(Globals.SCREEN_SPHERE_RADIUS,50,50)
		bg_sphere.color(1,0,0)
		bg_sphere.alpha(0)
		#bg_sphere.depthFunc(viz.GL_LESS)
		#bg_sphere.drawOrder(4)
		#bg_sphere.polyMode(viz.POLY_WIRE)
		
		bg_quad = createBackgroundGrid(-50,50)
		bg_quad.setScale(0.25,0.25,1.0)
		bg_quad.setPosition(0,0,10)

		#Set mode to disable interaction while the trigger is shown
		mode = InteractionMode.SELECTION_TRIGGER
		
		collision_test = []
		
		#create identity matrix to be used in transformations
		identity = vizmat.Transform()
		identity.makeIdent()

		#print "Creating Trigger: "
		trigger = createCircle(Globals.TRIGGER_SIZE,0,0,Globals.SCREEN_SPHERE_RADIUS)
		trigger.color(0.7,0.7,0.3)
		#print "End Trigger Creation"
		
		#Number of trials per condition - should be 8 for experiment
		total_trial_iterations = 8
		
		#Number of trials per condition for training - 4 is enough, as it ends in 90s
		total_trial_iterations_training = 8

		#input file with experimental settings - created by batch file
		sortedIT = [0,0,0]
		maxZoom = [0,0,0,0]
		input_file = open('Trials.txt','r')
		parseInputFile(input_file)
		
		'''
		Study.*.size denotes the number of levels of each variable, e.g. 2IT, 3DD, 3TS

		num_trials: number of conditions for the experiment - Not used anymore
		max_iterations: total number of trials per technique - conditions * repetitions per condition
		num_iterations: same as max_iterations
		num_iterations_training: maximum  number of trials per technique for 
								 training - conditions * repetitions per condition
								 stops at whichever comes first, this or 90s
		max_tracking: number of runs for each tracking condition: 2T + 2 experimental sessions
					  + 2 training sessions + 1 initial trainining

		'''
		#num_trials = Study.InteractionTechnique.size*Study.DistractorsDensity.size*Study.TargetSize.size
		original_max_iterations = total_trial_iterations*Study.TargetSize.size
		max_iterations = [original_max_iterations,original_max_iterations,original_max_iterations,original_max_iterations,original_max_iterations,original_max_iterations,original_max_iterations]
		num_iterations = max_iterations[0]
		num_iterations_training = total_trial_iterations_training*Study.TargetSize.size
		
		'''
		list to hold each iteration of the experiment
		'''
		trials = []
		
		currentSortedIT = 0
		current_it = sortedIT[currentSortedIT]*9
		current_iteration = 0
		
		initializeTrials()
		
		#create file to record data
		start_timestamp = time.localtime()
		formatted_time = time.strftime("%Y%m%d_%H%M%S",start_timestamp)

		data_file = open('Results/participant_'+str(user_id)+'_data_'     +formatted_time+'.txt', 'a')

		data_file.write('Results\nParticipant '+str(user_id)+'\n\n')
		data_file.write('Experiment started at '+time.strftime("%a, %d %b %Y %H:%M:%S",start_timestamp)+'\n')

		#flag to disable interaction while trial is being set up
		setting_up_trial = False
		
		#flag to determine if input is needed from the experimenter
		input_needed = True

		
		#flag to start the training timer
		start_training = True
		
		#tell trainig to stop when 90 seconds and all conditions were performed
		stop_training = False
		
		#initialize timer for training (90s)	
		training_timer = None
		
		#flag to disable interaction while trial is being set up
		settingUpTrial = False
		
		#black quad to fill out the screen while error message is displayed
		black_quad = viz.addTexQuad(viz.SCREEN,size=10000)
		black_quad.color(viz.BLACK)
		
		errorMessageTimeOut = 0.75
		
		setupTrial()
		
	viz.callback(viz.KEYDOWN_EVENT, keyDown)
	viz.callback(viz.KEYUP_EVENT, keyUp)
		
	viz.playSound("BUZZER.WAV")
	
	############################
	# callbacks
	vizact.ontimer(0,update)
	
