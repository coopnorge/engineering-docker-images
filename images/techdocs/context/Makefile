# https://www.gnu.org/software/make/manual/make.html
SHELL := bash
.PHONY: default
default:

docker := docker
docker_compose := $(docker) compose
docker_compose_run := $(docker_compose) run --rm -T

BASE_BRANCH := origin/main
MARKDOWN_FILES := $(shell git diff --name-only --diff-filter=ACMRT $(BASE_BRANCH) | grep .md$$)

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

package-lock.json: package.json ## Generate requirements-techdocs.txt
	$(docker_compose_run) npm-tools npm install \
		--package-lock-only

########################################################################
# TechDocs targets
########################################################################

.PHONY: validate
validate: lint linguistics-check ## Validate the content

.PHONY: validate-fix
validate-fix: lint-fix ## Fix auto-fixable validation errors

../markdownlint.yaml:
	if [ -s .markdownlint.yaml ]; then \
	    yq '. *= load(".markdownlint.yaml")' /usr/local/share/techdocs/markdownlint.yaml > $@ ;\
	else \
	    cp /usr/local/share/techdocs/markdownlint.yaml $@ ;\
	fi

.PHONY: lint
lint: ../markdownlint.yaml ## Check markdown syntax
	markdownlint --config=../markdownlint.yaml $(MARKDOWN_FILES)

.PHONY: lint-fix
lint-fix: ../markdownlint.yaml ## Fix auto-fixable markdownlint failures
	markdownlint --fix --config=../markdownlint.yaml $(MARKDOWN_FILES)

.PHONY: linguistics-check
linguistics-check: ## Check spelling, grammar and other linguistics issues
	vale $(MARKDOWN_FILES)

SITE_NAME := $(shell  yq --no-doc '.metadata.title // .metadata.name' ./catalog-info.yaml)

.PHONY: mkdocs.yml
mkdocs.yml: /usr/local/share/techdocs/mkdocs.yml
	cp /usr/local/share/techdocs/mkdocs.yml mkdocs.yml

.PHONY: build
build: mkdocs.yml ## Build the website
	export SITE_NAME="$(SITE_NAME)" && export REPO_NAME=$(REPO_NAME) export REPO_URL=$(REPO_URL) && export EDIT_URI=$(EDIT_URI) && techdocs-cli generate --no-docker

ENTITY := $(shell yq --no-doc '[.metadata.namespace // "default", .kind, .metadata.name] | join("/")' ./catalog-info.yaml)

serve: mkdocs.yml ## Run a preview site
	export SITE_NAME="$(SITE_NAME)" && export REPO_NAME=$(REPO_NAME) export REPO_URL=$(REPO_URL) && export EDIT_URI=$(EDIT_URI) && techdocs-cli serve --no-docker

.PHONY: publish
publish: site ## Publish the website to the TechDocs Bucket
	techdocs-cli publish --publisher-type googleGcs --storage-name $(TECHDOCS_BUCKET) --entity $(ENTITY)
