#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################################
"""
------------------------------------------------------------------------------------------
Description:

This script takes fasta

Requirements:

	vsearch (v2.22.1, https://github.com/torognes/vsearch)
		Must be in PATH or use -b option to specify the path to containing folder


Outputs:
	output_prefix.uc (see vsearch manual)
	output_prefix_clusters.txt (only if -w option is applied)

Example: 
	vsearchClustering.py *.consensus.fasta -o plate_E7 -w 

Future improvement ideas:




### VSEARCH installation (https://github.com/torognes/vsearch)
wget https://github.com/torognes/vsearch/archive/v2.22.1.tar.gz
tar xzf v2.22.1.tar.gz
cd vsearch-2.22.1
./autogen.sh
./configure CFLAGS="-O3" CXXFLAGS="-O3"
make
make install  # as root or sudo make install

or download precompiled version from https://github.com/torognes/vsearch/releases
or use the vsearch integrated un Mothur, just put it on the PATH

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
	parser.add_argument('input_files', nargs="*", type = str, help = 'list or regex for input fasta files to include')
	parser.add_argument('-o', dest='output', type = str, required=True, help = 'Output prefix name')

	parser.add_argument('-i', dest = 'identity', type = int, default = 0.99, help = 'Minimum identity to build clusters: Default: 0.99')
	parser.add_argument('-b', dest = 'binpath', type = str, help = 'VSEARCH containing folder. If not specify it is expected to be in PATH')
	parser.add_argument('-w', dest = 'from_wellConsensusMothur', action='store_true', default = False, help = 'Input sequences were generated using wellConsensusMothur.py and the vsearch output will be parsed considering the number of reads and SNV/Indel detected during consensus building to choose a representative sequence. Default: False')

	parser.add_argument('-k', dest = 'keep_temporal', action='store_true', default = False, help = 'Use this option to keep temporal files. Default: False')
	parser.add_argument('-v', '--version', action='version', version=__file__ + ' Version: ' + __version__)

	args = parser.parse_args()
	##########################################################################################
	#--Check the number of input files (>=2)
	if len(args.input_files) < 2:
		sys.exit('#'*90 + '\nERROR: at least 2 files must be given\n' + '#'*90)

	#--Defining path and check requirements
	binpath = ''
	if args.binpath:
		binpath = args.binpath + "/"
		if not checkfile(f'{binpath}vsearch'):
			sys.exit('#'*90 + '\nERROR: vsearch were not found in specify path\n' + '#'*90)
	else:
		if not checkPATH("vsearch"):
			sys.exit('#'*90 + '\nERROR: vsearch were not found in PATH\n' + '#'*90)

	#--Joining all sequences in a single file
	with open(f'{args.output}.fasta', 'w') as all_seq_file:
		for file in args.input_files:
			for name, seq in fastaRead(file):
				all_seq_file.write(f'>{name}\n{seq}\n')

	#--Running vsearh
	### Vsearch uses all threads and ran memory avaible in the machine and I do no know how to change this
	cmd=f'{binpath}vsearch --cluster_fast {args.output}.fasta -id {args.identity} -uc {args.output}.uc'
	print(cmd)
	run_log = runCMD(cmd)
	print(run_log)
	# outputs:
		# output_prefix.uc


	#--Parsing vsearch output (-w)
	if args.from_wellConsensusMothur:

		fasta = fasta2dict(f'{args.output}.fasta')

		from collections import defaultdict
		clusters = defaultdict(list)

		for col in readTSV(f'{args.output}.uc'):
			if col[0] == 'S' or col[0] == 'H': #--Cluster reference sequences accordingly to vsearch
				cluster = col[1] #--Cluster number
				reads = float(col[8].split('_')[-3].split('=')[1])
				snvs = float(col[8].split('_')[-2].split('=')[1])
				indels = float(col[8].split('_')[-1].split('=')[1])
				quality = reads / (snvs+indels+1) #--the higher the value, the smaller the number of variants per read

				clusters[cluster].append([col[8], quality])


		with open(f'{args.output}_clusters.txt', 'w') as output:
			with open(f'{args.output}_representative.fasta', 'w') as outputfasta:

				output.write('Representative\tN_Members\tMembers\n')
				for cluster in clusters:
					output.write(str(len(clusters[cluster])) + '\t')
					sorted_cluster = sorted(clusters[cluster], key = lambda x: x[1], reverse=True)
					output.write(sorted_cluster[0][0] + '\t')
					outputfasta.write('>{}\n{}\n'.format(sorted_cluster[0][0], fasta[sorted_cluster[0][0]]))
					members = [seqname[0] for seqname in sorted_cluster[1:]]
					output.write(','.join(members) + '\n')

#--Functions
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

def runCMD(cmd):
	out, err = subprocess.Popen(cmd, shell = True, stdout=subprocess.PIPE).communicate()
	return out.decode()

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

def checkfile(file):

	return os.path.exists(file)

def checkPATH(program):

	""" Return true if program is on PATH """

	from shutil import which

	return which(program) is not None

##########################################################################################
if __name__ == "__main__":

	main()


