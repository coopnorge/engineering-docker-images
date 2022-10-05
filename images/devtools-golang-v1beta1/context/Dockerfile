FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.48.0-alpine@sha256:e9ce901b7974d641d6288b070fc619d199a823d0f696563fec8be90f19789b57 AS golangci-lint
FROM docker.io/mikefarah/yq:4@sha256:87ac4405188ce28f428b8e3d013dfe7e1341ef0de5aeef66ea1d5d87369b1840 AS yq
FROM docker.io/hadolint/hadolint:v2.10.0@sha256:93f0afd12c3be5d732227c0226dd8e7bb84f79319a773d7f8519e55f958ba415 AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.6@sha256:534ecfe2204403e1b563d61b255ddd4762b20c9d72ce7af239fb1135be6c9569 AS dockle
FROM docker.io/moby/buildkit:v0.10.4-rootless@sha256:fc81ed8d967a60bf0e6bff38d4cf9d40be6e815d559c5796c8428cd82fd05674 AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.11.0@sha256:40823185f184cfc2fed19318988ad5119f4d2fd1eadee51d8b2b365016a6c03b AS crane
FROM docker.io/bufbuild/buf:1.8.0@sha256:0793bed84c08f77c9d558b1ebac5de915386eaf672f39c09c4f9cd0144558ba8 AS buf
FROM docker.io/library/golang:1.19.2-bullseye@sha256:aa5113dbcd625bfc6299b01a995c06dadb20471973adef869a218de835dc8df8 AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

# https://packages.debian.org/search?keywords=busybox&searchon=names&suite=buster&section=all
RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make \
        socat \
        curl \
        ca-certificates \
        busybox \
        rsync \
        protobuf-compiler \
        git \
        jq \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true

ARG prototool_version=1.10.0

COPY prototool-${prototool_version}-Linux-x86_64.sha256sum /var/tmp/build/

RUN \
    cd /var/tmp/build && \
    curl -L "https://github.com/uber/prototool/releases/download/v1.10.0/prototool-Linux-x86_64" -o prototool-${prototool_version}-Linux-x86_64 && \
    sha256sum -c "prototool-${prototool_version}-Linux-x86_64.sha256sum" && \
    install -o root -g root -m 0755 "prototool-${prototool_version}-Linux-x86_64" /usr/local/bin/prototool && \
    rm -rf /var/tmp/build && \
    true

COPY go.mod go.sum tools.go /var/tmp/build/

RUN \
    export GOBIN=/usr/local/bin && \
    cd /var/tmp/build/ && \
    awk -F '"' '/_.*toolchain/{print $2}' tools.go | xargs -t -I{} go install {} && \
    rm -rf "$(go env GOPATH)" && \
    rm -rf /var/tmp/build/* && \
    protoc-gen-doc --version && \
    true


VOLUME /srv/workspace
WORKDIR /srv/workspace

COPY --from=golangci-lint /usr/bin/golangci-lint /usr/bin/golangci-lint
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock
COPY --from=yq /usr/bin/yq /usr/local/bin/yq
COPY --from=hadolint /bin/hadolint /usr/local/bin/hadolint
COPY --from=dockle /usr/bin/dockle /usr/local/bin/dockle
COPY --from=crane /ko-app/crane /usr/local/bin/
COPY --from=buf /usr/local/bin/buf /usr/local/bin/
COPY --from=buildkit /usr/bin/buildkit* /usr/bin/buildctl* /usr/bin/rootlesskit /usr/local/bin/

COPY .golangci.yml /.golangci.yml

COPY maker /usr/local/bin/maker

RUN \
    set -x; \
    targets=(help validate validate-fix validate-static test validate-golang validate-golang-fix validate-golang-static test-golang build publish watch build-oci validate-oci push-oci); \
    for target in "${targets[@]}"; \
    do \
        ln -s /usr/local/bin/maker "/usr/local/bin/${target}"; \
    done && \
    true

COPY Makefile /usr/local/share/devtools-golang/
COPY Dockerfile.app /usr/local/share/devtools-golang/

CMD ["validate", "build"]
