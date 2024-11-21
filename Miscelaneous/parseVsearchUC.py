#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
'''
------------------------------------------------------------------------------------------
Parsing vsearch cluster_fast output (uc file, see format below).

Representative sequence is chosen by the minimun number of SNVS (present in fasta names
produce by wellConsensus.sh)

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
'''
##########################################################################################

#--Imports
import sys
import os
import argparse
from collections import defaultdict

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('ucfile', type = str, help = 'vsearch --cluster_fast output file')
	parser.add_argument('fasta', type = str, help = 'fasta input for vsearh')
	args = parser.parse_args()
	##########################################################################################
	##########################################################################################
	fasta = fasta2dict(args.fasta)

	clusters = defaultdict(list)
	for col in readTSV(args.ucfile):
		if col[0] == 'S' or col[0] == 'H': #--Cluster reference sequences
			cluster = col[1]
			clusters[cluster].append([col[8], int(col[8].split('=')[-1])])

	with open('.'.join(args.ucfile.split('.')[:-1]) + '_clusters.txt', 'w') as output:
		with open('.'.join(args.fasta.split('.')[:-1]) + '_representative.fasta', 'w') as outputfasta:
			output.write('N_Wells\tRepresentative\tMembers\n')
			for cluster in clusters:
				output.write(str(len(clusters[cluster])) + '\t')
				sorted_cluster_by_snvs = sorted(clusters[cluster], key = lambda x: x[1])
				output.write(sorted_cluster_by_snvs[0][0] + '\t')
				outputfasta.write('>{}\n{}\n'.format(sorted_cluster_by_snvs[0][0], fasta[sorted_cluster_by_snvs[0][0]]))
				members = [seqname[0] for seqname in sorted_cluster_by_snvs[1:]]
				output.write(','.join(members) + '\n')


def fasta2dict(file, split_names=False):
	
	""" Función que recorre un fichero fasta y almacena la información en un diccionario """
	
	#--Variables
	fasta = {}
	seq = "" 

	#--Recorremos el fichero que contiene las secuencias en fasta 
	infile = open (file, 'r')
	
	for line in infile:
		line = line.rstrip('\n')

		if line[0] == '>':
		
			if seq:
			
				fasta[name] = seq
				seq = ""
				
			name = line[1:]
			if split_names: name = line.split()[0][1:]
			
		else:
		
			seq = seq + line

	#--La última secuencia
	fasta[name] = seq
	infile.close()
	
	#--Devolvemos el diccionario
	return fasta

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
if __name__ == '__main__':

	main()



