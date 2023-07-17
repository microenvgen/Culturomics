#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
This script extract sequences from a genbank file and creates an 
annotated fasta as follows:

>seqID	fam	x1:y1:s1:product1:protid1 x2:y2:s2:product2:protid2....
taggcggcttgactagcgcgatcagctagcgcgacgcgcgctatttcgagcatc....
------------------------------------------------------------------------------------------
"""
##########################################################################################

#--Imports
import sys
import os
import argparse

__author__ = "Alberto Rastrojo"
__version_info__ = ('1','0','0')
__version__ = '.'.join(__version_info__)

def main():
	
	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('input', type = str, help = '')
	parser.add_argument('output', type = str, help = '.....')
	parser.add_argument('-x', dest = 'debug', action='store_true', default = False, help = 'Debug. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' v' + __version__)
	args = parser.parse_args()
	##########################################################################################



##########################################################################################
if __name__ == "__main__":

	main()


	# parser.add_argument('-t', dest = 'type', type = str, required = True, choices=['GTF', 'GFF'], help = 'file format: GTF or GFF. Default: GTF')
	# parser.add_argument('-t', dest = 'table', type = str, required = True, help = 'tsv')
	# parser.add_argument('files', nargs="*", type = str, help = '.....')
	# parser.add_argument('-c', dest = 'cores', type = str, default = 4, help = 'number of threads')
	# parser.add_argument('-l', '--min_aln_length', dest = 'minAlnLength', type = int, default = 100, help = 'Minimum alignment length')
	
	# #--Mutually exclusive options
	# group = parser.add_mutually_exclusive_group(required=True)
	# group.add_argument('-t', dest='taxo', type = str, help = 'Taxo from nuclid2taxo_v2.py')
	# group.add_argument('-l', dest='labes', type = str, help = 'Label for all input sequences')

	# parser.add_argument('-x', dest = 'debug', action='store_true', default = False, help = 'Debug. Default: False')


	# args = parser.parse_args()

	# #  outfile = os.path.basename(infile) + '.below'
