"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Input: 
1. The PATH to a directory containing chromosome files. Each CHROMOSOME FILE should have a first line
that reads >chrN, where N is an integer or X/Y, and subsequent lines are bases (including 'N').

2. A tab-delimited text FILE with two columns, and no header. One column should be the names of the
chromosome files (e.g. chr1.txt, chr2.txt, ..., chrX.txt) and the second should be the coordinate of 
the beginning of the sequence for that chromosome. (This can be found by entering the first sequence 
of non-N base pairs on the chromosome into UCSC genome browser's Blat tool).

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Output: 
One output file per input file; each with the header:

CHR#	START	STOP	SEQUENCE	N_COUNT 	N_LOWERCASE 	DIRECTION

...and every sequence of 23 bp, ending in NGG, in the chromosome (in either forward or reverse direction)

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Sample command line input:
pypy gen_guideRNA.py -p /users/jondoe/genome/ -f chrom_starts.txt

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

WARNING: for a full genome, this process takes up to 24 hours to complete on my four-core machine with
8GB RAM! pypy or other JIT-compiled flavor of Python strongly recommended.

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
"""

import argparse
import strip_file
import multiprocess_multiprocessor as multi
import merge_files as merge
import time


def main():

	beginning = time.time()

	parser = argparse.ArgumentParser(description = "Path to chromosome files and start sites")
	parser.add_argument('-p', action="store", dest="path", type=str)
	parser.add_argument('-f', action="store", dest="filename", type=str)

	results = parser.parse_args()

	path, start_sites_filename = results.path, results.filename
	start_sites = []
	filenames = []

	with open(start_sites_filename) as fo:
		for line in fo:
			filenames.append(line.strip().split()[0])
			start_sites.append(line.strip().split()[1])

	#step 1: strip files
	print "STEP 1: STRIP CHROMOSOMES OF STARTING AND LEADING N"
	start = time.time()
	strip_file.main(path, filenames)
	print "STEP 1 COMPLETE IN %f SEC" % (time.time() - start)
	print ''

	#step 2: generate guide sequences
	start = time.time()
	print "STEP 2: GENERATE POTENTIAL GUIDE SEQUENCES"
	multi.main(start_sites_filename, path, '_edited_double_reordered.txt')
	print "STEP 2 COMPLETE IN %f SEC" % (time.time() - start)
	print ''

	#step 3: merge guide sequences
	start = time.time()
	print "STEP 3: MERGE GUIDE SEQUENCES"
	merge.main(path, start_sites_filename, '_edited_double_reordered.txt')
	print "STEP 3 COMPLETE IN %f SEC" % (time.time() - start)
	print ''

	print "PROCESS COMPLETE IN %f SEC" % (time.time() - beginning)

if __name__ == "__main__":
	main()