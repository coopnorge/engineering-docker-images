FROM docker.io/library/node:25.6.1-bookworm@sha256:39f92e620aa34854b8877b43bdffd411a301a50eefb38400785a01991f25a2f6 AS node
FROM plantuml/plantuml:1.2026.1@sha256:0cd265d12d84b8a0cf307a7dd8c74f237d137b9327b5053bd5aa822f38952caa AS plantuml
FROM mikefarah/yq:4.52.4@sha256:a4c2cafdf4674b2dc3c6ac457fe1486d55d7d93edb3ed4459637afda3c286af6 AS yq
FROM docker.io/library/python:3.14.3-bookworm@sha256:dea5c0690cedf3c93529f8b62467fe6206a0b6163c2bf9a0c5115f4c8367a33d AS base

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
    jq \
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
ENV JDK_PACKAGE_VERSION=17.0.17+10-1~deb12u1

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

ENV VALE_VERSION=3.13.1

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
    ln -rs /usr/local/bin/maker /usr/local/bin/format-check && \
    ln -rs /usr/local/bin/maker /usr/local/bin/format-fix && \
    ln -rs /usr/local/bin/maker /usr/local/bin/build && \
    ln -rs /usr/local/bin/maker /usr/local/bin/serve && \
    ln -rs /usr/local/bin/maker /usr/local/bin/publish && \
    true

COPY Makefile /usr/local/share/techdocs/Makefile
COPY mkdocs.yml /usr/local/share/techdocs/mkdocs.yml
COPY markdownlint.yaml /usr/local/share/techdocs/markdownlint.yaml
COPY .prettierrc /usr/local/share/techdocs/.prettierrc
COPY merge_prettier_configs.sh /usr/local/share/techdocs/merge_prettier_configs.sh

RUN git config --system --add safe.directory /srv/workspace

VOLUME /srv/workspace
WORKDIR /srv/workspace
