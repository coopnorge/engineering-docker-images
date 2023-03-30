FROM docker.io/library/python:3.10.10@sha256:14b683d63e171ad811b5ff3d55d3a1138f34bb324e2e222fe37b6eab121a8517 as python

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
