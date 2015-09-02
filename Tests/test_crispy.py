"""
Test classes for CRISpy package.
Run py.test from CRISPR/Tests working directory.
"""

from abc import ABCMeta, abstractmethod

# allow python access to directory with CRISpy modules
import sys
sys.path.insert(0, '/users/philnova/CRISPR/CRISpy/')

import os

#class TestAbstract(object):
#	__metaclass__ = ABCMeta
	#Abstract test class is currently unused, but would allow behaviors to be standardized across all of its
	#child classes.

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#

class TestGenRNA(object):
	"""Assess function of modules that generate potential guide RNA sequences."""
	
	def test_revcomp(self):
		"""Test that the reverse complement function works."""
		import find_guideRNA
		assert find_guideRNA.reverse_complement('AGCT') == 'TCGA'

	def test_strip_file_IO(self):
		"""Test that strip_file produces the intermediate edited files."""
		import strip_file
		filename, path = ['chrZ',], '/users/philnova/CRISPR/Tests/'
		strip_file.main(path, filename)
		for fname in ['chrz_edited_double_reordered.txt', 'chrz_edited_double.txt','chrz_edited.txt']:
			assert os.path.isfile(fname)

	def test_N_removed_by_strip_file(self):
		import strip_file
		fname = 'chrz_edited_double_reordered.txt'
		target = ['>chrZ','ATAGCTCCATTAAGCCAATCAGCAATGCTGACTGCCTAGTGACTGTAAAG','ATTGAGGGGACCATGAGGCCTTATATGGATGAGTTCCTGAGATGACTGGA',
		'GGAACTGTTTAAATGTGTTTTCTTCATTGCTCTCTTCATTCCAGACTGAA','CAAGTATGCAGATCCTGTtgagaggtgacagcgtgctggcagtcctcaca']
		assert os.path.isfile(fname)
		with open(fname, 'r') as fo:
			for i, l in enumerate(fo):
				assert l.strip() == target[i]

	def test_scanchrm_dynamic_bidirectional_IO(self):
		"""Test that find_guideRNA handles the non-integer chromosome name Z"""
		import find_guideRNA
		find_guideRNA.scan_chromosome_dynamic_bidirection('chrz_edited_double_reordered.txt',1,'out')
		for fname in ['out_F.txt', 'out_R.txt']:
			assert os.path.isfile(fname)

	def test_scanchrm_dynamic_bidirectional_F(self):
		"""Test that find_guideRNA has correctly identified forward-directed guideRNA"""
		fname = 'out_F.txt'
		assert os.path.isfile(fname)
		with open(fname, 'r') as fo:
			for i, l in enumerate(fo):
				if i==1:
					print l.strip()
					assert int(l.split()[1].strip()) == 35
					assert int(l.split()[2].strip()) == 57
					assert l.split()[3].strip() == 'CCTAGTGACTGTAAAGATTGAGG'

	def test_scanchrm_dynamic_bidirectional_R(self):
		"""Test that find_guideRNA has correctly identified reverse-directed guideRNA"""
		fname = 'out_R.txt'
		assert os.path.isfile(fname)
		with open(fname, 'r') as fo:
			for i, l in enumerate(fo):
				if i==1:
					assert int(l.split()[1].strip()) == 7
					assert int(l.split()[2].strip()) == 30
					assert l.split()[3].strip() == 'CCATTAAGCCAATCAGCAATGCTG'
		assert 1==1

	def test_merge_files_IO(self):
		"""Test that merge_files creates a new file"""
		import merge_files
		path, filename, modifier = '/users/philnova/CRISPR/Tests/', 'out', '.txt'
		merge_files.worker_test(path, filename, modifier)

	def test_merge_files(self):
		fname = "out_mergedguides.txt"
		assert os.path.isfile(fname)
		with open(fname, 'r') as fo:
			for i, l in enumerate(fo):
				if i==1:
					assert int(l.split()[1].strip()) == 35
					assert int(l.split()[2].strip()) == 57
					assert l.split()[3].strip() == 'CCTAGTGACTGTAAAGATTGAGG'
				if i==10:
					assert int(l.split()[1].strip()) == 7
					assert int(l.split()[2].strip()) == 30
					assert l.split()[3].strip() == 'CCATTAAGCCAATCAGCAATGCTG'

	def test_cleanup_mergefiles(self):
		"""Clean up files created by test_merge_files_IO"""
		fname = "out_mergedguides.txt"
		if os.path.isfile(fname):
			os.remove(fname)
		assert 1==1

	def test_cleanup_scanchrm(self):
		"""Clean up files created by test_scanchrm_dynamic_bidirectional_IO"""
		for fname in ['out_F.txt', 'out_R.txt']:
			if os.path.isfile(fname):
				os.remove(fname)
		assert 1==1

	def test_cleanup_stripfile(self):
		"""Clean up files created by test_strip_file_IO"""
		for fname in ['chrz_edited_double_reordered.txt', 'chrz_edited_double.txt','chrz_edited.txt']:
			if os.path.isfile(fname):
				os.remove(fname)
		assert 1==1


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#

class TestScoreGuide(object):
	"""Assess function of modules that score guide RNAs."""
	pass