#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
'''
------------------------------------------------------------------------------------------
Merging clusters file (from vsearchClustering.py) and taxonomy output from mothur (fasta2taxo.py)

Clusters output:
N_Members	Representative	Members
10	E7_Well_E5_Locus_16S_long_READS=33_VARIANTS=11:16:0_Q=0.550	E7_Well_C5_Locus_16S_long_READS=27_VARIANTS=16:15:1_Q=0.458,E7_Well_C11_Locus_16S_long_READS=13_VARIANTS=37:24:1_Q=0.173,E7_Well_B12_Locus_16S_long_READS=6_VARIANTS=41:33:0_Q=0.075,E7_Well_F6_Locus_16S_long_READS=8_VARIANTS=90:25:0_Q=0.065,E7_Well_C6_Locus_16S_long_READS=9_VARIANTS=128:33:1_Q=0.053,E7_Well_G3_Locus_16S_long_READS=14_VARIANTS=278:41:3_Q=0.042,E7_Well_A11_Locus_16S_long_READS=3_VARIANTS=76:267:12_Q=0.008,E7_Well_D10_Locus_16S_long_READS=4_VARIANTS=346:183:12_Q=0.007,E7_Well_G12_Locus_16S_long_READS=3_VARIANTS=292:136:52_Q=0.006
1	E7_Well_E11_Locus_16S_long_READS=5_VARIANTS=367:150:41_Q=0.009	
33	E7_Well_G6_Locus_16S_long_READS=22_VARIANTS=8:19:0_Q=0.449	E7_Well_E6_Locus_16S_long_READS=23_VARIANTS=15:37:0_Q=0.307,E7_Well_C10_Locus_16S_long_READS=11_VARIANTS=9:18:0_Q=0.289,E7_Well_D6_Locus_16S_long_READS=20_VARIANTS=22:28:0_Q=0.286,E7_Well_G4_Locus_16S_long_READS=13_VARIANTS=20:31:0_Q=0.203,E7_Well_F5_Locus_16S_long_READS=11_VARIANTS=16:31:0_Q=0.190,E7_Well_D4_Locus_16S_long_READS=20_VARIANTS=45:53:0_Q=0.169,E7_Well_D3_Locus_16S_long_READS=13_VARIANTS=32:49:0_Q=0.138,E7_Well_H2_Locus_16S_long_READS=11_VARIANTS=50:28:1_Q=0.122,E7_Well_A4_Locus_16S_long_READS=6_VARIANTS=27:21:2_Q=0.107,E7_Well_C4_Locus_16S_long_READS=17_VARIANTS=112:32:0_Q=0.106,E7_Well_D8_Locus_16S_long_READS=15_VARIANTS=118:36:0_Q=0.089,E7_Well_B8_Locus_16S_long_READS=10_VARIANTS=70:34:0_Q=0.088,E7_Well_D12_Locus_16S_long_READS=21_VARIANTS=226:33:0_Q=0.075,E7_Well_E3_Locus_16S_long_READS=23_VARIANTS=257:30:0_Q=0.074,E7_Well_E4_Locus_16S_long_READS=8_VARIANTS=80:37:0_Q=0.064,E7_Well_F8_Locus_16S_long_READS=20_VARIANTS=238:37:20_Q=0.063,E7_Well_C7_Locus_16S_long_READS=11_VARIANTS=210:42:2_Q=0.042,E7_Well_D5_Locus_16S_long_READS=12_VARIANTS=215:93:0_Q=0.037,E7_Well_G11_Locus_16S_long_READS=8_VARIANTS=239:29:0_Q=0.029,E7_Well_D7_Locus_16S_long_READS=10_VARIANTS=363:71:6_Q=0.022,E7_Well_C8_Locus_16S_long_READS=6_VARIANTS=261:20:4_Q=0.021,E7_Well_D9_Locus_16S_long_READS=6_VARIANTS=244:29:9_Q=0.021,E7_Well_D11_Locus_16S_long_READS=6_VARIANTS=250:41:11_Q=0.019,E7_Well_F3_Locus_16S_long_READS=3_VARIANTS=73:84:2_Q=0.019,E7_Well_B6_Locus_16S_long_READS=7_VARIANTS=286:83:14_Q=0.018,E7_Well_G8_Locus_16S_long_READS=5_VARIANTS=341:124:1_Q=0.011,E7_Well_F9_Locus_16S_long_READS=4_VARIANTS=298:108:9_Q=0.010,E7_Well_F10_Locus_16S_long_READS=3_VARIANTS=137:149:9_Q=0.010,E7_Well_E9_Locus_16S_long_READS=3_VARIANTS=290:81:9_Q=0.008,E7_Well_B9_Locus_16S_long_READS=4_VARIANTS=414:142:11_Q=0.007,E7_Well_G5_Locus_16S_long_READS=4_VARIANTS=377:176:10_Q=0.007,E7_Well_C3_Locus_16S_long_READS=4_VARIANTS=449:234:4_Q=0.006

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
import common_functions as cf

def main():

	##########################################################################################
	#--Argument
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('taxo', type = str, help = 'taxonomy file from mothur')
	parser.add_argument('clusters', type = str, help = 'clusters file from vsearchClustering.py -p (vsearch)')
	parser.add_argument('output', type = str, help = 'output file name')
	args = parser.parse_args()
	##########################################################################################
	clusters = {col[1]:col for col in cf.readTSV(args.clusters, header=True)}
	taxo = {col[0]:col[1] for col in cf.readTSV(args.taxo)}

	with open(args.output, 'w') as output:
		output.write("{}\t{}\t{}\t{}\n".format("Number_of_wells", "Representative", "Taxonomy", "Members"))

		for rep in taxo.keys():
			cluster_info = clusters[rep]
			output.write("{}\t{}\t{}\t{}\n".format(cluster_info[0], rep, taxo[rep], cluster_info[2]))

##########################################################################################
if __name__ == '__main__':

	main()



