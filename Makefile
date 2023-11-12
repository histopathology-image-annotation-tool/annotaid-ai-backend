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

build:
	@docker build . -f Dockerfile.dev -t nuclick_demo

build_prod:
	@docker build . -f Dockerfile.prod -t nuclick_demo

run:
	@docker run -p 8000:8000 -dt nuclick_demo

.PHONY: help
help:
	@echo "Commands        :"
	@echo "venv            : creates a virtual environment."
	@echo "activate        : activates the virtual environment"
	@echo "download_nuclick_weights: downloads NuClick weights"
	@echo "download_mc_weights: downloads MC weights"
	@echo "build: builds dev docker image"
	@echo "build_prod: builds prod docker image"
	@echo "run: runs docker image"
