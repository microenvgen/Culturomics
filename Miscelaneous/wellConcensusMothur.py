#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:



Requirements:

- Mothur (v.1.48.0, https://github.com/mothur/mothur/releases/download/)
	Must be in PATH or use -m option to specify the path to containing folder

- Seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
	It is expected to be in the current directory, otherwise use -s option to specify the 
	path to containing folder


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
	# parser.add_argument('output', type = str, help = '.....')

	parser.add_argument('-m', dest = 'mothur_path', type = str, help = 'Mothur containing folder. If not specify it should expected to be in PATH')
	parser.add_argument('-s', dest = 'seed_path', type = str, help = 'seed containing folder. If not specify it should expected to be in the current directory')

	parser.add_argument('-l', dest = 'length', type = int, default = 900, help = 'Minumim read length to include in downstream analysis. Default: 900')
	parser.add_argument('-c', dest = 'cutoff', type = int, default = 50, help = 'Cutoff (%) for defining consensus base: Default: 50')



	parser.add_argument('-t', dest = 'threads', type = str, default = 2, help = 'Number of threads. Default: 2')

	args = parser.parse_args()
	##########################################################################################

	#--Input file prefix
	prefix = '.'.join(args.fastq.split('.')[:-1])

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
		sys.exit('No reads were found in fasta file.')

	####--Running Mothur--####
	#--Defining paths
	mothur_path = ''
	if args.mothur_path: mothur_path = args.mothur_path + "/"

	seed_path = ''
	if args.seed_path: seed_path = args.seed_path + "/"

	#--Aligning reads against seed database
	cmd = f'{mothur_path}mothur "#align.seqs(candidate={fasta_file_name}, template={seed_path}silva.seed_v138_1.align, processors={args.threads})"'
	print(cmd)
	runCMD(cmd)

	#--Consensus (filtering all dots otherwise consensus calculation takes to long....)
	cmd = f'{mothur_path}mothur "#filter.seqs(fasta={prefix}.align, vertical=T, trump=.)"'
	print(cmd)
	runCMD(cmd)

	cmd = f'{mothur_path}mothur "#consensus.seqs(fasta={prefix}.filter.fasta, cutoff={args.cutoff})"'
	print(cmd)
	runCMD(cmd)

	#--Removing gaps from consensus
	# mothur "#degap.seqs(fasta=${input}.good.filter.cons.fasta)"




#--Functions
def runCMD(cmd):
	out, err = subprocess.Popen(cmd, shell = True, stdout=subprocess.PIPE).communicate()
	print('#################')
	print(out.decode())
	print('#################')
	print(err)

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

##########################################################################################
if __name__ == "__main__":

	main()


