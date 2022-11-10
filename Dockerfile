FROM docker.io/safewaters/docker-lock:0.8.10@sha256:e87cfa64db3ceb8e5d14ec41136b068e2335fdcdfbb890fa20dd091e82735d04 as docker-lock
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e as hadolint
FROM docker.io/goodwithtech/dockle:v0.4.9@sha256:2a5fc2c1a467dd229720baf6c002798e5a1f86ce37e5657bc9c4b2cc3503fd64 as dockle
FROM docker.io/library/python:3.11.0@sha256:20416fc02584edd936eb740ac16c1aed4a765fccd99656f3d0b6d2e5ba725d66 as python

FROM python as devtools

RUN apt update && \
    apt-get install --yes \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
    && true \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install --yes \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin \
    && true


RUN curl -sSL https://install.python-poetry.org | python3 -

RUN python -m ensurepip

ENV PATH=/root/.local/bin:$PATH

WORKDIR /tmp/workspace
COPY pyproject.toml poetry.toml ./
RUN poetry install
