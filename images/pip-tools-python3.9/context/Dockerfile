FROM docker.io/library/python:3.9.16@sha256:7ac171271f185d4f05824b68ab1995981872e8f9b0cac262fe7da138fbd82e9a as python

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
