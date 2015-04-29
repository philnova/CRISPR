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

FILENAME_SHORT = "HAR_information_table.txt"
FILENAME_LONG = "Extended_HAR_information_table.txt"
OUTPUT = "test.txt"

# N.B. the following HARs are in the Extended file but not the short file:
# 2xHAR.521
# 2xHAR.387
# 2xHAR.169
# 2xHAR.538
# All HARs in the short file are in the extended file



##########################################
################ HELPERS #################
##########################################



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


def check_repeat(string, repeat_tolerance = 8, check_from = "left"):
	if check_from == "right":
		string = "".join([i for i in reversed(string)])

	if len(string) < repeat_tolerance:
		return False

	i = 1
	while i < repeat_tolerance:
		if string[i] == string[i-1] and not string[i] == "-":
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

	def extend(self, target_length = 171, repeat_tolerance = 8, escape_chars = {"-" : 1}, gap_tolerance = 25):
		self.substring_start = self.longer_string.find(self.string)
		self.substring_end = self.substring_start + self.length

		self.left_string = ""
		self.right_string = ""
		extend_left, extend_right = True, True
		self.extension_left, self.extension_right = 0, 0
		self.gaps_left, self.gaps_right = 0, 0

		error_message = ""

		#march outward on both sides
		while len_without_dashes(self.left_string + self.string + self.right_string) < target_length:
			if extend_left:
				current_char = self.longer_string[self.substring_start - 1]
				
				if not current_char in escape_chars.keys():
					
					self.extension_left += 1
					
				else:
					self.gaps_left += 1 #escape_chars[current_char]
				
				self.left_string = current_char + self.left_string
				self.substring_start -= 1

			if len_without_dashes(self.left_string + self.string + self.right_string) == target_length:
				break

			if extend_right:
				current_char = self.longer_string[self.substring_end]

				if not current_char in escape_chars.keys():
					
					self.extension_right += 1
				else:
					self.gaps_right += 1 #escape_chars[current_char]

				self.right_string += current_char
				self.substring_end += 1

			#check whether repeat condition is violated
			if extend_left:
				if self.substring_start == 1:
					extend_left = False
					error_message += "reached far left "

				if self.gaps_left <= gap_tolerance:
					extend_left = not check_repeat(self.left_string, repeat_tolerance, "left")
				else:
					extend_left = False
					error_message += "too many gaps on left "

			if extend_right:
				if self.substring_end == len(self.longer_string) - 1:
					extend_right = False
					error_message += "reached far right "

				if self.gaps_left <= gap_tolerance:
					extend_right = not check_repeat(self.right_string, repeat_tolerance, "right")
				else:
					extend_right = False
					error_message += "too many gaps on right "

			if not extend_left and not extend_right:
				print "No further extension possible"
				print error_message
				print self.gaps_left, self.gaps_right
				break

		self.extended_string = self.left_string + self.string + self.right_string

		print len(self.extended_string), len_without_dashes(self.extended_string)

		self.extend_left, self.extend_right = extend_left, extend_right
	
	def further_extend(self, amt_left=0, amt_right=0):
		try:
			self.left_string
		except:
			print "Error: Must call extend() before further_extend()!"
			return

		if amt_left and not self.extend_left:
			raise ValueError("Cannot extend left")
		if amt_right and not self.extend_right:
			raise ValueError("Cannot extend right")

		new_left_string, new_right_string = "", ""
		while amt_left:
			new_left_string = self.longer_string[self.substring_start - 1] + new_left_string
			amt_left -= 1
		while amt_right:
			new_right_string += self.longer_string[self.substring_end]
			amt_right -= 1

		self.extended_string = new_left_string + self.extended_string + new_right_string


class OligoPair(object):

	def __init__(self, oligo1, oligo2):
		self.oligo1 = oligo1
		self.oligo2 = oligo2

	def paired_extend(self, target_length):
		self.oligo1.extend(target_length)
		self.oligo2.extend(target_length)

		if not len(self.oligo1.extended_string) == len(self.oligo2.extended_string):

			#establish which is longer
			diff = len(self.oligo1.extended_string) - len(self.oligo2.extended_string)

			#need to extend the shorter string on left and right
			#take into account the number of gaps on each side, as well as whether we are allowed to keep extending to given side

			diff_left = self.oligo1.extension_left - self.oligo2.extension_left
			diff_right = self.oligo1.extension_right - self.oligo2.extension_right

			#assert (diff_left > 0 and diff_right > 0) or (diff_left < 0 and diff_right < 0)
			#assert diff == (self.oligo1.gaps_left - self.oligo2.gaps_left) + (self.oligo1.gaps_right - self.oligo2.gaps_right)

			if diff > 0:

				# oligo1 longer
				self.oligo2.further_extend(diff_left, diff_right)
			else:
				#oligo2 longer
				self.oligo1.further_extend(-diff_left, -diff_right)

		return self.oligo1.extended_string, self.oligo2.extended_string

def extend(input_short, input_long, output, target_length):
	shortfile = harfile_parse(FILENAME_SHORT)
	longfile = harfile_parse(FILENAME_LONG)

	for key in shortfile.keys():

		humanshort, humanlong = shortfile[key][2], longfile[key][2]
		chimpshort, chimplong = shortfile[key][5], longfile[key][5]

		olig_human = Oligo(humanshort, humanlong)
		olig_chimp = Oligo(chimpshort, chimplong)

		olig_pair = OligoPair(olig_human, olig_chimp)
		longer_human, longer_chimp = olig_pair.paired_extend(target_length)
		print longer_human
		print longer_chimp
	return


		

##########################################
################## MAIN ##################
##########################################



def main(input_short, input_long, output, target_length = 171):
	extend(input_short, input_long, output, target_length)

if __name__ == "__main__":
	main(FILENAME_SHORT, FILENAME_LONG, OUTPUT)

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





