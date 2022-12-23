#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
'''
------------------------------------------------------------------------------------------
Merging clusters file (from parseVsearchUC.py) and taxonomy output from mothur ()

Clusters output:
N_wells	Representative	Members
1	all.fastq_B10_Well_H8_locus_16S_long_READS=2_SNVS=0	
1	all.fastq_B10_Well_D1_locus_16S_long_READS=2_SNVS=0	
1	all.fastq_B10_Well_H1_locus_16S_long_READS=4_SNVS=195	
7	all.fastq_B10_Well_C10_locus_16S_long_READS=10_SNVS=50	all.fastq_B10_Well_F1_locus_16S_long_READS=6_SNVS=77,all.fastq_B10_Well_H6_locus_16S_long_READS=7_SNVS=126,all.fastq_B10_Well_A8_locus_16S_long_READS=4_SNVS=249,all.fastq_B10_Well_G5_locus_16S_long_READS=4_SNVS=280,all.fastq_B10_Well_G6_locus_16S_long_READS=8_SNVS=351,all.fastq_B10_Well_H5_locus_16S_long_READS=9_SNVS=390

Taxonomy output from mothur (mothur classify.seqs(fasta=representative.unique.fasta, count=representative.count_table, representative=silva.seed_v138_1.align, taxonomy=silva.seed_v138_1.tax))
all.fastq_B10_Well_F6_locus_16S_long_READS=297_SNVS=326	Bacteria(100);Actinobacteriota(100);Actinobacteria(100);Propionibacteriales(100);Propionibacteriaceae(100);Cutibacterium(100);
all.fastq_B10_Well_D1_locus_16S_long_READS=2_SNVS=0	Bacteria(100);Proteobacteria(100);Gammaproteobacteria(100);Pseudomonadales(100);Pseudomonadaceae(100);Pseudomonas(100);
all.fastq_B10_Well_H8_locus_16S_long_READS=2_SNVS=0	Bacteria(100);Proteobacteria(100);Gammaproteobacteria(100);Pseudomonadales(100);Pseudomonadaceae(100);Pseudomonas(100);

------------------------------------------------------------------------------------------
'''
##########################################################################################

#--Imports
import sys
import os
import argparse

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('taxo', type = str, help = 'taxonomy file from mothur')
	parser.add_argument('clusters', type = str, help = 'clusters fiel from parseVsearchUC.py (vsearch)')
	parser.add_argument('output', type = str, help = 'output file name')
	args = parser.parse_args()
	##########################################################################################
	clusters = {col[1]:col for col in readTSV(args.clusters, header=True)}
	taxo = {col[0]:col[1] for col in readTSV(args.taxo)}

	with open(args.output, 'w') as output:
		output.write("{}\t{}\t{}\t{}\n".format("Representative", "Taxonomy", "Number_of_wells", "Members"))

		for rep in taxo.keys():
			cluster_info = clusters[rep]
			output.write("{}\t{}\t{}\t{}\n".format(rep, taxo[rep], cluster_info[0], cluster_info[2]))






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



