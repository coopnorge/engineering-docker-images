# syntax=docker/dockerfile:1.3
FROM zegl/kube-score:v1.14.0@sha256:df26b2d3978be960b41e8c09906a38f3e5ad7ef3c63b8770c693dc3405005299 as kube-score
FROM golang:1.18.2@sha256:10e33fc8fc78d9f2ddc99ae16eb81819d010dee92f8c0df18a271a339e5ecdf1 as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:26c68657ccce2cb0a31b330cb0be2b5e108d467f641c62e13ab40cbec258c68d AS base

RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make \
        ca-certificates \
        curl \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true



VOLUME /srv/workspace
WORKDIR /srv/workspace

COPY --from=golang /usr/local/bin/goenv.sh /usr/local/bin/goenv.sh
COPY --from=kube-score /kube-score /usr/bin/kube-score

RUN \
    mkdir -vp ~/.cache ~/.local/bin ~/bin && \
    true

ARG kubeval_version="0.16.1"
COPY kubeval_${kubeval_version}_checksums.txt /var/tmp/build/kubeval_${kubeval_version}_checksums.txt

# Kubeval only publishes a docker image with a binary that is dynamically linked musl libc, download release artifact directly
RUN \
    cd /var/tmp/build && \
    . /usr/local/bin/goenv.sh && \
    curl -LOJ "https://github.com/instrumenta/kubeval/releases/download/v${kubeval_version}/kubeval-${GOOS}-${GOARCH}.tar.gz" && \
    sed -i "/-${GOOS}-${GOARCH}.tar.gz/!d" "kubeval_${kubeval_version}_checksums.txt" && \
    sha256sum -c "kubeval_${kubeval_version}_checksums.txt" && \
    tar -xvf "kubeval-${GOOS}-${GOARCH}.tar.gz" -C /usr/local/bin kubeval && \
    true

ARG kubectl_version="1.23.0"
COPY kubectl_${kubectl_version}_checksums.txt /var/tmp/build/kubectl_${kubectl_version}_checksums.txt

# From https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
# Use ./get_kubectl_checksums to retrieve checksums for a release
RUN \
    cd /var/tmp/build && \
    . /usr/local/bin/goenv.sh && \
    curl -LJ "https://dl.k8s.io/release/v${kubectl_version}/bin/${GOOS}/${GOARCH}/kubectl" -o "kubectl-${GOOS}-${GOARCH}" && \
    sed -i "/-${GOOS}-${GOARCH}/!d" "kubectl_${kubectl_version}_checksums.txt" && \
    sha256sum -c "kubectl_${kubectl_version}_checksums.txt" && \
    install -o root -g root -m 0755 "kubectl-${GOOS}-${GOARCH}" /usr/local/bin/kubectl && \
    true

RUN \
    rm -rf /var/tmp/build && \
    true

COPY maker /usr/local/bin/maker
RUN \
    ln -rs /usr/local/bin/maker /usr/local/bin/help && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
    true

COPY Makefile /usr/local/share/devtools-kubernetes/Makefile

CMD ["validate"]
