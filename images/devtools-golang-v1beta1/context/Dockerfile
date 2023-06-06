FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.52-alpine@sha256:639dbebd312e31bb470ef70e83967eb2840a8cea39e857ac6494df2fe1b324fa AS golangci-lint
FROM docker.io/fullstorydev/grpcurl:v1.8.7@sha256:d42ef512419560776bee5bb51e338a1734a0edb99f450b6d98fd98bcc93796f3 AS grpcurl
FROM docker.io/mikefarah/yq:4@sha256:414a2cd52d0ac9c03cbaeb2b1e07bab9ed551d25b4578d4a4dccaffb82406fba AS yq
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.11@sha256:79ef341552b293f13e7d915747b325c19f6ac47ed4d7bff2bff909fdd493acd7 AS dockle
FROM docker.io/moby/buildkit:v0.11.6-rootless@sha256:07612ce3422e8fe5b385266900a7fd238b0f909ea8330eeb72371cbd9eb6262e AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.15.2@sha256:be47a641ac6b98004251e1dccdd6fe8cbfca233d1239c751d3eb142608ab3fee AS crane
FROM docker.io/bufbuild/buf:1.21.0@sha256:2802575d7eee755bc2c49118c99a094d87ec2e95f1f4802e171f2ac51eb8779a AS buf
FROM docker.io/library/golang:1.20.4-bullseye@sha256:918857f4064db0fff49799ce5e7c4d43e394f452111cd89cca9af539c18a76a8 AS base

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
        golang-validate golang-validate-fix golang-validate-static golang-test golang-generate golang-run \
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

RUN git config --system --add safe.directory /srv/workspace

VOLUME /srv/workspace
WORKDIR /srv/workspace

CMD ["validate", "build"]
