FROM docker.io/library/python:3.10.20@sha256:a5ef46a93e429aa07466f536c25962f3c157c0db77f5b9691d1a04a832cd62f4 AS python
FROM docker.io/hadolint/hadolint:v2.14.0@sha256:27086352fd5e1907ea2b934eb1023f217c5ae087992eb59fde121dce9c9ff21e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9 AS dockle
FROM docker.io/moby/buildkit:v0.28.1-rootless@sha256:4004494c888b51a51118b68e49662472d48e132ef7b03806d65b04c2eb44774e AS buildkit
FROM gcr.io/go-containerregistry/crane:latest@sha256:cf88890f8a6b21183cd6628ad1e83051494e9d5094b8412115f798f4ddf35437 AS crane
FROM docker.io/mikefarah/yq:4@sha256:603ebff15eb308a05f1c5b8b7613179cad859aed3ec9fdd04f2ef5d32345950e AS yq

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
