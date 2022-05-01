# syntax=docker/dockerfile:1.3
FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM ghcr.io/terraform-linters/tflint-bundle:v0.35.0.1@sha256:96b605e0e3a06181dffd6aec99148179d019bad653d8aa448ec3912f9afbea4e AS tflint
FROM docker.io/aquasec/tfsec:v1.19.1@sha256:7c693fecba97e450f3ea6756c1e60529bead648e0f37b5d52da1497109d22cbb AS tfsec
FROM docker.io/hashicorp/terraform:1.1.9@sha256:25542989c8ad942f81d4219ab21027c83af339078d854643b7e8962f14bd57c9 AS terraform
FROM docker.io/library/golang:1.18.1@sha256:12d3995156cb0dcdbb9d3edb5827e4e8e1bf5bf92436bfd12d696ec997001a9a as golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:22.04@sha256:26c68657ccce2cb0a31b330cb0be2b5e108d467f641c62e13ab40cbec258c68d AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

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
        jq  \
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

ARG tfswitcher_version=""

COPY --from=terraform /bin/terraform /usr/bin/terraform
COPY --from=tflint /root/.tflint.d /root/.tflint.d
COPY --from=tflint /usr/local/bin/tflint /usr/bin/tflint
COPY --from=tfsec  /usr/bin/tfsec /usr/bin/tfsec
COPY --from=golang /usr/local/bin/goenv.sh /usr/local/bin/goenv.sh
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock

COPY terraform_switcher_checksums.txt terraform_switcher_checksums.txt

# Setting TF_PLUGIN_CACHE_DIR makes things a lot faster but this somehow
# causes weird permission issues.
# ENV TF_PLUGIN_CACHE_DIR=/root/.cache/terraform.d/plugin-cache

RUN \
    mkdir -vp ~/.cache ~/.local/bin ~/bin && \
    true

RUN --mount=type=secret,id=github_token \
    if [[ -e "/run/secrets/github_token" ]]; then GITHUB_AUTH="-u \"$(cat /run/secrets/github_token):x-oauth-basic\""; else GITHUB_AUTH=""; fi && \
    if [[ $tfswitcher_version == "" ]]; then TERRAFORM_SWITCHER_TAG="latest"; else TERRAFORM_SWITCHER_TAG="tags/tfswitcher_version"; fi && \
    ASSETS=$(curl -H "Accept: application/vnd.github.v3+json" "${GITHUB_AUTH}" "https://api.github.com/repos/warrensbox/terraform-switcher/releases/${TERRAFORM_SWITCHER_TAG}" | jq --raw-output ".assets[]") && \
    TERRAFORM_SWITCHER_FILE_NAME=$(echo "${ASSETS}" | jq --raw-output "select(.name | contains(\"linux_amd64\")) | .name") && \
    TERRAFORM_SWITCHER_URL=$(echo "${ASSETS}" | jq --raw-output "select(.name | contains(\"linux_amd64\")) | .browser_download_url") && \
    curl -LO "${TERRAFORM_SWITCHER_URL}" && \
    sed -i "/${TERRAFORM_SWITCHER_FILE_NAME}/!d" "terraform_switcher_checksums.txt" && \
    sha256sum -c "terraform_switcher_checksums.txt" && \
    tar -xvf "${TERRAFORM_SWITCHER_FILE_NAME}" -C /usr/local/bin tfswitch && \
    rm -rf "${TERRAFORM_SWITCHER_FILE_NAME}" "terraform_switcher_checksums.txt" && \
    # mkdir -vp ~/.cache/.terraform.versions && \
    # ln -s ~/.cache/.terraform.versions ~/.terraform.versions && \
    # for ver in ${terraform_versions}; \
    # do \
    #     tfswitch "${ver}"; \
    # done; \
    true


CMD ["validate"]
