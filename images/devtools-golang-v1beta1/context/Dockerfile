FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.59-alpine@sha256:2a5293b5d25319a515db44f00c7e72466a78488106fbb995730580ef25fb8b20 AS golangci-lint
FROM docker.io/fullstorydev/grpcurl:v1.9.1@sha256:8bc96d11c8c08388b30cffafd177a1083a84e18c5bed314de5520c81171236a9 AS grpcurl
FROM docker.io/mikefarah/yq:4@sha256:bcb889a1f9bdb0613c8a054542d02360c2b1b35521041be3e1bd8fbd0534d411 AS yq
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.14@sha256:68f7473909b49013f97984e9917fb7edd0c440bf15e38f41449860f8a2680d51 AS dockle
FROM docker.io/moby/buildkit:v0.13.2-rootless@sha256:cf1c082979eec06a0eff50cd9b20172a0bf8bfe9af3bb9f8261d439f5af07ce1 AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.15.2@sha256:be47a641ac6b98004251e1dccdd6fe8cbfca233d1239c751d3eb142608ab3fee AS crane
FROM docker.io/bufbuild/buf:1.32.2@sha256:d616aaedf90773fc35bf33b1ca5a8f20d1fb497472756803a5ad126912daf0b4 AS buf
FROM docker.io/library/golang:1.22.3-bookworm@sha256:5c56bd47228dd572d8a82971cf1f946cd8bb1862a8ec6dc9f3d387cc94136976 AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

# https://packages.debian.org/search?keywords=busybox&searchon=names&suite=buster&section=all
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
        protobuf-compiler \
        rsync \
        socat \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true

COPY go.mod go.sum tools.go /var/tmp/build/

RUN \
    export GOBIN=/usr/local/bin && \
    cd /var/tmp/build/ && \
    awk -F '"' '/_.*toolchain/{print $2}' tools.go | xargs -t -I{} go install {} && \
    rm -rf "$(go env GOPATH)" && \
    rm -rf /var/tmp/build/* && \
    # Check that expected commands are available.
    protoc-gen-go-grpc --version && \
    protoc-gen-go --version && \
    protoc-gen-doc --version && \
    mockgen --version && \
    gomockhandler -h && \
    go-enum --help >/dev/null && \
    modd --version && \
    true


COPY --from=golangci-lint /usr/bin/golangci-lint /usr/bin/golangci-lint
COPY --from=grpcurl /bin/grpcurl /bin/grpcurl
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
    targets=( \
        help \
        validate validate-fix validate-static test \
        generate build publish watch clean \
        golang-validate golang-validate-fix golang-validate-static golang-test golang-generate golang-run golang-build golang-debug \
        oci-build oci-validate oci-push \
        buf-validate buf-generate \
    ); \
    for target in "${targets[@]}"; \
    do \
        ln -s /usr/local/bin/maker "/usr/local/bin/${target}"; \
    done && \
    true

COPY Makefile /usr/local/share/devtools-golang/
COPY Dockerfile.app /usr/local/share/devtools-golang/

RUN git config --system --add safe.directory /srv/workspace; \
    go env -w GOPRIVATE=github.com/coopnorge/*

VOLUME /srv/workspace
WORKDIR /srv/workspace

CMD ["validate", "build"]
