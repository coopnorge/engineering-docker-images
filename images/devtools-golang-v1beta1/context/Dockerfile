FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.46.2-alpine@sha256:6a09f1e87ecce4eab163470467cd88dab3a0efa31cb708ba6d514a6889816095 AS golangci-lint
FROM docker.io/mikefarah/yq:4@sha256:71d9de06ec2a0f906dcd8f4182dd3b5c4fb014d40da4f539a6261112551b4989 AS yq


# golangci-lint does not work with go1.18
# https://github.com/golangci/golangci-lint/issues/2649
FROM golang:1.18.3-bullseye@sha256:2120a5e5b1e4c0f67ba0566d15281eeb38d7659eff9d932dfe56fbd1d58f108f AS base

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

ARG buf_version=1.5.0

COPY buf-fetch.sh buf-${buf_version}.sha256sum /var/tmp/build/

RUN \
    cd /var/tmp/build && \
    . /usr/local/bin/goenv.sh && \
    FILE_SELECTOR="$(uname -s)-$(uname -m)" FILE_VERSION="${buf_version}" OUTPUT_PATH=/usr/local/bin /var/tmp/build/buf-fetch.sh && \
    buf --version && \
    rm -rf /var/tmp/build/* && \
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

COPY .golangci.yml /.golangci.yml

COPY Makefile /usr/local/share/devtools-golang/Makefile
COPY maker /usr/local/bin/maker

RUN \
    ln -s /usr/local/bin/maker /usr/local/bin/help && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-static && \
    ln -s /usr/local/bin/maker /usr/local/bin/test && \
    ln -s /usr/local/bin/maker /usr/local/bin/build && \
    true

CMD ["validate", "build"]
