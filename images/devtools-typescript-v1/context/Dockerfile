FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM docker.io/mikefarah/yq:4@sha256:ccb1c89bdf01be8b2fcb2b22f3d75b033854893bb7db0e7ce9879a5eacb50ccd AS yq
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.11@sha256:79ef341552b293f13e7d915747b325c19f6ac47ed4d7bff2bff909fdd493acd7 AS dockle
FROM docker.io/moby/buildkit:v0.11.5-rootless@sha256:72b833daae4a9875a3193dabb0037811e2e56e605fc414bb0bda6643323ab994 AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.13.0@sha256:9ddb050949d8e9a37a96d7f9762095c332e015246200dc2984481f1771602fba AS crane
FROM docker.io/library/node:20.0.3-bullseye@sha256:4e271ab266a4b76874c8e7c8aa431a8dbe636af19fa5e76403e3acbd9b8d3450 AS base

ARG TOOLS_DIR=/opt/devtools-typescript/

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
	apt-get update && \
	apt-get install -y \
	--no-install-recommends \
	busybox \
	ca-certificates \
	curl \
	git \
	jq \
	make \
	rsync \
	socat \
	&& \
	rm -vr /var/lib/apt/lists/* && \
	true


COPY package.json package-lock.json $TOOLS_DIR

RUN \
	cd $TOOLS_DIR && \
	npm i && \
	true


COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock
COPY --from=yq /usr/bin/yq /usr/local/bin/yq
COPY --from=hadolint /bin/hadolint /usr/local/bin/hadolint
COPY --from=dockle /usr/bin/dockle /usr/local/bin/dockle
COPY --from=crane /ko-app/crane /usr/local/bin/
COPY --from=buildkit /usr/bin/buildkit* /usr/bin/buildctl* /usr/bin/rootlesskit /usr/local/bin/

COPY .eslintrc.js $TOOLS_DIR/.eslintrc.js

COPY maker /usr/local/bin/maker

RUN \
	set -x; \
	targets=( \
	help \
	validate validate-fix validate-static test \
	build publish watch clean \
	ts-validate ts-validate-fix ts-validate-static ts-test ts-run \
	oci-build oci-validate oci-push \
	); \
	for target in "${targets[@]}"; \
	do \
	ln -s /usr/local/bin/maker "/usr/local/bin/${target}"; \
	done && \
	true

COPY Makefile /usr/local/share/devtools-typescript/

RUN git config --system --add safe.directory /srv/workspace

VOLUME /srv/workspace
WORKDIR /srv/workspace

CMD ["validate", "build"]
