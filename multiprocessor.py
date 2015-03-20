import find_guideRNA as find

PATH = "C:\Users\Phil\Desktop\Genome\Cleaned files\\"

with open(PATH+"_chromosome_map.txt") as file:
	for line in file:
		inputfile, chrm_start = line.split()[0], int(line.split()[1])
		print inputfile, chrm_start
		try:
			find.scan_chromosome_dynamic_bidirection(PATH+inputfile, chrm_start, PATH+inputfile+'out')
			print 'success'
		except:
			print 'fail'
		#print inputfile