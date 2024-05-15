#!/bin/bash

# Notes:
# This script is used to check if the images of the worker, backend, and reader services needs to be updated. The idea is to run this script periodically to check if the newer version of the image is available in the registry. If the newer version of the image is available in the registry, the script will redeploy the services. The script is not working properly. Feel free to fix it.

SCRIPT_NAME=$(basename $0)
LOCK_FILE_PATH="/tmp/<user>/$SCRIPT_NAME.lock"

if [ -f $LOCK_FILE_PATH ]; then
    echo "$SCRIPT_NAME is already running. Exiting..."
    exit 1
fi

touch $LOCK_FILE_PATH

./check_image_update.sh -r annotaid/worker -t latest

if [ $? -eq 1 ]
then
        ./redeploy_worker.sh
fi

./check_image_update.sh -r annotaid/backend -t latest

if [ $? -eq 1 ]
then
        ./redeploy_backend.sh
fi

./check_image_update.sh -r annotaid/reader -t latest

if [ $? -eq 1 ]
then
        ./redeploy_reader.sh
fi

rm $LOCK_FILE_PATH
