import viz
import math
import os, sys
import vizshape
import random
import time
import copy
from LowPassDynamicFilter import LowPassDynamicFilter
from Vector3 import Vector3
	
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
	TOTAL_ANIMATION_TIME_COMBINED = 0.25

class InteractionMode:
	SELECTION = 0
	SELECTION_QUADRANTS = 1
	
class Quadrant:
	TOP=0
	BOTTOM=1
	LEFT=2
	RIGHT=3
	NONE=4

class InteractionTechnique:
	SQUAD = 0
	DiscreteZoom = 1
	ContinuousZoom = 2
	CombinedZoomv1 = 3
	CombinedZoomv2 = 4
	CombinedZoomv3 = 5
	CombinedZoomv4 = 6
	Raycasting = 7
	size = 8

class Globals:
	technique = InteractionTechnique.CombinedZoomv1
	#technique = InteractionTechnique.ContinuousZoom
	#technique = InteractionTechnique.DiscreteZoom
	
	ONE_PX_IN_M          = 0.00238125
	ONE_PX_IN_DEG        = 0.000080645
	SCREEN_SPHERE_RADIUS = 2.155
	
	#what's the meaning of these radii?
	#1 is bigger than the screen, so it's not normalized, neither absolute
	#absolute should be 10ft = 3.048m -> 3.048/2 = 1.524 -> diameter of the screen
	TINY_SPHERE_RADIUS   = ONE_PX_IN_M/4.0
	NORMAL_SPHERE_RADIUS = 0.6465
	
	USE_FILTERING = True
	
	DEBUG = False#True
	
# getmodels()
# creates a node3d for each model in the loaded .ive file 
def getModels():
	'''
	nodeNames = supermarket.getNodeNames()
	for name in nodeNames:
		supermarket.getChild(name)
	'''
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

#-------------------------------------------------------------------------------
# <node3d:on-the-fly> objects functions
#-------------------------------------------------------------------------------
# createBoundingBox()
# creates a bounding box with the given size
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

# createSphere()
# creates a sphere 
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

# createQuad()
# creates a rectangle on the top portion of the screen to display the current 
# technique
def createQuad(left_bot,left_top,right_bot,right_top):
	viz.startlayer(viz.QUADS) 
	viz.vertexcolor(0,0,0)
	viz.vertex(left_bot)
	viz.vertex(left_top)
	viz.vertex(right_top)
	viz.vertex(right_bot)
	return viz.endlayer()

# createQuadLin()
# creates the lines used in the quad menu
def createQuadLin():
	viz.startlayer(viz.LINES) 
	viz.linewidth(2)
	viz.vertex(-1000,-1000,0) #Vertices are split into pairs.
	viz.vertex( 1000, 1000,0)
	viz.vertex(-1000, 1000,0)
	viz.vertex( 1000,-1000,0)
	return viz.endlayer()

# createQuadTri()
# creates the triangles used in the quad menu quadrants
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
# SQUAD quadrants functions
#-------------------------------------------------------------------------------
# createSQUADQuadrants()
# distributes the items that were inside the sphere among the different 
# quadrants
def createSQUADQuadrants(list,centered=0):
	global clone_list
	clone_list = []
	#print "selecting an object among:",list
	user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
	#print "size of the array:",len(list)
	aspect = (viz.getWindowList())[0].getAspectRatio()
	clone_total_level_1 = [0.0,0.0,0.0,0.0]
	clone_total_level_2 = [0.0,0.0,0.0,0.0]
	clone_total_level_3 = [0.0,0.0,0.0,0.0]
	clone_dist_level_1 = [0.0,0.0,0.0,0.0]
	clone_dist_level_2 = [0.0,0.0,0.0,0.0]
	clone_dist_level_3 = [0.0,0.0,0.0,0.0]
	index = 0
	for child in list:
		if clone_total_level_2[index%4] > clone_total_level_3[index%4]+2.0:
			clone_total_level_3[index%4]+=1.0
		elif clone_total_level_1[index%4] > clone_total_level_2[index%4]+2.0:
			clone_total_level_2[index%4]+=1.0
		else:
			clone_total_level_1[index%4]+=1.0
		index += 1
	#print "clone total        level 1:",clone_total_level_1,"         level 2:",clone_total_level_2,"         level 3:",clone_total_level_3
	distance_level_1 = [110 + 30*(clone_total_level_1[0]),110 + 30*(clone_total_level_1[1]),110 + 30*(clone_total_level_1[2]),110 + 30*(clone_total_level_1[3])]
	distance_level_2 = [110 + 30*(clone_total_level_2[0]),110 + 30*(clone_total_level_2[1]),110 + 30*(clone_total_level_2[2]),110 + 30*(clone_total_level_2[3])]
	distance_level_3 = [110 + 30*(clone_total_level_3[0]),110 + 30*(clone_total_level_3[1]),110 + 30*(clone_total_level_3[2]),110 + 30*(clone_total_level_3[3])]
	index = 0
	#print "list"
	for child in list:
		clone = child
		#clone.collideNone()
		clone.depthFunc(viz.GL_ALWAYS)
		clone.drawOrder(3)
		obj_position = []
			
		x,y = 0.5,0.5
		if index%4 == 0: # top
			#print "-------- TOP ---------"
			if clone_dist_level_2[0] > clone_dist_level_3[0]+2.0 and clone_total_level_3[0] > 1:
				x,y = 0.4+((clone_dist_level_3[0]/(clone_total_level_3[0]-1.0))*0.2),0.66
				clone_dist_level_3[0]+=1.0
				#print "if"
			elif clone_dist_level_2[0] > clone_dist_level_3[0]+2.0:
				x,y = 0.5,0.66
				clone_dist_level_3[0]+=1.0
				#print "elif"
			elif clone_dist_level_1[0] > clone_dist_level_2[0]+2.0 and clone_total_level_2[0] > 1:
				x,y = 0.3+((clone_dist_level_2[0]/(clone_total_level_2[0]-1.0))*0.4),0.78
				clone_dist_level_2[0]+=1.0
				#print "if"
			elif clone_dist_level_1[0] > clone_dist_level_2[0]+2.0:
				x,y = 0.5,0.78
				clone_dist_level_2[0]+=1.0
				#print "elif"
			elif clone_total_level_1[0] > 1:
				x,y = 0.2+((clone_dist_level_1[0]/(clone_total_level_1[0]-1.0))*0.6),0.9
				clone_dist_level_1[0]+=1.0
				#print "elif"
			else:
				x,y = 0.5,0.9
				clone_dist_level_1[0]+=1.0
				#print "else"
			#print "top      level 1:",clone_dist_level_1[0],"  level 2:",clone_dist_level_2[0]
		elif index%4 == 1: # bottom
			#print "-------- BOTTOM ---------"
			if clone_dist_level_2[1] > clone_dist_level_3[1]+2.0 and clone_total_level_3[1] > 1:
				x,y = 0.4+((clone_dist_level_3[1]/(clone_total_level_3[1]-1.0))*0.2),0.34
				clone_dist_level_3[1]+=1.0
				#print "if"
			elif clone_dist_level_2[1] > clone_dist_level_3[1]+2.0:
				x,y = 0.5,0.34
				clone_dist_level_3[1]+=1.0
				#print "if"
			elif clone_dist_level_1[1] > clone_dist_level_2[1]+2.0 and clone_total_level_2[1] > 1:
				x,y = 0.3+((clone_dist_level_2[1]/(clone_total_level_2[1]-1.0))*0.4),0.22
				clone_dist_level_2[1]+=1.0
				#print "if"
			elif clone_dist_level_1[1] > clone_dist_level_2[1]+2.0:
				x,y = 0.5,0.22
				clone_dist_level_2[1]+=1.0
				#print "if"
			elif clone_total_level_1[1] > 1:
				x,y = 0.2+((clone_dist_level_1[1]/(clone_total_level_1[1]-1.0))*0.6),0.1
				clone_dist_level_1[1]+=1.0
				#print "elif"
			else:
				x,y = 0.5,0.1
				clone_dist_level_1[1]+=1.0
				#print "else"
			#print "bottom   level 1:",clone_dist_level_1[1],"  level 2:",clone_dist_level_2[1]
		elif index%4 == 2: # left
			#print "-------- LEFT ---------"
			if clone_dist_level_2[2] > clone_dist_level_3[2]+2.0 and clone_total_level_3[2] > 1:
				x,y = 0.34,0.4+((clone_dist_level_3[2]/(clone_total_level_3[2]-1.0))*0.2)
				clone_dist_level_3[2]+=1.0
				#print "if"
			elif clone_dist_level_2[2] > clone_dist_level_3[2]+2.0:
				x,y = 0.34,0.5
				clone_dist_level_3[2]+=1.0
				#print "if"
			elif clone_dist_level_1[2] > clone_dist_level_2[2]+2.0 and clone_total_level_2[2] > 1:
				x,y = 0.22,0.3+((clone_dist_level_2[2]/(clone_total_level_2[2]-1.0))*0.4)
				clone_dist_level_2[2]+=1.0
				#print "if"
			elif clone_dist_level_1[2] > clone_dist_level_2[2]+2.0:
				x,y = 0.22,0.5
				clone_dist_level_2[2]+=1.0
				#print "if"
			elif clone_total_level_1[2] > 1:
				x,y = 0.1,0.2+((clone_dist_level_1[2]/(clone_total_level_1[2]-1.0))*0.6)
				clone_dist_level_1[2]+=1.0
				#print "elif"
			else:
				x,y = 0.1,0.5
				clone_dist_level_1[2]+=1.0
				#print "else"
			#print "left     level 1:",clone_dist_level_1[2],"  level 2:",clone_dist_level_2[2]
		else: # right
			#print "-------- RIGHT ---------"
			if clone_dist_level_2[3] > clone_dist_level_3[3]+2.0 and clone_total_level_3[3] > 1:
				x,y = 0.66,0.4+((clone_dist_level_3[3]/(clone_total_level_3[3]-1.0))*0.2)
				clone_dist_level_3[3]+=1.0
				#print "if"
			elif clone_dist_level_2[3] > clone_dist_level_3[3]+2.0:
				x,y = 0.66,0.5
				clone_dist_level_3[3]+=1.0
				#print "if"
			elif clone_dist_level_1[3] > clone_dist_level_2[3]+2.0 and clone_total_level_2[3] > 1:
				x,y = 0.78,0.3+((clone_dist_level_2[3]/(clone_total_level_2[3]-1.0))*0.4)
				clone_dist_level_2[3]+=1.0
				#print "if"
			elif clone_dist_level_1[3] > clone_dist_level_2[3]+2.0:
				x,y = 0.78,0.5
				clone_dist_level_2[3]+=1.0
				#print "if"
			elif clone_total_level_1[3] > 1:
				x,y = 0.9,0.2+((clone_dist_level_1[3]/(clone_total_level_1[3]-1.0))*0.6)
				clone_dist_level_1[3]+=1.0
				#print "elif"
			else:
				x,y = 0.9,0.5
				clone_dist_level_1[3]+=1.0
				#print "else"
			#print "right    level 1:",clone_dist_level_1[3],"  level 2:",clone_dist_level_2[3]
		#print index," ",x,y
		#print "index ",index,"   screentoworld at ",x,y
		#print "clone dist      level 1:",clone_dist_level_1,"of",clone_total_level_1,"     level 2:",clone_dist_level_2,"of",clone_total_level_2,"     level 3:",clone_dist_level_3,"of",clone_total_level_3
		line = viz.screentoworld(x,y)
		#print index," ",line.begin,"to",line.end,". Dir:",line.dir
		dir_vector = line.dir
		length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
		dir_vector[0] = (dir_vector[0]/length)#*1.3
		dir_vector[1] = (dir_vector[1]/length)#*1.3
		dir_vector[2] = (dir_vector[2]/length)#*1.3
		#print index,"  dir_vector[%.4f,"%((x*aspect)-aspect/2.0)+"%.4f"%y+"] =",dir_vector,"    length =",length
		#if index%4 == 0:
		#	print "going to",(user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4]
		clone.setMatrix(identity,viz.ABS_GLOBAL)		
		obj_position = clone.getBoundingBox(viz.ABS_GLOBAL).center
		#clone.parent(supermarket)
		curPos = clone.getPosition() #Save current position
		if clone_total_level_2[0] > 2 and clone_dist_level_2[0] > clone_dist_level_3[0]:
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_3[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_3[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_3[index%4], viz.ABS_GLOBAL)
		elif clone_total_level_1[0] > 2 and clone_dist_level_1[0] > clone_dist_level_2[0]:
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_2[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_2[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_2[index%4], viz.ABS_GLOBAL)
		else:
			clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance_level_1[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance_level_1[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance_level_1[index%4], viz.ABS_GLOBAL)
		gotoPos = clone.getPosition() #Get computed local pos
		clone.setPosition(curPos) #Restore position
		#clone.runAction(vizact.goto(gotoPos,.25,viz.TIME))
		clone.setPosition(gotoPos)
		#clone.setPosition((user_position[0]-obj_position[0])+dir_vector[0]*distance[index%4],(user_position[1]-obj_position[1])+dir_vector[1]*distance[index%4],(user_position[2]-obj_position[2])+dir_vector[2]*distance[index%4])
		clone_list.append(clone)
		index+=1

# selectSQUADQuadrant()
# callback for selection of quadrants, called by the real callback that checks
# if the select button was pressed during the SELECTION mode or 
# SELECTION_QUADRANTS
def selectSQUADQuadrant():
	global mode
	global clone_list
	
	if len(clone_list) > 0:
		#print "selecting those items who are in",selected_quad
		#print "clone_list had",len(clone_list),"items"
		new_clone_list = []
		index = 0
		for clone in clone_list:
			if index%4 != selected_quad: 
				#print "removing index",index,"..."
				#clone.visible(viz.OFF)
				clone.endAction(viz.ALL_POOLS)
				#clone.setPosition(0,0,0,viz.ABS_GLOBAL)
				clone.setMatrix(identity,viz.ABS_GLOBAL)
				clone.depthFunc(viz.GL_LESS)
				clone.drawOrder(0)
				#print len(clone_list)
			else:
				new_clone_list.append(clone)
			index+=1
		#print "now clone_list has",len(new_clone_list),"items"
		if len(new_clone_list) > 1:
			#print "more than 1 left..."
			createSQUADQuadrants(new_clone_list,1)
		else:
			viz.phys.enable()
			if len(new_clone_list) == 1 and mode == InteractionMode.SELECTION_QUADRANTS:
				#print "adding",new_clone_list[0]
				for i in intersectingObjects:
					if new_clone_list[0] == i:
						intersectingObjects.remove(i)
						break
				resetSQUADMenu()
				mode = InteractionMode.SELECTION
			else:
				mode = InteractionMode.SELECTION
	else:
		mode = InteractionMode.SELECTION

# updateSQUADQuadrants()
# updates rendering of the quadrants and the objects in the quadrants
def updateSQUADQuadrants():
	global clone_list
	global selected_quad
	
	x,y = float(centroid[0])/float(windowSize[0]), float(centroid[1])/float(windowSize[1])
	
	if y >= 0.5 and x >= (0.5-(y-0.5)) and x <= (0.5+(y-0.5)):
		quad_tri.color([0.2,0.6,1],'top')
		selected_quad = Quadrant.TOP
	else:
		quad_tri.color([1,1,1],'top')
	if y < 0.5 and x >= (0.5-((1.0-y)-0.5)) and x <= (0.5+((1.0-y)-0.5)):
		quad_tri.color([0.2,0.6,1],'bottom')
		selected_quad = Quadrant.BOTTOM
	else:
		quad_tri.color([1,1,1],'bottom')
	if x < 0.5 and y >= (0.5-((1.0-x)-0.5)) and y <= (0.5+((1.0-x)-0.5)):
		quad_tri.color([0.2,0.6,1],'left')
		selected_quad = Quadrant.LEFT
	else:
		quad_tri.color([1,1,1],'left')
	if x >= 0.5 and y >= (0.5-(x-0.5)) and y <= (0.5+(x-0.5)):
		quad_tri.color([0.2,0.6,1],'right')
		selected_quad = Quadrant.RIGHT
	else:
		quad_tri.color([1,1,1],'right')
	
	user_position = viz.MainView.getPosition(viz.ABS_GLOBAL)
	
	for item in clone_list:
		if item.getAction() == None:
			oldposition = item.getBoundingBox(viz.ABS_GLOBAL).center
			screenposition = viz.MainWindow.worldToScreen(oldposition, eye = viz.BOTH_EYE, mode = viz.WINDOW_NORMALIZED)
			distance = math.sqrt(math.pow((user_position[0]-oldposition[0]),2)+math.pow((user_position[1]-oldposition[1]),2)+math.pow((user_position[2]-oldposition[2]),2))
			item.setMatrix(identity,viz.ABS_GLOBAL)
			item.setAxisAngle(-.5,1,0,rotQUAD,viz.ABS_GLOBAL)
			center = item.getBoundingBox(viz.ABS_GLOBAL).center
			#print "screen position:",screenposition
			line = viz.screentoworld(screenposition[0],screenposition[1])
			#distance = screenposition[2]
			dir_vector = line.dir
			length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
			dir_vector[0] = (dir_vector[0]/length)
			dir_vector[1] = (dir_vector[1]/length)
			dir_vector[2] = (dir_vector[2]/length)
			point = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
			item.setPosition(point[0]-center[0],point[1]-center[1],point[2]-center[2],viz.ABS_GLOBAL)

# resetSQUADMenu()
# resets SQUAD quadrants
def resetSQUADMenu():
	global mode
	global clone_list
	
	if mode == InteractionMode.SELECTION_QUADRANTS:
		for clone in clone_list:
			#print "removing index",index,"..."
			#clone.visible(viz.OFF)
			clone.endAction(viz.ALL_POOLS)
			clone.setMatrix(identity,viz.ABS_GLOBAL)
			clone.depthFunc(viz.GL_LESS)
			clone.drawOrder(0)
			#print len(clone_list)
		clone_list = []
	
	mode = InteractionMode.SELECTION

# resetObjects()
# resets objects to their original positions
def resetObjects():
	global children
	global supermarket
	
	index = 0
	
	for child in children:
		obj_size = object_size[index]#child.getBoundingBox(viz.ABS_GLOBAL).size
		#print child,": ",obj_size
		if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
			parents = child.getParents()
			for parent in parents:
				if parent != supermarket:
					child.unparent(parent)
					child.parent(supermarket)
					break
			child.setMatrix(identity,viz.ABS_GLOBAL)
			object_position[index] = child.getBoundingSphere(viz.ABS_GLOBAL).center
		index += 1

# createZoomQuad()
# creates the quad used by the discrete zoom techniques based on cursor position
def createZoomQuad(zoomFactor):
	global aspectRatio
	
	texQuad = viz.addTexQuad(viz.SCREEN)
	#texQuad.setPosition(0.25,0.75)
	texQuad.setScale(5.115*1.25*2.0/zoomFactor,5.115*2.0/zoomFactor,1)
	texQuad.color([0.2,0.6,1])
	texQuad.alpha(0.3)
	#texQuad.setPosition(0.5,0.5)
	
	return texQuad

# createQuadrantsZoom()
# creates the quadrants of the discrete zoom technique
def createQuadrantsZoom():
	global aspectRatio
	
	quadrants = []
	
	# quadrants
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
	
	# lines
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

# colorQuadrants()
# changes the color of the quadrants based on the cursor position
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
# pointer functions
#-------------------------------------------------------------------------------
# resetBoundingBoxes()
# reset the zoom variable
def resetBoundingBoxes():
	global boundingBoxes
	
	for bb in boundingBoxes:
		bb.remove()
	boundingBoxes = []

# drawIntersectObjsBoundingBoxes()
# creates the bounding boxes of all objects that are inside the sphere, independent of its size
def drawIntersectObjsBoundingBoxes():
	global boundingBoxes
	
	resetBoundingBoxes()
	
	for object in intersectingObjects:
		aux_bb = object.getBoundingBox(viz.ABS_GLOBAL)
		min,max = [aux_bb.xmin,aux_bb.ymin,aux_bb.zmin],[aux_bb.xmax,aux_bb.ymax,aux_bb.zmax]
		bb = createBoundingBox(min,max)
		boundingBoxes.append(bb)

# updateWindowDimensionsDiscrete()
# updates zoom window position and dimensions for the zoom animation
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

# updateWindowDimensionsContinuous()
# updates zoom window position and dimensions for the zoom animation
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
		if buttonState[0] == True and zoomingLevel < 128.0:
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

# updateWindowDimensionsCombined()
# updates zoom window position and dimensions for the zoom animation
def updateWindowDimensionsCombined(animationState):
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
	global animationCurrentWindow
	
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
	
	
	animationCurrentWindow = [[(1 - animationState) * previousWindow[0][0] + animationState * currentWindow[0][0],
							   (1 - animationState) * previousWindow[0][1] + animationState * currentWindow[0][1]],
							  [(1 - animationState) * previousWindow[1][0] + animationState * currentWindow[1][0],
							   (1 - animationState) * previousWindow[1][1] + animationState * currentWindow[1][1]]]

# updateFrustum()
# updates the frustum based on the zoom window dimensions and position
def updateFrustum(animationState = 1.0):
	global windowSize
	global VFOV
	global currentWindow
	global previousWindow
	
	if Globals.technique == InteractionTechnique.ContinuousZoom:
		updateWindowDimensionsContinuous(animationState)
	elif Globals.technique == InteractionTechnique.DiscreteZoom:
		updateWindowDimensionsDiscrete(animationState)
	elif Globals.technique == InteractionTechnique.CombinedZoomv1:
		updateWindowDimensionsCombined(animationState)
	elif Globals.technique == InteractionTechnique.CombinedZoomv2:
		updateWindowDimensionsCombined(animationState)
	elif Globals.technique == InteractionTechnique.CombinedZoomv3:
		updateWindowDimensionsCombined(animationState)
	elif Globals.technique == InteractionTechnique.CombinedZoomv4:
		updateWindowDimensionsCombined(animationState)
	
	# calculate frustum
	cameraNear = 0.1
	cameraFar  = 1000.0
	ratio = windowSize[0]/windowSize[1]
	yfov = 2.0 * math.atan( math.tan( (defaultHFOV/57.2957795) / 2.0 ) / aspectRatio ) * 57.2957795;
	ymax = cameraNear*math.tan(yfov*math.pi/360.0)
	ymin = -ymax
	xmax = ymax*ratio
	xmin = ymin*ratio
	
	# previous window frustm
	pxmin = -((previousWindow[0][0]/windowSize[0]) * (xmin * 2.0) - xmin)
	pxmax = (previousWindow[1][0]/windowSize[0]) * (xmax * 2.0) - xmax
	pymin = -((previousWindow[0][1]/windowSize[1]) * (ymin * 2.0) - ymin)
	pymax = (previousWindow[1][1]/windowSize[1]) * (ymax * 2.0) - ymax
	
	# current window frustum
	cxmin = -((currentWindow[0][0]/windowSize[0]) * (xmin * 2.0) - xmin)
	cxmax = (currentWindow[1][0]/windowSize[0]) * (xmax * 2.0) - xmax
	cymin = -((currentWindow[0][1]/windowSize[1]) * (ymin * 2.0) - ymin)
	cymax = (currentWindow[1][1]/windowSize[1]) * (ymax * 2.0) - ymax
	
	# final frustum - linear interpolation
	xmin = (1 - animationState) * pxmin + animationState * cxmin
	xmax = (1 - animationState) * pxmax + animationState * cxmax
	ymin = (1 - animationState) * pymin + animationState * cymin
	ymax = (1 - animationState) * pymax + animationState * cymax
	viz.MainWindow.frustum(xmin,xmax,ymin,ymax,cameraNear,cameraFar)

# cursorOverQuadrant()
# returns the center of the zoom window quadrant being currently highlighted 
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

# calculateDiscreteCursorOffset()
# returns the origin position of the quadrant window
def calculateDiscreteCursorOffset(level):
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

# zoomInButton()
# callback for the zoom in button
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
	if Globals.technique == InteractionTechnique.DiscreteZoom:
		#print "discrete zoom"
		if zoomingLevel*2 > 128.0:
			lastZoomingLevel = zoomingLevel
			zoomingLevel = 128.0
			zoomingAnimation = 0
		else:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME)
			if zoomingLevel == 1:
				previousCenterOffset = [0,0]
			selectedQuadrant = cursorOverQuadrant()
			zoomingStack.append(newCenterOffset)
			newCenterOffset = calculateDiscreteCursorOffset(zoomingLevel)
			zooming = True
			zoomingAnimation = 1 # zoom in
			zoomingCount = 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel *= 2
	elif Globals.technique == InteractionTechnique.ContinuousZoom:
		#print "continuous zoom - iteration",zoomingCount
		if zoomingLevel < 128.0:
			if zoomingCount > 0.0:
				zoomingCount += 1.0 - math.sqrt(zoomingCount*0.01)
			else:
				zoomingCount += 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * 127.0
	elif Globals.technique == InteractionTechnique.CombinedZoomv1:
		#print "combined zoom"
		if zoomingLevel*2.0 > 128.0:
			lastZoomingLevel = zoomingLevel
			#zoomingLevel = 128.0
			zoomingAnimation = 0
		else:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME_COMBINED)
			if zoomingLevel == 1:
				previousCenterOffset = [0,0]
			zoomingStack.append(newCenterOffset)
			x,y = centroid[0],centroid[1]
			newCenterOffset = [previousCenterOffset[0]+(x*windowSize[0]/(zoomingLevel*2.0))/windowSize[0], 
							   previousCenterOffset[1]+(y*windowSize[1]/(zoomingLevel*2.0))/windowSize[1]]
			zooming = True
			zoomingAnimation = 1 # zoom in
			zoomingCount = 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel *= 2.0
	elif Globals.technique == InteractionTechnique.CombinedZoomv2:
		#print "combined zoom"
		if zoomingLevel*2.0 > 128.0:
			lastZoomingLevel = zoomingLevel
			#zoomingLevel = 128.0
			zoomingAnimation = 0
		else:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME_COMBINED)
			if zoomingLevel == 1:
				previousCenterOffset = [0,0]
			zoomingStack.append(newCenterOffset)
			x,y = centroid[0],centroid[1]
			newCenterOffset = [0,0]
			if x < float(windowSize[0])/4.0:
				newCenterOffset[0] = previousCenterOffset[0]
			elif x > windowSize[0]-float(windowSize[0])/4.0:
				newCenterOffset[0] = previousCenterOffset[0]+(float(windowSize[0])/(zoomingLevel*2.0))
			else:
				newCenterOffset[0] = previousCenterOffset[0]+(float(x)/zoomingLevel)-(float(windowSize[0])/(zoomingLevel*4.0))
				
			if y < float(windowSize[1])/4.0:
				newCenterOffset[1] = previousCenterOffset[1]
			elif y > windowSize[1]-float(windowSize[1])/4.0:
				newCenterOffset[1] = previousCenterOffset[1]+(float(windowSize[1])/(zoomingLevel*2.0))
			else:
				newCenterOffset[1] = previousCenterOffset[1]+(float(y)/zoomingLevel)-(float(windowSize[1])/(zoomingLevel*4.0))
			
			zooming = True
			zoomingAnimation = 1 # zoom in
			zoomingCount = 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel *= 2.0
	elif Globals.technique == InteractionTechnique.CombinedZoomv3:
		#print "combined zoom"
		if zoomingLevel*2.0 > 128.0:
			lastZoomingLevel = zoomingLevel
			#zoomingLevel = 128.0
			zoomingAnimation = 0
		else:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME_COMBINED)
			if zoomingLevel == 1:
				previousCenterOffset = [0,0]
			zoomingStack.append(newCenterOffset)
			x,y = centroid[0],centroid[1]
			newCenterOffset = [0,0]
			newCenterOffset[0] = previousCenterOffset[0]+(float(x)/zoomingLevel)-(float(windowSize[0])/(zoomingLevel*4.0))
			newCenterOffset[1] = previousCenterOffset[1]+(float(y)/zoomingLevel)-(float(windowSize[1])/(zoomingLevel*4.0))
			
			zooming = True
			zoomingAnimation = 1 # zoom in
			zoomingCount = 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel *= 2.0
	elif Globals.technique == InteractionTechnique.CombinedZoomv4:
		#print "combined zoom"
		if zoomingLevel*2.0 > 128.0:
			lastZoomingLevel = zoomingLevel
			#zoomingLevel = 128.0
			zoomingAnimation = 0
		else:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME_COMBINED)
			if zoomingLevel == 1:
				previousCenterOffset = [0,0]
			zoomingStack.append(newCenterOffset)
			x,y = centroid[0],centroid[1]
			newCenterOffset = [previousCenterOffset[0]+(x*windowSize[0]/(zoomingLevel*2.0))/windowSize[0], 
							   previousCenterOffset[1]+(y*windowSize[1]/(zoomingLevel*2.0))/windowSize[1]]
			zooming = True
			zoomingAnimation = 1 # zoom in
			zoomingCount = 1.0
			lastZoomingLevel = zoomingLevel
			zoomingLevel *= 2.0

# zoomOutButton()
# callback for the zoom out button
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
	if Globals.technique == InteractionTechnique.DiscreteZoom:
		#print "discrete zoom cancel"
		if zoomingLevel > 1:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME)
			zoomingLevel /= 2
			zooming = True
			zoomingAnimation = 2 # zoom out
			zoomingCount = 1.0
			previousCenterOffset = newCenterOffset
			newCenterOffset = zoomingStack.pop()
	elif Globals.technique == InteractionTechnique.ContinuousZoom:
		#print "continuous zoom - iteration",zoomingCount
		if zoomingCount > 0.0:
			zoomingCount -= .5
			lastZoomingLevel = zoomingLevel
			zoomingLevel = 1.0 + (zoomingCount / (VFOV-minFOV)) * 127.0
	elif Globals.technique == InteractionTechnique.CombinedZoomv1:
		#print "combined zoom cancel"
		if zoomingLevel > 1:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME)
			zoomingLevel /= 2.0
			zooming = True
			zoomingAnimation = 2 # zoom out
			zoomingCount = 1.0
			previousCenterOffset = newCenterOffset
			newCenterOffset = zoomingStack.pop()
	elif Globals.technique == InteractionTechnique.CombinedZoomv2:
		#print "combined zoom cancel"
		if zoomingLevel > 1:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME)
			zoomingLevel /= 2.0
			zooming = True
			zoomingAnimation = 2 # zoom out
			zoomingCount = 1.0
			previousCenterOffset = newCenterOffset
			newCenterOffset = zoomingStack.pop()
	elif Globals.technique == InteractionTechnique.CombinedZoomv3:
		#print "combined zoom cancel"
		if zoomingLevel > 1:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME)
			zoomingLevel /= 2.0
			zooming = True
			zoomingAnimation = 2 # zoom out
			zoomingCount = 1.0
			previousCenterOffset = newCenterOffset
			newCenterOffset = zoomingStack.pop()
	elif Globals.technique == InteractionTechnique.CombinedZoomv4:
		#print "combined zoom cancel"
		if zoomingLevel > 1:
			totalAnimationFrames = (60*Navigation.TOTAL_ANIMATION_TIME)
			zoomingLevel /= 2.0
			zooming = True
			zoomingAnimation = 2 # zoom out
			zoomingCount = 1.0
			previousCenterOffset = newCenterOffset
			newCenterOffset = zoomingStack.pop()

# selectButton()
# callback for the selection button
def selectButton():
	global zooming
	global zoomingCount
	global zoomingLevel
	global buttonState
	global zoomingStack
	global lastZoomingCount
	global mode
	
	if Globals.technique != InteractionTechnique.SQUAD and Globals.technique != InteractionTechnique.Raycasting:
		lastZoomingCount = 0
		zooming = False
		zoomingLevel = 1.0
		zoomingCount = 0.0
		zoomingStack = []
	if Globals.technique == InteractionTechnique.SQUAD:
		if mode == InteractionMode.SELECTION and len(intersectingObjects) > 0:
			createSQUADQuadrants(intersectingObjects)
			mode = InteractionMode.SELECTION_QUADRANTS
		elif mode == InteractionMode.SELECTION_QUADRANTS:
			selectSQUADQuadrant()

# resetZoom()
# reset the zoom variable
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

# updateTechniqueLabel()
# updates the technique label when changing techniques
def updateTechniqueLabel():
	global techniqueBG
	
	if Globals.technique == InteractionTechnique.ContinuousZoom:
		techniqueLabel.message("Continuous Zoom")
	elif Globals.technique == InteractionTechnique.DiscreteZoom:
		techniqueLabel.message("Discrete Zoom - quadrant-based")
	elif Globals.technique == InteractionTechnique.CombinedZoomv1:
		techniqueLabel.message("Discrete Zoom - cursor-based v1")
	elif Globals.technique == InteractionTechnique.CombinedZoomv2:
		techniqueLabel.message("Discrete Zoom - cursor-based v2")
	elif Globals.technique == InteractionTechnique.CombinedZoomv3:
		techniqueLabel.message("Discrete Zoom - cursor-based v3")
	elif Globals.technique == InteractionTechnique.CombinedZoomv4:
		techniqueLabel.message("Discrete Zoom - cursor-based v4")
	elif Globals.technique == InteractionTechnique.Raycasting:
		techniqueLabel.message("Ray-casting")
	elif Globals.technique == InteractionTechnique.SQUAD:
		techniqueLabel.message("SQUAD")
	
	if techniqueBG != None:
		techniqueBG.remove()
		techniqueBG = None
	
	techniqueLabel.clearActions()
	techniqueLabel.alpha(1.0)
	
	user_position = viz.MainView.getPosition()
	techniqueBG = createQuad([0,0,0],[0,0,0],[0,0,0],[0,0,0])
	distance = 10
	
	line = viz.screentoworld(0.0,1.0)
	dir_vector = line.dir
	length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
	dir_vector = (dir_vector[0]/length),(dir_vector[1]/length),(dir_vector[2]/length)
	left_top = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
	
	line = viz.screentoworld(0.0,0.95)
	dir_vector = line.dir
	length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
	dir_vector = (dir_vector[0]/length),(dir_vector[1]/length),(dir_vector[2]/length)
	left_bot = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
	
	line = viz.screentoworld(1.0,1.0)
	dir_vector = line.dir
	length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
	dir_vector = (dir_vector[0]/length),(dir_vector[1]/length),(dir_vector[2]/length)
	right_top = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
	
	line = viz.screentoworld(1.0,0.95)
	dir_vector = line.dir
	length = math.sqrt(dir_vector[0]*dir_vector[0] + dir_vector[1]*dir_vector[1] + dir_vector[2]*dir_vector[2])
	dir_vector = (dir_vector[0]/length),(dir_vector[1]/length),(dir_vector[2]/length)
	right_bot = [user_position[0]+dir_vector[0]*distance,user_position[1]+dir_vector[1]*distance,user_position[2]+dir_vector[2]*distance]
	
	techniqueBG.setVertex(0, left_top)
	techniqueBG.setVertex(1, left_bot)
	techniqueBG.setVertex(2, right_bot)
	techniqueBG.setVertex(3, right_top)	
	techniqueBG.color(0.0,0.0,0.0)
	techniqueBG.alpha(0.7)
	
	techniqueBG.addAction(vizact.fadeTo(0,time=2))
	techniqueLabel.addAction(vizact.fadeTo(0,time=2))

# cycleTechniqueForward()
# changes to the next technique
def cycleTechniqueForward():
	Globals.technique += 1
	if Globals.technique == InteractionTechnique.size:
		Globals.technique = 0
		
	resetZoom()
	resetSQUADMenu()
	resetObjects()
	resetBoundingBoxes()
	updateTechniqueLabel()

# cycleTechniqueBackward()
# changes to the previous technique
def cycleTechniqueBackward():
	Globals.technique -= 1
	if Globals.technique < 0:
		Globals.technique = InteractionTechnique.size-1
		
	resetZoom()
	resetSQUADMenu()
	resetObjects()
	resetBoundingBoxes()
	updateTechniqueLabel()

# keyDown()
# keyboard, key pressed callback
def keyDown(whichKey):
	global mode
	global clone_list
	global hideMenu

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
		
	if whichKey == 't' or whichKey == 'T':
		cycleTechniqueForward()
		
	if whichKey == '+':
		Navigation.TOTAL_ANIMATION_TIME_COMBINED +=0.05
		print "Zoom animation duration changed:",Navigation.TOTAL_ANIMATION_TIME_COMBINED
	if whichKey == '-':
		Navigation.TOTAL_ANIMATION_TIME_COMBINED -=0.05
		print "Zoom animation duration changed:",Navigation.TOTAL_ANIMATION_TIME_COMBINED
		
	if whichKey == 'h' or whichKey == 'H':
		hideMenu = not hideMenu
	
# keyUp()
# keyboard, key released callback
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

# updateIS900Data()
# callback for the is900
def updateIS900Data():
	global old_data
	global all_data
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
	global mode
	
	old_data = all_data
	joystick = is900Sensor.getData()
	all_data = [is900Sensor.buttonState(),joystick[0],joystick[1]]
	
	# use callbacks for every button...
	
	if is900Sensor:
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
			selectButton()
			buttonState[2] = True
		elif old_state & 32 and not(state & 32):
			buttonState[2] = False
		
		# joystick
		if (old_data[2] <= 230 and all_data[2] > 230) or (all_data[2] > 230 and Globals.technique == InteractionTechnique.ContinuousZoom):
			#print 'joystick up pressed'
			if Globals.technique == InteractionTechnique.ContinuousZoom:
				zoomInButton()
			buttonState[0] = True		
		elif old_data[2] > 230 and all_data[2] <= 230:
			#print 'joystick up released'
			if zoomingAnimation == 0:
				if Globals.technique == InteractionTechnique.DiscreteZoom or Globals.technique == InteractionTechnique.CombinedZoomv1 or Globals.technique == InteractionTechnique.CombinedZoomv2 or Globals.technique == InteractionTechnique.CombinedZoomv3:
					zoomInButton()
			buttonState[0] = False
			if Globals.technique == InteractionTechnique.ContinuousZoom:
				previousWindow = animationCurrentWindow
				#print animationCurrentWindow,"==",previousWindow	
		elif all_data[2] > 230 and zoomingAnimation == 0 and Globals.technique == InteractionTechnique.CombinedZoomv4:
			zoomInButton()
		elif (old_data[2] > 25 and all_data[2] <= 25) or (all_data[2] <= 25 and Globals.technique == InteractionTechnique.ContinuousZoom):
			#print 'joystick down pressed'
			if Globals.technique == InteractionTechnique.ContinuousZoom:
				if old_data[2] > 25 and all_data[2] <= 25:
					currentWindow = animationCurrentWindow
				previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
				zoomOutButton()	
			buttonState[1] = True
		elif old_data[2] <= 25 and all_data[2] > 25:
			#print 'joystick down released'
			zoomOutButton()
			buttonState[1] = False
			if Globals.technique == InteractionTechnique.ContinuousZoom:
				previousWindow = animationCurrentWindow
				#print animationCurrentWindow,"==",previousWindow
		elif all_data[2] <= 25 and zoomingAnimation == 0 and Globals.technique == InteractionTechnique.CombinedZoomv4:
			zoomOutButton()
			
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
			newEuler = filter.Apply(vector3(is900Euler[0],is900Euler[1],is900Euler[2]),fps)
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

# updateMouseData()
# callback for the mouse
# if not using the IS900, we use this
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
	global mode
	
	# Get current mouse button state
	
	state = viz.mouse.getState()
	oldMouseState = mouseState
	mouseState = state

	# Check which buttons are currently pressed
	if (not (oldMouseState & viz.MOUSEBUTTON_LEFT) and mouseState & viz.MOUSEBUTTON_LEFT) or (mouseState & viz.MOUSEBUTTON_LEFT and Globals.technique == InteractionTechnique.ContinuousZoom):
		#print 'left button down'
		if Globals.technique == InteractionTechnique.ContinuousZoom:
			zoomInButton()
		elif Globals.technique == InteractionTechnique.CombinedZoomv4 and zoomingAnimation == 0:
			zoomInButton()
		buttonState[0] = True
	elif oldMouseState & viz.MOUSEBUTTON_LEFT and not (mouseState & viz.MOUSEBUTTON_LEFT):
		#print 'left button up'
		if zoomingAnimation == 0:
			if Globals.technique == InteractionTechnique.DiscreteZoom or Globals.technique == InteractionTechnique.CombinedZoomv1 or Globals.technique == InteractionTechnique.CombinedZoomv2 or Globals.technique == InteractionTechnique.CombinedZoomv3:
				zoomInButton()
		buttonState[0] = False
		if Globals.technique == InteractionTechnique.ContinuousZoom:
			previousWindow = animationCurrentWindow
	elif mouseState & viz.MOUSEBUTTON_LEFT and zoomingAnimation == 0 and Globals.technique == InteractionTechnique.CombinedZoomv4:
		zoomInButton()
		
	elif (not (oldMouseState & viz.MOUSEBUTTON_MIDDLE) and mouseState & viz.MOUSEBUTTON_MIDDLE) or (mouseState & viz.MOUSEBUTTON_MIDDLE and Globals.technique == InteractionTechnique.ContinuousZoom):
		#print 'middle button down'	
		if Globals.technique == InteractionTechnique.ContinuousZoom:
			if not (oldMouseState & viz.MOUSEBUTTON_MIDDLE) and mouseState & viz.MOUSEBUTTON_MIDDLE:
				currentWindow = animationCurrentWindow
			previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
			zoomOutButton()	
		buttonState[1] = True
	elif oldMouseState & viz.MOUSEBUTTON_MIDDLE and not (mouseState & viz.MOUSEBUTTON_MIDDLE):
		#print 'middle button up'	
		zoomOutButton()
		buttonState[1] = False
		if Globals.technique == InteractionTechnique.ContinuousZoom:
			previousWindow = animationCurrentWindow
	elif mouseState & viz.MOUSEBUTTON_MIDDLE and zoomingAnimation == 0 and Globals.technique == InteractionTechnique.CombinedZoomv4:
		zoomOutButton()
		
	if not (oldMouseState & viz.MOUSEBUTTON_RIGHT) and mouseState & viz.MOUSEBUTTON_RIGHT:
		#print 'right button down' 
		selectButton()
		buttonState[2] = True
	elif oldMouseState & viz.MOUSEBUTTON_RIGHT and not (mouseState & viz.MOUSEBUTTON_RIGHT):
		#print 'right button up' 	
		buttonState[2] = False
		
	# Get mouse position in pixel coordinates
	centroid = viz.mouse.getPosition(viz.WINDOW_PIXELS) 

# updateSQUADCursor()
# main update function for squad, needs to be called every frame/every time the cursor is updated
def updateSQUADCursor():
	global rotQUAD
	global scSphereRadius
	global intersecting
	global mode
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	user_position = viz.MainView.getMatrix(viz.ABS_GLOBAL)
	aspect = (viz.getWindowList())[0].getAspectRatio()
	
	#print "User Position:", user_position[12], user_position[13], user_position[14]
	#print "orientation:",viz.MainView.getEuler()
	
	#print "width: ", aspect, "  height: ", 1.0
	#line = viz.screentoworld(x*aspect-(aspect-1.0)/2.0,(1.0-y))
	
	rotQUAD += 1
	if rotQUAD == 360:
		rotQUAD = 1
		
	if mode == InteractionMode.SELECTION:
		quad_lin.visible(viz.OFF)
		quad_tri.visible(viz.OFF)
		scSphere.visible(viz.ON)
		crosshair.visible(viz.OFF)
		
		line = viz.screentoworld([x,y],mode = viz.WINDOW_PIXELS)
		begin = line[:3]
		end = line[3:]
		
		all_info = viz.intersect(begin,end,True)
		index = 0
		intersecting = False
		for info in all_info:
			if info.valid == True:
				#print 'Intersected with object id:', info.object.id 
				if info.object != scSphere:
					scSphere.setPosition(info.point,viz.ABS_GLOBAL)
					distance = math.sqrt(((info.point[0]-user_position[12])*(info.point[0]-user_position[12])) + ((info.point[1]-user_position[13])*(info.point[1]-user_position[13])) + ((info.point[2]-user_position[14])*(info.point[2]-user_position[14])))
					scSphereRadius = 5.0+distance/50.0
					scSphere.setScale(scSphereRadius,scSphereRadius,scSphereRadius)
					#print index," distance:", distance, " sphere radius:", scSphereRadius
					intersecting = True
					break
				#else:
				#	print index," colliding with sphere"
			index += 1
		
		if intersecting == True:
			scSphere.visible(viz.ON)
		else:
			scSphere.visible(viz.OFF)
		
		intersectingObjects = []
		
		if intersecting == True:
			is_position = scSphere.getPosition(viz.ABS_GLOBAL)
			
			index = 0
			for child in children:
				obj_size = object_size[index]#child.getBoundingBox(viz.ABS_GLOBAL).size
				#print child,": ",obj_size
				if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
					obj_pos = object_position[index]
					distance = math.sqrt((obj_pos[0]-is_position[0])*(obj_pos[0]-is_position[0])+
										 (obj_pos[1]-is_position[1])*(obj_pos[1]-is_position[1])+
										 (obj_pos[2]-is_position[2])*(obj_pos[2]-is_position[2]))
					
					#if viz.MainWindow.isCulled(child) == 0: 
					if distance < scSphereRadius*1.2:
						intersectingObjects.append(child)
				index+=1

		drawIntersectObjsBoundingBoxes()
		
	elif mode == InteractionMode.SELECTION_QUADRANTS:
		quad_lin.setMatrix(user_position, viz.ABS_GLOBAL)
		quad_lin.setPosition([0,0,50], viz.REL_LOCAL)
		quad_lin.setScale(aspect,1,1)
		quad_lin.visible(viz.ON)
		quad_tri.setMatrix(user_position, viz.ABS_GLOBAL)
		quad_tri.setPosition([0,0,50], viz.REL_LOCAL)
		quad_tri.setScale(aspect,1,1)
		quad_tri.visible(viz.ON)
		
		crosshair.visible(viz.ON)
		scSphere.visible(viz.OFF)
		
		crosshair.setPosition(x/windowSize[0],y/windowSize[1],0)
		
		updateSQUADQuadrants()

# updateRayCasting()
# main update function for ray-casting, needs to be called every frame/every time the cursor is updated
def updateRayCasting(x,y):
	global intersectingObjects
	
	crosshair.visible(viz.ON)
	scSphere.visible(viz.OFF)
	
	obj = viz.pick(pos = [x,y])
	if obj.valid():
		obj_size = obj.getBoundingBox(viz.ABS_GLOBAL).size
		#print intersectObj,": ",obj_size
		if obj_size[0] < 40 and obj_size[1] < 40 and obj_size[2] < 40:
			intersectingObjects = []
			intersectingObjects.append(obj)
			drawIntersectObjsBoundingBoxes()
		else:
			intersectingObjects = []
			resetBoundingBoxes()
	else:
		intersectingObjects = []
		resetBoundingBoxes()
	
	crosshair.setPosition(x,y,0)

# updateContinuousCursor()
# main update function for the continuous zoom technique, needs to be called every frame/every time the cursor is updated
def updateContinuousCursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
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
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	global zoomPreview
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	updateRayCasting(x/windowSize[0],y/windowSize[1])
	
	if zooming == True:
		previousCenterOffset = [0,0]
		if buttonState[0]:
			print "zoom in button pressed"
			if zoomingLevel < 128.0:
				#print "setting new center offset"
				newCenterOffset = [(animationCurrentWindow[0][0]+x * ((animationCurrentWindow[1][0]-animationCurrentWindow[0][0]) / windowSize[0])), 
								   (animationCurrentWindow[0][1]+y * ((animationCurrentWindow[1][1]-animationCurrentWindow[0][1]) / windowSize[1]))]
				#print " ",newCenterOffset
				#print " ",zoomingLevel
			if VFOV-minFOV-lastZoomingCount == 0:
				updateFrustum(0.0)
			else:
				updateFrustum((zoomingCount-lastZoomingCount)/(VFOV-minFOV-lastZoomingCount))
		elif buttonState[1]:
			print "zoom out button pressed"
			if lastZoomingCount != 0:
				updateFrustum(zoomingCount/lastZoomingCount)
			else:
				updateFrustum(0.0)
		else:
			print "zoom button released"
			updateFrustum(0.0)
			lastZoomingCount = zoomingCount
	else:
		updateFrustum()

# updateDiscreteCursor()
# main update function for the discrete zoom technique, needs to be called every frame/every time the cursor is updated
def updateDiscreteCursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
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
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	global zoomPreview
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	updateRayCasting(x/windowSize[0],y/windowSize[1])
	
	if zoomingAnimation == 0:
		showMenu = True
	else:
		showMenu = False
	
	# quadrants calculation
	cursor = cursorOverQuadrant()
	
	matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
	
	#quadrants.setMatrix(matrix, viz.ABS_GLOBAL)
	#quadrants.setPosition([0,0,50], viz.REL_LOCAL)
	
	if zoomingAnimation != 0:
		#calculate the direction vector based on the selected quadrant
		x,y = previousCenterOffset[0]+selectedQuadrant[0],previousCenterOffset[1]+selectedQuadrant[1]
		#print x,y
		
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
		updateFrustum()
	
	
	if showMenu == True and hideMenu == False:
		if Globals.technique == InteractionTechnique.DiscreteZoom:
			for quad in quadrants:
				quad.visible(viz.ON)
			#quadrants.visible(viz.ON)	
			colorQuadrants()
	
	if zooming == False:
		updateFrustum()

# updateCombinedv1Cursor()
# main update function for the combined zoom technique, needs to be called every frame/every time the cursor is updated
def updateCombinedv1Cursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
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
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	global zoomPreview
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	updateRayCasting(x/windowSize[0],y/windowSize[1])
	
	if zoomingAnimation == 0:
		showMenu = True
	else:
		showMenu = False

	if zoomingLevel < 128.0:
		#print "setting new center offset"
		possiblenewoffset = [(float(x)*float(windowSize[0])/2.0)/float(windowSize[0]), 
							 (float(y)*float(windowSize[1])/2.0)/float(windowSize[1])]
		zoomPreview.setPosition((possiblenewoffset[0]+float(windowSize[0])/4.0)/float(windowSize[0]),
								(possiblenewoffset[1]+float(windowSize[1])/4.0)/float(windowSize[1]))

	matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
	
	if zoomingAnimation != 0:
		updateFrustum(zoomingCount/totalAnimationFrames)
		
		if zoomingCount+1 < totalAnimationFrames:
			#print zoomingCount
			zoomingCount += 1
		else:
			#print "done!"
			zoomingCount = 0
			zoomingAnimation = 0
			previousCenterOffset = newCenterOffset
	else:
		#fov = (VFOV/zoomingLevel)
		updateFrustum()

	if showMenu == True and hideMenu == False:
		zoomPreview.visible(viz.ON)
	
	if zooming == False:
		updateFrustum()

# updateCombinedv2Cursor()
# main update function for the combined zoom techniques, needs to be called every frame/every time the cursor is updated
def updateCombinedv2Cursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
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
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	global zoomPreview
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	updateRayCasting(x/windowSize[0],y/windowSize[1])
	
	if zoomingAnimation == 0:
		showMenu = True
	else:
		showMenu = False

	if zoomingLevel < 128.0:
		#print "setting new center offset"
		possiblenewoffset = [0,0]
		if x < float(windowSize[0])/4.0:
			possiblenewoffset[0] = 0.0
		elif x > windowSize[0]-float(windowSize[0])/4.0:
			possiblenewoffset[0] = float(windowSize[0])-float(windowSize[0])/2.0
		else:
			possiblenewoffset[0] = float(x)-float(windowSize[0])/4.0
			
		if y < float(windowSize[1])/4.0:
			possiblenewoffset[1] = 0.0
		elif y > windowSize[1]-float(windowSize[1])/4.0:
			possiblenewoffset[1] = float(windowSize[1])-float(windowSize[1])/2.0
		else:
			possiblenewoffset[1] = float(y)-float(windowSize[1])/4.0
		
		#print possiblenewoffset[0],possiblenewoffset[1]
		
		zoomPreview.setPosition((possiblenewoffset[0]+float(windowSize[0])/4.0)/float(windowSize[0]),
								(possiblenewoffset[1]+float(windowSize[1])/4.0)/float(windowSize[1]))
		
	matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
	
	if zoomingAnimation != 0:
		updateFrustum(zoomingCount/totalAnimationFrames)
		
		if zoomingCount+1 < totalAnimationFrames:
			#print zoomingCount
			zoomingCount += 1
		else:
			#print "done!"
			zoomingCount = 0
			zoomingAnimation = 0
			previousCenterOffset = newCenterOffset
	else:
		#fov = (VFOV/zoomingLevel)
		updateFrustum()
	
	if showMenu == True and hideMenu == False:
		zoomPreview.visible(viz.ON)
	
	if zooming == False:
		updateFrustum()
		

# updateCombinedv3Cursor()
# main update function for the combined zoom techniques, needs to be called every frame/every time the cursor is updated
def updateCombinedv3Cursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
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
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	global zoomPreview
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	updateRayCasting(x/windowSize[0],y/windowSize[1])
	
	if zoomingAnimation == 0:
		showMenu = True
	else:
		showMenu = False

	if zoomingLevel < 128.0:
		#print "setting new center offset"
		possiblenewoffset = [0,0]
		possiblenewoffset[0] = float(x)-float(windowSize[0])/4.0
		possiblenewoffset[1] = float(y)-float(windowSize[1])/4.0
		
		#print possiblenewoffset[0],possiblenewoffset[1]
		
		zoomPreview.setPosition((possiblenewoffset[0]+float(windowSize[0])/4.0)/float(windowSize[0]),
								(possiblenewoffset[1]+float(windowSize[1])/4.0)/float(windowSize[1]))
		
	matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
	
	if zoomingAnimation != 0:
		updateFrustum(zoomingCount/totalAnimationFrames)
		
		if zoomingCount+1 < totalAnimationFrames:
			#print zoomingCount
			zoomingCount += 1
		else:
			#print "done!"
			zoomingCount = 0
			zoomingAnimation = 0
			previousCenterOffset = newCenterOffset
	else:
		#fov = (VFOV/zoomingLevel)
		updateFrustum()
	
	if showMenu == True and hideMenu == False:
		zoomPreview.visible(viz.ON)
	
	if zooming == False:
		updateFrustum()

# updateCombinedv1Cursor()
# main update function for the combined zoom technique, needs to be called every frame/every time the cursor is updated
def updateCombinedv4Cursor():
	global VFOV
	global windowSize
	global aspectRatio
	global centroid
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
	global crosshair
	global totalAnimationFrames
	global bg_sphere
	global previousZoomingLevel
	global lastZoomingCount
	global zoomPreview
	global intersectingObjects
	
	x,y = centroid[0],centroid[1]
	
	updateRayCasting(x/windowSize[0],y/windowSize[1])
	
	if zoomingAnimation == 0:
		showMenu = True
	else:
		showMenu = False

	if zoomingLevel < 128.0:
		#print "setting new center offset"
		possiblenewoffset = [(float(x)*float(windowSize[0])/2.0)/float(windowSize[0]), 
							 (float(y)*float(windowSize[1])/2.0)/float(windowSize[1])]
		zoomPreview.setPosition((possiblenewoffset[0]+float(windowSize[0])/4.0)/float(windowSize[0]),
								(possiblenewoffset[1]+float(windowSize[1])/4.0)/float(windowSize[1]))

	matrix = viz.MainView.getMatrix(viz.ABS_GLOBAL)
	
	if zoomingAnimation != 0:
		updateFrustum(zoomingCount/totalAnimationFrames)
		
		if zoomingCount+1 < totalAnimationFrames:
			#print zoomingCount
			zoomingCount += 1
		else:
			#print "done!"
			zoomingCount = 0
			zoomingAnimation = 0
			previousCenterOffset = newCenterOffset
	else:
		#fov = (VFOV/zoomingLevel)
		updateFrustum()

	if showMenu == True and hideMenu == False:
		zoomPreview.visible(viz.ON)
	
	if zooming == False:
		updateFrustum()

# updateView()
# updates camera for main application
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

def resetSQUAD():	
	quad_lin.visible(viz.OFF)
	quad_tri.visible(viz.OFF)
	scSphere.visible(viz.OFF)
	
def resetContinuous():
	crosshair.visible(viz.OFF)
	scSphere.visible(viz.OFF)
	
def resetDiscrete():
	crosshair.visible(viz.OFF)
	scSphere.visible(viz.OFF)
	for quad in quadrants:
		quad.visible(viz.OFF)

def resetCombined():
	crosshair.visible(viz.OFF)
	scSphere.visible(viz.OFF)
	zoomPreview.visible(viz.OFF)

def update():
	global windowSize
	global aspectRatio
	global VFOV
	global minFOV
	global previousFrameTick
	global fps
	global totalAnimationFrame
	
	windowSize = viz.MainWindow.getSize(viz.WINDOW_PIXELS)
	aspectRatio = windowSize[0]/windowSize[1]
	VFOV = 2.0 * math.atan( math.tan( (defaultHFOV/57.2957795) / 2.0 ) / aspectRatio ) * 57.2957795
	minFOV = VFOV / 128.0
	currentFrameTick = viz.tick()
	fps = 1/(currentFrameTick-previousFrameTick)
	previousFrameTick = currentFrameTick
	#print "minFOV: ",minFOV 
	
	updateView()
	if is900Sensor.valid() and not Globals.DEBUG:
		updateIS900Data()
	else:
		updateMouseData()
	
	resetSQUAD()
	resetContinuous()
	resetDiscrete()
	resetCombined()
	
	if Globals.technique == InteractionTechnique.SQUAD:
		updateSQUADCursor()
	elif Globals.technique == InteractionTechnique.ContinuousZoom:
		updateContinuousCursor()
	elif Globals.technique == InteractionTechnique.DiscreteZoom:
		updateDiscreteCursor()
	elif Globals.technique == InteractionTechnique.Raycasting:
		updateRayCasting(centroid[0]/windowSize[0],centroid[1]/windowSize[1])
	elif Globals.technique == InteractionTechnique.CombinedZoomv1:
		updateCombinedv1Cursor()
	elif Globals.technique == InteractionTechnique.CombinedZoomv2:
		updateCombinedv2Cursor()
	elif Globals.technique == InteractionTechnique.CombinedZoomv3:
		updateCombinedv3Cursor()
	elif Globals.technique == InteractionTechnique.CombinedZoomv4:
		updateCombinedv4Cursor()

# main
if __name__ == '__main__':
	global VFOV
	global minFOV
	global children
	global windowSize
	global aspectRatio
	global centroid
	global buttonState
	global showMenu
	global hideMenu
	global is900Sensor
	global old_data
	global all_data
	global is900Euler
	global crosshair
	global previousCenterOffset
	global newCenterOffset
	global previousFrameTick
	global fps
	
	# technique
	global scSphere
	global scSphereRadius
	global children
	global mode
	global intersectingObjects
	global identity
	global filter
	global mouseState
	global oldMouseState
	
	# zoom techniques
	global zooming
	global zoomingAnimation
	global zoomingCount
	global zoomingLevel
	global previousZoomingLevel
	global lastZoomingCount
	global zoomingStack
	global maxZoom
	global currentWindow
	global previousWindow
	global animationCurrentWindow
	global lastZoomingLevel
	# only for discrete zoom, cursor-based
	global zoomPreview
	# only for discrete zoom, quad-based
	global quadrants
	
	#SQUAD variables
	global intersecting
	global quad_lin
	global quad_tri
	global object_position
	global object_size
	global clone_list
	global rotQUAD
	global mode
	
	global techniqueBG
	
	# create identity matrix to be used in transformations
	identity = vizmat.Transform()
	identity.makeIdent()
	
	##################################################
	# setup vizard
	viz.collision(viz.OFF)
	viz.clearcolor(viz.BLACK)
	#viz.setOption('viz.fullscreen.x',1280)
	#viz.setOption('viz.fullscreen.y',0)
	#viz.setOption('viz.fullscreen.width',1400)
	#viz.setOption('viz.fullscreen.height',1050)
	#viz.setOption('viz.fullscreen.monitor',2)
	#viz.go(viz.FULLSCREEN)
	viz.go()
	
	# initial frustum setup
	aspectRatio = viz.MainWindow.getAspectRatio()
	defaultHFOV = 90.0 # vertical -> horizontal = vertical * aspect 
	VFOV = 2.0 * math.atan( math.tan( (defaultHFOV/57.2957795) / 2.0 ) / aspectRatio ) * 57.2957795
	minFOV = VFOV / 128.0
	viz.MainWindow.fov(VFOV)
	print viz.MainWindow.getVerticalFOV()
	print viz.MainWindow.getHorizontalFOV()
	
	# get the window size
	# this is updated all the time in the update() function
	windowSize = viz.MainWindow.getSize(viz.WINDOW_PIXELS)
	
	##################################################
	# setup the application
	# load the supermarket model
	print "Loading the supermarket model"	
	supermarket = viz.add('finalM.ive')
	#supermarket.appearance(viz.TEXMODULATE)
	supermarket.ambient(.6,.6,.6)
	#Make the objects in supermarket.wrl accessible
	print "GetModels"
	getModels()
	children = supermarket.getChildren()
	
	# setup objects bounding boxes...
	object_position = []
	object_size = []
	for child in children:
		object_position.append(child.getBoundingBox(viz.ABS_GLOBAL).center)
		object_size.append(child.getBoundingBox(viz.ABS_GLOBAL).size)
	
	# initialize user's position and orientation	
	defaultPosition = [-80,57,-420]
	defaultOrientation = [45.0,17.0,0.0]
	viz.MainView.setPosition(defaultPosition,viz.ABS_GLOBAL)
	viz.MainView.setEuler([0,0,0],viz.BODY_ORI,viz.ABS_GLOBAL)
	viz.MainView.setEuler(defaultOrientation,viz.BODY_ORI,viz.REL_PARENT)
	
	# setup technique label
	techniqueBG = None
	updateTechniqueLabel()
	
	##################################################
	# setup interaction devices 
	# cursor control
	viz.mouse.setOverride(viz.ON)
	buttonState = [False, False, False]
	centroid = [0,0] # position of the cursor on the screen
	
	# mouse control
	mouseState = 0
	oldMouseState = 0
	
	# add the intersense tracker
	isense = viz.add('intersense.dle')
	is900Sensor = isense.addTracker(port=1,station=2)
	if is900Sensor.valid():
		is900Sensor.setEnhancement(0)
		is900Sensor.setPrediction(0)
		#is900Sensor.setSensitivity(4)
		print "Wand Enhancement: "+str(is900Sensor.getEnhancement())
		print "Wand Prediction: "+str(is900Sensor.getPrediction())
		print "Wand Sensitivity: "+str(is900Sensor.getSensitivity())
	else:
		print "USING THE MOUSE AS THE CURSOR" 
	
	# data used for intersense
	all_data = [0,0,0,0,0,0,0,0,0,0]
	old_data = [0,0,0,0,0,0,0,0,0,0]
	is900Euler = [0,0,0]
	
	# low pass filter initialization, converted to degrees, which is how the filter is now being applied
	filter = LowPassDynamicFilter(.25, 5, 0.33745, 6.7492)
	
	# used to determine the number of frames used in the animation and also the low pass filter
	previousFrameTick = viz.tick()
	fps = 0.0
	
	##################################################
	# TECHNIQUES SETUP
	
	##############################################
	# used by ALL techniques, either small or large, this is the sphere-casting's sphere but also is used for ray-casting
	scSphereRadius = Globals.TINY_SPHERE_RADIUS
	scSphere = createSphere(20,20)
	scSphere.setScale(scSphereRadius,scSphereRadius,scSphereRadius)
	scSphere.color(0.2,0.6,1.0)
	scSphere.visible(viz.OFF)
	scSphere.alpha(0.6)
	
	# don't really know what to do here... is this part of the technique class?
	intersectingObjects = []
	
	##############################################
	# used for ray-casting
	crosshair = viz.addTexQuad(viz.SCREEN,texture=viz.add('bline.png'))
	
	##############################################
	# SQUAD
	intersecting = False
	
	# initialize quadrants
	quad_lin = createQuadLin()
	quad_lin.depthFunc(viz.GL_ALWAYS)
	quad_lin.drawOrder(1)
	quad_lin.color(0,0,0)
	quad_tri = createQuadTri()
	quad_tri.color(0.8,0.8,0.8)
	quad_tri.depthFunc(viz.GL_ALWAYS)
	quad_tri.drawOrder(0)
	
	# object clone list for the quadrants
	clone_list = []
	
	# bounding boxes for sphere-casting
	boundingBoxes = []
	
	# determines the selected quadrant
	selected_quad = Quadrant.NONE
	
	# SQUAD selection mode, can be SELECTION and SELECTION_QUADRANT
	mode = InteractionMode.SELECTION
	
	# setup quadrants and intersection sphere for SQUAD
	quad_lin.visible(viz.OFF)
	quad_tri.visible(viz.OFF)
	
	# variable that controls the animation of the objects in the quadrants
	rotQUAD = 0

	##############################################
	# used by all the zoom techniques
	zooming = False
	zoomingAnimation = 0
	zoomingCount = 0
	zoomingLevel = 1
	lastZoomingLevel = zoomingLevel
	previousZoomingLevel = 1
	previousCenterOffset = [0,0]
	newCenterOffset = [0,0]
	lastZoomingCount = 0
	previousWindow = [[0,0],[windowSize[0],windowSize[1]]]
	currentWindow = [[0,0],[windowSize[0],windowSize[1]]]
	animationCurrentWindow = [[0,0],[windowSize[0],windowSize[1]]]
	
	##############################################
	# initialize variables with all the discrete techniques
	zoomingStack = []
	showMenu = False
	hideMenu = False
	
	##############################################
	# initializes quadrants for the discrete zoom, quad-based
	quadrants = createQuadrantsZoom()
	for quad in quadrants:
		quad.alpha(.3)
		quad.visible(viz.OFF)
	
	##############################################
	# initializes the quadrant that is used discrete zoom, cursor-based techniques
	zoomPreview = createZoomQuad(2.0)
	zoomPreview.visible(viz.OFF)
		
	############################
	# callbacks
	viz.callback(viz.KEYDOWN_EVENT, keyDown)
	viz.callback(viz.KEYUP_EVENT, keyUp)
	
	vizact.ontimer(0,update)
	
