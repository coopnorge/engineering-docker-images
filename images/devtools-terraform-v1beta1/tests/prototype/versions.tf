# https://www.terraform.io/docs/language/settings/index.html
# https://www.terraform.io/docs/language/expressions/version-constraints.html
terraform {
  required_providers {
    null = {
      source = "hashicorp/null"
    }
  }
  required_version = "~> 1.0"
}
