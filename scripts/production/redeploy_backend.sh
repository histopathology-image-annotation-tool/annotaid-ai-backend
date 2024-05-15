#!/bin/bash

if [ ! -f .env ]; then
    echo ".env file not found" >> /dev/stderr
    exit 1
fi

docker stop backend
docker rm backend

docker image rm annotaid/backend:latest

docker run -dt -p 8000:8000 --env-file .env --name backend --net=host annotaid/backend:latest
