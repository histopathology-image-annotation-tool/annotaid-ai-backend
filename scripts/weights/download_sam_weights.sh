#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

# Import functions
source $SCRIPT_PATH/functions.sh

# Define the MD5 checksum
md5Checksum="01ec64d29a2fca3f0661936605ae66f8"

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# NP weights download URL
url="https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"

fileName="sam_vit_b_01ec64.pth"
filePath="$directoryPath/$fileName"

download_file $url $filePath $md5Checksum
if [[ $? -ne 0 ]]; then
    echo "The model weights downloaded unsuccessfully. Exiting script with error."
    exit 1
fi
