#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

# Import functions
source $SCRIPT_PATH/functions.sh

# Define the MD5 checksum
md5Checksum="ee942fcbdaa306f46d807e7e3137447d"

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# NP weights download URL
url="https://drive.usercontent.google.com/download?id=1DdQLXbEZOaUm_3IqWj1YfCMK25MA0m5b&confirm=t"

fileName="NP_model.pt"
filePath="$directoryPath/$fileName"

download_file $url $filePath $md5Checksum
if [[ $? -ne 0 ]]; then
    echo "The model weights downloaded unsuccessfully. Exiting script with error."
    exit 1
fi
