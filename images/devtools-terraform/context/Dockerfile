# syntax=docker/dockerfile:1.3
FROM ghcr.io/terraform-linters/tflint-bundle:v0.34.1.2@sha256:25889a5d3738a97ba1fa1e72bdc1b05dd1e7087c58213597cb0e1ed30f52615a AS tflint
FROM docker.io/aquasec/tfsec:v1.1@sha256:c867867e5eb038f8c3e9f0cf698c7b6158006ff68088273934718060c8c7002b AS tfsec
FROM docker.io/hashicorp/terraform:1.1.6@sha256:6f68122ab2981c609d9a7ee9cd3ba5564e4b1bf9b26ca3bc3628c106f98e9c35 AS terraform
FROM docker.io/library/golang:latest as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:20.04@sha256:669e010b58baf5beb2836b253c1fd5768333f0d1dbcb834f7c07a4dc93f474be AS base


RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make=4.2.1-1.2 \
        socat=1.7.3.3-2 \
        curl=7.68.0-1ubuntu2.7 \
        ca-certificates=20210119~20.04.2 \
    && true



COPY Makefile /usr/local/share/devtools-terraform/Makefile
COPY maker /usr/local/bin/maker
RUN \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate-fix && \
    true

VOLUME /srv/workspace
WORKDIR /srv/workspace

ARG tfswitcher_version=0.13.1201

COPY --from=terraform /bin/terraform /usr/bin/terraform
COPY --from=tflint /root/.tflint.d /root/.tflint.d
COPY --from=tflint /usr/local/bin/tflint /usr/bin/tflint
COPY --from=tfsec  /usr/bin/tfsec /usr/bin/tfsec
COPY --from=golang /usr/local/bin/goenv.sh /usr/local/bin/goenv.sh

COPY terraform-switcher_${tfswitcher_version}_checksums.txt /var/tmp/terraform-switcher_${tfswitcher_version}_checksums.txt

ARG terraform_versions="0.15.5 1.0.11 1.1.6"

RUN \
    mkdir -vp ~/.cache ~/.local/bin ~/bin && \
    true

RUN \
    cd /var/tmp && \
    . /usr/local/bin/goenv.sh && \
    curl -LOJ https://github.com/warrensbox/terraform-switcher/releases/download/${tfswitcher_version}/terraform-switcher_${tfswitcher_version}_${GOOS}_${GOARCH}.tar.gz && \
    sed -i "/_${GOOS}_${GOARCH}.tar.gz/!d" terraform-switcher_${tfswitcher_version}_checksums.txt && \
    sha256sum -c terraform-switcher_${tfswitcher_version}_checksums.txt && \
    tar -xvf terraform-switcher_${tfswitcher_version}_${GOOS}_${GOARCH}.tar.gz -C /usr/local/bin tfswitch && \
    mkdir -vp ~/.cache/.terraform.versions && \
    ln -s ~/.cache/.terraform.versions ~/.terraform.versions && \
    true; \
    for ver in ${terraform_versions}; \
    do \
        tfswitch "${ver}"; \
    done; \
    true


CMD ["validate"]
