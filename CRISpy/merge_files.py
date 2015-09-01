
import multiprocessing

PATH = ''

def worker(filename):
	with open(PATH+filename+'_mergedguides.txt', 'a') as fNew:

		with open(PATH+filename+modifier.replace('.txt','_F.txt'), 'r') as fF:
			for i, line in enumerate(fF):
				if i:
					fNew.write(line.strip() + '\t' + 'F')
					fNew.write('\n')
				else:
					fNew.write(line.strip() + '\t' + 'DIRECTION')
					fNew.write('\n')


		with open(PATH+filename+modifier.replace('.txt','_R.txt'), 'r') as fR:
			for i, line in enumerate(fR):
				if i:
					fNew.write(line.strip() + '\t' + 'R')
					fNew.write('\n')
				else:
					pass
	print filename, ' success! :)'


def main(path, chromosome_filename, mod = '.txt'):
	global PATH
	global modifier
	PATH = path
	modifier = mod

	filenames = []

	with open(chromosome_filename) as fo:
		for line in fo:
			filename = line.strip().split()[0]
			filenames.append(filename)

	pool = multiprocessing.Pool(multiprocessing.cpu_count()) #limit pool to number of cores
	pool.map(worker, filenames)

if __name__ == "__main__":


	PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/GuideRNA/"
	main(PATH, CHROMOSOMES, '.txt')