import find_guideRNA as find
import time
import timing

PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/"

#Profiling: took 2659s to process chromosomes 21 and 22 (~=44 min, 1.5x slower than multiprocess_multiprocessor)

def main(filename):
	with open(filename) as file:
		for line in file:
			inputfile, chrm_start = line.split()[0], int(line.split()[1])
			print inputfile, chrm_start
			try:
				find.scan_chromosome_dynamic_bidirection(PATH+inputfile+'.txt', chrm_start, PATH+inputfile)
				print 'success :)'
			except:
				print 'fail :('
			#print inputfile

#with open('chr_starts.txt') as file:
if __name__ == "__main__":
	start = time.time()
	filename = 'test_starts.txt'
	main(filename)
	print time.time() - start