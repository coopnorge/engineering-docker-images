# syntax=docker/dockerfile:1.3
FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM ghcr.io/terraform-linters/tflint-bundle:v0.35.0.1@sha256:96b605e0e3a06181dffd6aec99148179d019bad653d8aa448ec3912f9afbea4e AS tflint
FROM docker.io/aquasec/tfsec:v1.1@sha256:c867867e5eb038f8c3e9f0cf698c7b6158006ff68088273934718060c8c7002b AS tfsec
FROM docker.io/hashicorp/terraform:1.1.9@sha256:25542989c8ad942f81d4219ab21027c83af339078d854643b7e8962f14bd57c9 AS terraform
FROM docker.io/library/golang:1.17@sha256:dba09c285770f58d6685b25a0606d72420b0a7525a2338080807d138a258c671 as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:d0bca7e423d7eb1f8a334762ca173164b4f8cac656b0ca3ce7f7d198fdb28143 AS base


# https://packages.ubuntu.com/search?keywords=busybox&searchon=names&suite=focal&section=all
RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make \
        socat \
        git \
        curl \
        ca-certificates \
        busybox \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true



COPY Makefile /usr/local/share/devtools-terraform/Makefile
COPY maker /usr/local/bin/maker
RUN \
    ln -rs /usr/local/bin/maker /usr/local/bin/help && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
    ln -rs /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -rs /usr/local/bin/maker /usr/local/bin/terraform-reinit && \
    true

VOLUME /srv/workspace
WORKDIR /srv/workspace

ARG tfswitcher_version=0.13.1201

COPY --from=terraform /bin/terraform /usr/bin/terraform
COPY --from=tflint /root/.tflint.d /root/.tflint.d
COPY --from=tflint /usr/local/bin/tflint /usr/bin/tflint
COPY --from=tfsec  /usr/bin/tfsec /usr/bin/tfsec
COPY --from=golang /usr/local/bin/goenv.sh /usr/local/bin/goenv.sh
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock

COPY terraform-switcher_${tfswitcher_version}_checksums.txt /var/tmp/terraform-switcher_${tfswitcher_version}_checksums.txt

# Setting TF_PLUGIN_CACHE_DIR makes things a lot faster but this somehow
# causes weird permission issues.
# ENV TF_PLUGIN_CACHE_DIR=/root/.cache/terraform.d/plugin-cache

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


CMD ["validate"]
