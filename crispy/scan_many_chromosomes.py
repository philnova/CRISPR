"""

Module to run scan_one_chromosome repeatedly and distribute each chromosomal scan over a distinct
process pool. One process will be generated per core on the CPU, and one chromosome will be scanned
at a time per process.

Command line flags are -p, the path to the chromosome files to be scanned, and -f, the name of the info file.
Recall that chromosome files should be FASTA files converted to plain text.

The info file should be a plain text file with two columns and no header. The first column
should match the name of the chromosome files to be scanned, minus the .txt suffix.

The second column should be integers representing the chromosomal coordinates of the start sites
of the sequence on the corresponding chromosome.

For example, for hg19, this file would look like:
chr1 10001
chr2 10001
chr3 10001
chr4 10001
chr5 10619
chr6 60001
chr7 10001
chr8 60001
chr9 10001
chr10 10001
chr11 60001
chr12 10001
chr13 16000001
chr14 16000001
chr15 17000001
chr16 10001
chr17 60001
chr18 10001
chr19 60001
chr20 60001
chr21 5010001
chr22 10510001
chrX 10001
chrY 10001

Optional arguments are:
-c: whether intermediate files in the guideRNA scanning workflow should be deleted once the scan is complete
-s: whether chromosome sequences contain repetitive NNNN at the start and/or end that need to be removed
Both default to True

"""

#Python2/3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import scan_one_chromosome as scan1
import multiprocessing
import itertools
import argparse
import time



def worker(inputfile, chrm_start, path, cleanup, strip):
	print(inputfile)
	try:
		#cf = scan1.ChromosomeFile(inputfile, chrm_start, path, strip_needed = strip, cleanup = cleanup, eager = True)
		ChromFile = scan1.ChromosomeFile(inputfile, chrm_start, path, strip_needed = strip, cleanup = cleanup, eager = False)
		with ContextManager(ChromFile):
			ChromFile.workflow()

		print(inputfile, ' success! :)')
	except:
		print(inputfile, ' fail! :(')

def worker_splat(args):
    """Convert `worker([1,2,3,...])` to `worker(1,2,3,...)` call."""
    return worker(*args)

def main(filename, path, strip, cleanup):
	inputs = []
	with open(filename) as file:
		for line in file:
			inputfile, chrm_start = line.split()[0], int(line.split()[1])
			inputs.append((inputfile, chrm_start, path, cleanup, strip))
			print inputs

	i, ch, p, cl, s = zip(*inputs)

	pool = multiprocessing.Pool(multiprocessing.cpu_count()) #limit pool to number of cores
	pool.map(worker_splat, itertools.izip(i, ch, p, cl, s))

class ContextManager():
	"""Allows us to clean up intermediate files even if we exit worker() through a KeyboardInterrupt"""
	def __init__(self, chromfile):
		self.chromfile = chromfile

	def __enter__(self):
		pass

	def __exit__(self, type, value, traceback):
		"""This method is called by the with statement no matter how we exit"""
		print("Cleaning up after early exit")
		if self.chromfile.cleanup:
			self.chromfile.clean_intermediate_files()

if __name__ == "__main__":
	start = time.time() #should use CPU time instead of clock time

	parser = argparse.ArgumentParser(description = "Path to chromosome fasta files and info file")
	parser.add_argument('-p', action="store", dest="path", type=str, default='')
	parser.add_argument('-f', action="store", dest="filename", type=str)
	parser.add_argument('-c', action="store", dest="cleanup", type=bool, default=True)
	parser.add_argument('-s', action="store", dest="strip", type=bool, default=True)

	results = parser.parse_args()
	
	main(results.filename, results.path, results.strip, results.cleanup)
	end = time.time()
	print('job finished in',end-start)