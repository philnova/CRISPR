import find_guideRNA as find
import timing
import argparse



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
	
	PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/"
	FILENAME = 'test_starts.txt'


	parser = argparse.ArgumentParser(description = "Path to chromosome files and start sites")
	parser.add_argument('-p', action="store", dest="path", type=str, default=PATH)
	parser.add_argument('-f', action="store", dest="filename", type=str, default=FILENAME)

	results = parser.parse_args()
	PATH = results.path
	
	main(results.filename)