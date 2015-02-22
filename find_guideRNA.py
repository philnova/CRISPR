
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

	for char_idx, char in enumerate(chromosome[1]): #actual chromosomal content is second item in list
		if char_idx - 21 >= 0: #make sure we don't go outside the text
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
	"""Turn fasta file for chromosome into a list of (chromosome number, sequence)"""
	with open(filename, 'r') as fo:
		chrm = []
		chrm_string = ''
		for line in fo:
			if line[0] == '>':
				chrm.append(line)
			else:
				chrm_string += line.strip()
		chrm.append(chrm_string)
	return chrm

guides = scan_chromosome(fasta_to_chrom_string('chrm22_edited.txt'), 16050001, 'guide_test.txt')

def output_guides(guide_list, filename):
	"""Deprecated"""
	with open(filename, 'w') as fo:
		fo.write('CHR#'+'\t'+'START'+'\t'+'STOP'+'\t'+'SEQUENCE'+'N_COUNT'+'\t'+'N_LOWERCASE')
		for guide in guide_list:
			fo.write('chr'+guide.chromosome_num+'\t'+guide.range[0]+'\t'+guide.range[1]+'\t'+guide.sequence+'\t'+guide.nscore+'\t'+guide.lowerscore+'\n')

	return

#output_guides(guides, 'guide_test.txt')