#!/bin/bash

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# NuClick weights download URL
url="https://docs.google.com/uc?export=download&id=1JBK3vWsVC4DxbcStukwnKNZm-vCSLdOb&confirm=t"

fileName="nuclick_40x.pth"
filePath="$directoryPath/$fileName"

echo "Downloading $url to $filePath..."
curl -L -o "$filePath" "$url"

echo "Download completed: $filePath"
