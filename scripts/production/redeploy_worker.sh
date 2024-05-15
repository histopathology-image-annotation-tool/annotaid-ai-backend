#!/bin/bash

if [ ! -f .env ]; then
    echo ".env file not found" >> /dev/stderr
    exit 1
fi

docker stop worker_1 worker_2 worker_reader || true
docker rm worker_1 worker_2 worker_reader || true
docker image rm annotaid/worker:latest

docker run --privileged --gpus all -dt --env-file .env --name worker_1 annotaid/worker:latest celery -A src.core.celery worker --pool=solo --loglevel=info -Q celery,AL
docker run --privileged --gpus all -dt --env-file .env --name worker_2 annotaid/worker:latest celery -A src.core.celery worker --pool=solo --loglevel=info -Q celery,AL
docker run --privileged --gpus all -dt --env-file .env --name worker_reader annotaid/worker:latest celery -A src.core.celery worker --pool=gevent --concurrency=2 --loglevel=info -Q reader
