# syntax=docker/dockerfile:1.3
FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM ghcr.io/terraform-linters/tflint-bundle:v0.48.0.0@sha256:523a85b4bf7af415cbb5f53ac1b56cd7501c8c8125f96c5b5cc19c895d894513 AS tflint
FROM docker.io/aquasec/tfsec:v1.28.5@sha256:0e651e8f1862193ce20aeea3771d8e9f222bbbc478b9fa75539f5573fd0e01d8 AS tfsec
FROM docker.io/hashicorp/terraform:1.7.4@sha256:432446e203a6aed6da5c8245544e87cbd77ffebc4a17e9fe8bb0d18fd9639191 AS terraform
FROM quay.io/terraform-docs/terraform-docs:0.17.0@sha256:ab2d5d464547223b4e296d163b8bcb767f40e916e29f4f586cee608eb96246d1 as tfdocs
FROM docker.io/library/golang:1.22.0@sha256:7b297d9abee021bab9046e492506b3c2da8a3722cbf301653186545ecc1e00bb as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:f9d633ff6640178c2d0525017174a688e2c1aef28f0a0130b26bd5554491f0da AS base


# https://packages.ubuntu.com/search?keywords=busybox&searchon=names&suite=focal&section=all
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

VOLUME /srv/workspace
WORKDIR /srv/workspace

ARG tfswitcher_version=0.13.1300

COPY --from=terraform /bin/terraform /usr/bin/terraform
COPY --from=tflint /root/.tflint.d /root/.tflint.d
COPY --from=tflint /usr/local/bin/tflint /usr/bin/tflint
COPY --from=tfsec  /usr/bin/tfsec /usr/bin/tfsec
COPY --from=golang /usr/local/bin/goenv.sh /usr/local/bin/goenv.sh
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock
COPY --from=tfdocs /usr/local/bin/terraform-docs /usr/local/bin/terraform-docs

COPY terraform-switcher_${tfswitcher_version}_checksums.txt /var/tmp/terraform-switcher_${tfswitcher_version}_checksums.txt


ARG terraform_versions="0.15.5 1.0.11 1.1.7"

RUN \
    mkdir -vp ~/.cache ~/.local/bin ~/bin && \
    true

RUN \
    cd /var/tmp && \
    . /usr/local/bin/goenv.sh && \
    curl -LOJ "https://github.com/warrensbox/terraform-switcher/releases/download/${tfswitcher_version}/terraform-switcher_${tfswitcher_version}_${GOOS}_${GOARCH}.tar.gz" && \
    sed -i "/_${GOOS}_${GOARCH}.tar.gz/!d" "terraform-switcher_${tfswitcher_version}_checksums.txt" && \
    sha256sum -c "terraform-switcher_${tfswitcher_version}_checksums.txt" && \
    tar -xvf "terraform-switcher_${tfswitcher_version}_${GOOS}_${GOARCH}.tar.gz" -C /usr/local/bin tfswitch && \
    # mkdir -vp ~/.cache/.terraform.versions && \
    # ln -s ~/.cache/.terraform.versions ~/.terraform.versions && \
    # for ver in ${terraform_versions}; \
    # do \
    #     tfswitch "${ver}"; \
    # done; \
    true

ENV TF_PLUGIN_CACHE_DIR=/root/.cache/terraform.d/plugin-cache


COPY maker /usr/local/bin/maker
RUN \
    ln -rs /usr/local/bin/maker /usr/local/bin/help && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -rs /usr/local/bin/maker /usr/local/bin/terraform-reinit && \
    ln -rs /usr/local/bin/maker /usr/local/bin/terraform-upgrade && \
    ln -rs /usr/local/bin/maker /usr/local/bin/terraform-relock && \
    ln -rs /usr/local/bin/maker /usr/local/bin/tf-docs && \
    true

COPY Makefile /usr/local/share/devtools-terraform/Makefile

RUN git config --system --add safe.directory /srv/workspace

CMD ["validate"]
