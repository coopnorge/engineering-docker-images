FROM docker.io/library/node:22.3.0-bullseye@sha256:a27e56bb261136ad17f936d4d1158165baceb09589bad78bfffb4fd03e9c882f as node
FROM jdkato/vale:v3.4.2@sha256:da6a0901858421b282aa8d935e72831c84cebf716ae4e276658e9e5d382fad20 as vale
FROM plantuml/plantuml:1.2024.5@sha256:1d0bffdefca5fcebda68ffdb0a66f402ed214a74a9d115f93c70e29c1d1e57cf as plantuml
FROM mikefarah/yq:4.44.2@sha256:2ecaeeff15976cd00c4627f119b592b5c9311b7080beff469211606c42c6cbd2 as yq

FROM docker.io/library/python:3.12.4@sha256:f6d04873f0a67146854270e5f6513ed5e0165557c1b10689f1a20e9e65c8fe8e as base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN mkdir -p /usr/local/share/techdocs
WORKDIR /usr/local/share/techdocs

RUN apt-get clean \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        apt-transport-https=2.6.1 \
        git \
        lsb-release=12.0-1 \
        graphviz \
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
    openjdk-17-jdk-headless=17.0.10+7-1~deb12u1 \
    openjdk-17-jdk=17.0.10+7-1~deb12u1 \
    openjdk-17-jre-headless=17.0.10+7-1~deb12u1 \
    openjdk-17-jre=17.0.10+7-1~deb12u1 \
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
