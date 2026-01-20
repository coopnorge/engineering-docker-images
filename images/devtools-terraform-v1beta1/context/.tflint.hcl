plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "azurerm" {
    enabled = true
    version = "0.30.0"
    source  = "github.com/terraform-linters/tflint-ruleset-azurerm"
}

plugin "google" {
    enabled = true
    version = "0.38.0"
    source  = "github.com/terraform-linters/tflint-ruleset-google"
}

rule "terraform_unused_declarations" {
  enabled = false
}

rule "azurerm_resources_missing_prevent_destroy" {
    enabled = false
}
