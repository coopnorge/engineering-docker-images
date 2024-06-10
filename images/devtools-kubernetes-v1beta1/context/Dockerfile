# hadolint global ignore=DL4006,DL3003,SC2046
# syntax=docker/dockerfile:1.3
FROM docker.io/argoproj/argocd:v2.6.15@sha256:58ebb4ed23c8db4cd4cc3f954f8d94c4b4e3d9669c0751c484108d22b86d52de as argocd
FROM zegl/kube-score:v1.18.0@sha256:1b23495ad2528e51d7f6e5936072bbf9f2953312308abacfc5f3a2bd92249202 as kube-score
FROM ghcr.io/yannh/kubeconform:v0.6.6@sha256:e4c69e6966a4842196ad3babc6f4c869d4ee51dc306fcf012faf10b25bb63a9c as kubeconform
FROM docker.io/mikefarah/yq:4.44.1@sha256:bcb889a1f9bdb0613c8a054542d02360c2b1b35521041be3e1bd8fbd0534d411 as yq

FROM golang:1.22.4@sha256:969349b8121a56d51c74f4c273ab974c15b3a8ae246a5cffc1df7d28b66cf978 as buildenv

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


FROM golang:1.22.4@sha256:969349b8121a56d51c74f4c273ab974c15b3a8ae246a5cffc1df7d28b66cf978 as base
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
