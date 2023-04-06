FROM docker.io/library/python:3.11.3@sha256:7adb2f6d6b0fdaf2d3029c42b5a40833589f969c18728f5b5b126a61394848b6 as python

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
