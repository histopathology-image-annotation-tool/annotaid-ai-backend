#!/bin/bash

# Define the directory path
directoryPath="models/"

# Create the directory if it doesn't exist
mkdir -p $directoryPath

# NP weights download URL
url="https://drive.usercontent.google.com/download?id=1DdQLXbEZOaUm_3IqWj1YfCMK25MA0m5b&confirm=t"

fileName="NP_model.pt"
filePath="$directoryPath/$fileName"

echo "Downloading $url to $filePath..."
curl -L -o "$filePath" "$url"

echo "Download completed: $filePath"
