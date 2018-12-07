#!/bin/bash

RESOLVE_LINK=`readlink -f $0`

SBF_CONVERTER_HOME=`dirname ${RESOLVE_LINK}`
LIB_PATH=${SBF_CONVERTER_HOME}/lib

if [ $# -lt 2 ] 
 then
     echo "Usage: "
     echo "       $0 [-i|-m|-u] [file.xml | folder] [file suffix]"     
     echo "              will transform the given file(s) and update his annotations."
     echo ""
     echo "              -m will update the given sbml file to use miriam urn-uris"
     echo "              -i will update the given sbml file to use miriam url-uris (identifiers.org urls)"
     echo "              -u will update the given sbml file to the correct and up-to-date miriam urn-uris"

     exit 1
fi

export ANNO_UPDATE_OPTION=$1
SBML_DIR=$2
FILE_SUFFIX=""
CONVERTER_NAME="identifiersUtil"

if [ $# -ge 3 ] 
then
    FILE_SUFFIX=$3
fi
# If not suffix given, the java class will decided of a suffix depending of the options given (-i, -m or -u)
# Nothing will be overwritten.

# For path2model, we have too many files so we are going back to only one log file per day
#LOG_FILE_FOLDER=${SBF_CONVERTER_HOME}/log/`basename $SBML_DIR .xml`
#LOG_FILE=${LOG_FILE_FOLDER}/`basename $SBML_DIR .xml`-$CONVERTER_NAME-export-`date +%F`.log
LOG_FILE=${SBF_CONVERTER_HOME}/log/$CONVERTER_NAME-export-`date +%F`.log

COMMAND="bsub $BSUB_OPTIONS -o $LOG_FILE java -Dmiriam.xml.export=${SBF_CONVERTER_HOME}/miriam.xml "
USE_BSUB="yes"

#
# TODO : add an option to enable or not the use of the cluster, the default being not enabled so that biomodels does not need to change anything.
#
#if [ "`which bsub 2> /dev/null`" == "" ] ; then
    COMMAND="java -Dmiriam.xml.export=${SBF_CONVERTER_HOME}/miriam.xml "
    USE_BSUB="no"
#fi

export CLASSPATH=

for jarFile in $LIB_PATH/*.jar
do
    export CLASSPATH=$CLASSPATH:$jarFile
done

if [ -d $SBML_DIR ]
then
    for file in $SBML_DIR/*.xml
    do
        # Creating a log file specific to each file.
	LOG_FILE_FOLDER=${SBF_CONVERTER_HOME}/log/`basename $file .xml`
	LOG_FILE_MULTI=${LOG_FILE_FOLDER}/`basename $file .xml`-$CONVERTER_NAME-export-`date +%F`.log

	# checks that the model specific folder does exist and create it if not.
	if [ ! -d "$LOG_FILE_FOLDER" ]; then
	    mkdir -p $LOG_FILE_FOLDER
	fi
	if [ "$USE_BSUB" == "yes" ] ; then
	    COMMAND="bsub $BSUB_OPTIONS -o $LOG_FILE_MULTI java -Dmiriam.xml.export=${SBF_CONVERTER_HOME}/miriam.xml "
	fi

	echo "------------------------------------------------------------" >> $LOG_FILE_MULTI   2>&1
	echo "`date +"%F %R"`" >> $LOG_FILE_MULTI  2>&1
	echo "`basename $0`: Convertion, using $CONVERTER_NAME, for '$file'..." >> $LOG_FILE_MULTI  2>&1
	echo "------------------------------------------------------------" >> $LOG_FILE_MULTI  2>&1

	eval $COMMAND org.sbfc.converter.sbml2sbml.IdentifiersUtil ${ANNO_UPDATE_OPTION} $file $FILE_SUFFIX >> $LOG_FILE_MULTI  2>&1
	sleep 0.3
    done
else

    # checks that the model specific folder does exist and create it if not.
    # if [ ! -d "$LOG_FILE_FOLDER" ]; then
    # 	mkdir -p $LOG_FILE_FOLDER
    # fi

    file=${SBML_DIR}    

    echo "------------------------------------------------------------" >> $LOG_FILE  2>&1
    echo "`date +"%F %R"`" >> $LOG_FILE  2>&1
    echo "`basename $0`: Convertion, using $CONVERTER_NAME, for '$file'..." >> $LOG_FILE  2>&1
    echo "------------------------------------------------------------" >> $LOG_FILE  2>&1

    eval $COMMAND  org.sbfc.converter.sbml2sbml.IdentifiersUtil ${ANNO_UPDATE_OPTION} $file $FILE_SUFFIX >> $LOG_FILE  2>&1

    ## This grep command will display directly to the user if they were any wrong annotations
    ## so that there is no need to check the log file to do that.
    grep miriamws $LOG_FILE

    exit 0
fi


