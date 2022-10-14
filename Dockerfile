FROM docker.io/safewaters/docker-lock:0.8.10@sha256:e87cfa64db3ceb8e5d14ec41136b068e2335fdcdfbb890fa20dd091e82735d04 as docker-lock
FROM docker.io/hadolint/hadolint:v2.10.0@sha256:93f0afd12c3be5d732227c0226dd8e7bb84f79319a773d7f8519e55f958ba415 as hadolint
FROM docker.io/goodwithtech/dockle:v0.4.7@sha256:97a57c34009cdff979184185f686c4664f34d8702b427a21d02b6ac67c045fbd as dockle
FROM docker.io/library/python:3.10.7@sha256:fe068d8c06a719e26a1388c9d5c7c67d94923b0654ba89b0b7b5e518609e3304 as python

FROM python as devtools

RUN \
    apt update && \
    apt-get install -y \
        docker \
    && true

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN python -m ensurepip

ENV PATH=/root/.poetry/bin:$PATH

WORKDIR /tmp/workspace
COPY pyproject.toml poetry.toml ./
RUN poetry install
