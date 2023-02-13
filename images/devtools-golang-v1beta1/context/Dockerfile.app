# https://docs.docker.com/engine/reference/builder/
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

FROM docker.io/redboxoss/scuttle:1.3.7@sha256:23939d3bff7616b47341c13bb3c644991c05253c95bb70b174a259817c2711dd AS scuttle
FROM docker.io/library/alpine:3@sha256:69665d02cb32192e52e07644d76bc6f25abeb5410edc1c7a81a10ba3f0efb90a AS alpine

FROM alpine AS runtime

# hadolint ignore=DL3018
RUN \
    apk --no-cache update &&\
    apk --no-cache add \
        tzdata \
    && \
    ln -vfs /usr/share/zoneinfo/UTC /etc/localtime && \
    true

COPY --from=scuttle /scuttle /usr/local/bin/scuttle

ARG app_name

RUN \
    1>&2 echo "The app_name build arg should be set" && \
    test -n "${app_name}"

ARG app_executable=${app_name}
ARG outputs_dir=var/outputs


ARG group_name=${app_name}
ARG user_name=${app_name}
ARG workdir=/var/opt/${app_name}

RUN \
    addgroup -S ${group_name} && \
    adduser -S -H -D -h ${workdir} -G ${group_name} ${user_name} && \
    mkdir -vp ${workdir} && \
    chown -R ${user_name}:${group_name} ${workdir} && \
    true

COPY --chown=root:root ${outputs_dir}/${app_executable} /usr/local/bin/${app_executable}

RUN \
    chmod ugo-w /usr/local/bin/${app_executable}

USER ${user_name}:${group_name}
WORKDIR ${workdir}

ENV __dba_app_executable=${app_executable}
ENV __dba_app_name=${app_name}

HEALTHCHECK CMD ["sh", "-c", "exec /usr/local/bin/${__dba_app_executable} healthcheck"]
ENTRYPOINT ["sh", "-c", "exec /usr/local/bin/${__dba_app_executable} \"${@}\"", "/usr/local/bin/${__dba_app_executable}"]
