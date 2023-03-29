FROM docker.io/library/python:3.8.16@sha256:a07637d351af5829bbd650735a5beed77fb467a124388191ac3fa5b8812e67c5 as python

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
