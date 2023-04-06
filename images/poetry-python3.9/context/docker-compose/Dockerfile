FROM docker.io/library/python:3.10.11@sha256:5a71ab8ffc96d7ac9cbe32aff7878371242d36a3038a266941ccdb5c83cc5dd5 as python

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
