[![AGPL 3.0][license-shield]][license]

# AnnotAid AI Backend
The AnnotAid AI Backend, built on FastAPI, offers a range of deep learning techniques to enhance the annotation process in the AnnotAid annotation tool. It facilitates the annotation of cells or more complex structures and offers assistance in evaluating individual criteria of the Nottingham Grading System.

## Project Structure
```
+---.github                    # Github workflows
|   \---workflows
+---.vscode                    # VSCode settings
+---docker                     # Backend and Celery worker dockerfiles
+---models                     # Downloaded weights
+---scripts
|   +---api                    # Scripts for backend
|   \---weights                # Scripts used to download model weights
+---src
|   +---alembic
|   |   +---versions           # Database migrations
|   +---api                    # API endpoints
|   |   +---api_v1
|   |   |   +---endpoints
|   +---celery
|   |   +---active_learning    # Active learning tasks
|   |   +---mc                 # Mitotic count tasks
|   |   +---np                 # Nuclear pleomoprhism tasks
|   |   +---nuclick            # NuClick tasks
|   |   +---sam                # SAM tasks
|   |   +---shared             # Shared tasks
|   +---core                   # Configuration files
|   +---examples               # Sample images used in documentation
|   +---models
|   |   +---mc                 # Mitotic count models
|   |   +---np                 # Nuclear pleomorphism models
|   |   +---nuclick            # NuClick model
|   +---schemas                # Validation schemas
|   +---scripts
|   +---utils
\---tests
|   .env                       # Environment variables
|   .env.example               # Example template of environment variables
|   .flake8                    # Flake8 config
|   .pre-commit-config.yaml    # Pre-commit config
|   alembic.ini                # Alembic config
|   Makefile                   # Project makefile
|   mypy.ini                   # Mypy config
|   pyproject.toml             # Project config
```

## Prerequisites
Make sure you have the following tools installed before setting up the project:
* [Python 3](https://www.python.org/downloads/)
* [Docker](https://www.docker.com/)

## Installation and Setup
Clone the repository:
```
git clone https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend AnnotAidAIBE
cd AnnotAidAIBE
```

### Local development
Create a Virtual Environment:
```
make venv
```

#### Setup .env file
```
cp .env.example .env
```

#### (Optional) Setup Datastore
If you want to use active learning, you need to download a sample [VSI image](https://www.annotaid.com/) or put custom images into pre-configured folder specified in the .env file.

#### Download Weights:
```
make download_weights
```

#### Run the project
```
make run env=dev
```

## Documentation
* [Swagger](http://localhost:8000/docs)
* [Redoc](http://localhost:8000/redoc)

## License
[AnnotAid AI Backend](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend) by [Adam Bublavý](https://github.com/Sangalaa/) is licensed under a
[GNU Affero General Public License v3.0 or later][license].

[license]: https://spdx.org/licenses/AGPL-3.0-or-later.html
[license-shield]: https://img.shields.io/badge/License-AGPL%203.0-lightgrey.svg
