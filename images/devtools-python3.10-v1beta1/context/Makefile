# https://www.gnu.org/software/make/manual/make.html
# Configure the shell.
SHELL=bash
.SHELLFLAGS=-ec -o pipefail
PYTHON_BIN?=python
py_source?=./src ./tests
tests_source?=./tests

# Load settings.
$(if $(wildcard devtools-settings.mk),$(info loading devtools-settings.mk)$(eval include devtools-settings.mk),)
$(if $(wildcard devtools.env),$(info loading devtools.env)$(eval include devtools.env),)
$(if $(wildcard default.env),$(info loading default.env)$(eval include default.env),)
$(if $(wildcard .env),$(info loading .env)$(eval include .env),)
$(if $(and $(ENVIRONMENT),$(wildcard env.$(ENVIRONMENT))),$(info loading env.$(ENVIRONMENT))$(eval include env.$(ENVIRONMENT)),)

ifneq ($(filter all vars,$(VERBOSE)),)
dump_var=$(info var $(1)=$($(1)))
dump_vars=$(foreach var,$(1),$(call dump_var,$(var)))
else
dump_var=
dump_vars=
endif

# Capture the current makefile.
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

venv_dir=.venv
localstatedir?=var
outputs_dir?=$(localstatedir)/outputs

poetry=$(PYTHON_BIN) -m poetry

PYTHON_PROJECT_PATH?=.
APP_DOCKERFILE?=build/package/Dockerfile
BUILD_OCI?=$(if $(wildcard $(APP_DOCKERFILE)),true,false)
OCI_METADATA?=oci-metadata.json
XDG_CACHE_HOME?=$(localstatedir)/.cache

giti_commit_hash=$(shell git log -1 --format="%H")

define __newline


endef

skip=
# skipable makes the targets passed to it skipable with skip=foo%
# $(1): targets that should be skipable
skipable=$(filter-out $(skip),$(1))

# checks if $(1) and $(2) is equal
seq = $(if $(subst x$(1)x,,x$(2)x)$(subst x$(2)x,,x$(1)x),,T)
# parse true|false to a make boolean
parse_bool = $(if $(call seq,$(1),true),T,$(if $(call seq,$(1),false),,$(error invalid boolean value $(1))))
# merge the list items in $2 with the seperator $1
merge = $(strip $(if $2, $(if $(filter 1,$(words $2)),$2,$(firstword $2)$1$(call merge,$1,$(wordlist 2,$(words $2),$2)))))
comma:=,

.PHONY: default
default:

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: generate-requirements
generate-requirements: ## prepare requirements.txt
generate-requirements: requirements.txt

requirements.txt: requirements.in
	pip-compile \
		--allow-unsafe \
		--annotate \
		--generate-hashes \
		--output-file requirements.txt \
		--rebuild \
		--resolver backtracking \
		--verbose \
		requirements.in

.PHONY: configure
configure: poetry-install ## configure the project
	@if [ ! -f ".flake8" ]; then \
		cp /usr/local/share/devtools-python3.10-v1beta1/.flake8 .; \
	fi
	@if [ ! -f "mypy.ini" ]; then \
		cp /usr/local/share/devtools-python3.10-v1beta1/mypy.ini .; \
	fi

.PHONY: poetry-install
poetry-install: ## installs the project dependencies
	$(poetry) install

.PHONY: validate
validate: validate-static test

.PHONY: validate-static
validate-static: configure ## perform static validation
	$(poetry) run mypy --show-error-codes --show-error-context \
		$(py_source)
	$(poetry) run codespell $(py_source)
	$(poetry) run isort --check $(py_source)
	$(poetry) run black --check $(py_source)
	$(poetry) run flake8 $(py_source)
	$(poetry) export --without-hashes --dev --format requirements.txt

.PHONY: validate-fix
validate-fix: configure ## fix auto-fixable validation errors
	$(poetry) run pycln --expand-stars --all $(py_source)
	$(poetry) run isort $(py_source)
	$(poetry) run black $(py_source)

.PHONY: test
test: configure ## run the project's tests
	@if [ -d "$(tests_source)" ]; then \
		$(poetry) run pytest --cov-config=pyproject.toml --cov-report term --cov-report xml --cov=src $(tests_source); \
	else \
		echo "no tests found in $(tests_source), skipping tests"; \
	fi

.PHONY: test-verbose
test-verbose: configure ## run the project's tests with verbose output
	@if [ -d "$(tests_source)" ]; then \
		$(poetry) run pytest -rA --log-level DEBUG --cov-config=pyproject.toml --cov-report term --cov-report xml --cov=src $(tests_source) \
	else \
		echo "no tests found in $(tests_source), skipping tests"; \
	fi

.PHONY: build
build: ## Build the source.

########################################################################
# OCI
########################################################################

oci_rebuild=false
oci_context_dir?=.
oci_images_dir=$(localstatedir)/oci_images
oci_cache_dir=$(XDG_CACHE_HOME)/buildkit

.PHONY: oci-context
oci-context: oci-context-wheel

.PHONY: oci-context-wheel
oci-context-wheel: ## build the OCI context wheel
oci-context-wheel:
	$(poetry) build --format wheel


clean: clean-oci-context
clean-oci-context: clean-$(oci_context_dir)/

.PHONY: oci-dockerfile-validate
oci-dockerfile-validate: ## validate the dockerfile
oci-dockerfile-validate: $(APP_DOCKERFILE)
	hadolint $(<)

oci_tag_prefix=

OCI_TAG_SUFFIX_USER=

oci_tag_suffixes_git = \
	gitc-$(giti_commit_hash) \

oci_tag_suffixes = \
	$(oci_tag_suffixes_git) \
	$(OCI_TAG_SUFFIX_USER) \

oci_refs_local=\
	$(foreach oci_tag_suffix,\
		$(oci_tag_suffixes),\
		ocreg.invalid/$(APP_NAME):$(oci_tag_prefix)$(oci_tag_suffix))

OCI_REF_NAMES?=
OCI_REFS_REMOTE?=\
	$(foreach oci_tag_suffix,\
		$(oci_tag_suffixes),\
		$(foreach oci_ref_name,$(OCI_REF_NAMES),$(oci_ref_name):$(oci_tag_prefix)$(oci_tag_suffix)))


oci_refs = \
	$(oci_refs_local) \
	$(OCI_REFS_REMOTE) \

oci_build_args ?= \
	outputs_dir=$(outputs_dir) \
	app_name=$(APP_NAME) \
	$(if $(APP_NAME),app_executable=$(APP_NAME)) \
	$(OCI_BUILD_ARGS) \

$(call dump_vars,OCI_REF_NAMES OCI_REFS_REMOTE oci_build_args OCI_BUILD_ARGS)

buildctl=buildctl-daemonless.sh

oci-build-stage-%: $(APP_DOCKERFILE) oci-dockerfile-validate
	echo $(<) :: $(@)
	mkdir -p $(oci_images_dir)
	$(buildctl) build \
		--export-cache type=local,dest=$(oci_cache_dir) \
		--import-cache type=local,src=$(oci_cache_dir) \
		--progress=plain \
		--frontend dockerfile.v0 \
		--opt filename=$(notdir $(<)) \
		--local context=$(oci_context_dir) \
		--local dockerfile=$(dir $(<)) \
		--metadata-file $(OCI_METADATA) \
		--output $(oci_build_stage_output) \
    	$(buildctl_extra_args) \
		$(foreach oci_build_arg,$(oci_build_args),--opt build-arg:$(oci_build_arg)) \

$(oci_images_dir)/stage-%.oci.tar: buildctl_extra_args=--opt target=$(*)
$(oci_images_dir)/stage-%.oci.tar: oci_build_stage_output=type=docker,\"name=$(call merge,$(comma),$(oci_refs))\",dest=$(oci_images_dir)/stage-$(*).oci.tar
$(oci_images_dir)/stage-%.oci.tar: oci-build-stage-%
	@echo $(<) :: $(@)


$(oci_images_dir)/stage-runtime.oci.tar: $(call skipable,oci-dockerfile-validate oci-context)
$(oci_images_dir)/stage-runtime.oci.tar: docker_image_build_extra_args=$(foreach oci_tag,$(oci_refs),--tag $(oci_tag))

.PHONY: oci-build
oci-build: $(oci_images_dir)/stage-runtime.oci.tar

.PHONY: validate-oci
oci-validate: ## validate the OCI image
oci-validate: $(call skipable,oci-build)
	dockle $(dockle_args) \
		--input $(oci_images_dir)/stage-runtime.oci.tar

oci-push: ## push the OCI image to registries
oci-push: $(oci_images_dir)/stage-runtime.oci.tar
	$(foreach oci_ref_remote,$(OCI_REFS_REMOTE),\
		crane push $(<) $(oci_ref_remote)$(__newline))

ifneq ($(call parse_bool,$(BUILD_OCI)),)
$(info adding OCI targets ...)
validate: oci-dockerfile-validate oci-validate
build: oci-build
publish: oci-push
endif

## Clean directories
.PHONY: clean-%/
clean-%/:
	@{ test -d $(*) && { set -x; rm -vr $(*); set +x; } } || echo "directory $(*) does not exist ... nothing to clean"
