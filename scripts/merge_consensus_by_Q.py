#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------

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
	parser.add_argument('files', nargs="*", type = str, help = '.....')
	parser.add_argument('-o', dest = 'output', type = str, required = True, help = 'output file name')
	parser.add_argument('-x', dest = 'debug', action='store_true', default = False, help = 'Debug. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' v' + __version__)
	args = parser.parse_args()
	##########################################################################################

	#--Reading second file
	best = {name.split()[0]:(name, seq) for name, seq in fastaRead(args.files[0])}

	#--Reading first file (reference) and writing best consensus
	for file in args.files[1:]:
		for name, seq in fastaRead(file):
			if best.get(name.split()[0]):
				if float(name.split("_Q=")[1]) > float(best[name.split()[0]][0].split("_Q=")[1]):
					best[name.split()[0]] = (name, seq)
			else:
				best[name.split()[0]] = (name, seq)



	with open(args.output, 'w') as output:
		for name in best.keys():
			output.write('>{}\n{}\n'.format(best[name][0], best[name][1]))



	# with open (args.output, 'w') as output:

	# 	for name, seq in fastaRead(args.first):
	# 		if second.get(name.split()[0]):
	# 			second_Q = float(second[name.split()[0]][0].split("_Q=")[1])
	# 			first_Q = float(name.split("_Q=")[1])
	# 			if second_Q > first_Q:
	# 				output.write(">{}\n{}\n".format(second[name.split()[0]][0], second[name.split()[0]][1]))
	# 			else:
	# 				output.write(">{}\n{}\n".format(name, seq))
	# 		else:
	# 			output.write(">{}\n{}\n".format(name, seq))

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

