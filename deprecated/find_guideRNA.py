
import sys, getopt

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
		#assert len(sequence) == end_coord - start_coord
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
	def __init__(self, input_filename, start_pos, output_filename):
		self.inputfile = input_filename
		self.outputfile = output_filename
		self.chrom_start = start_pos
		self.linecounter = 0
		self.file = open(self.inputfile)
		self.chromosome_num = ''
		self.chrom_window = ''

	def closefile(self):
		self.file.close()

	def initialize_output_file(self, filename):
		with open(filename, 'w') as fo: #initialize output file
			fo.write('CHR#'+'\t'+'START'+'\t'+'STOP'+'\t'+'SEQUENCE'+'\t'+'N_COUNT'+'\t'+'N_LOWERCASE'+'\n')

	def forward_scan(self, char, char_idx):
		if char.upper() == self.chrom_window[char_idx+1].upper() == "G": #guide RNA should be 20bp+NGG
			try:
				guide = self.chrom_window[char_idx-21:char_idx+2]

				if not self.chrom_start + self.window_start + char_idx - 21 in self.start_positions_fwd.keys(): #this helps avoid duplicates
					rna = GuideRNA(guide, self.chrom_start + self.window_start + char_idx - 21, self.chrom_start + self.window_start + char_idx + 1, self.chromosome_num)
					rna.write_to_file(self.outputfile+'_F.txt')
					self.start_positions_fwd[self.chrom_start+self.window_start+char_idx-21] = True #remember that we already captured this guide
				else:
					pass

			except IndexError: #this seems to happen sometimes, not sure why
				pass

	def reverse_scan(self, char, char_idx):
		if char.upper() == self.chrom_window[char_idx+1].upper() == "C": #guide RNA should be 20bp+NGG
			try:
				guide = self.chrom_window[char_idx:char_idx+24]

				if not self.chrom_start + self.window_start + char_idx in self.start_positions_rev.keys(): #this helps avoid duplicates
					rna = GuideRNA(guide, self.chrom_start + self.window_start + char_idx, self.chrom_start + self.window_start + char_idx + 23, self.chromosome_num)
					rna.write_to_file(self.outputfile+'_R.txt')
					self.start_positions_rev[self.chrom_start + self.window_start + char_idx] = True #remember that we already captured this guide
				else:
					pass

			except IndexError: #this seems to happen sometimes, not sure why
				pass

	def scan_bidirection(self):
		self.start_positions_fwd = {}
		self.start_positions_rev = {}
		self.window_start = 0

		self.initialize_output_file(self.outputfile+'_F.txt')
		self.initialize_output_file(self.outputfile+'_R.txt')

		#first line contains chromosome ID
		line = self.file.next()
		self.chromosome_num = line[line.index('r')+1:].strip()

		#load two more lines into the sliding window to initialize
		line = self.file.next()
		self.chrom_window += line.strip()

		line = self.file.next()
		
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
				self.chrom_window = self.chrom_window[50:] #advance window forward
				self.window_start += 50
				try:
					line = self.file.next()
				except StopIteration: #file generator has reached end
					return
				self.linecounter += 1
			
		self.closefile()	
	

def scan_chromosome_dynamic_bidirection(inputfile, chrom_start, outputfile):
	"""Combines scan_chromosome() and fasta_to_chrom_string() into a single function. Scan through
	chromosome using a 50bp sliding window. Once the window slides beyond a given 50bp line, dump that
	from memory and advance the window."""
	CF = ChromosomeFile(inputfile, chrom_start, outputfile)
	CF.scan_bidirection()


def main(argv):
	print(argv)
	inputfile, chrm_start, outputfile = argv 
	scan_chromosome_dynamic_bidirection(inputfile, int(chrm_start), outputfile)

if __name__ == "__main__":
	main(sys.argv[1:]) #first element in argv is the script name; don't want this
	#command line example: python find_guideRNA.py "C:\Users\Phil\Desktop\Genome\chr1_noN.txt" 10001 'chr1_guides'

