FROM docker.io/library/python:3.11.2@sha256:08e538ee415a46998b19a6451da95d831f9e7e81be506925df51467b94e9cd43 as python

WORKDIR /srv/workspace

FROM python as pip-tools

COPY requirements.txt requirements.txt

RUN pip install \
    --no-cache-dir \
    --require-hashes \
    --verbose \
    --use-pep517 \
    --requirement requirements.txt && \
    rm -rf requirements.txt

RUN git config --system --add safe.directory /srv/workspace
