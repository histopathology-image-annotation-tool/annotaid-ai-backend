#!/bin/bash

# Notes:
# The script should be used to check if the newer version of the image is available in the registry. It has some issues when the image has multiple build platforms. Feel free to fix it.

SHORT=t:,r:
LONG=tag:,repository:
OPTS=$(getopt -a --options $SHORT --longoptions $LONG -- "$@")

eval set -- "$OPTS"

while :
do
    case "$1" in
        -t | --tag )
                TAG="$2"
                shift 2
                ;;
        -r | --repository )
                REPOSITORY="$2"
                shift 2
                ;;
        --)
                shift;
                break
                ;;
        *)
                echo "Unexpected argument: $1"
                exit 2
                ;;
    esac
done

TOKEN=$(curl -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:$REPOSITORY:pull" | python3 -c 'import sys, json; print(json.load(sys.stdin)["token"])')

TARGET_DIGEST=$(curl -s -D - -H "Authorization: Bearer $TOKEN" \
     https://registry-1.docker.io/v2/$REPOSITORY/manifests/$TAG 2>&1 \
  | grep docker-content-digest \
  | cut -d' ' -f2 | tr -d " \t\n\r")

CURRENT_DIGEST=$(docker image inspect $REPOSITORY:$TAG --format '{{.RepoDigests}}' | grep -oE "sha256:[0-9a-f]{64}" | tr -d " \t\n\r")

if [ "$CURRENT_DIGEST" == "$TARGET_DIGEST" ]; then
    echo "$REPOSITORY:$TAG up to date"
    exit 0
else
    echo "WARNING: $REPOSITORY:$TAG is out of date"
    echo "remote digest $TARGET_DIGEST"
    exit 1
fi
