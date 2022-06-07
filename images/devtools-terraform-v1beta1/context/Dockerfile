# syntax=docker/dockerfile:1.3
FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM ghcr.io/terraform-linters/tflint-bundle:v0.37.0.1@sha256:48abd0cd1a521b675d142861d29741d723befcc6c349675970b6b8d5d4e7f830 AS tflint
FROM docker.io/aquasec/tfsec:v1.22.1@sha256:b89240cdc2e4309fff30ee590f1a6e4bf4269ecf79c02b6543acc8b76a336cad AS tfsec
FROM docker.io/hashicorp/terraform:1.2.2@sha256:02214c4408e9af68e4a3b886eb423ec6330718f9f73a2d6abb460cf8a35c3108 AS terraform
FROM docker.io/library/golang:1.18.3@sha256:b203dc573d81da7b3176264bfa447bd7c10c9347689be40540381838d75eebef as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:0b8153d771cdca9185be7c730b64c25697f30e63f122fbce49dd4f1f5ae9b26e AS base


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

VOLUME /srv/workspace
WORKDIR /srv/workspace

ARG tfswitcher_version=0.13.1221

COPY --from=terraform /bin/terraform /usr/bin/terraform
COPY --from=tflint /root/.tflint.d /root/.tflint.d
COPY --from=tflint /usr/local/bin/tflint /usr/bin/tflint
COPY --from=tfsec  /usr/bin/tfsec /usr/bin/tfsec
COPY --from=golang /usr/local/bin/goenv.sh /usr/local/bin/goenv.sh
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock

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
    true

COPY Makefile /usr/local/share/devtools-terraform/Makefile

CMD ["validate"]
