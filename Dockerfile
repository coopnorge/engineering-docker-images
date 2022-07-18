FROM docker.io/safewaters/docker-lock:0.8.10@sha256:e87cfa64db3ceb8e5d14ec41136b068e2335fdcdfbb890fa20dd091e82735d04 as docker-lock
FROM docker.io/hadolint/hadolint:v2.10.0@sha256:93f0afd12c3be5d732227c0226dd8e7bb84f79319a773d7f8519e55f958ba415 as hadolint
FROM docker.io/goodwithtech/dockle:v0.4.5@sha256:ebd36f6c92ac850408c7cbbf1eddf97e53565da9d661c5fb8ec184ad82a5358d as dockle
FROM docker.io/library/ubuntu:22.04@sha256:b6b83d3c331794420340093eb706a6f152d9c1fa51b262d9bf34594887c2c7ac as ubuntu

FROM ubuntu as devtools

RUN \
    apt update && \
    apt-get install -y \
        make \
        docker \
    && true

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN python -m ensurepip

ENV PATH=/root/.poetry/bin:$PATH

WORKDIR /tmp/workspace
COPY pyproject.toml ./
RUN poetry install
