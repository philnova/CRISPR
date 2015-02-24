
import sys, getopt

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

def scan_chromosome(chromosome, start_coord, output_file):

	"""Single forward scan through chromosome. Input chromosome as list of (chromosome number, string) and UCSC absolute starting coordinate.
	Output list of potential guide RNAs, with each guide represented using a basic class. Also store this information in a tab delimited text file
	of chromosome number, starting coord, ending coord, sequence, # of uncallable bases in sequence, # of lowercase letters
	in sequence."""
	
	with open(output_file, 'w') as fo:
		fo.write('CHR#'+'\t'+'START'+'\t'+'STOP'+'\t'+'SEQUENCE'+'\t'+'N_COUNT'+'\t'+'N_LOWERCASE'+'\n')

	chromosome_num = int(chromosome[0][chromosome[0].index('r')+1::]) #first line is always ">chr##"
	chromosome_string = chromosome[1]
	guide_RNA = []

	for char_idx, char in enumerate(chromosome_string): #actual chromosomal content is second item in list
		if char_idx - 21 >= 0 and char_idx <= len(chromosome_string)-2: #make sure we don't go outside the text
			if char.upper() == chromosome_string[char_idx+1].upper() == "G": #guide RNA should be 20bp+NGG
				try:
					guide = chromosome_string[char_idx-21:char_idx+2]
					rna = GuideRNA(guide, start_coord + char_idx - 21, start_coord + char_idx + 1, chromosome_num)
					guide_RNA.append(rna)
					with open(output_file, 'a') as fo:
						fo.write('chr'+str(rna.chromosome_num)+'\t'+str(rna.range[0])+'\t'+str(rna.range[1])+'\t'+rna.sequence+'\t'+str(rna.nscore)+'\t'+str(rna.lowerscore)+'\n')
					#print GuideRNA(guide, start_coord + char_idx - 21, start_coord + char_idx + 1, chromosome_num)
				except IndexError:
					pass
	return guide_RNA

def fasta_to_chrom_string(filename):
	"""Turn fasta file for chromosome into a list of (chromosome number, sequence)
	Should not be used for very large chromosomes (e.g. Chrm 1) as will cause a
	memory overflow."""
	with open(filename, 'r') as fo:
		chrm = []
		chrm_string = ''
		for idx, line in enumerate(fo):
			if not idx%100000:
				print "parsed "+str(idx)+" lines"
			if line[0] == '>':
				chrm.append(line)
			else:
				chrm_string += line.strip()
		chrm.append(chrm_string)
	print "parsing complete"
	return chrm

def scan_chromosome_dynamic(inputfile, chrom_start, outputfile):
	"""Combines scan_chromosome() and fasta_to_chrom_string() into a single function. Scan through
	chromosome using a 50bp sliding window. Once the window slides beyond a given 50bp line, dump that
	from memory and advance the window."""

	chrom_window = "" #initialize cache

	window_start = 0

	start_positions = {}

	with open(outputfile, 'w') as fo: #initialize output file
		fo.write('CHR#'+'\t'+'START'+'\t'+'STOP'+'\t'+'SEQUENCE'+'\t'+'N_COUNT'+'\t'+'N_LOWERCASE'+'\n')

	
	with open(inputfile, 'r') as fo:
		for line_num, line in enumerate(fo): #enumerate() uses .next() so we do not maintain the whole file object in cache
			if line_num == 0: #note chromosome number on 0th line
				chromosome_num = int(line[line.index('r')+1:])
			elif line_num in (1,2): #start with a 100bp window
				chrom_window += line.strip()
			else:
				if not line_num % 10:
					start_positions = {} #empty hash table every 10 lines to avoid overflow
				chrom_window += line.strip() #load the latest line into cache

				#loop through cache and look for guide RNAs
				for char_idx, char in enumerate(chrom_window[0:-1]):
					if char_idx >= 21: #make sure we don't try to slice outside the string
						if char.upper() == chrom_window[char_idx+1].upper() == "G": #guide RNA should be 20bp+NGG

							try:
								guide = chrom_window[char_idx-21:char_idx+2]

								if not chrom_start + window_start + char_idx - 21 in start_positions.keys(): #this helps avoid duplicates
									rna = GuideRNA(guide, chrom_start + window_start + char_idx - 21, chrom_start + window_start + char_idx + 1, chromosome_num)
									with open(outputfile, 'a') as fi:
										fi.write('chr'+str(rna.chromosome_num)+'\t'+str(rna.range[0])+'\t'+str(rna.range[1])+'\t'+rna.sequence+'\t'+str(rna.nscore)+'\t'+str(rna.lowerscore)+'\n')
									start_positions[chrom_start+window_start+char_idx-21] = True #remember that we already captured this guide
								else:
									pass

							except IndexError: #this seems to happen sometimes, not sure why
								pass

					

				else:
					chrom_window = chrom_window[50:] #advance window forward
					window_start += 50
					

				

			

		

#scan_chromosome_dynamic("C:\Users\Phil\Desktop\Genome\chr22_noN.txt", 16050001, 'test.txt')
#guides = scan_chromosome(fasta_to_chrom_string("C:\Users\Phil\Desktop\Genome\chr1_noN.txt"), 10001, 'chr1_F_guides.txt')

def main(argv):
	inputfile, chrm_start, outputfile = argv 
	scan_chromosome_dynamic(inputfile, chrm_start, outputfile)

if __name__ == "__main__":
	main(sys.argv[1:]) #first element in argv is the script name; don't want this
	#command line example: python find_guideRNA.py "C:\Users\Phil\Desktop\Genome\chr1_noN.txt" 10001 'chr1_F_guides.txt'

