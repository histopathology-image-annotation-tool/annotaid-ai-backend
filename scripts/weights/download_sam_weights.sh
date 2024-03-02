#!/bin/bash

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# NP weights download URL
url="https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"

fileName="sam_vit_b_01ec64.pth"
filePath="$directoryPath/$fileName"

echo "Downloading $url to $filePath..."
curl -L -o "$filePath" "$url"

echo "Download completed: $filePath"
