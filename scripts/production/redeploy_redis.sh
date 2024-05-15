#!/bin/bash

docker stop redis
docker rm redis

docker run -dt --name redis -p 6379:6379 redis:alpine3.18
