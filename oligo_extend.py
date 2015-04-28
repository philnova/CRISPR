import random

def create_string(length, dash_prob = 0.1):
	initial = [random.choice(['A', 'G', 'C', 'T']) for dummy in range(length)]
	modified = [i if random.random() > dash_prob else '-' for i in initial]
	return ''.join(modified)

def check_repeat(string, repeat_tolerance = 8, check_from = "left"):
	if check_from == "right":
		string = "".join([i for i in reversed(string)])

	if len(string) < repeat_tolerance:
		return False

	i = 1
	while i < repeat_tolerance:
		if string[i] == string[i-1]:
			pass
		else:
			return False
		i+=1
	return True

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

		#march outward on both sides
		while self.length + self.extension_left + self.extension_right < target_length:
			if extend_left:
				current_char = self.longer_string[self.substring_start - 1]
				if not current_char in escape_chars.keys():
					self.left_string = current_char + self.left_string
					self.extension_left += 1
				else:
					self.gaps_left += escape_chars[current_char]
				self.substring_start -= 1

			if self.length + self.extension_left + self.extension_right == target_length:
				break

			if extend_right:
				current_char = self.longer_string[self.substring_end + 1]
				if not current_char in escape_chars.keys():
					self.right_string += current_char
					self.extension_right += 1
				else:
					self.gaps_right += escape_chars[current_char]
				self.substring_end += 1



			#check whether repeat condition is violated
			if extend_left:
				if self.substring_start == 1:
					extend_left = False

				if self.gaps_left <= gap_tolerance:
					extend_left = not check_repeat(self.left_string, repeat_tolerance, "left")
				else:
					extend_left = False

			if extend_right:
				if self.substring_end == len(self.longer_string) - 2:
					extend_right = False

				if self.gaps_left <= gap_tolerance:
					extend_right = not check_repeat(self.right_string, repeat_tolerance, "right")
				else:
					extend_right = False

		self.extended_string = self.left_string + self.string + self.right_string
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
		oligo1.extend(target_length)
		oligo2.extend(target_length)

		if not len(oligo1.extended_string) == len(oligo2.extended_string):

			#establish which is longer
			diff = len(oligo1.extended_string) - len(oligo2.extended_string)

			#need to extend the shorter string on left and right
			#take into account the number of gaps on each side, as well as whether we are allowed to keep extending to given side

			diff_left = oligo1.extension_left - oligo2.extension_left
			diff_right = oligo1.extension_right - oligo2.extension_right

			assert (diff_left and diff_right > 0) or (diff_left and diff_right < 0)
			assert diff == (oligo1.gaps_left - oligo2.gaps_left) + (oligo1.gaps_right - oligo2.gaps_right)

			if diff > 0:

				# oligo1 longer
				oligo2.further_extend(diff_left, diff_right)
			else:
				#oligo2 longer
				oligo1.further_extend(-diff_left, -diff_right)

		return oligo1.extended_string, oligo2.extended_string


def file_parse(filename):
	pass

def main(input_filename, output_filename):
	pass

if __name__ == "__main__":
	long_string = create_string(300)
	short_string = long_string[100:151]
	print long_string
	print short_string
	o = Oligo(short_string, long_string)
	o.extend()
	print len(o.extended_string)
	print o.extension_left, o.extension_right
	print o.gaps_left, o.gaps_right
	o.further_extend(2,2)
	print len(o.extended_string)
	INPUT_FILENAME = ""
	OUTPUT_FILENAME = ""
	main(INPUT_FILENAME, OUTPUT_FILENAME)




