# hadolint global ignore=DL4006,DL3003,SC2046
# syntax=docker/dockerfile:1.3
FROM quay.io/argoproj/argocd:v3.0.11@sha256:1cb4ede2fc4a6332c128d9ba29d19e8cb5b76f9260dc47550a4b3b154269ff86 AS argocd
FROM zegl/kube-score:v1.20.0@sha256:ac4c43ad560af905d66f6bf57b0937c591332e6dbf2167c31193a13b4695ab97 AS kube-score
FROM ghcr.io/yannh/kubeconform:v0.7.0@sha256:85dbef6b4b312b99133decc9c6fc9495e9fc5f92293d4ff3b7e1b30f5611823c AS kubeconform
FROM docker.io/mikefarah/yq:4.46.1@sha256:e4ec3062f63c5dd56c5fb79e325d24b91f1ca0d66d01cbc06ea2dd6a6ff867ab AS yq
FROM ghcr.io/kyverno/kyverno-cli:v1.14.4@sha256:bcc4db143edb795cb6a20b111b60368925a9b2ebdc66284afe748c3f7c27dab4 AS kyverno

FROM golang:1.24.5@sha256:267159cb984d1d034fce6e9db8641bf347f80e5f2e913561ea98c40d5051cb67 AS buildenv

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

RUN \
git clone --depth 1 https://github.com/coopnorge/mage-kubernetes-lib.git /tmp/mage-kubernetes-lib && \
mkdir -p /kyverno-policies && \
cp -r /tmp/mage-kubernetes-lib/kyverno-policies/* /kyverno-policies/

COPY ./magefiles /magefiles
WORKDIR /magefiles
RUN \
    mage -compile  ./mage-k8s


FROM golang:1.24.5@sha256:267159cb984d1d034fce6e9db8641bf347f80e5f2e913561ea98c40d5051cb67 AS base
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

