FROM docker.io/library/python:3.10.4@sha256:edc8e6a550e4be7c340df18b252364554ea46a5ac14be4dcad711c285d25d1db

RUN \
    apt update -y

RUN curl -fsSL https://deb.nodesource.com/setup_17.x | bash -

RUN \
    apt-get install -y \
        aspell \
        nodejs \
        yarn \
        busybox \
        pandoc \
    && \
    true

ARG STAGING_DIR=/var/tmp/devtools-mkdocs-staging

RUN mkdir -vp ${STAGING_DIR}

COPY package-lock.json package.json ${STAGING_DIR}/

# RUN cd ${STAGING_DIR}/ && npm install -g .

# COPY requirements.base.txt ${STAGING_DIR}/

# RUN pip install -r ${STAGING_DIR}/requirements.base.txt

# COPY requirements.extra.txt ${STAGING_DIR}/

# RUN pip install -r ${STAGING_DIR}/requirements.extra.txt

# COPY requirements.mkdocs.txt ${STAGING_DIR}/

# RUN pip install -r ${STAGING_DIR}/requirements.mkdocs.txt

# COPY actual.mk /usr/local/share/devtools-mkdocs/Makefile
# COPY maker /usr/local/bin/maker
# RUN \
#     ln -rs /usr/local/bin/maker /usr/local/bin/help && \
#     ln -rs /usr/local/bin/maker /usr/local/bin/validate && \
#     ln -rs /usr/local/bin/maker /usr/local/bin/validate-fix && \
#     ln -rs /usr/local/bin/maker /usr/local/bin/build && \
#     true

# CMD ["validate", "build"]
