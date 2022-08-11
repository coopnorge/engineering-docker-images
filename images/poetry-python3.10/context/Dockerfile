FROM docker.io/library/python:3.10.6@sha256:7517e835bc65aad07aed20fc7ddba37abc3f707eed6ef2ebb3fdbe26f5f52914 as python

WORKDIR /srv/workspace

FROM python as pip-tools

COPY requirements-pip-tools.txt requirements-pip-tools.txt

RUN pip install \
    --no-cache-dir \
    --require-hashes \
    --verbose \
    --use-pep517 \
    --requirement requirements-pip-tools.txt && \
    rm -rf requirements-pip-tools.txt

FROM python as poetry

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/srv/workspace" \
    VENV_PATH="/srv/workspace/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY requirements-poetry.txt requirements-poetry.txt
RUN pip install \
    --no-cache-dir \
    --require-hashes  \
    --verbose \
    --use-pep517 \
    --requirement requirements-poetry.txt && \
    rm -rf requirements-poetry.txt
