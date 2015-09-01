# CRISpy
Gene editing made easy

## Finding all guideRNA sequences in a genome
Run the script gen_guideRNA to find all potential guideRNA sequences for  set of chromosome files (as text files).
Parameters are -f, a text file containing the names of each chromosome files as one column and the coordinate of the beginning of each chromosome's sequence as the second column;
and -p, the path to the file containing the chromosome files.

pypy or other JIT-compiled build of Python strongly recommended!

Sample command:
pypy gen_guideRNA.py -f chrm_starts.txt -p /users/jondoe/genome/
