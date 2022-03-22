FROM golangci/golangci-lint:v1.45-alpine@sha256:e2e0e2d5016a35e80cce1c78f294384e006f4dd9e36fe39f8792a22c5ebd58e5 as golangci-lint

# golangci-lint does not work with go1.18
# https://github.com/golangci/golangci-lint/issues/2649
FROM golang:1.17-buster@sha256:4a4f99be38fc652b55665f87115761e6fcbbdfd7fe60c1e48d11960682562edb as base

RUN \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends \
        make=4.2.1-1.2 \
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

CMD ["validate", "build"]
