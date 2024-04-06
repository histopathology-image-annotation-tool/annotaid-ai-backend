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
	$(PYTHON) -m pip install poetry==1.6.1 && \
	poetry install && \
	pre-commit install

# Activate the virtual environment
activate:
	$(ACTIVATE)

# Download all weights
download_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\weights\index.ps1
else
	./scripts/weights/index.sh
endif

# Download NuClick weights
download_nuclick_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\weights\download_nuclick_weights.ps1
else
	./scripts/weights/download_nuclick_weights.sh
endif

# Download MC weights
download_mc_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\weights\download_mc_weights.ps1
else
	./scripts/weights/download_mc_weights.sh
endif

# Download NP weights
download_np_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\weights\download_np_weights.ps1
else
	./scripts/weights/download_np_weights.sh
endif

# Download SAM weights
download_sam_weights:
ifeq ($(OS),Windows_NT)
	powershell .\scripts\weights\download_sam_weights.ps1
else
	./scripts/weights/download_sam_weights.sh
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
	@docker build . -f ./docker/worker.dockerfile -t annotaid/worker.dev
else ifeq ($(env),prod)
	@docker build . -f ./docker/worker.dockerfile -t annotaid/worker
else
	@echo "Invalid arguments, supported only: dev, prod"
	@echo "Examples:"
	@echo " make build_worker env=dev"
endif

run_be:
ifeq ($(env),docker)
	@docker run -dt -p 8000:8000 --env-file .env annotaid/backend.dev
else ifeq ($(env),local)
	@watchmedo auto-restart --directory=./src --pattern=* --recursive -- uvicorn src.main:app
else
	@echo "Invalid arguments, supported only: docker, local"
	@echo "Examples:"
	@echo " make run_be env=local"
endif

run_worker:
ifeq ($(env),docker)
	@docker run -dt --env-file .env annotaid/worker.dev
else ifeq ($(env),local)
	@watchmedo auto-restart --directory=./src/celery --pattern=*.py --recursive -- celery -A src.core.celery worker --pool=solo --loglevel=info -Q celery,AL,reader
else
	@echo "Invalid arguments, supported only: docker, local"
	@echo "Examples:"
	@echo " make run_worker env=docker"
endif

run_redis:
	@docker stop redis || exit 0
	@docker rm redis || exit 0
	@docker run -p 6379:6379 --name redis -d redis

run_postgis:
	@docker stop postgis || exit 0
	@docker rm postgis || exit 0
	@docker volume create annotaid_data || exit 0
	@docker run -p 5432:5432 --name postgis --env-file .env -v annotaid_data:/var/lib/postgresql/data -d postgis/postgis

	@$(MAKE) migrate

run:
ifeq ($(env),prod)
	@docker-compose -f ./docker/docker-compose.dev.yml -f ./docker/docker-compose.prod.yml up
else ifeq ($(env),dev)
	@docker-compose -f ./docker/docker-compose.dev.yml up
else ifeq ($(env),local)
	@$(MAKE) -j run_redis run_postgis run_worker env=local run_be env=local
else
	@echo "Invalid arguments, supported only: dev, prod, local"
	@echo "Examples:"
	@echo " make run env=local"
endif

migrate:
	@$(PYTHON) -m src.scripts.wait-for-db
	@alembic upgrade head

.PHONY: venv activate download_weights download_nuclick_weights download_mc_weights \
	download_sam_weights build_be build_worker run_be run_worker run_redis run_postgis \
	run migrate help
help:
	@echo "Commands                :"
	@echo "venv                    : creates a virtual environment."
	@echo "activate                : activates the virtual environment"
	@echo "download_weights        : downloads all weights"
	@echo "download_nuclick_weights: downloads NuClick weights"
	@echo "download_mc_weights     : downloads MC weights"
	@echo "download_np_weights     : downloads NP weights"
	@echo "download_sam_weights"   : downloads SAM weights"
	@echo "build_be                : builds backend"
	@echo "build_worker            : builds celery worker"
	@echo "run_be                  : runs backend"
	@echo "run_worker              : runs celery worker"
	@echo "run_redis               : runs redis docker image"
	@echo "run_postgis             : runs postgis docker image and migrations"
	@echo "run                     : runs docker-compose or local dev"
	@echo "migrate                 : runs migrations"
