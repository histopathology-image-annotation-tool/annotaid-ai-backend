#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

# Import functions
source $SCRIPT_PATH/functions.sh

# Define the MD5 checksum
md5Checksum="8ff0c2fd069c303d1c8d7d34a52968e8"

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# NuClick weights download URL
url="https://drive.usercontent.google.com/download?id=1JBK3vWsVC4DxbcStukwnKNZm-vCSLdOb&confirm=t"

fileName="nuclick_40x.pth"
filePath="$directoryPath/$fileName"

download_file $url $filePath $md5Checksum
if [[ $? -ne 0 ]]; then
    echo "The model weights downloaded unsuccessfully. Exiting script with error."
    exit 1
fi
