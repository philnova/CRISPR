Run the script gen_guideRNA to find all potential guideRNA sequences for set of chromosome files (as text files). Parameters are: -f, a text file containing the names of each chromosome files as one column and the coordinate of the beginning of each chromosome's sequence as the second column;

e.g. (human genome hg20): chr1.txt 10001 chr2.txt 10001 chr3.txt 10001 chr4.txt 10001 chr5.txt 10619 chr6.txt 60001 chr7.txt 10001 chr8.txt 60001 chr9.txt 10001 chr10.txt 10001 chr11.txt 60001 chr12.txt 10001 chr13.txt 16000001 chr14.txt 16000001 chr15.txt 17000001 chr16.txt 10001 chr17.txt 60001 chr18.txt 10001 chr19.txt 60001 chr20.txt 60001 chr21.txt 5010001 chr22.txt 10510001 chrX.txt 10001 chrY.txt 10001

and -p, the path to the file containing the chromosome files.

pypy or other JIT-compiled build of Python strongly recommended!

Sample command: pypy gen_guideRNA.py -f chrm_starts.txt -p /users/jondoe/genome/