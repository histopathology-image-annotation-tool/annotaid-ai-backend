ARG PYTHON_VERSION=3.11.6

FROM python:${PYTHON_VERSION}-slim-bookworm as base

# Create ML-API-USER
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    ml-api-user

ENV PYTHONFAULTHANDLER=1\
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    PYTHONHASHSEED=random \
    # pip:
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    # poetry:
    POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Download the NuClick model
COPY scripts/download_nuclick_weights.sh /code/scripts/
RUN chmod +x /code/scripts/download_nuclick_weights.sh
RUN /code/scripts/download_nuclick_weights.sh

# Download the MC models
COPY scripts/download_mc_weights.sh /code/scripts/
RUN chmod +x /code/scripts/download_mc_weights.sh
RUN /code/scripts/download_mc_weights.sh

# Download the NP model
COPY scripts/download_np_weights.sh /code/scripts/
RUN chmod +x /code/scripts/download_np_weights.sh
RUN /code/scripts/download_np_weights.sh

# Download the SAM model
COPY scripts/download_sam_weights.sh /code/scripts/
RUN chmod +x /code/scripts/download_sam_weights.sh
RUN /code/scripts/download_sam_weights.sh

# Uninstall curl
RUN apt remove -y curl

WORKDIR /code

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /code/

RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
    poetry version \
    && poetry run pip install -U pip \
    && poetry install --no-root --only main,celery --no-interaction

# Swith to ML-API-USER
USER ml-api-user

COPY src/ /code/src

EXPOSE 8000

CMD ["celery", "-A", "src.core.celery", "worker", "--pool", "solo", "--loglevel", "info"]
