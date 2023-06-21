FROM docker.io/library/node:20.3.0-bullseye@sha256:6a6f34a061419cdbd33cd7cdf0ca68d7ded2aa2e89c9b65b3a538b0bdbb238db as node
FROM jdkato/vale:v2.27.0@sha256:8b92de3714c2e6ddfd6ed4c36191fd0c899de1a722e2d2f27f9a5a69d5a765d9 as vale
FROM plantuml/plantuml:1.2023.9@sha256:0b1fcb1ed16ec704d9c17fa66639723baa3b783b69e9a801f4a7eb090118080b as plantuml
FROM mikefarah/yq:4.34.1@sha256:414a2cd52d0ac9c03cbaeb2b1e07bab9ed551d25b4578d4a4dccaffb82406fba as yq

FROM docker.io/library/python:3.11.3@sha256:3a619e3c96fd4c5fc5e1998fd4dcb1f1403eb90c4c6409c70d7e80b9468df7df as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN mkdir -p /usr/local/share/techdocs
WORKDIR /usr/local/share/techdocs

RUN apt-get clean \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        apt-transport-https=2.2.4 \
        git \
        lsb-release=11.1.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/include/node /usr/local/include/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node /usr/local/share/doc/node /usr/local/share/doc/node
COPY --from=node /usr/local/share/man/man1/node.1 /usr/local/share/man/man1/node.1
RUN ln -s /usr/local/lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack \
    && ln -s /usr/local/bin/node /usr/local/bin/nodejs \
    && ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN apt-get update && apt-get install --no-install-recommends -y \
    openjdk-17-jdk-headless=17.0.6+10-1~deb11u1 \
    openjdk-17-jdk=17.0.6+10-1~deb11u1 \
    openjdk-17-jre-headless=17.0.6+10-1~deb11u1 \
    openjdk-17-jre=17.0.6+10-1~deb11u1 \
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

ENV PATH="${PATH}:/usr/local/share/techdocs/node_modules/.bin/"

COPY requirements-techdocs.txt requirements-techdocs.txt
RUN pip install \
    --no-cache-dir \
    --require-hashes \
    --verbose \
    --use-pep517 \
    --requirement requirements-techdocs.txt && \
    rm -rf requirements-techdocs.txt

COPY maker /usr/local/bin/maker
RUN \
    ln -rs /usr/local/bin/maker /usr/local/bin/help && \
    ln -rs /usr/local/bin/maker /usr/local/bin/vale-sync && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -rs /usr/local/bin/maker /usr/local/bin/lint-fix && \
    ln -rs /usr/local/bin/maker /usr/local/bin/lint && \
    ln -rs /usr/local/bin/maker /usr/local/bin/linguistics-check && \
    ln -rs /usr/local/bin/maker /usr/local/bin/build && \
    ln -rs /usr/local/bin/maker /usr/local/bin/serve && \
    ln -rs /usr/local/bin/maker /usr/local/bin/publish && \
    true

COPY Makefile /usr/local/share/techdocs/Makefile
COPY mkdocs.yml /usr/local/share/techdocs/mkdocs.yml
COPY markdownlint.yaml /usr/local/share/techdocs/markdownlint.yaml

RUN git config --system --add safe.directory /srv/workspace

VOLUME /srv/workspace
WORKDIR /srv/workspace
