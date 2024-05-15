#!/bin/sh

docker stop reader
docker rm reader

docker image rm annotaid/reader:latest
READER_SOURCE_DATA=/home/<user>/annotaid_ai_be/WSI
READER_TARGET_DATA=/mnt
READER_MEM_SOURCE=$PWD/.cache/reader/
READER_MEM_TARGET=/tmp/reader/

rm -rf $READER_MEM_SOURCE
mkdir -p $READER_MEM_SOURCE

docker run -dt -p 9090:9090 \
        --name reader \
        --mount type=bind,source="$READER_SOURCE_DATA",target=$READER_TARGET_DATA,readonly \
        --mount type=bind,source=$READER_MEM_SOURCE,target=$READER_MEM_TARGET \
        -e MEM_TMP_DIR=$READER_MEM_TARGET \
        annotaid/reader
