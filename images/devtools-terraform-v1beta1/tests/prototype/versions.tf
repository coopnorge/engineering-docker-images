# https://www.terraform.io/docs/language/settings/index.html
# https://www.terraform.io/docs/language/expressions/version-constraints.html
terraform {
  required_providers {
    null = {
      source = "hashicorp/null"
      # version = "~> 3.1.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.4"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.4"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.90"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.13"
    }
    github = {
      source  = "integrations/github"
      version = "~> 4.19"
    }
  }
  required_version = "~> 1.0"
}
