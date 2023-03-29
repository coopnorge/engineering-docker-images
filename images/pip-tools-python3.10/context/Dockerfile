FROM docker.io/library/python:3.10.10@sha256:0dda75f6f0476095f8d7d5bd288c9652e143bbb37b333a76369c2d1552bda692 as python

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
