FROM docker.io/library/python:3.11.2@sha256:5329e75033c4446dc92d702cf8ebbeb63e549d9b83076a776f6753e10817fc3c as python

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
