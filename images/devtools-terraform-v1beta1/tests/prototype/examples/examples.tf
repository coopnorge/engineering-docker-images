module "test_github_repo" {
  count = var.environment == "production" ? 1 : 0

  source  = "terraform.coop.no/coopnorge/repos/github"
  version = "..."

  name = "repo-name"

  teams = {
    "team-a" = {
      permission = "push"
    }
    "team-b" = {
      permission = "maintain"
    }
  }
}
