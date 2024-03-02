#!/bin/bash

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

echo "Downloading $url_first_stage to $filePathFirstStage..."
curl -L -o "$filePathFirstStage" "$url_first_stage"

echo "Download completed: $filePathFirstStage"

echo "Downloading $url_second_stage to $filePathSecondStage..."
curl -L -o "$filePathSecondStage" "$url_second_stage"

echo "Download completed: $filePathSecondStage"
