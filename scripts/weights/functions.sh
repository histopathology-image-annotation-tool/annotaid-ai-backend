#!/bin/bash

download_file() {
    local url=$1
    local filePath=$2
    local md5Checksum=$3
    local maxRetries=5
    local retry=1

    while ((retry <= maxRetries)); do
        echo "Downloading $url to $filePath..."
        curl -L -o "$filePath" "$url"
        echo "Download completed: $filePath"

        echo "Checking MD5 checksum..."
        local md5=$(md5sum "$filePath" | awk '{ print $1 }')

        if [[ $md5 == $md5Checksum ]]; then
            echo "MD5 checksum is correct."
            return 0
        else
            echo "MD5 checksum is incorrect. Retrying download..."
            ((retry++))
        fi
    done

    echo "Failed to download $url after $maxRetries attempts."
    return 1
}
