# Terraform Development Tools

- `.tfsec-ignore` file: If this file is present in a directory with terraform
  then tfsec will not be used on the directory.

- `TFDIRS` environment variable: This is a space separated list of directories
  for which terraform validation will be run.

  Default: If this is not set it is auto-detected.

- `TFDIRS_EXCLUDE` environment variable: This is a space separated list of GNU
  make string pattens (which use `%` as wildcard) to exclude directories from
  terraform validation.

  Default: `%/examples %/example`

## Updating terraform-switcher checksums file

In order to update terraform-switcher checksum file you can use
`update-terraform-switcher-checksums` target.

- Update to the latest available version in GitHub
  ```shell
  make update-terraform-switcher-checksums
  ```

- Update to the specific version
  ```shell
  make update-terraform-switcher-checksums terraform_switcher_version=<version>
  ```

Target will try to use GitHub CLI if you have it installed. Otherwise, target
will use GitHub API. If you want to make authenticated requests please specify
parameter `github_oauth_token`. The token needs to have `public_repo` scope
(access to public repositories).
