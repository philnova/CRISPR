"""Quick script to remove lines of "NNNNNN...." from the start of FASTA files."""



def main(path, filenames):
	for filen in filenames:
		#remove repetitive NNNNN from beginning of file
		flag = False
		readfile = open(path+filen+'.txt', 'r')
		writefile = open(path+filen+'_edited.txt', 'a')
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
		readfile = open(path+filen+'_edited.txt', 'r')
		writefile = open(path+filen+'_edited_double.txt', 'a')

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
		readfile = open(path+filen+'_edited_double.txt', 'r')
		writefile = open(path+filen+'_edited_double_reordered.txt', 'a')

		for line in reversed(readfile.readlines()):
				writefile.write(line.strip())
				writefile.write('\n')

		readfile.close()
		writefile.close()

if __name__ == "__main__":
	FILENAMES = ["chr"+str(i) for i in range(1,23)]
	FILENAMES.extend(['chrX', 'chrY'])
	PATH = '/Users/philnova/Desktop/Human Genome/Complete Chromosomes/'
	main(PATH, FILENAMES)

	
	