# hadolint global ignore=DL4006,DL3003,SC2046
# syntax=docker/dockerfile:1.3
FROM quay.io/argoproj/argocd:v3.2.0@sha256:3c9b3b33a7e6c9c56a9d8417af1845afc516f714941962208b125017bbc1e4b1 AS argocd
FROM zegl/kube-score:v1.20.0@sha256:ac4c43ad560af905d66f6bf57b0937c591332e6dbf2167c31193a13b4695ab97 AS kube-score
FROM ghcr.io/yannh/kubeconform:v0.7.0@sha256:85dbef6b4b312b99133decc9c6fc9495e9fc5f92293d4ff3b7e1b30f5611823c AS kubeconform
FROM docker.io/mikefarah/yq:4.48.1@sha256:75b3a60dce1fa4641b0f02bdb4465eddc5da95e62028118a292239ca8e3921e5 AS yq
FROM ghcr.io/kyverno/kyverno-cli:v1.15.2@sha256:82d2359550442f96a11292e410fb7a5c929a12265b98b819c5858f88dcf29cf7 AS kyverno

FROM golang:1.25.4@sha256:6ca9eb0b32a4bd4e8c98a4a2edf2d7c96f3ea6db6eb4fc254eef6c067cf73bb4 AS buildenv

COPY --from=yq /usr/bin/yq /usr/local/bin/yq

ENV MAGE_VERSION=v1.15.0
ENV DYFF_VERSION=v1.10.2

WORKDIR /build
COPY go.mod go.sum tools.go /build/
# hadolint ignore=DL3062
RUN \
    cd $(go mod download -json "github.com/magefile/mage@$MAGE_VERSION" | yq .Dir)  && \
    go run bootstrap.go

WORKDIR /build
# hadolint ignore=DL3062
RUN \
    cd $(go mod download -json "github.com/homeport/dyff@$DYFF_VERSION" | yq .Dir)/cmd/dyff  && \
    go build -o /go/bin/dyff

RUN \
git clone --depth 1 https://github.com/coopnorge/mage-kubernetes-lib.git /tmp/mage-kubernetes-lib && \
mkdir -p /kyverno-policies && \
cp -r /tmp/mage-kubernetes-lib/kyverno-policies/* /kyverno-policies/

COPY ./magefiles /magefiles
WORKDIR /magefiles
RUN \
    mage -compile  ./mage-k8s


FROM golang:1.25.4@sha256:6ca9eb0b32a4bd4e8c98a4a2edf2d7c96f3ea6db6eb4fc254eef6c067cf73bb4 AS base
RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        busybox \
        ca-certificates \
        curl \
        git \
        make \
        socat \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true


COPY --from=kube-score /kube-score /usr/local/bin/kube-score
COPY --from=argocd /usr/local/bin/argocd /usr/local/bin/argocd
COPY --from=argocd /usr/local/bin/helm /usr/local/bin/helm
COPY --from=argocd /usr/local/bin/kustomize /usr/local/bin/kustomize
COPY --from=kubeconform /kubeconform /usr/local/bin/kubeconform
COPY --from=buildenv /magefiles/mage-k8s /usr/local/bin/mage-k8s
COPY --from=buildenv /go/bin/mage /usr/local/bin/mage
COPY --from=buildenv /go/bin/dyff /usr/local/bin/dyff
COPY --from=buildenv /kyverno-policies /kyverno-policies
COPY --from=kyverno /ko-app/kubectl-kyverno /usr/local/bin/kyverno

COPY ./magefiles /magefiles


VOLUME /srv/workspace
WORKDIR /srv/workspace


RUN git config --system --add safe.directory /srv/workspace

ENTRYPOINT ["/usr/local/bin/mage-k8s"]
CMD ["validate"]

