#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
	------------------------------------------------------------------------------------------
	Remove non-bacterial sequences from silva.seed_v138_1.align
	Obtained from Mothur: https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz
	------------------------------------------------------------------------------------------
"""
##########################################################################################

#--Imports
import sys
import os
import argparse



def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('input', type = str, help = '')
	args = parser.parse_args()
	##########################################################################################
	outputname = "{}_onlyBac.{}".format('.'.join(args.input.split('.')[:-1]),args.input.split('.')[-1]) 


	with open(outputname, 'w') as output:
		for name, seq in fastaRead(args.input):
			taxo = name.split()[2].split(";")[0]
			if taxo == "Bacteria":
				output.write('>{}\n{}\n'.format(name, seq))


	##########################################################################################
def fastaRead(fasta, split_names=False):

	with open(fasta, 'r') as infile:
		
		seq = ''
		for line in infile:

			line = line.strip()

			if line.startswith(">"):
				
				if seq:

					yield name, seq
					seq = ''

				name = line[1:]
				if split_names: name = line.split()[0][1:]

			else:
				seq = seq + line

	#--Last sequence
	yield name, seq

##########################################################################################
if __name__ == "__main__":

	main()

##########--seed.align--##########
# https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz

# En la base de datos Seed, como tenemos la taxonomía nos quedamos sólo con las bacterias y luego eliminar las posiciones con ".".

# grep -c Eukaryota silva.seed_v138_1.align   --> 1824
# grep -c Bacteria silva.seed_v138_1.align    --> 5736
# grep -c Archaea silva.seed_v138_1.align     -->   81

# #--Remove non bacteria sequences
# python removeNonBacs.py silva.seed_v138_1.align 
# grep -c '>' silva.seed_v138_1_onlyBac.align --> 5736

# #--Remove all dots columns (.)
# mothur "#filter.seqs(fasta=silva.seed_v138_1_onlyBac.align, vertical=T, trump=.)"
# 279Mb --> 29Mb

# mv silva.seed_v138_1_onlyBac.filter.fasta seed.align

