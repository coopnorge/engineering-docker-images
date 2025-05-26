# https://docs.docker.com/engine/reference/builder/
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

FROM docker.io/kvij/scuttle:1.1.11@sha256:cc34a43fbc9c652ebf693cfdefaff3d425c631a944dfbbc2a7f8d9437bc73a21 AS scuttle
FROM docker.io/library/alpine:3@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c AS alpine

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
