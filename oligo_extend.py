"""
Set of tools to pull out pairs of short human and chimp HARs and
extend both along their orthologous long HARs.

Each short human HAR will be extended the exact same amount as the
corresponding short chimp HAR, until both strings have at least
171 bases (in addition to however many escape characters are picked
up during traversal).
"""



##########################################
################ GLOBALS #################
##########################################



import random
import sys
import getopt

DASH_TOLERANCE = 25 #total number of dashes allowed on one side of the extension
REPEAT_TOLERANCE = 8
FILENAME_SHORT = "HAR_information_table.txt"
FILENAME_LONG = "Extended_HAR_information_table.txt"
OUTPUT = "final_hars.txt"

# N.B. the following HARs are in the Extended file but not the short file:
# 2xHAR.521
# 2xHAR.387
# 2xHAR.169
# 2xHAR.538
# All HARs in the short file are in the extended file



##########################################
################ HELPERS #################
##########################################

def prune(string1, string2):
	"""Remove any leading or ending dashes common to both strings."""
	while True:
		if string1[0] == string2[0] == "-":
			string1 = string1[1:]
			string2 = string2[1:]
		elif string1[-1] == string2[-1] == "-":
			string1 = string1[:-1]
			string2 = string2[:-1]
		else:
			return string1, string2


def harfile_parse(filename):
	filedict = {}
	with open(filename) as fo:
		for line in fo:
			filedict[line.split()[0]] = line.split()[1::]
	return filedict


def create_string(length, dash_prob = 0.1):
	initial = [random.choice(['A', 'G', 'C', 'T']) for dummy in range(length)]
	modified = [i if random.random() > dash_prob else '-' for i in initial]
	return ''.join(modified)


def len_without_dashes(string):
	counter = 0
	#dash_counter = 0
	for char in string:
		if not char == "-":
			counter += 1
		#else:
			#dash_counter += 1
	return counter #, dash_counter


def check_repeat(string, repeat_tolerance = 1000, check_from = "left"):
	if check_from == "right":
		string = "".join([i for i in reversed(string)])

	if len(string) < repeat_tolerance:
		return False

	i = 1
	while i < repeat_tolerance:
		if string[i] == "-":
			return False
		else:
			if string[i] == string[i-1]:
				pass
			else:
				return False
		i+=1
	return True



##########################################
############### STRUCTURES ###############
##########################################



class Oligo(object):

	def __init__(self, short_string, longer_string):
		self.string = short_string
		self.length = len(self.string)
		self.longer_string = longer_string


class OligoPair(object):

	def __init__(self, oligo1, oligo2):
		self.oligo1 = oligo1
		self.oligo2 = oligo2
		self.oligos = [oligo1, oligo2]


	def extend(self, target_length, gap_tolerance = DASH_TOLERANCE, repeat_tolerance = REPEAT_TOLERANCE, escape_chars = {"-" : 1}):
		oligo1 = self.oligo1
		oligo2 = self.oligo2
		self.error = []

		for oligo in (oligo1, oligo2):
			oligo.substring_start = oligo.longer_string.find(oligo.string)
			oligo.substring_end = oligo.substring_start + oligo.length

			oligo.left_string = ""
			oligo.right_string = ""
			oligo.extend_left, oligo.extend_right = True, True
			oligo.extension_left, oligo.extension_right = 0, 0
			oligo.gaps_left, oligo.gaps_right = 0, 0

		if len_without_dashes(oligo1.string) > target_length:
			self.error.append(" human oligo already exceeds target ")
		if len_without_dashes(oligo2.string) > target_length:
			self.error.append(" chimp oligo already exceeds target ")

		while len_without_dashes(oligo1.left_string + oligo1.string + oligo1.right_string) < target_length or len_without_dashes(oligo2.left_string + oligo2.string + oligo2.right_string) < target_length:
			if not ((oligo1.extend_left and oligo2.extend_left) or (oligo1.extend_right and oligo2.extend_right)):
				self.error.append(" no further extension possible ")
				break

			if oligo1.extend_left and oligo2.extend_left:
				current_char_l1 = oligo1.longer_string[oligo1.substring_start - 1]
				current_char_l2 = oligo2.longer_string[oligo2.substring_start - 1]
				
				if not current_char_l1 in escape_chars.keys():
					oligo1.extension_left += 1
				else:
					oligo1.gaps_left += 1 #escape_chars[current_char]

				if not current_char_l2 in escape_chars.keys():
					oligo2.extension_left += 1
				else:
					oligo2.gaps_left += 1

				
				oligo1.left_string = current_char_l1 + oligo1.left_string
				oligo1.substring_start -= 1

				oligo2.left_string = current_char_l2 + oligo2.left_string
				oligo2.substring_start -= 1

				if oligo1.substring_start == 1:
					oligo1.extend_left = False
					self.error.append(" left limit reached in human sequence ")
				if oligo2.substring_start == 1:
					oligo2.extend_left = False
					self.error.append(" left limit reached in chimp sequence ")

				if oligo1.gaps_left > gap_tolerance:
					oligo1.extend_left = False
					self.error.append(" too many gaps on left side of human sequence ")
				if oligo2.gaps_left > gap_tolerance:
					oligo2.extend_left = False
					self.error.append(" too many gaps on left side of chimp sequence ")

				if check_repeat(oligo1.left_string, REPEAT_TOLERANCE, "left"):
					oligo1.extend_left = False
					self.error.append(" repeat on left side of human sequence ")
				if check_repeat(oligo2.left_string, REPEAT_TOLERANCE, "left"):
					oligo2.extend_left = False
					self.error.append(" repeat on left side of chimp sequence ")

			if len_without_dashes(oligo1.left_string + oligo1.string + oligo1.right_string) >= target_length and len_without_dashes(oligo2.left_string + oligo2.string + oligo2.right_string) >= target_length:
				break

			if oligo1.extend_right and oligo2.extend_right:

				current_char_r1 = oligo1.longer_string[oligo1.substring_end]
				current_char_r2 = oligo2.longer_string[oligo2.substring_end]

				if not current_char_r1 in escape_chars.keys():
					oligo1.extension_right += 1
				else:
					oligo1.gaps_right += 1 #escape_chars[current_char]

				if not current_char_r2 in escape_chars.keys():
					oligo2.extension_right += 1
				else:
					oligo2.gaps_right += 1

				oligo1.right_string += current_char_r1
				oligo1.substring_end += 1

				oligo2.right_string += current_char_r2
				oligo2.substring_end += 1

				if oligo1.substring_end == len(oligo1.longer_string):
					oligo1.extend_right = False
					self.error.append(" right limit reached in human sequence ")
				if oligo2.substring_end == len(oligo2.longer_string):
					oligo2.extend_right = False
					self.error.append(" right limit reached in chimp sequence ")

				if oligo1.gaps_right > gap_tolerance:
					oligo1.extend_left = False
					self.error.append(" too many gaps on right side of human sequence ")
				if oligo2.gaps_right > gap_tolerance:
					oligo2.extend_left = False
					self.error.append(" too many gaps on right side of chimp sequence ")

				if check_repeat(oligo1.right_string, REPEAT_TOLERANCE, "right"):
					oligo1.extend_right = False
					self.error.append(" repeats on right side of human sequence ")
				if check_repeat(oligo2.right_string, REPEAT_TOLERANCE, "right"):
					oligo2.extend_right = False
					self.error.append(" repeats on right side of chimp sequence ")

		oligo1.extended_string = oligo1.left_string + oligo1.string + oligo1.right_string
		oligo2.extended_string = oligo2.left_string + oligo2.string + oligo2.right_string

		self.error = list(set(self.error))
		error_msg = "".join(self.error)


		return oligo1.extended_string, oligo2.extended_string, error_msg


def mainloop(input_short, input_long, output, target_length, verbose = True, gap_tolerance = DASH_TOLERANCE, repeat_tolerance = REPEAT_TOLERANCE):
	shortfile = harfile_parse(FILENAME_SHORT)
	longfile = harfile_parse(FILENAME_LONG)

	with open(output, 'w') as fo:
			fo.write("HAR NAME" + '\t' + "HUMAN SEQ" + '\t' + "BP IN SEQ" + "\t" + "TOTAL LEN" + '\t' + "CHIMP SEQ" '\t' + "BP IN SEQ" + "\t" + "TOTAL LEN" + '\t' + "LOG")
			fo.write('\n')

	for key in shortfile.keys():
		
		humanshort, humanlong = shortfile[key][2], longfile[key][2]
		chimpshort, chimplong = shortfile[key][5], longfile[key][5]

		olig_human = Oligo(humanshort, humanlong)
		olig_chimp = Oligo(chimpshort, chimplong)

		olig_pair = OligoPair(olig_human, olig_chimp)
		longer_human, longer_chimp, error_message = olig_pair.extend(target_length, gap_tolerance, repeat_tolerance)

		longer_human, longer_chimp = prune(longer_human, longer_chimp)

		with open(output, 'a') as fo:
			fo.write(key + '\t' + longer_human + '\t' + str(len_without_dashes(longer_human)) + '\t' + str(len(longer_human)) + '\t' + longer_chimp + '\t' + str(len_without_dashes(longer_chimp)) + '\t' + str(len(longer_chimp)) + error_message)
			fo.write('\n')

		if verbose:
			print key
			print longer_human, len_without_dashes(longer_human), len(longer_human)
			print longer_chimp, len_without_dashes(longer_chimp), len(longer_chimp)
			print error_message
			print ""
	return


		

##########################################
################## MAIN ##################
##########################################

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "s:l:o:t:r:g:v:", ["shortfile=", "longfile=", "output=", "targetlenth=", "repeattolerance=", "gaptolerance=", "verbose="])

		target_length = 171
		repeattolerance = REPEAT_TOLERANCE
		gaptolerance = DASH_TOLERANCE
		verbose = True
		input_short = FILENAME_SHORT
		input_long = FILENAME_LONG
		output = "testfile.txt"

		if opts:
			for opt, arg in opts:
				if opt in ("-s", "--shortfile"):
					input_short = arg
				elif opt in ("-l", "--longfile"):
					input_long = arg
				elif opt in ("-o", "--output"):
					output = arg
				elif opt in ("-t", "--targetlength"):
					target_length = int(arg)
				elif opt in ("-r", "--repeattolerance"):
					repeattolerance = int(arg)
				elif opt in ("-g", "--gaptolerance"):
					gaptolerance = arg
				elif opt in ("-v", "--verbose"):
					verbose = bool(int(arg))
				else:
					raise ValueError("Error: unrecognized argument flag!")

		mainloop(input_short, input_long, output, target_length, verbose, gaptolerance, repeattolerance)
		print "output successful!"

	except getopt.GetoptError:
		raise ValueError("Error: unrecognized argument flag!")      
        #usage()                          
		sys.exit(2)  


if __name__ == "__main__":
	main(sys.argv[1:]) #sys.argv[0] is the name of the script; not useful

# if __name__ == "__main__":
# 	main(FILENAME_SHORT, FILENAME_LONG, OUTPUT)

	# long_string1, long_string2 = create_string(400), create_string(400)
	# short_string1, short_string2 = long_string1[100:250], long_string2[100:250]

	# o1 = Oligo(short_string1, long_string1)
	# o2 = Oligo(short_string2, long_string2)
	
	# op = OligoPair(o1, o2)
	# op.paired_extend(171)

	# #print op.oligo1.extended_string
	# #print op.oligo2.extended_string

	# #print op.oligo1.extended_string
	# #print len(op.oligo1.extended_string) - op.oligo1.gaps_left - op.oligo1.gaps_right
	# #print op.oligo1.gaps_left, op.oligo1.gaps_right
	# print len_without_dashes(op.oligo1.extended_string), len_without_dashes(op.oligo2.extended_string)
	# print op.oligo1.extend_left, op.oligo1.extend_right

	# print len(op.oligo1.extended_string), len(op.oligo2.extended_string)





