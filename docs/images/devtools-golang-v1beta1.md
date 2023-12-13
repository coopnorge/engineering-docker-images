# Golang development tools

## Usage

```console
docker-compose run --rm golang-devtools help
```

### Prerequisites

#### Local Go configuration

To allow the container to access private go modules over SSH your Git
configuration must be compatible.

1. Generate an RSA key pair and upload the public key to
   [GitHub](https://github.com/settings/keys).

   ```console
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

   Make sure to not set a passphrase, and to `Configure SSO` to Authorize the

2. Configure git to access the repositories over SSH instead of HTTPS

   ```console title="Example"
   git config --global url."git@github.com:example/".insteadOf "https://github.com/example/"
   ```

   ```console title="Coop specific"
   git config --global url."git@github.com:coopnorge/".insteadOf "https://github.com/coopnorge/"
   ```  key for use with coopnorge after you have added it to GitHub.

### Configuration

Interface variables are configurable with environment variables.

If any of the following files are found they will be loaded in the order they
are listed in before any variables are defined:

- `devtools-settings.mk`
- `devtools.env`
- `default.env`,
- `.env`
- `${ENVIRONMENT}.env`

If `devtools-targets.mk` is present then it will be loaded after all targets are
defined.

```Dockerfile title="docker-compose/Dockerfile"
FROM ghcr.io/coopnorge/engineering-docker-images/e0/devtools-golang-v1beta1:latest@sha256:7e54fe41351af1b7b4cdf75c2cb8251f80b89845b49179ae2003b200b3054369 AS golang-devtools
```

```yaml title="docker-compose.yml"
services:
  golang-devtools:
    build:
      context: docker-compose
      target: golang-devtools
      dockerfile: Dockerfile
    privileged: true
    security_opt:
      - seccomp:unconfined
      - apparmor:unconfined
    volumes:
      - .:/srv/workspace:z
      - ${DOCKER_CONFIG:-~/.docker}:/root/.docker
      - ${GIT_CONFIG:-~/.gitconfig}:${GIT_CONFIG_GUEST:-/root/.gitconfig}
      - ${SSH_CONFIG:-~/.ssh}:/root/.ssh
      - ${XDG_CACHE_HOME:-xdg-cache-home}:/root/.cache
    environment:
      SERVICE_PORT: ":50051"
      SHUTDOWN_TIMEOUT: 5s
      GOMODCACHE: /root/.cache/go-mod
    ports:
      - "50051:50051"
    networks:
      - default
    working_dir: /srv/workspace
    command: "golang-run"
networks:
  default:
volumes:
    xdg-cache-home: {}
```

## Features

### OCI image building

!!! warning "Security Consideration"
    OCI building requires that the devtools container run in privileged mode.
    For this to be more secure of a rootless OCI runtime
    (e.g. rootless dockerd) should be used.

This devtool provides a simple Dockerfile which should cover typical service use
cases. To use it set the `APP_DOCKERFILE` variable to
`/usr/local/share/devtools-golang/Dockerfile.app`. Complex use cases can
otherwise supply their own Dockerfile.

A `Dockerfile` supplied by `APP_DOCKERFILE` must have a stage named `runtime`,
and this is the stage that will be pushed when running the `publish` make
target.

It is possible to supplement the devtool-supplied Dockerfile by appending
additional commands. This is particularly useful when only a small set of
customisations are required. To do this:

- Provide a Dockerfile with the additional commands, and set its path in
  `APP_DOCKERFILE`.
- Set `APPEND_APP_DOCKERFILE=true`

In the above case the provided Dockerfile will be concatenated to the
devtool-supplied one. As such it is not necessary to begin the Dockerfile with a
`FROM` statement.

Example Dockerfile.app when extending the devtool-supplied one:

```Dockerfile
# APPEND_APP_DOCKERFILE has been set. The following commands are appended to
# the devtools app Docker image.

COPY --chown=root:root app-resources /usr/local/your-app/resources
```

When pushing docker images credentials from `~/.docker/config.json` will be
used, and these can be set using commands like:

```bash
gcloud --verbosity debug auth print-access-token \
  | docker login -u oauth2accesstoken --password-stdin https://europe-docker.pkg.dev

printenv GITHUB_TOKEN \
  | docker login ghcr.io -u aucampia --password-stdin
```

#### Variables

- `APP_NAME`: The name of the application.

  This will be used as the group and user name in the OCI image.

  e.g. `productinfosvc`.

- `APP_EXECUTABLE`: The name of the main application executable.

  This will be used as the entrypoint of the OCI image.

  Default: The value of `APP_NAME`.

- `APP_DOCKERFILE`: The dockerfile to use when building an OCI image.

  Default: `build/package/Dockerfile`.

- `BUILD_OCI`: `true` or `false` indicating whether to build an OCI image.

  Default: This defaults to `true` if a user supplied `APP_DOCKERFILE` exists
  and to `false` in other cases.

- `OCI_REF_NAMES`: The space seperated OCI reference names that the OCI image
  should be published as.

  e.g.
  `OCI_REF_NAMES=europe-docker.pkg.dev/sandbox-i^Cn-aucamp-e332/common-docker/golang-devtools-prototype`
  will result in the image being published as
  `europe-docker.pkg.dev/sandbox-i^Cn-aucamp-e332/common-docker/golang-devtools-prototype:latest`
  and
  `europe-docker.pkg.dev/sandbox-i^Cn-aucamp-e332/common-docker/golang-devtools-prototype:gitc-${git_hash}`.

- `DELVE_PORT`: The port the Delve server should listen to.

  Default: `4000`.
