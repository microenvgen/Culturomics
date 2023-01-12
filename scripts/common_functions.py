#!/usr/bin/env python
#-*- coding: UTF-8 -*-


##########################################################################################  

#--Sequence manipulation
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

def fasta2dict(file, split_names=False):
	
	""" Reads a fasta file and store sequences in a dictionary """
	
	#--Variables
	fasta = {}
	seq = "" 

	#--Reading fasta file
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

	#--Last sequences
	fasta[name] = seq
	infile.close()

	return fasta

#--File manipulations
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

	"""Check if a file/folder exits """

	from os import path

	return path.exists(file)

def checkpath(program):

	""" Return true if program is on PATH """

	from shutil import which

	return which(program) is not None

#--Miscelaneous
def runexternalcommand(cmd):

	""" Facilitates the running of external commands by using subprocesses """
	import subprocess

	out, err = subprocess.Popen(cmd, shell = True, stdout=subprocess.PIPE).communicate()

	log = ''
	if out: 
		out = out.decode()
		log += out
	if err: 
		err = err.decode()
		log += err

	return log
