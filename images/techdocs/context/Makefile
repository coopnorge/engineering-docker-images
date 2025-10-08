# https://www.gnu.org/software/make/manual/make.html
SHELL := bash
.PHONY: default
default:

docker := docker
docker_compose := $(docker) compose
docker_compose_run := $(docker_compose) run --rm -T

CURRENT_DIR := $(shell pwd)

BASE_BRANCH := origin/main
MARKDOWN_FILES ?= $(shell git diff --name-only --diff-filter=ACMRT $(BASE_BRANCH) | grep .md$$)

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

########################################################################
# Image dependencies management targets
########################################################################

requirements-%.txt: requirements-%.in
	$(docker_compose_run) pip-tools pip-compile \
		--verbose \
		--annotate \
		--generate-hashes \
		--rebuild \
		--resolver backtracking \
		--output-file $(@) \
		$(<)
requirements-pip-tools.txt: ## Generate requirements-pip-tools.txt
requirements-techdocs.txt: ## Generate requirements-techdocs.txt

update-python-packages-pip-tools: requirements-pip-tools.in
	$(docker_compose_run) pip-tools pip-compile \
		--upgrade \
		--verbose \
		--annotate \
		--generate-hashes \
		--rebuild \
		--resolver backtracking \
		--output-file requirements-pip-tools.txt \
		$(<)

.PHONY: update-python-packages-techdocs
update-python-packages-techdocs: requirements-techdocs.in
	$(docker_compose_run) pip-tools pip-compile \
		--upgrade \
		--verbose \
		--annotate \
		--generate-hashes \
		--rebuild \
		--resolver backtracking \
		--output-file requirements-techdocs.txt \
		$(<)

package-lock.json: package.json ## Generate requirements-techdocs.txt
	$(docker_compose_run) npm-tools npm install \
		--package-lock-only

########################################################################
# TechDocs targets
########################################################################

.PHONY: validate
validate: lint linguistics-check ## Validate the content

.PHONY: validate-pwd
validate-pwd:
	@if [[ $(CURRENT_DIR) = /srv/workspace ]] || [[ $(CURRENT_DIR) = /srv/workspace/* ]]; then \
	    echo "Info: Workspace OK" 1>&2 ; \
	else \
	    echo "Error: Update docker compose working directory and volume to /srv/workspace" 1>&2 ; \
	    exit 1; \
	fi

.PHONY: validate-fix
validate-fix: lint-fix ## Fix auto-fixable validation errors

../markdownlint.yaml:
	if [ -s .markdownlint.yaml ]; then \
	    yq '. *= load(".markdownlint.yaml")' /usr/local/share/techdocs/markdownlint.yaml > $@ ;\
	else \
	    cp /usr/local/share/techdocs/markdownlint.yaml $@ ;\
	fi

.PHONY: lint
lint: validate-pwd ../markdownlint.yaml ## Check markdown syntax
	markdownlint --config=../markdownlint.yaml $(MARKDOWN_FILES)

.PHONY: lint-fix
lint-fix: ../markdownlint.yaml ## Fix auto-fixable markdownlint failures
	markdownlint --fix --config=../markdownlint.yaml $(MARKDOWN_FILES)

.PHONY: vale-sync
vale-sync:
	vale sync

.PHONY: linguistics-check
linguistics-check: validate-pwd vale-sync ## Check spelling, grammar and other linguistics issues
	vale $(MARKDOWN_FILES)

../.prettierrc:
	if [ -s ..prettierrc ]; then \
	    yq '. *= load("..prettierrc")' /usr/local/share/techdocs/.prettierrc > $@ ;\
	else \
	    cp /usr/local/share/techdocs/.prettierrc $@ ;\
	fi

.PHONY: format-check
format-check: validate-pwd ../.prettierrc ## Check markdown formatting
	prettier --check --config ../.prettierrc $(MARKDOWN_FILES)

.PHONY: format-fix
format-fix: ../.prettierrc ## Fix auto-fixable markdown formatting issues
	prettier --write --config ../.prettierrc $(MARKDOWN_FILES)

SITE_NAME := $(shell yq --no-doc 'select(document_index == 0) | .metadata.title // .metadata.name' ./catalog-info.yaml)
REPO_NAME := $(shell yq --no-doc 'select(document_index == 0) | .metadata.annotations."github.com/project-slug"' ./catalog-info.yaml)
ENTITY := $(shell yq --no-doc 'select(document_index == 0) | [.metadata.namespace // "default", .kind, .metadata.name] | join("/")' ./catalog-info.yaml)
FETCH_CONTRIBUTORS := false

.PHONY: mkdocs.yml
mkdocs.yml: /usr/local/share/techdocs/mkdocs.yml
	cp /usr/local/share/techdocs/mkdocs.yml mkdocs.yml

.PHONY: build
build: mkdocs.yml ## Build the website
	export SITE_NAME="$(SITE_NAME)" && export REPO_NAME=$(REPO_NAME) && export REPO_URL=$(REPO_URL) && export EDIT_URI=$(EDIT_URI) && export FETCH_CONTRIBUTORS=$(FETCH_CONTRIBUTORS) && export GITHUB_TOKEN=$(GITHUB_TOKEN) && techdocs-cli generate --no-docker --verbose

serve: mkdocs.yml ## Run a preview site
	export SITE_NAME="$(SITE_NAME)" && export REPO_NAME=$(REPO_NAME) && export REPO_URL=$(REPO_URL) && export EDIT_URI=$(EDIT_URI) && export FETCH_CONTRIBUTORS=$(FETCH_CONTRIBUTORS) && techdocs-cli serve --no-docker --verbose

.PHONY: publish
publish: site ## Publish the website to the TechDocs Bucket
	techdocs-cli publish --publisher-type googleGcs --storage-name $(TECHDOCS_BUCKET) --entity $(ENTITY)
