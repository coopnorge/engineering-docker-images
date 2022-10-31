FROM docker.io/library/node:18.10.0-bullseye@sha256:9d8a6466c6385e05f62f8ccf173e80209efb0ff4438f321f09ddf552b05af3ba as node
FROM jdkato/vale:v2.21.0@sha256:969b2f3488d35ff2831d60df41c9f2ab7a9f354fec7552153d099d61539ccddb as vale
FROM plantuml/plantuml:1.2022.12@sha256:658d63ac409ab3a813278f40c6a974998017180e2614c41120623b62045c41ac as plantuml
FROM mikefarah/yq:4.29.2@sha256:f0e1e617c6bb1cf89728b65a95c72a287f3d5dc9a19e205c0f18a9c779c3a7ff as yq

FROM docker.io/library/python:3.11.0@sha256:b5ff0c777972b45f9800d7410ff6d833c29f2b87924a921e6fd3992a8e79c3c9 as base

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

COPY maker /usr/local/bin/maker
RUN \
    ln -rs /usr/local/bin/maker /usr/local/bin/help && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
    ln -rs /usr/local/bin/maker /usr/local/bin/lint && \
    ln -rs /usr/local/bin/maker /usr/local/bin/linguistics-check && \
    ln -rs /usr/local/bin/maker /usr/local/bin/build && \
    ln -rs /usr/local/bin/maker /usr/local/bin/publish && \
    true

COPY Makefile /usr/local/share/techdocs/Makefile
COPY mkdocs.yml /usr/local/share/techdocs/mkdocs.yml
COPY markdownlint.yaml /usr/local/share/techdocs/markdownlint.yaml

RUN mkdir /content
WORKDIR /content
