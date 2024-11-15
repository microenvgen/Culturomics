#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------


Folder containing this script and the required ones, mut be in the PATH:

- common_functions.py
- fastq2consensus.py
- vsearchClustering.py
- fasta2taxo.py
- mergeClusterAndTaxo.py

Requirements:

- Mothur (v.1.48.0, https://github.com/mothur/mothur/releases/download/)
	Must be in PATH or use -m option to specify the path to containing folder

- Seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
	It is expected to be in the current directory, otherwise it will be downloaded

- wget and tar for database download and decompress

------------------------------------------------------------------------------------------
"""
##########################################################################################

#--Imports
import sys
import os
import argparse
import time
from multiprocessing import Process, Queue, Pool
import common_functions as cf

__author__ = "Alberto Rastrojo"
__version_info__ = ('1','0','0')
__version__ = '.'.join(__version_info__)

def main():
	
	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-f', dest='folder', type = str, required=True, help = 'Folder containing fastq/fq files')
	# parser.add_argument('output', type = str, help = '.....')
	parser.add_argument('-t', dest = 'threads', type = int, default = 1, help = 'Number of threads [1]')
	parser.add_argument('-x', dest = 'debug', action='store_true', default = False, help = 'Debug. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' v' + __version__)
	args = parser.parse_args()
	##########################################################################################
	bin_path = os.path.dirname(os.path.realpath(__file__))

	##########################################################################################
	root = os.getcwd()
	os.chdir(args.folder)
	files = []
	for file in os.listdir('.'): 
		if file.split('.')[-1] in ["fastq", "fq"]:
			files.append(file)

	print(files)

	##########################################################################################
	#--Runnning subjobs
	for i in range(0, len(files), args.threads):

		chunk = files[i:i+args.threads]

		with Pool(args.threads) as p:
			print(p.map(toy, chunk))

		# processes = []
		# for file in chunk:

		# 	processes.append(Process(target=cicleFind, args=(name, seq, args)))

		# for p in processes:
		# 	p.start()

		# for p in processes:
		# 	p.join()

def toy(file):
	log = cf.runexternalcommand(f'fastq2consensus.py {file}')
	return f'{log}'

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


#  untitled.py
#  
#  Copyright 2017 Alberto Rastrojo <arastrojo@cbm.csic.es>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
