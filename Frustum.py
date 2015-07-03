import math
from Vector3 import Vector3

# class that stores a frustum
class Frustum:
	def __init__(self, origin, dvector, uvector, rvector, dmin, dmax, ubound, rbound):
		self.Origin = origin
		self.DVector = dvector
		self.UVector = uvector
		self.RVector = rvector
		self.DMin = dmin
		self.DMax = dmax
		self.UBound = ubound
		self.RBound = rbound
		
		self.Update()
		
	def Update(self):
		self.mDRatio = self.DMax/self.DMin
		#self.mMTwoUF = -2.0*self.UBound*self.DMax
		#self.mMTwoRF = -2.0*self.RBound*self.DMax
		
	def ComputeVertices(self):
		vertex = [0,0,0,0,0,0,0,0]
		
		DScaled = self.DMin*self.DVector
		UScaled = self.UBound*self.UVector
		RScaled = self.RBound*self.RVector
		
		vertex[0] = DScaled - UScaled - RScaled
		vertex[1] = DScaled - UScaled + RScaled
		vertex[2] = DScaled + UScaled + RScaled
		vertex[3] = DScaled + UScaled - RScaled

		for i in range(4):
			vertex[i+4] = self.Origin + self.mDRatio*vertex[i]
			vertex[i] += self.Origin
		
		return vertex
		
	def CalculateCollisionBox(self,center,size):
		# for convenience
		#axes = [Vector3(1,0,0),Vector3(0,1,0),Vector3(0,0,1)]
		extents = [size/2.0,size/2.0,size/2.0]
		
		diff = center - self.Origin  # C-E

		A = Vector3(0,0,0)      # Dot(R,A[i])
		B = Vector3(0,0,0)      # Dot(U,A[i])
		C = Vector3(0,0,0)      # Dot(D,A[i])
		D = Vector3(0,0,0)      # (Dot(R,C-E),Dot(U,C-E),Dot(D,C-E))
		NA = Vector3(0,0,0)     # dmin*Dot(R,A[i])
		NB = Vector3(0,0,0)     # dmin*Dot(U,A[i])
		NC = Vector3(0,0,0)     # dmin*Dot(D,A[i])
		ND = Vector3(0,0,0)     # dmin*(Dot(R,C-E),Dot(U,C-E),?)
		RC = Vector3(0,0,0)     # rmax*Dot(D,A[i])
		RD = Vector3(0,0,0)     # rmax*(?,?,Dot(D,C-E))
		UC = Vector3(0,0,0)     # umax*Dot(D,A[i])
		UD = Vector3(0,0,0)     # umax*(?,?,Dot(D,C-E))
		NApRC = Vector3(0,0,0)  # dmin*Dot(R,A[i]) + rmax*Dot(D,A[i])
		NAmRC = Vector3(0,0,0)  # dmin*Dot(R,A[i]) - rmax*Dot(D,A[i])
		NBpUC = Vector3(0,0,0)  # dmin*Dot(U,A[i]) + umax*Dot(D,A[i])
		NBmUC = Vector3(0,0,0)  # dmin*Dot(U,A[i]) - umax*Dot(D,A[i])
		RBpUA = Vector3(0,0,0)  # rmax*Dot(U,A[i]) + umax*Dot(R,A[i])
		RBmUA = Vector3(0,0,0)  # rmax*Dot(U,A[i]) - umax*Dot(R,A[i])
		#DdD, radius, p, fmin, fmax, MTwoUF, MTwoRF, tmp
		
		# M = D
		D[2] = diff.Dot(self.DVector)
		for i in  range(3):
			C[i] = self.DVector[i]#axes[i].Dot(self.DVector)
		radius = extents[0]*math.fabs(C[0]) + extents[1]*math.fabs(C[1]) + extents[2]*math.fabs(C[2])
		if D[2] + radius < self.DMin or D[2] - radius > self.DMax:
			return False
		
		# M = n*R - r*D
		for i in range(3):
			A[i] = self.RVector[i]#axes[i].Dot(self.RVector)
			RC[i] = self.RBound*C[i]
			NA[i] = self.DMin*A[i]
			NAmRC[i] = NA[i] - RC[i]
		D[0] = diff.Dot(self.RVector)
		radius = extents[0]*math.fabs(NAmRC[0]) + extents[1]*math.fabs(NAmRC[1]) + extents[2]*math.fabs(NAmRC[2])
		ND[0] = self.DMin*D[0]
		RD[2] = self.RBound*D[2]
		DdD = ND[0] - RD[2]
		MTwoRF = self.GetMTwoRF()
		if (DdD + radius) < MTwoRF or DdD > radius:
			return False

		# M = -n*R - r*D
		for i in range(3):
			NApRC[i] = NA[i] + RC[i]    
		radius = extents[0]*math.fabs(NApRC[0]) + extents[1]*math.fabs(NApRC[1]) + extents[2]*math.fabs(NApRC[2])
		DdD = -(ND[0] + RD[2])
		if (DdD + radius) < MTwoRF or DdD > radius:
			return False

		# M = n*U - u*D
		for i in range(3):
			B[i] = self.UVector[i]#axes[i].Dot(self.UVector)
			UC[i] = self.UBound*C[i]
			NB[i] = self.DMin*B[i]
			NBmUC[i] = NB[i] - UC[i]
		D[1] = diff.Dot(self.UVector)
		radius = extents[0]*math.fabs(NBmUC[0]) + extents[1]*math.fabs(NBmUC[1]) + extents[2]*math.fabs(NBmUC[2])
		ND[1] = self.DMin*D[1]
		UD[2] = self.UBound*D[2]
		DdD = ND[1] - UD[2]
		MTwoUF = self.GetMTwoUF()
		if (DdD + radius) < MTwoUF or DdD > radius:
			return False

		# M = -n*U - u*D
		for i in range(3):
			NBpUC[i] = NB[i] + UC[i]
		radius = extents[0]*math.fabs(NBpUC[0]) + extents[1]*math.fabs(NBpUC[1]) + extents[2]*math.fabs(NBpUC[2])
		DdD = -(ND[1] + UD[2])
		if (DdD + radius) < MTwoUF or DdD > radius:
			return False
		
		# M = A[i]
		for i in range(3):
			p = self.RBound*math.fabs(A[i]) + self.UBound*math.fabs(B[i])
			NC[i] = self.DMin*C[i]
			fmin = NC[i] - p
			if fmin < 0.0:
				fmin *= self.mDRatio
			fmax = NC[i] + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = A[i]*D[0] + B[i]*D[1] + C[i]*D[2]
			if (DdD + extents[i]) < fmin or (DdD - extents[i]) > fmax:
				return False

		# M = Cross(R,A[i])
		for i in range(3):
			p = self.UBound*math.fabs(C[i])
			fmin = -NB[i] - p
			if fmin < 0.0:
				fmin *= self.mDRatio
			fmax = -NB[i] + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = C[i]*D[1] - B[i]*D[2]
			radius = extents[0]*math.fabs(B[i]*C[0]-B[0]*C[i]) + extents[1]*math.fabs(B[i]*C[1]-B[1]*C[i]) + extents[2]*math.fabs(B[i]*C[2]-B[2]*C[i])
			if (DdD + radius < fmin or DdD - radius > fmax):
				return False

		# M = Cross(U,A[i])
		for i in range(3):
			p = self.RBound*math.fabs(C[i])
			fmin = NA[i] - p
			if fmin < 0.0:
				fmin *= self.mDRatio
			fmax = NA[i] + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = -C[i]*D[0] + A[i]*D[2]
			radius = extents[0]*math.fabs(A[i]*C[0]-A[0]*C[i]) + extents[1]*math.fabs(A[i]*C[1]-A[1]*C[i]) + extents[2]*math.fabs(A[i]*C[2]-A[2]*C[i])
			if (DdD + radius) < fmin or (DdD - radius) > fmax:
				return False

		# M = Cross(n*D+r*R+u*U,A[i])
		for i in range(3):
			fRB = self.RBound*B[i]
			fUA = self.UBound*A[i]
			RBpUA[i] = fRB + fUA
			RBmUA[i] = fRB - fUA
		
		for i in range(3):
			p = self.RBound*math.fabs(NBmUC[i]) + self.UBound*math.fabs(NAmRC[i])
			tmp = -self.DMin*RBmUA[i]
			fmin = tmp - p
			if fmin < 0.0:
				fmin *= self.mDRatio
			fmax = tmp + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = D[0]*NBmUC[i] - D[1]*NAmRC[i] - D[2]*RBmUA[i]
			radius = 0.0
			for j in range(3):
				radius += extents[j]*math.fabs(A[j]*NBmUC[i] - B[j]*NAmRC[i] - C[j]*RBmUA[i])
			if (DdD + radius) < fmin or (DdD - radius) > fmax:
				return False

		# M = Cross(n*D+r*R-u*U,A[i])
		for i in range(3):
			p = self.RBound*math.fabs(NBpUC[i]) + self.UBound*math.fabs(NAmRC[i])
			tmp = -self.DMin*RBpUA[i]
			fmin = tmp - p
			if fmin < 0:			
				fmin *= self.mDRatio
			fmax = tmp + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = D[0]*NBpUC[i] - D[1]*NAmRC[i] - D[2]*RBpUA[i]
			radius = 0.0
			for j in range(3):
				radius += extents[j]*math.fabs(A[j]*NBpUC[i] - B[j]*NAmRC[i] - C[j]*RBpUA[i])
			if (DdD + radius) < fmin or (DdD - radius) > fmax:
				return False

		# M = Cross(n*D-r*R+u*U,A[i])
		for i in range(3):
			p = self.RBound*math.fabs(NBmUC[i]) + self.UBound*math.fabs(NApRC[i])
			tmp = self.DMin*RBpUA[i]
			fmin = tmp - p
			if fmin < 0.0:
				fmin *= self.mDRatio
			fmax = tmp + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = D[0]*NBmUC[i] - D[1]*NApRC[i] + D[2]*RBpUA[i]
			radius = 0.0
			for j in range(3):
				radius += extents[j]*math.fabs(A[j]*NBmUC[i] -
					B[j]*NApRC[i] + C[j]*RBpUA[i])
			if (DdD + radius) < fmin or (DdD - radius) > fmax:
				return False

		# M = Cross(n*D-r*R-u*U,A[i])
		for i in range(3):
			p = self.RBound*math.fabs(NBpUC[i]) + self.UBound*math.fabs(NApRC[i])
			tmp = self.DMin*RBmUA[i]
			fmin = tmp - p
			if fmin < 0.0:
				fmin *= self.mDRatio
			fmax = tmp + p
			if fmax > 0.0:
				fmax *= self.mDRatio
			DdD = D[0]*NBpUC[i] - D[1]*NApRC[i] + D[2]*RBmUA[i]
			radius = 0.0
			for j in range(3):
				radius += extents[j]*math.fabs(A[j]*NBpUC[i] - B[j]*NApRC[i] + C[j]*RBmUA[i])
			if (DdD + radius) < fmin or (DdD - radius) > fmax:
				return False

		return True
