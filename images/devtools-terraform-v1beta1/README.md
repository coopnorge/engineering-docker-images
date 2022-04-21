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
