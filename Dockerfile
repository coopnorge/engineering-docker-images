FROM docker.io/safewaters/docker-lock:0.8.10@sha256:e87cfa64db3ceb8e5d14ec41136b068e2335fdcdfbb890fa20dd091e82735d04 AS docker-lock
FROM docker.io/hadolint/hadolint:2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM docker.io/goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9 AS dockle
FROM docker.io/library/python:3.13.6@sha256:68d0775234842868248bfe185eece56e725d3cb195f511a21233d0f564dee501 AS python

FROM python AS devtools

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
