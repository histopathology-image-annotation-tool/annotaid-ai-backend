#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

# Import functions
source $SCRIPT_PATH/functions.sh

# Define the MD5 checksums
md5ChecksumFirstStage="b925a51aa6acaf889f6104f239c1c0a5"
md5ChecksumSecondStage="50dbb9d396ef71cb660b1c0b7961cf62"

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# MC weights download URL
url_first_stage="https://drive.usercontent.google.com/download?id=1DDEfvJvhgjh3PXHRHW7pql_Lcmodkpri&confirm=t"
url_second_stage="https://drive.usercontent.google.com/download?id=1r8S42ksZgx0Cr1maBAaeQbPTOeUEWvFy&confirm=t"

fileNameFirstStage="MC_first_stage.pt"
filePathFirstStage="$directoryPath/$fileNameFirstStage"

fileNameSecondStage="MC_second_stage.pt"
filePathSecondStage="$directoryPath/$fileNameSecondStage"

download_file $url_first_stage $filePathFirstStage $md5ChecksumFirstStage
if [[ $? -ne 0 ]]; then
    echo "First stage download was unsuccessful. Exiting script with error."
    exit 1
fi

download_file $url_second_stage $filePathSecondStage $md5ChecksumSecondStage
if [[ $? -ne 0 ]]; then
    echo "Second stage download was unsuccessful. Exiting script with error."
    exit 1
fi
