[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

# AnnotAid AI Backend
This repository contains a FastAPI backend with celery for AnnotAid. The backend is wrapped in a Docker container for easy deployment.

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
Rename .env.sample to .env

#### Download NuClick Weights:
```
make download_nuclick_weights
```

#### Download MC Weights:
```
make download_mc_weights
```

#### Download NP Weights:
```
make download_np_weights
```

#### Download SAM Weights:
```
make download_sam_weights
```

#### Run the project
```
make run_be env=local
make run_worker env=local
make run_redis
```

### Docker
#### Setup .env file
Rename .env.sample to .env and update CELERY_BROKER_URL and CELERY_BACKEND_URL from localhost to `redis` container name.

#### Compose the project
dev:
```
make run
```

prod:
```
make run env=prod
```

## Documentation
* [Swagger](http://localhost:8000/docs)
* [Redoc](http://localhost:8000/redoc)

## License
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
