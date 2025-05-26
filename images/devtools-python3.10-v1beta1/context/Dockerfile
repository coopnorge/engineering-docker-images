FROM docker.io/library/python:3.10.13@sha256:d5b1fbbc00fd3b55620a9314222498bebf09c4bf606425bf464709ed6a79f202 AS python
FROM docker.io/hadolint/hadolint:2.12.0@sha256:30a8fd2e785ab6176eed53f74769e04f125afb2f74a6c52aef7d463583b6d45e AS hadolint
FROM --platform=linux/amd64 docker.io/goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9 AS dockle
FROM docker.io/moby/buildkit:v0.22.0-rootless@sha256:ef31818fffd0b9133d710742e06b492553f7ebc54f5fd66cd21a1a9bf2e51f76 AS buildkit
FROM gcr.io/go-containerregistry/crane:latest@sha256:13952b31a107e8bc4e4c170b0097edb708cd468486a28fc20bbf0d49f71c74e1 AS crane
FROM docker.io/mikefarah/yq:4@sha256:7cf28e5d67782f4b274a93a7bc54a840b553447a0807efd843d069f46bff718c AS yq

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
