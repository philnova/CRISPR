import find_guideRNA as find

PATH = "/Users/philnova/Desktop/Human Genome/Complete Chromosomes/Stripped Chromosomes/"


#with open('chr_starts.txt') as file:
with open('chr_starts_xy.txt') as file:
		for line in file:
			inputfile, chrm_start = line.split()[0], int(line.split()[1])
			print inputfile, chrm_start
			try:
				find.scan_chromosome_dynamic_bidirection(PATH+inputfile+'.txt', chrm_start, PATH+inputfile)
				print 'success'
			except:
				print 'fail'
			#print inputfile