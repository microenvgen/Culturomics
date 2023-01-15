#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:

Requirements:

-Mothur (v.1.48.0, https://github.com/mothur/mothur/releases/download/)
	Must be in PATH or use -m option to specify the path to containing folder

-Seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
	It is expected to be in the current directory, otherwise it will be download

-wget and tar for database download and decompress

Outputs:
-basename.consensus.fasta
-basename.log.txt
------------------------------------------------------------------------------------------
"""
##########################################################################################

#--Imports
import sys
import os
import argparse
import common_functions as cf

__author__ = "Alberto Rastrojo"
__version_info__ = ('1','0','0')
__version__ = '.'.join(__version_info__)

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('input_files', nargs="*", type = str, help = 'list or regex for input uncompressed fastq files to include')

	parser.add_argument('-k', dest = 'keep_temporal', action='store_true', default = False, help = 'Use this option to keep temporal files. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' Version: ' + __version__)

	args = parser.parse_args()
	##########################################################################################
	#--Checkign requirements
	for program in ['mothur', 'wget', 'tar']:
		if not cf.checkpath(program):
			sys.exit(f'ERROR: {program} were not found!\n' + '#'*90)

	#--Checking database in current directory or downloading it
	db = 'silva.seed_v138_1'
	if not cf.checkfile(f'{db}.align') or not cf.checkfile(f'{db}.tax'):
		print(f'>>>Downloading database...')
		cf.runexternalcommand(f'wget https://mothur.s3.us-east-2.amazonaws.com/wiki/{db}.tgz')
		cf.runexternalcommand(f'tar -xzf {db}.tgz')

	#--Processing files
	for fasta in args.input_files:

		#--Input file basename
		basename = '.'.join(fasta.split('.')[:-1])
		print(f'>>>Processing {fasta} file...')

		#--Align sequences to reference database
		cf.runexternalcommand(f'mothur "#align.seqs(candidate={fasta}, template={db}.align)"')
		# {basename}.align, {basename}.align.report

		#--Creating counts table
		with open(f'{basename}.count_table', 'w') as counttable:
			counttable.write('Representative_Sequence\ttotal\n')
			for name, seq in cf.fastaRead(fasta):
				counttable.write(f'{name}\t1\n')
		# {basename}.count_table
		# cf.runexternalcommand(f'mothur "#unique.seqs(fasta={fasta}, format=count)"')

		cf.runexternalcommand(f'mothur "#classify.seqs(fasta={basename}.fasta, count={basename}.count_table, reference={db}.align, taxonomy={db}.tax)"')
		# {basename}.{db}.wang.tax.summary, {basename}.{db}.wang.taxonomy

		print('>>>Done!!!')
		#--Removing intermediate files
		if not args.keep_temporal:
			os.remove(f'{basename}.align')
			os.remove(f'{basename}.align_report')
			# os.remove(f'{basename}.{db}.wang.tax.summary')
			# os.remove(f'{basename}.{db}.wang.taxonomy')

##########################################################################################
if __name__ == "__main__":

	main()


