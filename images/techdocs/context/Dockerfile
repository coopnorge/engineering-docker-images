FROM docker.io/library/node:24.1.0-bookworm@sha256:c332080545f1de96deb1c407e6fbe9a7bc2be3645e127845fdcce57a7af3cf56 AS node
FROM jdkato/vale:v3.4.2@sha256:da6a0901858421b282aa8d935e72831c84cebf716ae4e276658e9e5d382fad20 AS vale
FROM plantuml/plantuml:1.2025.3@sha256:7d0f1cb94b31a4fa7984c108306b683a625621e306f098b41827465bb7600b34 AS plantuml
FROM mikefarah/yq:4.45.4@sha256:7cf28e5d67782f4b274a93a7bc54a840b553447a0807efd843d069f46bff718c AS yq
FROM docker.io/library/python:3.12.7-bookworm@sha256:db1afbfdc089b792bed227d70e1b1607c16bacb391f1257b7af1f0e6b2384480 AS base

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

ENV JDK_VERSION=17
ENV JDK_PACKAGE_VERSION=17.0.15+6-1~deb12u1

RUN apt-get update && apt-get install --no-install-recommends -y \
    openjdk-${JDK_VERSION}-jdk-headless=${JDK_PACKAGE_VERSION} \
    openjdk-${JDK_VERSION}-jdk=${JDK_PACKAGE_VERSION} \
    openjdk-${JDK_VERSION}-jre-headless=${JDK_PACKAGE_VERSION} \
    openjdk-${JDK_VERSION}-jre=${JDK_PACKAGE_VERSION} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base AS pip-tools

COPY requirements-pip-tools.txt requirements-pip-tools.txt
RUN pip install \
    --no-cache-dir \
    --require-hashes \
    --no-deps \
    --verbose \
    --use-pep517 \
    --requirement requirements-pip-tools.txt && \
    rm -rf requirements-pip-tools.txt

FROM base AS npm-tools

FROM base AS techdocs-cli

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
    --no-deps \
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
