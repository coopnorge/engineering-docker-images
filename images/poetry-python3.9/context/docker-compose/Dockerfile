FROM docker.io/library/python:3.9.16@sha256:7ac171271f185d4f05824b68ab1995981872e8f9b0cac262fe7da138fbd82e9a as python

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
