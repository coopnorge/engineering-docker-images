# https://www.terraform.io/docs/language/values/variables.html

variable "secret" {
  type        = string
  sensitive   = true
  description = "A secret value"
}
