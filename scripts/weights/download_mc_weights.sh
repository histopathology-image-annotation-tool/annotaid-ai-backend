#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

# Import functions
source $SCRIPT_PATH/functions.sh

# Define the MD5 checksums
md5ChecksumFirstStage="1db89bc27cd96aeaa16b9894c879d3bc"
md5ChecksumSecondStage="85610a44afecb385c42c2eab9c60a4c6"

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# MC weights download URL
url_first_stage="https://drive.usercontent.google.com/download?id=1Zt9lCDMxcXIg-jtgMWQYpS43RkIHqUFi&confirm=t"
url_second_stage="https://drive.usercontent.google.com/download?id=1ZknkLXuiJovzp9hz3lciyXCB5xmK_Wen&confirm=t"

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
