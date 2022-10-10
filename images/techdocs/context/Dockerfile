FROM docker.io/library/node:18.10.0-bullseye@sha256:bb3b9f1867edba6d8892758889e43b2f0205ebbd381969a2c45577d38281ac90 as node
FROM jdkato/vale:v2.20.2@sha256:2025a2fae1f200e08d7c8b518c5cd1a556bee0087e5373b2a525b5580bed66db as vale
FROM plantuml/plantuml:1.2022.10@sha256:3d3d7b027213c911b3012c5818fcdd9e47bbe4503635b520bb10a563d1293c79 as plantuml
FROM mikefarah/yq:4.28.1@sha256:72d6139326c64b51e2006ea9bd9063cc5dcbb1eedf893bac88c69e467b687d6b as yq

FROM docker.io/library/python:3.10.7@sha256:0ad99314ad35ab18f2fe76a21be3b501c9cbcf9966bb621a26082f3fa95c287d as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN mkdir /srv/workspace
WORKDIR /srv/workspace

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        lsb-release=11.1.0 \
        apt-transport-https=2.2.4 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/include/node /usr/local/include/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node /usr/local/share/doc/node /usr/local/share/doc/node
COPY --from=node /usr/local/share/man/man1/node.1 /usr/local/share/man/man1/node.1
COPY --from=node /usr/local/share/systemtap/tapset/node.stp /usr/local/share/systemtap/tapset/node.stp
RUN ln -s /usr/local/lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack \
    && ln -s /usr/local/bin/node /usr/local/bin/nodejs \
    && ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN apt-get update && apt-get install --no-install-recommends -y \
    openjdk-17-jdk=17.0.4+8-1~deb11u1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base as pip-tools

COPY requirements-pip-tools.txt requirements-pip-tools.txt
RUN pip install \
    --no-cache-dir \
    --require-hashes \
    --verbose \
    --use-pep517 \
    --requirement requirements-pip-tools.txt && \
    rm -rf requirements-pip-tools.txt

FROM base as npm-tools

FROM base as techdocs-cli

COPY --from=vale /bin/vale /bin/vale
COPY --from=plantuml /opt/plantuml.jar /opt/plantuml.jar
COPY --from=yq /usr/bin/yq /usr/bin/yq
# hadolint ignore=SC2016
RUN echo $'#!/bin/sh\n\njava -jar '/opt/plantuml.jar' ${@}' >> /usr/local/bin/plantuml && \
    chmod 755 /usr/local/bin/plantuml

COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm install

ENV PATH="${PATH}:/srv/workspace/node_modules/.bin/"

COPY requirements-techdocs.txt requirements-techdocs.txt
RUN pip install \
    --no-cache-dir \
    --require-hashes \
    --verbose \
    --use-pep517 \
    --requirement requirements-techdocs.txt && \
    rm -rf requirements-techdocs.txt

RUN mkdir /content
WORKDIR /content
