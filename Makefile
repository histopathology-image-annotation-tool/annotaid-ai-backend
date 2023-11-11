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

.PHONY: help
help:
	@echo "Commands        :"
	@echo "venv            : creates a virtual environment."
	@echo "activate        : activates the virtual environment"
