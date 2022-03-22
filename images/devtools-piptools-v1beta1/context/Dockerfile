FROM python:3.8-slim-buster@sha256:b9c6d865d1a0e6c1a0c3e0ee7a15d37ac2e9d0a195c9c23d4ec5e6ccd6e06cc0 as python

COPY requirements.txt requirements.txt

RUN pip install --verbose --requirement requirements.txt

VOLUME /srv/workspace
WORKDIR /srv/workspace
