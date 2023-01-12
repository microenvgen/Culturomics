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

# vsearch --cluster_fast output file
# S	0	1438	*	*	*	*	*	all.fastq_B10_Well_B2_locus_16S_long_READS=362_SNVS=14	*
# H	0	1438	100.0	+	0	0	=	all.fastq_B10_Well_B4_locus_16S_long_READS=384_SNVS=7	all.fastq_B10_Well_B2_locus_16S_long_READS=362_SNVS=14
# H	0	1438	100.0	+	0	0	=	all.fastq_B10_Well_B5_locus_16S_long_READS=415_SNVS=11	all.fastq_B10_Well_B2_locus_16S_long_READS=362_SNVS=14
# H	0	1438	100.0	+	0	0	=	all.fastq_B10_Well_B6_locus_16S_long_READS=226_SNVS=16	all.fastq_B10_Well_B2_locus_16S_long_READS=362_SNVS=14
# H	0	1438	100.0	+	0	0	=	all.fastq_B10_Well_E7_locus_16S_long_READS=1076_SNVS=6	all.fastq_B10_Well_B2_locus_16S_long_READS=362_SNVS=14
# S	1	1386	*	*	*	*	*	all.fastq_B10_Well_B3_locus_16S_long_READS=467_SNVS=16	*
# C	0	5	*	*	*	*	*	all.fastq_B10_Well_B2_locus_16S_long_READS=362_SNVS=14	*
# C	1	1	*	*	*	*	*	all.fastq_B10_Well_B3_locus_16S_long_READS=467_SNVS=16	*
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

	parser.add_argument('-i', dest = 'identity', type = int, default = 0.99, help = 'Minimum identity to build clusters: Default: 0.99')
	parser.add_argument('-p', dest = 'from_fastq2consensus', action='store_true', default = False, help = 'Input fasta files were generated using fastq2consensus.py the vsearch output will be parsed considering the number of reads and SNV/Indel/Deg detected to choose a representative sequence. Default: False')

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
		sys.exit(f'{"#"*90}\nERROR: at least 2 files must be given\n{"#"*90}')

	#--Joining all sequences in a single file
	with open(f'{args.output}.fasta', 'w') as all_seq_file:
		for file in args.input_files:
			for name, seq in cf.fastaRead(file):
				all_seq_file.write(f'>{name}\n{seq}\n')

	#--Running vsearh
	### Vsearch uses all threads and ran memory avaible in the machine and I do no know how to change this
	cf.runexternalcommand(f'vsearch --cluster_fast {args.output}.fasta -id {args.identity} -uc {args.output}.uc')
	# outputs:
		# output_prefix.uc

	#--Parsing vsearch output (-p, sequence names should be: E7_Well_C9_Locus_16S_long_READS=7_SNVs=227_INDELS=22_DEG=101)
	if args.from_fastq2consensus:

		fasta = cf.fasta2dict(f'{args.output}.fasta')

		from collections import defaultdict
		clusters = defaultdict(list)

		for col in cf.readTSV(f'{args.output}.uc'):

			if col[0] == 'S' or col[0] == 'H':
				cluster = col[1] #--Cluster number
				seq_name = col[8]
				reads, snvs, indels, deg = [int(x.split('=')[1]) for x in seq_name.split("_")[-4:]]

				#--The higher the value, the smaller the number of variants per read. 
				#--If 2 sequences has the same number of variants, the higher the number of reads, 
				#--the higher the value, then, we are going to choose alwawys the best sequence 
				#--(minumin number of variants with the higher number of reads)
				variants = snvs + indels + deg
				quality = reads / (reads + variants) 

				#--Consensus built with a single sequence has no variants, but quality calculation will return q=1
				#--To reduce the risk of chosing this sequences over other with more reads quality of consensus
				#--with only 1 reads is assigned to 0 (q=0)
				if reads == 1: quality = 0 

				clusters[cluster].append([seq_name, quality]) #--seq_name, quality


		with open(f'{args.output}_clusters.txt', 'w') as output:
			output.write('N_Members\tRepresentative\tMembers\n')

			with open(f'{args.output}_representatives.fasta', 'w') as outputfasta:

				for cluster in clusters:
					sorted_cluster = sorted(clusters[cluster], key = lambda x: x[1], reverse=True)
					members = [f'{sc[0]}_Q={sc[1]:.2f}' for sc in sorted_cluster[1:]]

					outputfasta.write(f'>{sorted_cluster[0][0]}_Q={sorted_cluster[0][1]:.2f}\n{fasta[sorted_cluster[0][0]]}\n')
					output.write(f'{str(len(clusters[cluster]))}\t{sorted_cluster[0][0]}_Q={sorted_cluster[0][1]:.2f}\t{",".join(members)}\n')


##########################################################################################
if __name__ == "__main__":

	main()


