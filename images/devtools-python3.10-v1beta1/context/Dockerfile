FROM docker.io/library/python:3.10.20@sha256:e944b33fd76c802eeb5709737fdd3156277ea20904b0422d7361a16018c2a4c4 AS python
FROM docker.io/hadolint/hadolint:v2.14.0@sha256:27086352fd5e1907ea2b934eb1023f217c5ae087992eb59fde121dce9c9ff21e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9 AS dockle
FROM docker.io/moby/buildkit:v0.30.0-rootless@sha256:d76eb1caecac5733ef7553c1e90a1b21f1bb218cd1142d3553de0747b4a14ba9 AS buildkit
FROM gcr.io/go-containerregistry/crane:latest@sha256:0ae17ecb34315aa7cbff28f6eddee3b7adae0b2f90101260d990804db1eb0084 AS crane
FROM docker.io/mikefarah/yq:4@sha256:11a1f0b604b13dbbdc662260d8db6f644b22d8553122a25c1b5b2e8713ca6977 AS yq

FROM python AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /srv/workspace

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/srv/workspace" \
    VENV_PATH="/srv/workspace/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY --from=hadolint /bin/hadolint /usr/local/bin/hadolint
COPY --from=dockle /usr/bin/dockle /usr/local/bin/dockle
COPY --from=buildkit /usr/bin/buildkit* /usr/bin/buildctl* /usr/bin/rootlesskit /usr/local/bin/
COPY --from=crane /ko-app/crane /usr/local/bin/
COPY --from=yq /usr/bin/yq /usr/local/bin/yq

COPY requirements.txt requirements.txt
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install \
        --no-cache-dir \
        --require-hashes  \
        --verbose \
        --use-pep517 \
        --requirement requirements.txt && \
    rm -rf requirements.txt

COPY .flake8 /usr/local/share/devtools-python3.10-v1beta1/
COPY mypy.ini /usr/local/share/devtools-python3.10-v1beta1/

COPY maker /usr/local/bin/maker

COPY Makefile /usr/local/share/devtools-python3.10-v1beta1/
COPY Dockerfile.app /usr/local/share/devtools-python3.10-v1beta1/

RUN \
    set -x; \
    targets=( \
        help \
        poetry-install \
        validate validate-static validate-fix \
        test test-verbose \
        build publish clean \
        oci-build oci-validate oci-push \
    ); \
    for target in "${targets[@]}"; \
    do \
        ln -s /usr/local/bin/maker "/usr/local/bin/${target}"; \
    done && \
    true

RUN git config --system --add safe.directory /srv/workspace

VOLUME /srv/workspace
WORKDIR /srv/workspace

CMD ["validate"]
