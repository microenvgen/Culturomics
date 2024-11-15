#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
This scripts compares 2 consensus sequences sets from two different minion runs, and for
each sequence in the first input file (reference) returns the best consensus sequences
based on the Q-value between the 2 files (second file could contain more sequences, not
present in first file, but only those sequences present in first file will be analysed). If
a sequence is not present in second file, a warning will be shown and original sequence
will be returned (from first file). If both qualities values are equal first file consensus
will be returned.

Both files sequences must be named as follows:

>A7-A11 P5_P7_i5_i7_READS=10_VARIANTS=644_710_17_Q=0.007
ATTGAACGCTGGCGGCAGGCCTAACACATGCAAGTCKAGCGGATGANNNNAGCTTGCTCNNGNATTNAG

or,

>A7-A11 READS=76_VARIANTS=0_2_0_Q=0.974
AACGAACGCTGGCGGCAGGCTTAACACATGCAAGTCGAGCGCCCCGCAAG


------------------------------------------------------------------------------------------
"""
##########################################################################################

#--Imports
import sys
import os
import argparse
from collections import defaultdict

__author__ = "Alberto Rastrojo"
__version_info__ = ('1','0','0')
__version__ = '.'.join(__version_info__)

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('first', type = str, help = 'First fasta file used as reference file')
	parser.add_argument('second', type = str, help = 'Second fasta file to compare with')
	parser.add_argument('output', type = str, help = 'Output fasta file name')
	parser.add_argument('-x', dest = 'debug', action='store_true', default = False, help = 'Debug. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' v' + __version__)
	args = parser.parse_args()
	##########################################################################################

	#--Reading second file
	second = {name.split()[0]:(name, seq) for name, seq in fastaRead(args.second)}

	#--Reading first file (reference) and writing best consensus
	with open (args.output, 'w') as output:

		for name, seq in fastaRead(args.first):
			if second.get(name.split()[0]):
				second_Q = float(second[name.split()[0]][0].split("_Q=")[1])
				first_Q = float(name.split("_Q=")[1])
				if second_Q > first_Q:
					output.write(">{}\n{}\n".format(second[name.split()[0]][0], second[name.split()[0]][1]))
				else:
					output.write(">{}\n{}\n".format(name, seq))
			else:
				output.write(">{}\n{}\n".format(name, seq))

def fastaRead(fasta, split_names=False):

	with open(fasta, 'r') as infile:

		seq = ''
		for line in infile:

			line = line.strip()

			if line.startswith(">"):

				if seq:

					yield name, seq
					seq = ''

				name = line[1:]
				if split_names: 
					name = line.split()[0][1:]

			else:
				seq = seq + line

	#--Last sequence
	yield name, seq

##########################################################################################
if __name__ == "__main__":

	main()

