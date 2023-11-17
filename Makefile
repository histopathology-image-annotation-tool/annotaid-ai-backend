SHELL = /bin/bash

# Set the name of the virtual environment
VENV_NAME := .venv

# Determine the operating system
ifeq ($(OS),Windows_NT)
	PYTHON := python
	ACTIVATE := .\$(VENV_NAME)\Scripts\activate
else
	PYTHON := python3
	ACTIVATE := source $(VENV_NAME)/bin/activate
endif

# Create the virtual environment and setup pre-commit
venv:
	$(PYTHON) -m venv $(VENV_NAME)
	$(ACTIVATE) && \
	$(PYTHON) -m pip install poetry && \
	poetry install && \
	pre-commit install

# Activate the virtual environment
activate:
	$(ACTIVATE)

# Download NuClick weights
download_nuclick_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\download_nuclick_weights.ps1
else
	./scripts/download_nuclick_weights.sh
endif

# Download MC weights
download_mc_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\download_mc_weights.ps1
else
	./scripts/download_mc_weights.sh
endif

# Download NP weights
download_np_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\download_np_weights.ps1
else
	./scripts/download_np_weights.sh
endif

build_be:
ifeq ($(env),dev)
	@docker build . -f ./docker/backend.dockerfile -t annotaid/backend.dev
else ifeq ($(env),prod)
	@docker build . -f ./docker/backend.dockerfile -t annotaid/backend
else
	@echo "Invalid arguments, supported only: dev, prod"
	@echo "Examples:"
	@echo " make build_be env=dev"
endif

build_worker:
ifeq ($(env),dev)
	@docker build . -f /docker/worker.dockerfile -t annotaid/worker.dev
else ifeq ($(env),prod)
	@docker build . -f /docker/worker.dockerfile -t annotaid/worker
else
	@echo "Invalid arguments, supported only: dev, prod"
	@echo "Examples:"
	@echo " make build_worker env=dev"
endif

run_be:
ifeq ($(env),docker)
	@docker run -dt -p 8000:8000 --env-file .env annotaid/backend.dev
else ifeq ($(env),local)
	@uvicorn src.main:app --reload
else
	@echo "Invalid arguments, supported only: docker, local"
	@echo "Examples:"
	@echo " make run_be env=dev"
endif

run_worker:
ifeq ($(env),docker)
	@docker run -dt --env-file .env annotaid/worker.dev
else ifeq ($(env),local)
	@celery -A src.core.celery worker --pool=solo --loglevel=info
else
	@echo "Invalid arguments, supported only: docker, local"
	@echo "Examples:"
	@echo " make run_worker env=docker"
endif

run_redis:
	@docker run -p 6379:6379 --name redis -d redis

run:
ifeq ($(env),prod)
	@docker-compose -f ./docker/docker-compose.dev.yml -f ./docker/docker-compose.prod.yml up
else
	@docker-compose -f ./docker/docker-compose.dev.yml up
endif

.PHONY: help
help:
	@echo "Commands                :"
	@echo "venv                    : creates a virtual environment."
	@echo "activate                : activates the virtual environment"
	@echo "download_nuclick_weights: downloads NuClick weights"
	@echo "download_mc_weights     : downloads MC weights"
	@echo "download_np_weights     : downloads NP weights"
	@echo "build_be                : builds backend"
	@echo "build_worker            : builds celery worker"
	@echo "run_be                  : runs backend"
	@echo "run_worker              : runs celery worker"
	@echo "run_redis               : runs redis docker image"
	@echo "run                     : runs docker-compose"
