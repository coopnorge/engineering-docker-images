FROM docker.io/library/node:24.4.1-bookworm@sha256:9b2491ed2930a275b659f2f12ffe20ec525dc3628f2f323adca6cef4eed59742 AS node
FROM plantuml/plantuml:1.2025.4@sha256:227c418ce3811b3bfd48e022922af35839914d606d5ea1c8a4137d77d58d482c AS plantuml
FROM mikefarah/yq:4.46.1@sha256:e4ec3062f63c5dd56c5fb79e325d24b91f1ca0d66d01cbc06ea2dd6a6ff867ab AS yq
FROM docker.io/library/python:3.13.5-bookworm@sha256:1ab800bdbb82bf738bbf0cb074c2f2f4ad94476027a3ae516eef6f77b949c711 AS base

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

COPY --from=plantuml /opt/plantuml.jar /opt/plantuml.jar
COPY --from=yq /usr/bin/yq /usr/bin/yq
# hadolint ignore=SC2016
RUN echo $'#!/bin/sh\n\njava -jar '/opt/plantuml.jar' ${@}' >> /usr/local/bin/plantuml && \
    chmod 755 /usr/local/bin/plantuml

ENV VALE_VERSION=3.7.1

# hadolint ignore=DL4006
RUN curl -fsSL https://github.com/errata-ai/vale/releases/download/v${VALE_VERSION}/vale_${VALE_VERSION}_Linux_64-bit.tar.gz \
    | tar -xz -C /bin --strip-components=0 vale \
    && chmod +x /bin/vale

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
