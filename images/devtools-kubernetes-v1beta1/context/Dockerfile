# hadolint global ignore=DL4006,DL3003,SC2046
# syntax=docker/dockerfile:1.3
FROM docker.io/argoproj/argocd:v2.6.15@sha256:58ebb4ed23c8db4cd4cc3f954f8d94c4b4e3d9669c0751c484108d22b86d52de AS argocd
FROM zegl/kube-score:v1.19.0@sha256:94137f32ce139dc9fbdbbd380249025e4d378c282ff151a100b981cdeeb923b6 AS kube-score
FROM ghcr.io/yannh/kubeconform:v0.6.7@sha256:0925177fb05b44ce18574076141b5c3d83235e1904d3f952182ac99ddc45762c AS kubeconform
FROM docker.io/mikefarah/yq:4.44.3@sha256:5b3d851bf28b04ef902fee86305f4dd7e063919c1cafedab2042adb16221c025 AS yq
FROM ghcr.io/kyverno/kyverno-cli:v1.12@sha256:229154f8f42326c5a7568b3787887b81ca94f0824400574ffab1dd9d30931f01 AS kyverno

FROM golang:1.23.2@sha256:ad5c126b5cf501a8caef751a243bb717ec204ab1aa56dc41dc11be089fafcb4f AS buildenv

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
    

FROM golang:1.23.2@sha256:ad5c126b5cf501a8caef751a243bb717ec204ab1aa56dc41dc11be089fafcb4f AS base
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
COPY --from=kyverno /ko-app/kubectl-kyverno /usr/local/bin/kyverno

COPY ./magefiles /magefiles

VOLUME /srv/workspace
WORKDIR /srv/workspace


RUN git config --system --add safe.directory /srv/workspace

ENTRYPOINT ["/usr/local/bin/mage-k8s"]
CMD ["validate"]

