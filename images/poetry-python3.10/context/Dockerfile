FROM docker.io/library/python:3.10.14@sha256:f68383667ffe53e85cc0fe4f5a604d303dfa364f238ac37a4675980a2b93b1c5 as python
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.14@sha256:68f7473909b49013f97984e9917fb7edd0c440bf15e38f41449860f8a2680d51 AS dockle

FROM python as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

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

COPY --from=hadolint /bin/hadolint /usr/local/bin/hadolint
COPY --from=dockle /usr/bin/dockle /usr/local/bin/dockle

COPY requirements.txt requirements.txt
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install \
        --no-cache-dir \
        --require-hashes  \
        --verbose \
        --use-pep517 \
        --requirement requirements.txt && \
    rm -rf requirements.txt

COPY .flake8 .flake8
COPY mypy.ini mypy.ini

COPY maker /usr/local/bin/maker

COPY Makefile /usr/local/share/poetry-python3.10/

RUN \
    set -x; \
    targets=( \
        help \
        poetry-install \
        validate validate-static validate-fix \
        test test-verbose \
    ); \
    for target in "${targets[@]}"; \
    do \
        ln -s /usr/local/bin/maker "/usr/local/bin/${target}"; \
    done && \
    true

RUN git config --system --add safe.directory /srv/workspace

VOLUME /srv/workspace
WORKDIR /srv/workspace

CMD ["validate"]