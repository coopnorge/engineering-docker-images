# Allowing extending validation using project Makefile

- Status: draft
- Decider:
  - Arun Poudel <arun.poudel@coop.no>
- Data 2023-12-05

## Context and Problem Statement

Some projects want more validation than what is provided by the default
by devtools image.

For example: a project using `dbt` would want to run `dbt test` as part of
the validation process.

The current implementation limits us to only run validations defined in
specific devtool's Makefile.

## Decision Drivers

- We want to allow projects to define their own validation steps in addition
  to the ones provided by the devtools image.

## Considered Options

- Allow projects to define their own validation steps in their Makefile.
- Embed those validations in devtools itself.

## Decision Outcome

Chosen option: "Allow projects to define their own validation steps in their
Makefile", because:

- It is easier to maintain and extend.
- It is easier to understand.
- It allows projects to define their own validation steps without having to
make upstream contributions to devtools which might not be relevant to other
projects.

The way this works is, validate first runs the validations defined in the
devtools, and after that if Makefile exists in the project root, it runs
the `validate` target defined in the Makefile. If the target returns an error
(exit code != 0, this might happen when the target is missing as well), the validation fails.
