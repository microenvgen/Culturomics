#!/usr/bin/env python
#-*- coding: UTF-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------

------------------------------------------------------------------------------------------
"""
##########################################################################################

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
	parser = argparse.ArgumentParser()
	parser.add_argument('blast', type = str, help = 'blast output file (outfmt "6 std qcovs staxids ...")')
	parser.add_argument('-i', dest = 'ident', type = float, default = 25, help = 'default 25')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' v' + __version__)
	args = parser.parse_args()
	##########################################################################################

	with open('{}_confirmed.blasn'.format(args.blast.split('.')[0]), 'w') as output:
		for col in readTSV(args.blast):
			if col[1] in col[0] and float(col[2]) > args.ident:
				output.write('\t'.join(col) + '\n')

def readTSV(file, header=False, comments=None):

	with open(file, 'r') as infile:

		if header:

			h = infile.readline()

		for line in infile:

			line = line.rstrip('\n')

			if not line: #--Empty spaces
				continue

			if comments:

				if line.startswith(comments):
					continue

			col = line.split('\t')

			yield col

##########################################################################################
if __name__ == "__main__":
	
	main()

