# syntax=docker/dockerfile:1.3
FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM ghcr.io/terraform-linters/tflint-bundle:v0.43.0.1@sha256:7cd4888ba11f120112119118199107c6d5530e5ba6e6cc0e2055bd78c0e712d0 AS tflint
FROM docker.io/aquasec/tfsec:v1.28.1@sha256:dfb84d16b1668701bf0932063e8ebb5a730cff38e08c7c1a689b02c3eee2e577 AS tfsec
FROM docker.io/hashicorp/terraform:1.3.4@sha256:b1e8f54067efaf181841406c67df9c091cc01736d7589ef47718dadc5ee72e48 AS terraform
FROM quay.io/terraform-docs/terraform-docs:0.16.0@sha256:e24bf3fe70d15eeda95399f4fa5c70260cf4dfffbff4fb66931095d8d7ba9074 as tfdocs
FROM docker.io/library/golang:1.19.3@sha256:dc76ef03e54c34a00dcdca81e55c242d24b34d231637776c4bb5c1a8e8514253 as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:4b1d0c4a2d2aaf63b37111f34eb9fa89fa1bf53dd6e4ca954d47caebca4005c2 AS base


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

CMD ["validate"]
