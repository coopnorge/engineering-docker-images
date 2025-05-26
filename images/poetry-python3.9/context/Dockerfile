FROM docker.io/library/python:3.9.22@sha256:6021c6c9624cb975a2b80710f54f4afd19939a2e1da820fcec995b6ca3be9b0b AS python

FROM python AS poetry

WORKDIR /srv/workspace

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

COPY requirements.txt requirements.txt

RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install \
        --no-cache-dir \
        --require-hashes  \
        --verbose \
        --use-pep517 \
        --requirement requirements.txt && \
    rm -rf requirements.txt

RUN git config --system --add safe.directory /srv/workspace
