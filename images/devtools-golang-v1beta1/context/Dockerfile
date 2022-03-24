FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.45-alpine@sha256:392ae6fa26b7184cbcbc669024a7f48e3b2b64eded4c4323e9db533b51904243 as golangci-lint

# golangci-lint does not work with go1.18
# https://github.com/golangci/golangci-lint/issues/2649
FROM golang:1.17-buster@sha256:e9f0ce41eac62541ecbd9b7115916617c96a070fe0cca8e494eff829b234b31b as base

# https://packages.debian.org/search?keywords=busybox&searchon=names&suite=buster&section=all
RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make=4.2.1-1.2 \
        socat=1.7.3.2-2 \
        curl=7.64.0-4+deb10u2 \
        ca-certificates=20200601~deb10u2 \
        busybox=1:1.30.1-4 \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true

COPY Makefile /usr/local/share/devtools-golang/Makefile
COPY maker /usr/local/bin/maker

COPY .golangci.yml /.golangci.yml

RUN \
    ln -s /usr/local/bin/maker /usr/local/bin/help && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-static && \
    ln -s /usr/local/bin/maker /usr/local/bin/test && \
    ln -s /usr/local/bin/maker /usr/local/bin/build && \
    true

VOLUME /srv/workspace
WORKDIR /srv/workspace

COPY --from=golangci-lint /usr/bin/golangci-lint /usr/bin/golangci-lint
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock

CMD ["validate", "build"]
