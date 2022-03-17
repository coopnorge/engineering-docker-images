FROM golangci/golangci-lint:v1.44-alpine@sha256:e44ade2286749434ac58a90083b819ab19c4017c20a3d6ca2129fa669103f442 as golangci-lint

# golangci-lint does not work with go1.18
# https://github.com/golangci/golangci-lint/issues/2649
FROM golang:1.17-buster@sha256:645084f761154b6f9509f4f558993baceece127d9143371c3e6986cd0f777b59 as base

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

COPY .golangci.yml /usr/local/share/devtools-golang/.golangci.yml

RUN \
    ln -s /usr/local/bin/maker /usr/local/bin/validate && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-fix && \
    ln -s /usr/local/bin/maker /usr/local/bin/validate-static && \
    ln -s /usr/local/bin/maker /usr/local/bin/test && \
    true

VOLUME /srv/workspace
WORKDIR /srv/workspace

COPY --from=golangci-lint /usr/bin/golangci-lint /usr/bin/golangci-lint

CMD ["validate"]