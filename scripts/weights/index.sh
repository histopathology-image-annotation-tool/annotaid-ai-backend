#!/bin/bash

# Get the name of the current script
current_script_name=$(basename "$0")
current_directory=$(dirname "$0")

# Loop over all .sh files in the current directory
for file in $(find $current_directory -iname "*.sh")
do
    # If the file is not the current script, execute it
    if [ $(basename "$file") != "$current_script_name" ]
    then
        echo "Executing: $file"
        bash "$file"

        # Check the exit status of the script
        if [ $? -ne 0 ]
        then
            echo "Error: $file exited with a non-zero status code."
            exit 1
        fi
    fi
done
