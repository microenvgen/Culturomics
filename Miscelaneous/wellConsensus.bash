#!/bin/bash

#--Usage
syntax="$(basename "$0") -f <FASTQ_FOLDER>[-o <output_prefix>=consensus][-p <processors>=2][-h]"
usage="
################################################################################
${sintax}

Utility:
	Script for processing MinIon 16S long sequences.
	Sequences must be in fastq format (uncompressed).
	It takes all fastq files in the current folder and use the following protocol for each fastq file:
		-Remove sequences shorter than SEQMINLEN=900
		-Align sequence against a seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
		-Creates a consensus sequence (CONSENSUSCUTOFF=50)
		-Count nucleotide variants in consensus (SNVTHRESHOLD=0.8)

	Then, all consensus sequences are clustered (CLUSTERINGTHRESHOLD=0.99) and select a representative base on then minimun number os variants detected. 

	Finally, a taxonomical classifycation is performed with mothur using seed database

Dependencies:
	python3+
	Mothur and vsearch (vserach included in Mothur, https://github.com/mothur/mothur/releases/download/v1.48.0/Mothur.linux_7.zip)
	Seed database (https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v138_1.tgz)
	parseVsearchUC.py, a parsing script for vserach output (must be in BINPATH)
	mothurDistance2matrix.py, a parsing script for mothur distance output (must be in BINPATH)
	mergeClusterAndTaxo.py, a parsing script for mothur taxonomy output and clusters (must be in BINPATH)

	NOTE: mothur, vsearch and seed database must all be in BINPATH folder

Arguments (mandatory):
	-f folder containing fastq files (not compressed)

Arguments (optional):
	-o output name prefix (default=consensus)
	-p number of processors (default=2)

Help:
	-h  show help

Example:
	./wellConsensus.sh -f fastq_folder -o sample_xxx -p 12
	SLURM: sbatch -A microbioma_serv -p bio,biobis -N 1 -n 32 -o test_plate.log -s  wellConsensus.bash -f test_plate -o test_plate -p 32

To modify any of the parameters (including BINPATH) go to Default values section.



NOTE: when a "N" appears in consensus sequence it means that any base is represented by more than 50% of the reads.
Usually, this happens when very few reads are available and 50% of reads have one base while the other 50% of reads
have another. This could indicate that more than one species is being sequenced in the same well. 

################################################################################
"
#--Default values
OUTPUTNAME="consensus"
SEQMINLEN=900
CONSENSUSCUTOFF=50
SNVTHRESHOLD=0.8
CLUSTERINGTHRESHOLD=0.99
BINPATH="/home/proyectos/microbioma/resources/software/mothur-1.48.0/"
PROC=2

#--Avoid empty arguments
if [[ ! $@ =~ ^\-.+ ]]
	then
	printf "################################################################################\n"
	printf "\nERROR: arguments (-f) must be given. \n \n"
	printf "$syntax\n"
	printf "################################################################################\n"
	exit 1
fi

#--Argument parsing
while getopts 'hf:p:o:' option; do
	case "$option" in
		h) 
			printf "$usage"
			exit 1
			;;
		f)
			if [ -d ${OPTARG} ]
				then
					FOLDER=$OPTARG
				else
					printf "################################################################################\n"
					printf "\nERROR: Folder does not exits. Please, provide an existing directory. \n \n" >&2
					printf "################################################################################\n"
				exit 1
			fi
			;;
		o)
			OUTPUTNAME=$OPTARG
			;;
		p)
			PROC=$OPTARG
			;;
		:)
			printf "\nERROR: Missing value for -%s\n" "$OPTARG" >&2
			printf "$sintax \n" >& 2
			exit 1
			;;
		\?)
			printf "\nERROR: Illegal option: -%s\n" "$OPTARG" >&2
			printf "$sintax \n" >&2
			exit 1
			;;
	esac
done

#--Loading python3 in cluster
module load python/python-3.7-intel

#--Current directory
DATADIR=`pwd`

#--Creating a the working directory in temporal folder (only required for cluster usage)
WORKINGDIR=/temporal/$USER/$OUTPUTNAME'_'$$
if [ -d $WORKINGDIR ]
	then
	rm -fr $WORKINGDIR
fi
mkdir -p $WORKINGDIR
cd $WORKINGDIR

#--copy data WORKINGDIR (also seed database)
cp ${DATADIR}/${FOLDER}/*.fastq $WORKINGDIR
cp ${BINPATH}/silva.seed_v138_1.align $WORKINGDIR
cp ${BINPATH}/silva.seed_v138_1.tax $WORKINGDIR

#--INPUT files. File name format: all.fastq_B10_Well_A1_locus_16S_long.fastq
declare -a FILES=()
for f in *.fastq
do
	PREFIX=`basename ${f} .fastq`
	FILES=("${FILES[@]}" ${PREFIX})
done

#--Creating outputfile
if [ -f ${OUTPUTNAME}.fasta ]
	then
	rm -fr ${OUTPUTNAME}.fasta
fi
touch ${OUTPUTNAME}.fasta

#--Processing files with mothur
declare -a NOSEQFILES=()
for f in "${FILES[@]}"
do
	echo $f

	#--Counting FASTQ reads 
	r=`wc -l ${f}'.fastq' | awk '{print $1/4}'`
	if [[ $r < 1 ]] 
		then
			NOSEQFILES=("${NOSEQFILES[@]}" ${f})
		else
			#--fastq2fasta
			cat ${f}'.fastq' | gawk 'BEGIN{P=1}{if(P==1||P==2){gsub(/^[@]/,">");print}; if(P==4){P=0}; P++}' > ${f}'.fasta'

			#--Filtering sequences shorter than SEQMINLEN
			${BINPATH}/mothur "#screen.seqs(fasta=${f}.fasta, minlength=${SEQMINLEN}, processors=${PROC} )"

			#--Counting good reads
			READS=`grep -c '>' ${f}".good.fasta"`
			if [[ $READS < 1 ]] 
				then
					NOSEQFILES=("${NOSEQFILES[@]}" ${f})
				else
					#--Aligning reads against seed database
					${BINPATH}/mothur "#align.seqs(candidate=${f}.good.fasta, template=silva.seed_v138_1.align, processors=${PROC} )"

					#--Consensus (filter all dots otherwise consensus calculation takes to long....)
					${BINPATH}/mothur "#filter.seqs(fasta=${f}.good.align, vertical=T, trump=.)"
					${BINPATH}/mothur "#consensus.seqs(fasta=${f}.good.filter.fasta, cutoff=${CONSENSUSCUTOFF})"

					#--Removing gaps from consensus
					${BINPATH}/mothur "#degap.seqs(fasta=${f}.good.filter.cons.fasta)"

					#--Detecting Variants (reading .good.cons.summary file)
					VARIANTS=`cat ${f}".good.filter.cons.summary" | gawk -v SNVTHRESHOLD="$SNVTHRESHOLD" 'BEGIN { bases["A"]=2; bases["T"]=3; bases["G"]=4; bases["C"]=5;} {if (NR!=1 && $8!="-"){ if($bases[$8] < SNVTHRESHOLD) {s+=1}}} END {print s}'`
					#--If only 1 sequence in fasta file, no VARIANTS are detected...
					if [[ -z ${VARIANTS} ]] 
						then
							VARIANTS=0
					fi

					#--Joining all consensus sequences in a single file
					NEW_NAME=`printf "%s_READS=%s_SNVS=%s" ${f} ${READS} ${VARIANTS}`
					echo '>'$NEW_NAME >> ${OUTPUTNAME}.fasta
					cat ${f}'.good.filter.cons.ng.fasta' | gawk 'BEGIN{P=1}{if(P==2){print};P++}' >> ${OUTPUTNAME}.fasta

					#--Deleting all intermediate files
					# rm -fr ${f}.fasta
					# rm -fr ${f}.bad.accnos
					# rm -fr ${f}.good.fasta
					# rm -fr ${f}.good.align
					# rm -fr ${f}.good.align_report
					# rm -fr ${f}.good.filter.fasta
					# rm -fr ${f}.good.filter.cons.fasta
					# rm -fr ${f}.good.filter.cons.summary
					# rm -fr ${f}.good.filter.cons.ng.fasta

			fi
	fi

done

#--Clustering consensus sequences 
${BINPATH}/vsearch --cluster_fast ${OUTPUTNAME}.fasta -id ${CLUSTERINGTHRESHOLD} -uc ${OUTPUTNAME}.uc
### Vsearch uses all threads and ran memory avaible in the machine and I do no know how to change that

#--Parsing vsearch output
python ${BINPATH}/parseVsearchUC.py ${OUTPUTNAME}".uc" ${OUTPUTNAME}".fasta"

#--Creating dist table and classify sequences
${BINPATH}/mothur "#align.seqs(candidate=${OUTPUTNAME}_representative.fasta, template=silva.seed_v138_1.align, processors=${PROC} )"
${BINPATH}/mothur "#dist.seqs(fasta=${OUTPUTNAME}_representative.align, processors=${PROC} )"
${BINPATH}/mothur "#unique.seqs(fasta=${OUTPUTNAME}_representative.fasta, format=count)"
${BINPATH}/mothur "#classify.seqs(fasta=${OUTPUTNAME}_representative.unique.fasta, count=${OUTPUTNAME}_representative.count_table, reference=silva.seed_v138_1.align, taxonomy=silva.seed_v138_1.tax)"

# rm -fr ${OUTPUTNAME}_representative.align
# rm -fr ${OUTPUTNAME}_representative.align_report
# rm -fr mothur*logfile

#--Reporting files with no sequences
echo "##########################################################################################"
echo "The following were not processed as no sequences were found (before or after length filtering:"
for f in "${NOSEQFILES[@]}"
do
	echo ${f}
done
echo "##########################################################################################"

#--Copy files (only required for cluster running)
mv ${OUTPUTNAME}".fasta" ${OUTPUTNAME}"_wells.fasta"
cp ${OUTPUTNAME}"_wells.fasta" $DATADIR
# cp ${OUTPUTNAME}".uc" $DATADIR
cp ${OUTPUTNAME}"_representative.fasta" $DATADIR

${BINPATH}/mothurDistance2matrix.py ${OUTPUTNAME}"_representative.dist" ${OUTPUTNAME}"_representative_dist.tsv"
cp ${OUTPUTNAME}"_representative_dist.tsv" $DATADIR

${BINPATH}/mergeClusterAndTaxo.py ${OUTPUTNAME}"_representative.unique.seed_v138_1.wang.taxonomy" ${OUTPUTNAME}"_clusters.txt" ${OUTPUTNAME}"_results.tsv"
cp ${OUTPUTNAME}"_results.tsv" $DATADIR

# cp ${OUTPUTNAME}"_representative.count_table" $DATADIR
# cp ${OUTPUTNAME}"_clusters.txt" $DATADIR
# mv ${OUTPUTNAME}"_representative.unique.seed_v138_1.wang.taxonomy" ${OUTPUTNAME}"_representative_taxo.tsv"
# cp ${OUTPUTNAME}"_representative_taxo.tsv" $DATADIR
# cp ${OUTPUTNAME}"_representative.unique.seed_v138_1.wang.tax.summary" $DATADIR

#--Unloading python3 in cluster  (only required for cluster running)
module unload python/python-3.7-intel

#--Delete $WORKINDGIR  (only required for cluster running)
rm -fr $WORKINDGIR
