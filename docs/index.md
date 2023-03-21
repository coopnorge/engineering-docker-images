# Engineering Docker Images

## Images

### devtools

devtools images are intended for use in git repos to do validation and artifact building.

#### Security Considerations for devtools

!!! warning
    The devtools images should only be used with rootless docker or similar
    technologies.

devtools images are designed to be used with [rootless
docker](https://docs.docker.com/engine/security/rootless/), as they have to be
able to modify files on filesystem as the user that invokes them. One example
of this is when they have to enforce fixing validation errors (i.e.
`validation-fix` target), but this is also the case when they have to maintain
state across invocations like inside `.terraform`.

With rootless docker, all files of the user that runs the image is seen to the
container as root, and the root user in the docker container translates to the
invoking user. It is possible to assign non root ownership to files mounted
into the container but these permissions are not persisted as there is no place
for this permission to be persisted to, and the next time the same files are
mounted into a container they will again just have root permission.

To accomodate this situation default user of the containers is root, and using
them with a different user than root will likely only work in very select and
limited situations where they don't have to modify anything on disk. If these
containers run with rootless docker this  does not present the same security
risks as those presented by using the root user with docker daemon running as
root, as there is no potential for privilige escalation beyond the priviliges
of the invoking user, which is the exact privliges which the process in the
docker container should have anyway in order to operate as intended. This being
said, care should be taken to not use these images with a docker daemon that is
running as root.
