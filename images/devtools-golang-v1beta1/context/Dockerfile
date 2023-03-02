FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.51-alpine@sha256:d4441632fdd9787214ebcfe026339adb9ab24a94026df18c8835893bfcdc9e27 AS golangci-lint
FROM docker.io/fullstorydev/grpcurl:v1.8.7@sha256:d42ef512419560776bee5bb51e338a1734a0edb99f450b6d98fd98bcc93796f3 AS grpcurl
FROM docker.io/mikefarah/yq:4@sha256:3bdb5e6db331583864ffe89e8ba55288a9dfe116cf622ff4eac65745a87a3903 AS yq
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.11@sha256:79ef341552b293f13e7d915747b325c19f6ac47ed4d7bff2bff909fdd493acd7 AS dockle
FROM docker.io/moby/buildkit:v0.11.3-rootless@sha256:1e61e92773befbaffc45e06094203814e31528e650b4a0901cf65b7a452e7d6f AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.13.0@sha256:9ddb050949d8e9a37a96d7f9762095c332e015246200dc2984481f1771602fba AS crane
FROM docker.io/bufbuild/buf:1.15.0@sha256:966e0c5705850e7b1ce3dd34f3994a47ff14e769caf2fb521f86f0301d329542 AS buf
FROM docker.io/library/golang:1.20.1-bullseye@sha256:d35d4e6ee0e1627bbeaa6c2e7e35d49f9ae25cbe8c41a00ead262c0903c69978 AS base

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
