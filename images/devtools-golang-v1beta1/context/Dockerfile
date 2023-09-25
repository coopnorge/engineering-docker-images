FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.54-alpine@sha256:e950721f6ae622dcc041f57cc0b61c3a78d4bbfc588facfc8b0166901a9f4848 AS golangci-lint
FROM docker.io/fullstorydev/grpcurl:v1.8.8@sha256:caef4105620e160522cfd66b809339be5189f790cb099c2d3333283475648fdb AS grpcurl
FROM docker.io/mikefarah/yq:4@sha256:b7a40250d5018aeeabc33849f72581c6275323fb6117a8e143adc6b187463d34 AS yq
FROM docker.io/hadolint/hadolint:v2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.13@sha256:2e933954456219021389d1eec5fd09b35d89ff17fe7445abc0fc5748f71d7ae1 AS dockle
FROM docker.io/moby/buildkit:v0.12.2-rootless@sha256:bea93e450ad9cfd4bbbc846ebceba3382a9f9128fa7ae43afa00bc50ad026a32 AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.15.2@sha256:be47a641ac6b98004251e1dccdd6fe8cbfca233d1239c751d3eb142608ab3fee AS crane
FROM docker.io/bufbuild/buf:1.26.1@sha256:6a81c07bd0fb9f91ccd5a760de34c3df087f126bc0dc99acd04cdd583a08c4bd AS buf
FROM docker.io/library/golang:1.21.1-bullseye@sha256:d9203b088f9e50cc60eccfc0129d9bd5109b236a5e5cda1a4527aef834fd85ef AS base

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

RUN git config --system --add safe.directory /srv/workspace; \
    go env -w GOPRIVATE=github.com/coopnorge/*

VOLUME /srv/workspace
WORKDIR /srv/workspace

CMD ["validate", "build"]
