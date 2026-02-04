# syntax=docker/dockerfile:1.21
FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM ghcr.io/terraform-linters/tflint:v0.60.0@sha256:cef181224b4a9cea521d8f785d50957ea3215b449e2d97e7793f222e2808d188 AS tflint
FROM docker.io/aquasec/trivy:0.69.0@sha256:33f816d414b9d582d25bb737ffa4a632ae34e222f7ec1b50252cef0ce2266006 AS trivy
FROM docker.io/hashicorp/terraform:1.14.4@sha256:5dbdc45b411f4dd56c5b576b0ded0554859796fee2eaee9edd58dddddeac1acb AS terraform
FROM quay.io/terraform-docs/terraform-docs:0.20.0@sha256:37329e2dc2518e7f719a986a3954b10771c3fe000f50f83fd4d98d489df2eae2 AS tfdocs
FROM docker.io/library/golang:1.25.6@sha256:06d1251c59a75761ce4ebc8b299030576233d7437c886a68b43464bad62d4bb1 AS golang

RUN \
    go env > /usr/local/bin/goenv.sh && \
    true

FROM docker.io/library/ubuntu:24.04@sha256:cd1dba651b3080c3686ecf4e3c4220f026b521fb76978881737d24f200828b2b AS base


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
COPY .tflint.hcl /root/.tflint.hcl
COPY --from=tflint /usr/local/bin/tflint /usr/bin/tflint
COPY --from=trivy  /usr/local/bin/trivy /usr/local/bin/trivy
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

ENV ORAS_VERSION=1.3.0
RUN \
    cd /var/tmp && \
    . /usr/local/bin/goenv.sh && \
    curl -LOJ "https://github.com/oras-project/oras/releases/download/v${ORAS_VERSION}/oras_${ORAS_VERSION}_${GOOS}_${GOARCH}.tar.gz" && \
    tar -xvf "oras_${ORAS_VERSION}_${GOOS}_${GOARCH}.tar.gz" -C /usr/local/bin oras

ENV TF_PLUGIN_CACHE_DIR=/root/.cache/terraform.d/plugin-cache
ENV TRIVY_CHECKS_DB=ghcr.io/aquasecurity/trivy-checks:1
ENV TRIVY_CACHE_DIR=/root/.cache/trvy


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

# Include the current version of trivy checks db in the image
SHELL ["/bin/bash", "-exo", "pipefail", "-c"]
RUN DIGEST=$(oras pull $TRIVY_CHECKS_DB | grep Digest | cut -d' ' -f2) && \
    mv bundle.tar.gz /var/trivy-checks-db.tar.gz && \
    DOWNLOADED_AT=$(date +"%Y-%m-%dT%H:%M:%S.%6N%:z") && \
    echo "{\"Digest\":\"$DIGEST\",\"DownloadedAt\":\"$DOWNLOADED_AT\"}" > /var/trivy-checks-metadata.json

RUN tflint --init

CMD ["validate"]
