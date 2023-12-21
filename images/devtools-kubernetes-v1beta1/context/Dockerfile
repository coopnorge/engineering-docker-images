# hadolint global ignore=DL4006,DL3003,SC2046
# syntax=docker/dockerfile:1.3
FROM docker.io/argoproj/argocd:v2.6.15@sha256:58ebb4ed23c8db4cd4cc3f954f8d94c4b4e3d9669c0751c484108d22b86d52de as argocd
FROM zegl/kube-score:v1.17.0@sha256:d4c34b9560d9ad35a5113fbbff6d798c87e6986a306ee097a0eb4242f9714810 as kube-score
FROM ghcr.io/yannh/kubeconform:v0.6.4@sha256:e68a0b638c6e9b76f1b7d58b4ec94340ef3b6601db25b2e40b29e3ac2d68e4bf as kubeconform
FROM docker.io/mikefarah/yq:4.40.5@sha256:32be61dc94d0acc44f513ba69d0fc05f1f92c2e760491f2a27e11fc13cde6327 as yq

FROM golang:1.21.5@sha256:672a2286da3ee7a854c3e0a56e0838918d0dbb1c18652992930293312de898a6 as buildenv

COPY --from=yq /usr/bin/yq /usr/local/bin/yq

WORKDIR /build
COPY go.mod go.sum tools.go /build/
RUN \
    cd $(go mod download -json github.com/magefile/mage | yq .Dir)  && \
    go run bootstrap.go

WORKDIR /build
RUN \
    cd $(go mod download -json github.com/homeport/dyff | yq .Dir)/cmd/dyff  && \
    go build -o /go/bin/dyff

COPY ./magefiles /magefiles
WORKDIR /magefiles
RUN \
    mage -compile  ./mage-k8s


FROM golang:1.21.5@sha256:672a2286da3ee7a854c3e0a56e0838918d0dbb1c18652992930293312de898a6 as base
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

COPY ./magefiles /magefiles

VOLUME /srv/workspace
WORKDIR /srv/workspace


RUN git config --system --add safe.directory /srv/workspace

ENTRYPOINT ["/usr/local/bin/mage-k8s"]
CMD ["validate"]
