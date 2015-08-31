"""Extension to multiprocessor module to process all 24 chromosomes simultaneously
using multiple processing (Pythonic alternative to multithreading)"""

import find_guideRNA as find
import multiprocessing
import itertools
import time

#Profiling: took 1987s to process chromosomes 21 and 22 (~=33 min, 1.5x faster than multiprocessor)

PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/"

def worker(inputfile, chrm_start):
	print inputfile, chrm_start
	try:
		find.scan_chromosome_dynamic_bidirection(PATH+inputfile+'.txt', chrm_start, PATH+inputfile)
		print inputfile + ' success! :)'
	except:
		print inputfile + ' fail! :('

def func_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return worker(*a_b)

def multimulti(filename):
	inputs = []
	with open(filename) as file:
		for line in file:
			inputfile, chrm_start = line.split()[0], int(line.split()[1])
			inputs.append((inputfile, chrm_start))

	a_args, b_args = zip(*inputs)

	pool = multiprocessing.Pool(multiprocessing.cpu_count()) #limit pool to number of cores
	pool.map(func_star, itertools.izip(a_args, b_args))


if __name__ == "__main__":
	start = time.time()
	multimulti('test_starts.txt')
	print time.time() - start