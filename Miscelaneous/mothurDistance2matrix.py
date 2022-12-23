#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
'''
------------------------------------------------------------------------------------------
Parsing distance file output from: mothur dist.seqs(fasta=representative.align)

all.fastq_B10_Well_B1_locus_16S_long_READS=4_SNVS=524 all.fastq_B10_Well_D1_locus_16S_long_READS=2_SNVS=0 0.0953029
all.fastq_B10_Well_B1_locus_16S_long_READS=4_SNVS=524 all.fastq_B10_Well_H1_locus_16S_long_READS=4_SNVS=195 0.152055
all.fastq_B10_Well_B1_locus_16S_long_READS=4_SNVS=524 all.fastq_B10_Well_C10_locus_16S_long_READS=10_SNVS=50 0.0328767
all.fastq_B10_Well_B1_locus_16S_long_READS=4_SNVS=524 all.fastq_B10_Well_D7_locus_16S_long_READS=1011_SNVS=2 0.0290828
all.fastq_B10_Well_B1_locus_16S_long_READS=4_SNVS=524 all.fastq_B10_Well_B10_locus_16S_long_READS=7_SNVS=244 0.0712329


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
	parser.add_argument('dist', type = str, help = 'mothur dist.seqs(fasta=representative.align)')
	parser.add_argument('output', type = str, help = 'matrix output name')
	args = parser.parse_args()
	##########################################################################################
	dist =defaultdict(lambda:defaultdict(float))
	for col in readTable(args.dist):
		dist[col[0]][col[1]] = float(col[2])
		dist[col[1]][col[0]] = float(col[2])

	with open(args.output, 'w') as output:

		names = list(dist.keys())
		output.write("\t{}\n".format("\t".join(names)))
		for name1 in names:
			distances = [str(dist[name1][name2]) for name2 in names]
			output.write("{}\t{}\n".format(name1, "\t".join(distances)))




def readTable(file, header=False, comments=None):

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

			col = line.split()

			yield col

##########################################################################################
if __name__ == '__main__':

	main()



