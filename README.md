# engineering-docker-images

## Layout

Dockerfiles for images are all located in the `images/` directory. Each image
has a subdirectory from which it's name will be derived.

## Registries

Docker images are published to the following registries:

- `ghcr.io/coopnorge/engineering-docker-images/e0/${image_name}:latest`

  This is mainly for easy usage from github, once it is easier to setup workload identity we can remove this.


- `europe-north1-docker.pkg.dev/engineering-production-af50/images/${image_name}:latest`

  This is org readable for coop.no.

## Images

### Devtools

Devtools images are intended for use in git repos to do validation and artifact building.

- `devtools-golang-v1beta1`: Development tools for golang.

  [Usage example](./images/devtools-golang-v1beta1/tests/prototype/).

- `devtools-terraform-v1beta1`: Development tools for terraform.

  [README](./images/devtools-terraform-v1beta1/README.md).

  [Usage example](./images/devtools-terraform-v1beta1/tests/prototype/).

- `devtools-kubernetes-v1beta1`: Development tools for kubernetes.

  [README](./images/devtools-kubernetes-v1beta1/README.md).

  [Usage example](./images/devtools-kubernetes-v1beta1/tests/prototype/).

#### Security Considerations for devtools

**WARNING**: The devtools images should only be used with rootless docker or
similar technologies.

Devtools images are designed to be used with [rootless
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

## Developing

### Image Tests

To tests images, the run file inside the image's test directory will be
executed, for example, to test the `devtools-golang-v1beta1` image, the
`images/devtools-golang-v1beta1/tests/run` file will be executed. This file can
run any test framework.

### Using devtools

```bash
# build images
docker-compose build
# see available targets
docker-compose run --rm devtools make help
# validate
docker-compose run --rm devtools make validate VERBOSE=all
# run in watch mode
docker-compose run --rm devtools make watch
```

### without devtools

```bash
poetry install
make build validate test
```

### Useful commands

```bash
# run tests for only one image
make IMAGE_NAMES=devtools-terraform-v1beta1 build validate test
```
