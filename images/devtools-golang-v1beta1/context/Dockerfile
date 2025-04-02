FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.64-alpine@sha256:ae6460f78db54f22838d2a8aee0f2eaa4f785d5a01f638600072b60848f8deb4 AS golangci-lint
FROM docker.io/fullstorydev/grpcurl:v1.9.3@sha256:085e183ca334eb4e81ca81ee12cbb2b2737505d1d77f5e33dabc5d066593d998 AS grpcurl
FROM docker.io/mikefarah/yq:4@sha256:2c100efaca06e95ffe452cfe9bfc0048b493f0f3a072d5fe06f828c638d9462b AS yq
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9 AS dockle
FROM docker.io/moby/buildkit:v0.20.2-rootless@sha256:cb5bb371545222c430528556acfdf424144b69897f5deaad391bd227187e90df AS buildkit
FROM gcr.io/go-containerregistry/crane:latest@sha256:fc86bcad43a000c2a1ca926a1e167db26c053cebc3fa5d14285c72773fb8c11d AS crane
FROM docker.io/bufbuild/buf:1.51.0@sha256:fc35cd72f7638b19ae2b0a739fd738a8791ef5024fef50200ab831ea8be2cc8b AS buf
FROM docker.io/library/golang:1.24.1-bookworm@sha256:fa1a01d362a7b9df68b021d59a124d28cae6d99ebd1a876e3557c4dd092f1b1d AS base

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
