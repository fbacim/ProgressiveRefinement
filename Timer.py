from time import clock

class Timer:
	def __init__(self):
		self.start_time = clock()
		self.elapsed_time = 0.0		
		self.running = False
		
	def elapsed(self):
		if self.running:
			self.elapsed_time = clock()-self.start_time
			return self.elapsed_time
		else:
			return 0.0
	
	def start(self):
		self.start_time = clock()
		self.running = True
		
	def stop(self):
		elapsed = self.elapsed()
		self.running = False
		return elapsed
	
	def clear(self):
		self.start_time = 0.0
		self.elapsed_time = 0.0
		self.running = False
		