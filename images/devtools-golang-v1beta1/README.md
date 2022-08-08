# Golang development tools

## Configuration

Interface variables are configurable with environment variables.

If any of the following files are found they will be loaded in the order they are
listed in before any variables are defined:
- `devtools-settings.mk`
- `devtools.env`
- `default.env`,
- `.env`
- `${ENVIRONMENT}.env`

If `devtools-targets.mk` is present then it will be loaded after all targets
are defined.

## Features

### OCI image building

- Variable `APP_NAME`: The name of the application.

  This will be used as the group and user name in the OCI image.

  e.g. `productinfosvc`.

- Variable `APP_EXECUTABLE`: The name of the main application executable.

  This will be used as the entrypoint of the OCI image.

  Default: The value of `APP_NAME`.

- Variable `APP_DOCKERFILE`: The dockerfile to use when building an OCI image.

  Default: `build/package/Dockerfile`.

- Variable `BUILD_OCI`: `true` or `false` indicating whether to build an
  OCI image.

  Default: This defaults to `true` if a `APP_DOCKERFILE` is exists and to
  `false` in other cases.

- Variable `OCI_REF_NAMES`: The space seperated OCI reference names that the
  OCI image should be published as.

  e.g.
  `OCI_REF_NAMES=europe-docker.pkg.dev/sandbox-i^Cn-aucamp-e332/common-docker/golang-devtools-prototype`
  will result in the image being published as
  `europe-docker.pkg.dev/sandbox-i^Cn-aucamp-e332/common-docker/golang-devtools-prototype:latest`
  and
  `europe-docker.pkg.dev/sandbox-i^Cn-aucamp-e332/common-docker/golang-devtools-prototype:gitc-${git_hash}`.

The `Dockerfile` must have a stage named runtime, and this is the stage that
will be pushed when running `publish`.

When pushing docker images credentials from `~/.docker/config.json` will be used,
and these can be set using commands like:

```bash
gcloud --verbosity debug auth print-access-token \
  | docker login -u oauth2accesstoken --password-stdin https://europe-docker.pkg.dev

printenv GITHUB_TOKEN \
  | docker login ghcr.io -u aucampia --password-stdin
```

**WARNING: SECURITY CONSIDERATION**: OCI building requires that the devtools
container run in priviliged mode. For this to be more secure of a rootless OCI
runtime (e.g. rootless dockerd) should be used.

