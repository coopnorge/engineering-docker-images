# Terraform Development Tools

- `terraform-reinit` target: This target will run `terraform init` in each
  Terraform directory.

- `terraform-upgrade` target: This target will run `terraform init -upgrade` in
  each Terraform directory followed by `terraform providers lock`.

- `terraform-relock` target: This target will remove the existing Terraform
  lock file and then run `terraform providers lock` in each Terraform
  directory.

- `.tfsec-ignore` file: If this file is present in a directory with Terraform
    files then tfsec will not be used on the directory.

- `TFDIRS` environment variable: This is a space-separated list of directories
  for which Terraform validation will be run.

  Default: If this is not set it is auto-detected.

- `TFDIRS_EXCLUDE` environment variable: This is a space-separated list of GNU
  make string pattens (which use `%` as wildcard) to exclude directories from
  Terraform validation.

  Default: `%/examples %/example`

- `TF_LOCK_PLATFORMS` environment variable: A space-sperarated list of
  platforms that `terraform providers lock` should use.

  Default: `linux_arm64 linux_amd64 darwin_amd64 darwin_arm64 windows_amd64`.

## Updating tfswitch version

To update tfswitch to the latest version run:

```concole
images/devtools-terraform-v1beta1/context/update_tfswitch.py
```

This will download the checksums for the latest version of `terraform-switcher`
and then replace the version of `terraform-switcher` in the Dockerfile with the
latest version number.
