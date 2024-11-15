#!/bin/bash
hostname

#--Argument control
if [[ $# -ne 2 ]]
	then
	echo '--------------------------------------------------------------------------------------------------------------'
	echo 'Usage: runWellConsensusn.sh <folder><cores>'
	echo '--------------------------------------------------------------------------------------------------------------'
	exit
fi

#--Set environment
dt=`pwd`
folder=$1
cores=$2

startTime=`date +%s`

#--Create working dir #[[ -d $wd ]] && rm -fr $wd && mkdir -p $wd
wd=/junk/$USER/$folder'_'$$
if [ -d $wd ]
	then
	rm -fr $wd
fi
mkdir -p $wd
cd $wd

#--Copy data to junk/scratch
cp -r $dt/$folder $wd

#--Run programs
wellConsensus.py -f $folder -t $cores

#--Copying results back to data dir
cp -r $wd/$folder $dt

#--Deleting workdir
rm -fr $wd

echo "It took $(expr `date +%s` - $startTime) seconds"


