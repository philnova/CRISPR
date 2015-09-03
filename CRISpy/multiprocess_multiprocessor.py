"""Extension to multiprocessor module to process all 24 chromosomes simultaneously
using multiple processing (Pythonic alternative to multithreading)"""

import find_guideRNA as find
import multiprocessing
import itertools
import argparse

#Profiling: took 1987s to process chromosomes 21 and 22 (~=33 min, 1.5x faster than multiprocessor)

PATH = ''

def worker(inputfile, chrm_start):
	print(inputfile)
	try:
		find.scan_chromosome_dynamic_bidirection(PATH+inputfile, chrm_start, PATH+inputfile.replace('.txt', ''))
		print(inputfile, ' success! :)')
	except:
		print(inputfile, ' fail! :(')

def func_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return worker(*a_b)

def multimulti(filename, name_modifier = '.txt'):
	inputs = []
	with open(filename) as file:
		for line in file:
			inputfile, chrm_start = line.split()[0] + name_modifier, int(line.split()[1])
			inputs.append((inputfile, chrm_start))

	a_args, b_args = zip(*inputs)

	pool = multiprocessing.Pool(multiprocessing.cpu_count()) #limit pool to number of cores
	pool.map(func_star, itertools.izip(a_args, b_args))

def main(filename, path, name_modifier = '.txt'):
	global PATH
	PATH = path
	multimulti(filename, name_modifier)
	

if __name__ == "__main__":

	PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/"
	FILENAME = 'test_starts.txt'

	parser = argparse.ArgumentParser(description = "Path to chromosome files and start sites")
	parser.add_argument('-p', action="store", dest="path", type=str, default=PATH)
	parser.add_argument('-f', action="store", dest="filename", type=str, default=FILENAME)

	results = parser.parse_args()

	PATH = results.path

	# print PATH, results.filename

	main(results.filename)

	#command line example: pypy multiprocess_multiprocessor.py '/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/' 'chrm_starts.txt'