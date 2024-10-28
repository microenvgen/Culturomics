#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:

This scripts uses Mothur for building a consensus sequence using provided fastq file.
It also analyse variants (SNVs) and Indels present in read alignment produced by Mothur.
Output consensus sequence name will be form by the name of the input file plus the
number of reads use to build the consensus and the number of SNV and INDES (
E7_Well_C10_Locus_16S_long READS=5 SNVs=9 INDELS=18 DEG=14)

Requirements:

-Mothur (v.1.48.0, https://github.com/mothur/mothur/releases/download/)
	Must be in PATH or use -m option to specify the path to containing folder

-Seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
	It is expected to be in the current directory, otherwise it will be downloaded

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
__version_info__ = ('2','0','0')
__version__ = '.'.join(__version_info__)

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('input_files', nargs="*", type = str, help = 'list or regex for input uncompressed fastq files to include')

	parser.add_argument('-l', dest = 'length', type = int, default = 900, help = 'Minumim read length to include in downstream analysis. Default: 900')
	parser.add_argument('-c', dest = 'cutoff', type = int, default = 50, help = 'Cutoff for defining consensus base: Default: 50')
	parser.add_argument('-n', dest = 'variants', type = float, default = 0.8, help = 'Threshold to consider variants (SNVs and Indels). Default: 0.8')

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
	if not cf.checkfile(f'{db}.align'):
		print(f'>>>Downloading database...')
		cf.runexternalcommand(f'wget https://mothur.s3.us-east-2.amazonaws.com/wiki/{db}.tgz')
		cf.runexternalcommand(f'tar -xzf {db}.tgz')

	#--Processing files
	for fastq in args.input_files:

		#--Input file basename
		basename = '.'.join(fastq.split('.')[:-1])
		print(f'>>>Processing {fastq} file...')

		#--Converting fastq to fasta (length filtering and counting)
		reads = 0
		fasta = f'{basename}.fasta'
		with open(fasta, 'w') as fasta_file:
			for record in cf.fastqRead(fastq):
				if record:
					if len(record[1]) >= args.length:
						reads += 1
						fasta_file.write(f'>{record[0][1:]}\n{record[1]}\n')

		#--Empty fasta check (due to empty fastq or by length filtering)
		if reads == 0: 
			print(f'{"#"*90}\nERROR: No reads were found in fasta file!!!\n{"#"*90}')
			continue

		####--Running Mothur--####

		#--Aligning reads against seed database
		run_log = cf.runexternalcommand(f'mothur "#align.seqs(candidate={basename}.fasta, template={db}.align)"')
		# outputs:
			# basename.align
			# basename.align_report
			# basename.flip.accnos (sequence reversed and complemented)

		#--Consensus creation
		run_log = cf.runexternalcommand(f'mothur "#consensus.seqs(fasta={basename}.align, cutoff={args.cutoff})"')
		# outputs:
			# basename.cons.fasta
			# basename.cons.summary

		#--SNVs and Indels analysis (basename.cons.summary)
		# PositioninAlignment	A	T	G	C	Gap	NumberofSeqs	ConsensusBase
		# 1	0.000000	0.000000	0.000000	0.000000	1.000000	12	.
		# 3140	0.000000	0.083333	0.000000	0.916667	0.000000	12	C
		# 3141	0.000000	0.000000	0.000000	0.000000	1.000000	12	-
		# 3142	0.000000	0.000000	1.000000	0.000000	0.000000	12	G
		# 1164	0.000000	0.000000	0.250000	0.000000	0.750000	12	-

		consensus = []
		snvs = 0
		indels = 0
		deg = 0
		bases = ['A', 'T', 'G', 'C', '-']

		for col in cf.readTSV(f'{basename}.cons.summary', header=True):
			if col[-1] == '.': #--No bases in alignment
				continue
			elif col[-1] == '-': 
				if float(col[-3]) == 1: #--Only gaps in alignment
					continue
				else: #--Most abundant element in this position is a gap (not included in consensus)
					if float(col[-3]) <= args.variants:
						indels += 1
			else:
				consensus.append(col[-1])
				try:
					base_index = bases.index(col[-1].upper()) #--Lower case bases appears when a gap is equally represented than assigned base
					if float(col[base_index + 1]) <= args.variants:
						muts_freq = [float(x) for x in col[1:6]]
						muts_indexes = [i for i, x in enumerate(muts_freq) if i != base_index and x > 0]
						if len(muts_indexes) == 1:
							if bases[muts_indexes[0]] == '-':
								indels += 1
							else:
								snvs += 1
						else: #--More than 1 variant (Here, if 2 different bases or a base and a gap other than consensus have the same frequency, only 1 is randonmly reported and registered as snv or indel, althought both could be simultaneusly possible)
							variants = [[muts_freq[i], bases[i]] for i in muts_indexes]
							next_most_frequent = sorted(variants, reverse=True)[0]
							if next_most_frequent[1] == '-':
								indels += 1
							else:
								snvs += 1

				except ValueError: #--Degenerated bases (2 or more bases are equally represented in position)
					deg += 1

		#--Consensus quality calculation (q=reads/(reads+variants), variants = snvs+indels+deg, if reads = 1, q=0)
		#	The higher the value of q, the smaller the number of variants per read.
		#	If 2 sequences has the same number of variants, the higher the number of reads, 
		#	the higher the value and therefore the quality of the consensus
		#	Consensus built with a single sequence has no variants, but quality calculation will return q=1
		#	To reduce the risk of chosing this sequences over other with more reads, quality of consensus
		#	with only 1 reads is assigned to 0 (q=0)
		variants = snvs + indels + deg
		if reads == 1:
			quality = 0
		else:
			quality = reads / (reads + variants)

		#--Writing output
		with open(f'{basename}.consensus.fasta', 'w') as output:
			consensus_name = f'{basename}_READS={reads}_VARIANTS={snvs}_{indels}_{deg}_Q={quality:.3f}'
			output.write('>{}\n{}\n'.format(consensus_name, ''.join(consensus)))

		print('>>>Done!!!')
		#--Removing intermediate files
		if not args.keep_temporal:
			os.remove(f'{basename}.fasta')
			os.remove(f'{basename}.align')
			os.remove(f'{basename}.align_report')
			os.remove(f'{basename}.cons.fasta')
			os.remove(f'{basename}.cons.summary')
			cf.runexternalcommand(f'rm -fr {basename}.flip.accnos')
			cf.runexternalcommand('rm -fr *.logfile')

##########################################################################################
if __name__ == "__main__":

	main()


