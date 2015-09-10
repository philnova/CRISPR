"""Script to merge two guideRNA files for the same chromosome, one for the forward sequence
and one for the reverse sequence, into the same file."""


import multiprocessing

def worker(filename, path, modifier):
	with open(path+filename+'_mergedguides.txt', 'a') as fNew:

		with open(path+filename+modifier.replace('.txt','_F.txt'), 'r') as fF:
			#first process forward sequence
			for i, line in enumerate(fF):
				if i:
					fNew.write(line.strip() + '\t' + 'F') #F indicates forward direction
					fNew.write('\n')
				else:
					#add a new field to the first line: direction of the sequence
					fNew.write(line.strip() + '\t' + 'DIRECTION')
					fNew.write('\n')


		with open(path+filename+modifier.replace('.txt','_R.txt'), 'r') as fR:
			#second, process reverse sequence
			for i, line in enumerate(fR):
				if i:
					fNew.write(line.strip() + '\t' + 'R')
					fNew.write('\n')
				else:
					pass #ignore the header from the reverse sequence, as our file already has a header
	print(filename, ' success! :)')


def unpacker(args, function=worker):
	"""Quick helper function to use with pool.map"""
	function(*args)


def worker_test(path, filename, modifier):
	"""Testing-only version of worker."""
	with open(path+filename+'_mergedguides.txt', 'a') as fNew:
		with open(path+filename+modifier.replace('.txt','_F.txt'), 'r') as fF:
			for i, line in enumerate(fF):
				if i:
					fNew.write(line.strip() + '\t' + 'F')
					fNew.write('\n')
				else:
					fNew.write(line.strip() + '\t' + 'DIRECTION')
					fNew.write('\n')

		with open(path+filename+modifier.replace('.txt','_R.txt'), 'r') as fR:
			for i, line in enumerate(fR):
				if i:
					fNew.write(line.strip() + '\t' + 'R')
					fNew.write('\n')
				else:
					pass

def main(path, chromosome_filename, mod = '.txt'):
	modifier = mod

	filenames = []

	with open(chromosome_filename) as fo:
		for line in fo:
			filename = line.strip().split()[0]
			filenames.append(filename)

	pool = multiprocessing.Pool(multiprocessing.cpu_count()) #limit pool to number of cores
	pool.map(unpacker, [(f, path, modifier) for f in filenames])


if __name__ == "__main__":

	PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/GuideRNA/"
	main(PATH, CHROMOSOMES, '.txt')