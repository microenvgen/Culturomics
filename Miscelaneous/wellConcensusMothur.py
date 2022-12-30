#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:

This scripts uses Mothur for building a consensus sequence using provided fastq file.
It also analysis variants (SNVs) and Indels present

Requirements:

- Mothur (v.1.48.0, https://github.com/mothur/mothur/releases/download/)
	Must be in PATH or use -m option to specify the path to containing folder
- Seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
	It is expected to be in the current directory, otherwise use -s option to specify the 
	path to containing folder

Outputs:
- prefix.consensus.fasta
- prefix.log.txt
------------------------------------------------------------------------------------------
"""
##########################################################################################

#--Imports
import sys
import os
import argparse
import subprocess

__author__ = "Alberto Rastrojo"
__version_info__ = ('1','0','0')
__version__ = '.'.join(__version_info__)

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('fastq', type = str, help = 'fastq file (uncompressed)')

	parser.add_argument('-m', dest = 'mothur_path', type = str, help = 'Mothur containing folder. If not specify it should expected to be in PATH')
	parser.add_argument('-s', dest = 'seed_path', type = str, help = 'seed containing folder. If not specify it should expected to be in the current directory')

	parser.add_argument('-l', dest = 'length', type = int, default = 900, help = 'Minumim read length to include in downstream analysis. Default: 900')
	parser.add_argument('-c', dest = 'cutoff', type = int, default = 50, help = 'Cutoff (%) for defining consensus base: Default: 50')
	parser.add_argument('-v', dest = 'variants_threshold', type = float, default = 0.8, help = 'Threshold to consider variants (SNVs and Indels). Default: 0.8')

	parser.add_argument('-t', dest = 'threads', type = str, default = 2, help = 'Number of threads. Default: 2')
	parser.add_argument('-k', dest = 'keep_temporal', action='store_true', default = False, help = "Use this option to keep temporal files. Default: False")

	args = parser.parse_args()
	##########################################################################################

	#--Input file prefix
	prefix = '.'.join(args.fastq.split('.')[:-1])
	log_file = open(f'{prefix}.log.txt', 'w')

	#--Converting fastq to fasta (length filtering and counting)
	fastq_reads = 0
	fasta_reads = 0
	fasta_file_name = f'{prefix}.fasta'
	with open(fasta_file_name, 'w') as fasta_file:
		for record in fastqRead(args.fastq):
			if record:
				fastq_reads += 1
				if len(record[1]) >= args.length:
					fasta_reads += 1
					fasta_file.write(f'>{record[0][1:]}\n{record[1]}\n')

	#--Empty fasta check (due to empty fastq or by length filtering)
	if fasta_reads == 0: 
		msg = '#'*90 + '\n' + 'No reads were found in fasta file!!!!!' + '#'*90 + '\n'
		log_file.write(msg)
		sys.exit(msg)

	msg = f'InputFile:{prefix}\nFastq_reads: {fastq_reads}\nFasta_reads: {fasta_reads}'
	log_file.write('#'*90 + '\n' + msg + '\n' + '#'*90 + '\n')

	####--Running Mothur--####
	#--Defining paths
	mothur_path = ''
	if args.mothur_path: mothur_path = args.mothur_path + "/"

	seed_path = ''
	if args.seed_path: seed_path = args.seed_path + "/"

	#--Aligning reads against seed database
	cmd = f'{mothur_path}mothur "#align.seqs(candidate={prefix}.fasta, template={seed_path}silva.seed_v138_1.align, processors={args.threads})"'
	log_file.write('#'*90 + '\n' + cmd + '\n' + '#'*90 + '\n')
	run_log = runCMD(cmd)
	log_file.write('#'*90 + '\n' + run_log + '\n' + '#'*90 + '\n')
	# outputs: 
		# prefix.align
		# prefix.align_report
		# prefix.flip.accnos (sequence reversed and complemented)

	#--Consensus creation
	cmd = f'{mothur_path}mothur "#consensus.seqs(fasta={prefix}.align, cutoff={args.cutoff})"'
	log_file.write('#'*90 + '\n' + cmd + '\n' + '#'*90 + '\n')
	run_log = runCMD(cmd)
	log_file.write('#'*90 + '\n' + run_log + '\n' + '#'*90 + '\n')
	# outputs:
		# prefix.cons.fasta
		# prefix.cons.summary

	#--SNVs and Indels analysis (prefix.cons.summary)
	# PositioninAlignment	A	T	G	C	Gap	NumberofSeqs	ConsensusBase
	# 1	0.000000	0.000000	0.000000	0.000000	1.000000	12	.
	# 3140	0.000000	0.083333	0.000000	0.916667	0.000000	12	C
	# 3141	0.000000	0.000000	0.000000	0.000000	1.000000	12	-
	# 3142	0.000000	0.000000	1.000000	0.000000	0.000000	12	G
	# 1164	0.000000	0.000000	0.250000	0.000000	0.750000	12	-

	consensus = []
	snvs = 0
	indels = 0
	bases = ['A', 'T', 'G', 'C', '-']

	for col in readTSV(f'{prefix}.cons.summary', header=True):
		if col[-1] == '.': #--No bases in alignment
			continue
		elif col[-1] == '-':
			if float(col[-3]) == 1: #--Only gaps in alignment
				continue
			else: #--Most abundant element in this position is a gap (not included in consensus)
				if float(col[-3]) <= args.variants_threshold:
					indels += 1
		else: 
			consensus.append(col[-1])
			try:
				base_index = bases.index(col[-1].upper())
				if float(col[base_index + 1]) <= args.variants_threshold:
					muts = [float(x) for x in col[1:6]]



					#--if more than one element have the same percentage, python returns the first in the original array
					next_most_abundant = bases[muts.index(sorted(muts, reverse=True)[1])]
					print(col[-1], next_most_abundant)
					print(col)
					if next_most_abundant == '-':
						indels += 1
					else:
						snvs += 1

			except ValueError: #--Degenerated bases
				snvs += 1




	#--Writing output
	with open(f'{prefix}.consensus.fasta', 'w') as output:
		consensus_name = f'{prefix}_SNVs={snvs}_Indels={indels}'
		output.write('>{}\n{}\n'.format(consensus_name, ''.join(consensus)))

	msg = f'Variants analysis\nSNVs:{snvs}\nIndels: {indels}'
	log_file.write('#'*90 + '\n' + msg + '\n' + '#'*90 + '\n')
	log_file.close()


	#--Removing intermediate files
	if not args.keep_temporal:
		os.remove(f'{prefix}.fasta')
		os.remove(f'{prefix}.align')
		os.remove(f'{prefix}.align_report')
		os.remove(f'{prefix}.cons.fasta')
		os.remove(f'{prefix}.cons.summary')

		subprocess.call(f'rm -fr {prefix}.flip.accnos', shell=True)
		subprocess.call('rm -fr *.logfile', shell=True)

#--Functions
def runCMD(cmd):
	out, err = subprocess.Popen(cmd, shell = True, stdout=subprocess.PIPE).communicate()
	return out.decode()

def fastqRead(fastq):

	with open(fastq, 'r') as infile:

		while True:
			name = infile.readline().rstrip('\n')
			seq = infile.readline().rstrip('\n')
			coment = infile.readline().rstrip('\n')
			qual = infile.readline().rstrip('\n')

			if not name: break

			record = [name, seq, coment, qual]

			yield record

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


