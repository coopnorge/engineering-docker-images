# https://docs.docker.com/engine/reference/builder/
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

FROM docker.io/kvij/scuttle:1.1.15@sha256:1b3fb35aa13dd80b30ecceee9f913156eace6cf7656129a99a2dfad5010f68a4 AS scuttle
FROM docker.io/library/alpine:3@sha256:5b10f432ef3da1b8d4c7eb6c487f2f5a8f096bc91145e68878dd4a5019afde11 AS alpine

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
