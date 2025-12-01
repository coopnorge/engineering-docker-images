FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v2.6-alpine@sha256:a3abd55b17a74e36703f3d27e8183958b8bee15a1b1ffb25529192e114e0edbe AS golangci-lint
FROM docker.io/fullstorydev/grpcurl:v1.9.3@sha256:085e183ca334eb4e81ca81ee12cbb2b2737505d1d77f5e33dabc5d066593d998 AS grpcurl
FROM docker.io/mikefarah/yq:4@sha256:224eec1bdaf4903221117d65dd95a0f4f4a6d4e46c88e2c81e09398d1f2753a1 AS yq
FROM docker.io/hadolint/hadolint:v2.14.0@sha256:27086352fd5e1907ea2b934eb1023f217c5ae087992eb59fde121dce9c9ff21e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9 AS dockle
FROM docker.io/moby/buildkit:v0.26.2-rootless@sha256:0ffa2fcf6b8757c47d569b3ef0f03f9d5eb3b9ff5ce68d858f994f89b749da0c AS buildkit
FROM gcr.io/go-containerregistry/crane:latest@sha256:13952b31a107e8bc4e4c170b0097edb708cd468486a28fc20bbf0d49f71c74e1 AS crane
FROM docker.io/bufbuild/buf:1.61.0@sha256:3b7fb27f8ff153037b3f781924c6aa1327352f14ee547cf45fd75f6d994fe0eb AS buf
FROM docker.io/library/golang:1.25.4-bookworm@sha256:e17419604b6d1f9bc245694425f0ec9b1b53685c80850900a376fb10cb0f70cb AS base

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
