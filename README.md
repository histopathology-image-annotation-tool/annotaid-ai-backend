[![AGPL 3.0][license-shield]][license]

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

#### Download Weights:
```
make download_weights
```

#### Run the project
```
make run env=local
```

## Documentation
* [Swagger](http://localhost:8000/docs)
* [Redoc](http://localhost:8000/redoc)

## License
[AnnotAid AI Backend](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend) by [Adam Bublavý](https://github.com/Sangalaa/) is licensed under a
[GNU Affero General Public License v3.0 or later][license].

[license]: https://spdx.org/licenses/AGPL-3.0-or-later.html
[license-shield]: https://img.shields.io/badge/License-AGPL%203.0-lightgrey.svg
