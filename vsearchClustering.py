#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:

This script takes several fasta files (at least 2) and cluster all sequences using vsearch

Requirements:

-vsearch (v2.22.1, https://github.com/torognes/vsearch)

Outputs:
	output_prefix.uc (see vsearch manual)
	output_prefix_clusters.txt (only if -p option is used)

Example: 
	vsearchClustering.py *.consensus.fasta -o plate_E7 -p

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
	parser.add_argument('input_files', nargs="*", type = str, help = 'list or regex for input fasta files to include')
	parser.add_argument('-o', dest='output', type = str, required=True, help = 'Output prefix name')

	parser.add_argument('-i', dest = 'identity', type = float, default = 0.99, help = 'Minimum identity to build clusters: Default: 0.99')
	parser.add_argument('-p', dest = 'from_fastq2consensus', action='store_true', default = False, help = 'If input fasta files were generated using fastq2consensus.py the vsearch output will be parsed considering the quality of the consensus sequences (reads/(reads+SNV+Indel+Deg) to choose a representative sequence. Default: False')

	parser.add_argument('-k', dest = 'keep_temporal', action='store_true', default = False, help = 'Use this option to keep temporal files. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' Version: ' + __version__)

	args = parser.parse_args()
	##########################################################################################
	#--Checkign requirements
	for program in ['vsearch']:
		if not cf.checkpath(program):
			sys.exit(f'ERROR: {program} were not found!\n' + '#'*90)

	#--Check the number of input files (>=2)
	if len(args.input_files) < 2:
		parser.print_help()
		sys.exit(f'{"#"*90}\nERROR: at least 2 files must be given\n{"#"*90}')

	#--Joining all sequences in a single file
	with open(f'{args.output}_all_seqs.fasta', 'w') as all_seq_file:
		for file in args.input_files:
			for name, seq in cf.fastaRead(file):
				all_seq_file.write(f'>{name}\n{seq}\n')

	#--Running vsearh
	### Vsearch uses all threads and ran memory avaible in the machine and I do no know how to change this
	cf.runexternalcommand(f'vsearch --cluster_fast {args.output}_all_seqs.fasta -id {args.identity} -uc {args.output}.uc')
	# outputs:
		# output_prefix.uc

	#--Parsing vsearch output (-p, sequence names should be: E7_Well_C9_Locus_16S_long_READS=7_SNVs=227_INDELS=22_DEG=101)
	if args.from_fastq2consensus:

		fasta = cf.fasta2dict(f'{args.output}_all_seqs.fasta')

		from collections import defaultdict
		clusters = defaultdict(list)

		for col in cf.readTSV(f'{args.output}.uc'):

			if col[0] == 'S' or col[0] == 'H':
				cluster = col[1] #--Cluster number
				seq_name = col[8]
				quality = float(col[8].split('=')[-1])
				clusters[cluster].append([seq_name, quality]) #--seq_name, quality


		with open(f'{args.output}_clusters.txt', 'w') as output:
			output.write('N_Members\tRepresentative\tMembers\n')

			with open(f'{args.output}_representatives.fasta', 'w') as outputfasta:

				for cluster in clusters:
					sorted_cluster = sorted(clusters[cluster], key = lambda x: x[1], reverse=True)
					representative = sorted_cluster[0][0]
					members = ",".join([sc[0] for sc in sorted_cluster[1:]])

					outputfasta.write(f'>{representative}\n{fasta[representative]}\n')
					output.write(f'{len(clusters[cluster])}\t{representative}\t{members}\n')


##########################################################################################
if __name__ == "__main__":

	main()


