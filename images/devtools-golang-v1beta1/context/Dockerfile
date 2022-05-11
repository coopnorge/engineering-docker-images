FROM docker.io/safewaters/docker-lock:latest@sha256:432d90ddc2891f4845241adc63e5eef2dd1486fa14ea7882433cbd3f8ed64622 AS docker-lock
FROM golangci/golangci-lint:v1.46.0-alpine@sha256:a9be740033fde5c19fdb2e9be5ae72b3d5742647606d29bb1c9f6bbcad075646 as golangci-lint

# golangci-lint does not work with go1.18
# https://github.com/golangci/golangci-lint/issues/2649
FROM golang:1.18.2-buster@sha256:b251cba61cd79c89286eaf4610e0b5b200596a5b016dc90e1ba5103e855fd391 as base

# https://packages.debian.org/search?keywords=busybox&searchon=names&suite=buster&section=all
RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make \
        socat \
        curl \
        ca-certificates \
        busybox \
        && \
    rm -vr /var/lib/apt/lists/* && \
    true


COPY .golangci.yml /.golangci.yml



VOLUME /srv/workspace
WORKDIR /srv/workspace

COPY --from=golangci-lint /usr/bin/golangci-lint /usr/bin/golangci-lint
COPY --from=docker-lock /prod/docker-lock /usr/local/bin/docker-lock

COPY Makefile /usr/local/share/devtools-golang/Makefile
COPY maker /usr/local/bin/maker

RUN \
    ln -s /usr/local/bin/maker /usr/local/bin/help && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-static && \
    ln -s /usr/local/bin/maker /usr/local/bin/test && \
    ln -s /usr/local/bin/maker /usr/local/bin/build && \
    true

CMD ["validate", "build"]
