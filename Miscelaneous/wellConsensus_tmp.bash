#!/bin/bash

#--Default values
SEQMINLEN=900
CONSENSUSCUTOFF=50
SNVTHRESHOLD=0.8
CLUSTERINGTHRESHOLD=0.99


input=`basename ${1} .fastq`
output=${input}"_consensus.fasta"

#--Counting FASTQ reads 
r=`wc -l ${input}'.fastq' | awk '{print $1/4}'`
printf "FASTQ reads:${r}"
if [[ $r < 1 ]]
then
	printf "No sequences found in ${input}.fastq"
else
	#--fastq2fasta
	cat ${input}'.fastq' | gawk 'BEGIN{P=1}{if(P==1||P==2){gsub(/^[@]/,">");print}; if(P==4){P=0}; P++}' > ${input}'.fasta'

	#--Filtering sequences shorter than SEQMINLEN
	mothur "#screen.seqs(fasta=${input}.fasta, minlength=${SEQMINLEN})"

	#--Counting good reads
	READS=`grep -c '>' ${input}".good.fasta"`
	if [[ $READS < 1 ]] 
		then
			printf "No sequences found in ${input}.good.fasta"
		else
			#--Aligning reads against seed database
			mothur "#align.seqs(candidate=${input}.good.fasta, template=silva.seed_v138_1.align)"

			#--Consensus (filter all dots otherwise consensus calculation takes to long....)
			mothur "#filter.seqs(fasta=${input}.good.align, vertical=T, trump=.)"
			mothur "#consensus.seqs(fasta=${input}.good.filter.fasta, cutoff=${CONSENSUSCUTOFF})"

			#--Removing gaps from consensus
			mothur "#degap.seqs(fasta=${input}.good.filter.cons.fasta)"

			#--Detecting Variants (reading .good.cons.summary file)
			VARIANTS=`cat ${input}".good.filter.cons.summary" | gawk -v SNVTHRESHOLD="$SNVTHRESHOLD" 'BEGIN { bases["A"]=2; bases["T"]=3; bases["G"]=4; bases["C"]=5;} {if (NR!=1 && $8!="-"){ if($bases[$8] < SNVTHRESHOLD) {s+=1}}} END {print s}'`
			#--If only 1 sequence in fasta file, no VARIANTS are detected...
			if [[ -z ${VARIANTS} ]] 
				then
					VARIANTS=0
			fi

			printf "VARIANTS:${VARIANTS}"

