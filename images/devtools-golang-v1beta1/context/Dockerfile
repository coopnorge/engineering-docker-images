FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.48.0-alpine@sha256:e9ce901b7974d641d6288b070fc619d199a823d0f696563fec8be90f19789b57 AS golangci-lint
FROM docker.io/mikefarah/yq:4@sha256:22237bf6ac5e419bf225b9084867aa30222284df02bc73b04734c1a00778fa5d AS yq
FROM docker.io/hadolint/hadolint:v2.10.0@sha256:93f0afd12c3be5d732227c0226dd8e7bb84f79319a773d7f8519e55f958ba415 AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.9@sha256:2a5fc2c1a467dd229720baf6c002798e5a1f86ce37e5657bc9c4b2cc3503fd64 AS dockle
FROM docker.io/moby/buildkit:v0.10.4-rootless@sha256:fc81ed8d967a60bf0e6bff38d4cf9d40be6e815d559c5796c8428cd82fd05674 AS buildkit
FROM gcr.io/go-containerregistry/crane:v0.11.0@sha256:40823185f184cfc2fed19318988ad5119f4d2fd1eadee51d8b2b365016a6c03b AS crane
FROM docker.io/bufbuild/buf:1.9.0@sha256:24abb6b50fbdda65974f1b127b89e66c9d74c9e1415c4536a4755808ed679456 AS buf
FROM docker.io/library/golang:1.19.2-bullseye@sha256:80ede0f12980ec4fc580fa651aabff041d46d1255b323fa0b740ecbce9f89256 AS base

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
