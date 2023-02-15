# syntax=docker/dockerfile:1.3
FROM docker.io/argoproj/argocd:v2.6.1@sha256:7c8a4f49b7bda99e5b8f4b44dbc6a46b87ebb0f8696c5027aaaf9bbbd022ac7f as argocd
FROM zegl/kube-score:v1.16.1@sha256:2e46cd36a08c1c6eb90c4e8e87c61c22d9402c3f73a25a9c9645df909b79897f as kube-score
FROM golang:1.20.1@sha256:9911e9376e45de1ba865b16d878c0f7d063391fe4b7cedf39869874126741e62 as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:7cfe75438fc77c9d7235ae502bf229b15ca86647ac01c844b272b56326d56184 AS base

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
COPY --from=kube-score /kube-score /usr/local/bin/kube-score
COPY --from=argocd /usr/local/bin/argocd /usr/local/bin/argocd

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
    kubeval --version && \
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
    kubectl version --client=true && \
    true

ARG kubeconform_version="0.4.13"
COPY kubeconform_${kubeconform_version}_checksums.txt /var/tmp/build/kubeconform_${kubeconform_version}_checksums.txt
RUN \
    cd /var/tmp/build && \
    . /usr/local/bin/goenv.sh && \
    curl -LOJ "https://github.com/yannh/kubeconform/releases/download/v${kubeconform_version}/kubeconform-${GOOS}-${GOARCH}.tar.gz" && \
    sed -i "/-${GOOS}-${GOARCH}.tar.gz/!d" "kubeconform_${kubeconform_version}_checksums.txt" && \
    sha256sum -c "kubeconform_${kubeconform_version}_checksums.txt" && \
    tar -xvf "kubeconform-${GOOS}-${GOARCH}.tar.gz" -C /usr/local/bin kubeconform && \
    kubeconform -v && \
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
