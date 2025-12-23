# https://docs.docker.com/engine/reference/builder/
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

FROM docker.io/kvij/scuttle:1.1.12@sha256:a74554fa3a918c86e1ac1a0e992c5c7e764d3e60055bc859457592158702b91b AS scuttle
FROM docker.io/library/alpine:3@sha256:865b95f46d98cf867a156fe4a135ad3fe50d2056aa3f25ed31662dff6da4eb62 AS alpine

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

# The following line will be replaced by COPY statements for resource paths if any are provided in $APP_RESOURCE_PATHS
# @app_resource_commands

RUN \
    chmod ugo-w /usr/local/bin/${app_executable}

USER ${user_name}:${group_name}
WORKDIR ${workdir}

ENV __dba_app_executable=${app_executable}
ENV __dba_app_name=${app_name}

# Setup Datadog and APM commit tracking
# https://app.datadoghq.eu/source-code/setup/apm
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA

ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

HEALTHCHECK CMD ["sh", "-c", "exec /usr/local/bin/${__dba_app_executable} healthcheck"]
ENTRYPOINT ["sh", "-c", "exec /usr/local/bin/${__dba_app_executable} \"${@}\"", "/usr/local/bin/${__dba_app_executable}"]
