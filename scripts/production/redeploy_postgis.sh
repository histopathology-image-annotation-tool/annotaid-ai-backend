#!/bin/bash

if [ ! -f .env ]; then
    echo ".env file not found" >> /dev/stderr
    exit 1
fi

docker stop postgis
docker rm postgis

docker image rm postgis/postgis:latest

docker volume create annotaid_data
docker run -dt -p 5432:5432 --env-file .env --name postgis -v annotaid_data:/var/lib/postgresql/data -d postgis/postgis
