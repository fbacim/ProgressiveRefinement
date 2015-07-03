import viz
import viztask
import vizmultiprocess
from multiprocessing import Pool

def computeStuff(x,y):
	#print 'start process'
	test = []
	for i in range(1000):
		a = i*x
		b = i*y
		test.append(a+i-b)
	#print 'end process'
	return [a,b,test]

def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)		

if __name__ == '__main__':
	global result_list
	
	# This is the main entry point of the program.
	# This will not be executed by child processes launched by vizmultiprocess.    
	viz.go()
	
	pool = Pool(processes = 8)
	
	result_list = []
	start_time = viz.tick()
	
	print 'begin processing'
	for i in range(8):
		print 'calling ',i
		result_list.append(computeStuff(2, 3))
	print 'end processing'
		
	print viz.tick()-start_time
	#print result_list
	
	start_time = viz.tick()

	#for j in range(8):
	r = []
	result_list = []

	# Execute 'computeStuff' function in separate process
	print 'begin multi processing'
	for i in range(8):
		print 'calling ',i
		r.append(pool.apply_async(computeStuff, args = (2, 3, )))
	print 'end multi processing'
	
	for i in range(8):
		result_list.append(r[i].get())
	
	print viz.tick()-start_time
	
	print result_list
	