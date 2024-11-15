#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:

The input folder must contain fastq files from the wells/isolates to analysis. For each 
fastq a consensus sequence will be generated. All consensus sequences will be clustered
together to search for different isolated. Finally, a representative well/isolate will
be selected for each cluster (the one with best Q value). 

Folder containing this script and the required ones, must be in the PATH:

- common_functions.py
- fastq2consensus.py
- vsearchClustering.py
- fasta2taxo.py
- mergeClusterAndTaxo.py

Additional Requirements:

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
	parser.add_argument('-t', dest = 'threads', type = int, default = 1, help = 'Number of threads [1]')
	parser.add_argument('-x', dest = 'debug', action='store_true', default = False, help = 'Debug. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' v' + __version__)
	args = parser.parse_args()
	##########################################################################################
	# Reading input files
	root = os.getcwd()
	os.chdir(args.folder)
	files = []
	for file in os.listdir('.'): 
		if file.split('.')[-1] in ["fastq", "fq"]:
			files.append(file)

	#--Checking database in current directory or downloading it
	db = 'silva.seed_v138_1'
	if not cf.checkfile(f'{db}.align'):
		print(f'>>>Downloading database...')
		cf.runexternalcommand(f'wget https://mothur.s3.us-east-2.amazonaws.com/wiki/{db}.tgz')
		cf.runexternalcommand(f'tar -xzf {db}.tgz')

	#--Creating consensus sequences for each input file
	for i in range(0, len(files), args.threads):

		chunk = files[i:i+args.threads]

		with Pool(args.threads) as pool:
			logs = pool.map(make_consensus, chunk)

		for log in logs:
			print(log)

	time.sleep(60)

	# Clustering all consensus sequences
	print(f'vsearchClustering.py -o {args.folder} -p *consensus.fasta')
	log = cf.runexternalcommand(f'vsearchClustering.py -o {args.folder} -p *consensus.fasta')
	print(log)

	# Assigning taxonomy to representative sequences
	print(f'fasta2taxo.py {args.folder}_representatives.fasta')
	log = cf.runexternalcommand(f'fasta2taxo.py {args.folder}_representatives.fasta')
	print(log)

	# Merging cluster table and taxo info
	print(f'mergeClusterAndTaxo.py {args.folder}_representatives.seed_v138_1.wang.taxonomy {args.folder}_clusters.txt {args.folder}_results.tsv')
	log = cf.runexternalcommand(f'mergeClusterAndTaxo.py {args.folder}_representatives.seed_v138_1.wang.taxonomy {args.folder}_clusters.txt {args.folder}_results.tsv')
	print(log)

def make_consensus(file):
	log = cf.runexternalcommand(f'fastq2consensus.py {file}')
	return f'{log}'

##########################################################################################
if __name__ == "__main__":

	main()

