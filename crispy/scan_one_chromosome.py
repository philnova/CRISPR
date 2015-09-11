"""

Module to pull all potential guideRNAs (defined as a string of 20bp followed by NGG, in either forward
	or reverse sequence) from a single chromosomal file. File should be a FASTA file converted to a
simple text file.

The variable chrom_start represents the chromosomal coordinate of the start of that chromosome's sequence.

By default, the class ChromosomeFile will try to strip repeated NNNNNN from the beginning and end of the
FASTA file. If this behavior is not needed, set strip_needed to false.

As in most cases, a single chromosomal sequence is too large to be held in RAM, ChromosomeFile generates
several intermediate files. By default, these are cleaned up at the end, but this behavior can also be
disabled with the cleanup_needed flag.

By default, the prefix for all output files is the same as the input file (generally the chromosome's name).
However, this can also be overridden by providing an output_filename to the ChromosomeFile object.

The workflow of ChromosomeFile is:
	1. Open the input file for lazy evaluation, using self.openfile()
	2. If strip_needed is set to True, strip repeated NNNN from the start and end of the file with self.strip_fasta_file()
	3. Collect all guideRNAs, using self.scan_chromosome_dynamic_bidirection()
		- At the end of this, input file is automatically closed
	4. Merge the guides pulled from the forward sequence with those from the reverse sequence, using self.filemerge()
	5. If cleanup_needed is set to True, delete all intermediate files using self.clean_intermediate_files()

**If the option eager is set to True, all of these methods will be called as part of ChromosomeFile's constructor.**
If eager is set to False, these methods may be called individually. 

N.B. that workflow items 3 and 4 require that self.openfile() first be called; otherwise an assertion error will be thrown.

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

When run from the command line, the arguments are (required args marked with two stars):
-i, input_filename (**) : the fasta file to be read : type string
-s, start_pos (**) : the chromosomal coordinate of the beginning of the chromosome : type int
-p, path (default current directory) : the path to the input file : type string
-o, output_filename (default input_filename) : the prefix for the output : type string
-x, strip_needed (default True) : whether repretitive NNN needs to be removed from the fasta file : type bool
-c, cleanup (default True) : whether temporary files should be deleted after scan : type bool


"""

#REWRITE ENTIRE TEST MODULE
#CONSIDER PROTECTING CLASS ATTRIBUTES

import sys
import os
import argparse

def reverse_complement(dna_string):
	complement_dict = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N', 'n': 'n', 'a': 't', 't':'a', 'c':'g', 'g':'c'}
	rev_comp_string = ''
	for base in dna_string:
		rev_comp_string += complement_dict[base]
	return rev_comp_string

class GuideRNA(object):
	def __init__(self, sequence, start_coord, end_coord, chromosome_num):
		"""Basic class to represent and score guide RNAs"""
		self.sequence = sequence
		self.range = (start_coord, end_coord)
		self.chromosome_num = chromosome_num
		self.lowerscore = 0 #number of lower case letters in sequence; proxy for repeat content
		self.nscore = 0 #number of unidentifiable base pairs in sequence
		for item_idx, item in enumerate(self.sequence):
				if item != self.sequence.upper()[item_idx]:
					self.lowerscore += 1
				if item.upper() == 'N':
					self.nscore += 1

	def __str__(self):
		return str((self.sequence, self.range, self.lowerscore, self.nscore, self.chromosome_num))

	def write_to_file(self, outputfile):
		with open(outputfile, 'a') as fi:
			fi.write('chr'+str(self.chromosome_num)+'\t'+str(self.range[0])+'\t'+str(self.range[1])+'\t'+self.sequence+'\t'+str(self.nscore)+'\t'+str(self.lowerscore)+'\n')


class ChromosomeFile(object):
	def __init__(self, input_filename, start_pos, path = '', output_filename = None, strip_needed = True, cleanup = True, eager = True):
		self.path = path #path to input and output files

		self.inputfile = input_filename + '.txt'

		#by default, outputfile is same name as inputfile
		if not output_filename:
			self.outputfile = self.inputfile
		else:
			self.outputfile = output_filename

		
		self.strip = strip_needed #flag to indicate whether chromosome file starts and ends with repetitive NNN that need to be removed
		self.cleanup = cleanup #flag to indicate whether intermediate files should be deleted at end
		self.file = False #makes sure that self.openfile() has been called before self.scan_bidirection()

		#special attributes for chromosomal scans - should __protect
		self.chrom_start = start_pos
		self.linecounter = 0
		self.chromosome_num = ''
		self.chrom_window = ''

		if eager:
			self.workflow(strip_needed)
			

	def workflow(self):
		#if fasta file for chromosome starts and ends with repetitive N sequences, this option will remove them
			if self.strip:
				self.strip_fasta_file(self.inputfile)
				self.openfile(self.inputfile.replace('.txt', '_edited_double_reordered.txt'))
			else:
				self.openfile(self.inputfile)
			self.scan_bidirection()
			self.filemerge()
			if self.cleanup:
				self.clean_intermediate_files()


	def openfile(self, filename):
		self.file = open(self.path + filename)

	def closefile(self):
		self.file.close()

	@staticmethod
	def initialize_output_file(filename):
		with open(filename, 'w') as fo: #initialize output file
			fo.write('CHR#'+'\t'+'START'+'\t'+'STOP'+'\t'+'SEQUENCE'+'\t'+'N_COUNT'+'\t'+'N_LOWERCASE'+'\n')

	def strip_fasta_file(self, filen): #REFACTOR INTO SMALLER FUNCTION PIECES
		flag = False
		readfile = open(self.path+filen, 'r')
		writefile = open(self.path+filen.replace('.txt','_edited.txt'), 'a')
		for idx, line in enumerate(readfile):
			if line.strip() == "N"*len(line.strip()) and not flag: #flag lets us leave NNNN in middle of file alone
				pass
			else:
				if idx!=0:
					flag = True
				writefile.write(line.strip())
				writefile.write('\n')

		readfile.close()
		writefile.close()


		#remove repetitive NNNNN from end of file
		flag = False
		readfile = open(self.path+filen.replace('.txt','_edited.txt'), 'r')
		writefile = open(self.path+filen.replace('.txt', '_edited_double.txt'), 'a')

		for line in reversed(readfile.readlines()):
			if line.strip() == "N"*len(line.strip()) and not flag:
				pass
			else:
				flag = True
				writefile.write(line.strip())
				writefile.write('\n')

		readfile.close()
		writefile.close()

		#undo reversal caused by removing from end
		readfile = open(self.path+filen.replace('.txt', '_edited_double.txt'), 'r')
		writefile = open(self.path+filen.replace('.txt', '_edited_double_reordered.txt'), 'a')

		for line in reversed(readfile.readlines()):
				writefile.write(line.strip())
				writefile.write('\n')

		readfile.close()
		writefile.close()

	def delete_file(self, filename):
		if os.path.isfile(self.path+filename):
			os.remove(self.path+filename)
		else:
			print(filename, ' not found in directory ', self.path)

	def clean_intermediate_files(self):
		temp_files = [self.inputfile.replace('.txt', i) for i in ('_edited_double_reordered.txt', '_edited_double.txt', '_edited.txt', '_F.txt', '_R.txt')]
		for f in temp_files:
			self.delete_file(f)

	def forward_scan(self, char, char_idx):
		assert self.file
		if char.upper() == self.chrom_window[char_idx+1].upper() == "G": #guide RNA should be 20bp+NGG
			try:
				guide = self.chrom_window[char_idx-21:char_idx+2]

				if not self.chrom_start + self.window_start + char_idx - 21 in self.start_positions_fwd.keys(): #this helps avoid duplicates
					rna = GuideRNA(guide, self.chrom_start + self.window_start + char_idx - 21, self.chrom_start + self.window_start + char_idx + 1, self.chromosome_num)
					rna.write_to_file(self.path + self.outputfile.replace('.txt','_F.txt'))
					self.start_positions_fwd[self.chrom_start+self.window_start+char_idx-21] = True #remember that we already captured this guide
					#print('\t'+ str(self.chrom_start + self.window_start + char_idx)+ '     ' + guide)
				else:
					pass
					#print(self.chrom_start + self.window_start + char_idx)

			except IndexError: #this seems to happen sometimes, not sure why
				pass

	def reverse_scan(self, char, char_idx):
		assert self.file
		if char.upper() == self.chrom_window[char_idx+1].upper() == "C": #guide RNA should be 20bp+NGG
			try:
				guide = self.chrom_window[char_idx:char_idx+24]

				if not self.chrom_start + self.window_start + char_idx in self.start_positions_rev.keys(): #this helps avoid duplicates
					rna = GuideRNA(guide, self.chrom_start + self.window_start + char_idx, self.chrom_start + self.window_start + char_idx + 23, self.chromosome_num)
					rna.write_to_file(self.path + self.outputfile.replace('.txt','_R.txt'))
					self.start_positions_rev[self.chrom_start + self.window_start + char_idx] = True #remember that we already captured this guide
					#print('\t'+ str(self.chrom_start + self.window_start + char_idx))
				else:
					pass
					#print(self.chrom_start + self.window_start + char_idx)

			except IndexError: #this seems to happen sometimes, not sure why
				pass

	def scan_bidirection(self):
		assert self.file
		self.start_positions_fwd = {}
		self.start_positions_rev = {}
		self.window_start = 0

		self.initialize_output_file(self.path + self.outputfile.replace('.txt','_F.txt'))
		self.initialize_output_file(self.path + self.outputfile.replace('.txt','_R.txt'))

		#first line contains chromosome ID
		line = self.file.next()
		self.chromosome_num = line[line.index('r')+1:].strip()

		#load two more lines into the sliding window to initialize
		line = self.file.next()
		self.chrom_window += line.strip()

		line = self.file.next()
		self.linelen = len(line.strip())
		
		self.linecounter += 3

		while line:

			self.chrom_window += line.strip()

			if not self.linecounter % 10:
				self.start_positions_fwd = {} #empty cache every 10 lines to avoid overflow
				self.start_positions_rev = {}

			for char_idx, char in enumerate(self.chrom_window[0:-1]):
				if char_idx >= 21:
					self.forward_scan(char, char_idx)

				if char_idx <= 100-24: #make sure we don't try to slice outside the string
					self.reverse_scan(char, char_idx)

			else:
				self.chrom_window = self.chrom_window[self.linelen:] #advance window forward
				self.window_start += self.linelen
				try:
					line = self.file.next()
				except StopIteration: #file generator has reached end
					return
				self.linecounter += 1
			
		self.closefile()

	def filemerge(self):
		assert self.file
		with open(self.path+self.outputfile.replace('.txt', '_mergedguides.txt'), 'a') as fNew:

			with open(self.path+self.outputfile.replace('.txt','_F.txt'), 'r') as fF:
				#first process forward sequence
				for i, line in enumerate(fF):
					if i:
						fNew.write(line.strip() + '\t' + 'F') #F indicates forward direction
						fNew.write('\n')
					else:
						#add a new field to the first line: direction of the sequence
						fNew.write(line.strip() + '\t' + 'DIRECTION')
						fNew.write('\n')


			with open(self.path+self.outputfile.replace('.txt','_R.txt'), 'r') as fR:
				#second, process reverse sequence
				for i, line in enumerate(fR):
					if i:
						fNew.write(line.strip() + '\t' + 'R')
						fNew.write('\n')
					else:
						pass #ignore the header from the reverse sequence, as our file already has a header




def scan(inputfile, chrom_start, workingdir = ''):
	"""Helper function to construct ChromosomeFile object with default arguments"""
	CF = ChromosomeFile(inputfile, chrom_start, path = workingdir)


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
	

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = "Configure ChromosomeFile object")
	
	parser.add_argument('-i', action="store", dest="input_filename", type=str)
	parser.add_argument('-s', action="store", dest="start_pos", type=int, default=0)
	parser.add_argument('-p', action="store", dest="path", type=str, default='')
	parser.add_argument('-o', action="store", dest="output_filename", type=str, default=None)
	parser.add_argument('-x', action="store", dest="strip_needed", type=bool, default=True)
	parser.add_argument('-c', action="store", dest="cleanup", type=bool, default=True)

	results = parser.parse_args()

	CF = ChromosomeFile(results.input_filename, results.start_pos, results.path, results.output_filename, results.strip_needed, results.cleanup, eager = False)

	with ContextManager(CF):
		CF.workflow()



