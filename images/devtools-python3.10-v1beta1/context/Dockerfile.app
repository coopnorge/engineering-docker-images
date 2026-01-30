FROM docker.io/python:3.10-slim@sha256:f5d029fe39146b08200bcc73595795ac19b85997ad0e5001a02c7c32e8769efa AS python

FROM python AS runtime

ARG app_name

RUN \
    1>&2 echo "The app_name build arg should be set" && \
    test -n "${app_name}"

ARG wheels_dir=dist

COPY --chown=root:root ${wheels_dir}/*.whl /tmp
RUN \
    python -m pip install --no-cache-dir \
        /tmp/*.whl && \
    rm -rf /tmp && \
    pip show ${app_name}


ARG group_name=${app_name}
ARG user_name=${app_name}
ARG workdir=/var/opt/${app_name}

RUN \
    groupadd --system ${group_name} && \
    useradd --system --no-create-home --home-dir ${workdir} -G ${group_name} -g ${group_name} ${user_name} && \
    mkdir -vp ${workdir} && \
    chown -R ${user_name}:${group_name} ${workdir} && \
    true

USER ${user_name}:${group_name}
WORKDIR ${workdir}

RUN \
    printf '#!/bin/sh\n/usr/local/bin/%s $@' "${app_name}" > entrypoint.sh \
    && chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh"]
CMD [ "run"]
