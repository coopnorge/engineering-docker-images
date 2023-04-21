# https://www.gnu.org/software/make/manual/make.html

# Configure the shell.
SHELL=bash
.SHELLFLAGS=-ec -o pipefail

# Capture the current makefile.
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

# Define the default target.
.PHONY: all
all:

# Load settings.
$(if $(wildcard devtools-settings.mk),$(info loading devtools-settings.mk)$(eval include devtools-settings.mk),)
$(if $(wildcard devtools.env),$(info loading devtools.env)$(eval include devtools.env),)
$(if $(wildcard default.env),$(info loading default.env)$(eval include default.env),)
$(if $(wildcard .env),$(info loading .env)$(eval include .env),)
$(if $(and $(ENVIRONMENT),$(wildcard $(ENVIRONMENT).env)),$(info loading $(ENVIRONMENT).env)$(eval include $(ENVIRONMENT).env),)
$(if $(and $(ENVIRONMENT),$(wildcard .env.$(ENVIRONMENT))),$(info loading .env.$(ENVIRONMENT))$(eval include .env.$(ENVIRONMENT)),)

########################################################################
# boiler plate
########################################################################
ifneq ($(filter all vars,$(VERBOSE)),)
dump_var=$(info var $(1)=$($(1)))
dump_vars=$(foreach var,$(1),$(call dump_var,$(var)))
else
dump_var=
dump_vars=
endif

ifneq ($(filter all targets,$(VERBOSE)),)
__ORIGINAL_SHELL:=$(SHELL)
SHELL=$(warning Building $@$(if $<, (from $<))$(if $?, ($? newer)))$(TIME) $(__ORIGINAL_SHELL)
endif

# checks if $(1) and $(2) is equal
seq = $(if $(subst x$(1)x,,x$(2)x)$(subst x$(2)x,,x$(1)x),,T)
# parse true|false to a make boolean
parse_bool = $(if $(call seq,$(1),true),T,$(if $(call seq,$(1),false),,$(error invalid boolean value $(1))))
# merge the list items in $2 with the seperator $1
merge = $(strip $(if $2, $(if $(filter 1,$(words $2)),$2,$(firstword $2)$1$(call merge,$1,$(wordlist 2,$(words $2),$2)))))
comma:=,

skip=
# skipable makes the targets passed to it skipable with skip=foo%
# $(1): targets that should be skipable
skipable=$(filter-out $(skip),$(1))

define __newline


endef

########################################################################
# variables
########################################################################
## Variable APP_NAME : The name of the application.
## Variable APP_EXECUTABLE : The main executable of the application, defaults to APP_NAME
## Variable ENTRYPOINT : The Typescript file to use as the entrypoint to the program. Defaults to `src/main.ts`.
## Variable ENVIRONMENT : The environment name to use. If set variables will be loaded from env.$(ENVIRONMENT)
## Variable APP_DOCKERFILE : The path to the Dockerfile to use for building OCI images. Defaults to `build/package/Dockerfile`.
## Variable BUILD_OCI : boolean (true,false) indicating if OCI should be built. Defaults to true if $(APP_DOCKERFILE) exists
APP_EXECUTABLE?=$(APP_NAME)
ENTRYPOINT?=src/main.ts
APP_DOCKERFILE?=build/package/Dockerfile
BUILD_OCI?=$(if $(wildcard $(APP_DOCKERFILE)),true,false)
XDG_CACHE_HOME?=$(HOME)/.cache
OCI_METADATA?=oci-metadata.json

# setting this so that it is more likely things will work on MacOS and Linux
export POSIXLY_CORRECT:=1

# Get git information
giti_description=$(shell git describe --tags --always)
giti_commit_hash=$(shell git log -1 --format="%H")
giti_commit_date=$(shell git log -1 --format="%aI")
giti_url:=$(shell git remote get-url origin)

# Define Typescript vars
tsconfig ?= tsconfig.json

localstatedir?=var
generated_dir?=$(localstatedir)/generated
stamps_dir?=$(localstatedir)/stamps
outputs_dir?=$(localstatedir)/outputs

$(call dump_vars,APP_EXECUTABLE APP_DOCKERFILE BUILD_OCI XDG_CACHE_HOME)

########################################################################
# generic targets
########################################################################

.PHONY: clean
clean: ## Clean outputs.
clean: clean-$(localstatedir)/

.PHONY: configure
configure: ## Configure the project.

.PHONY: validate-fix
validate-fix: ## Fix auto-fixable validation errors.

.PHONY: validate-static
validate-static: ## Run static validation.

.PHONY: test
test: ## Run the project's tests.

.PHONY: validate
validate: ## Validate everything.
validate: validate-static test

.PHONY: build
build: ## Build the source.

.PHONY: watch
watch: ## Watch code for changes and re-build.

.PHONY: publish
publish: ## Publish artifacts.

.PHONY: deploy
deploy: ## Deploy the project.

.PHONY: all
all: ## Do everything.
all: validate build

########################################################################
# Typescript
########################################################################

jest := $(TOOLS_DIR)/node_modules/.bin/jest
eslint= $(TOOLS_DIR)/node_modules/.bin/eslint --ext .js,.ts,.jsx,.tsx
tsc := $(TOOLS_DIR)/node_modules/.bin/tsc $(if $(filter all commands,$(VERBOSE)),-v) --project $(tsconfig)
ts-node := $(TOOLS_DIR)/node_modules/.bin/ts-node --project $(tsconfig)

validate-fix: ts-validate-fix
.PHONY: ts-validate-fix
ts-validate-fix:
	$(eslint) --fix .

.PHONY: ts-validate-static
validate-static: ts-validate-static
ts-validate-static:
	$(eslint) .

.PHONY: ts-test
test: ts-test
ts-test: ## Test Typescript code.
ts-test coverage/%: | $(localstatedir)/
	$(jest) --coverage


.PHONY: ts-validate
validate: ts-validate
ts-validate: ts-validate-static ts-test  ## Run static and dynamic validation (tests).

.PHONY: ts-build
ts-build: ## Build Typescript source.
	$(tsc)

.PHONY: ts-build-outputs
build: ts-build-outputs
ts-build-outputs: ## Build Typescript outputs.
ts-build-outputs: | $(outputs_dir)/
	$(tsc) --outDir $(outputs_dir)

.PHONY: ts-watch
watch: ts-watch
ts-watch: ## Watch Typescript code for changes and rerun build on changes.
	$(tsc) --watch

.PHONY: ts-run
ts-run: ## Run project
	$(ts-node) $(ENTRYPOINT) $(run_args) $(CLI_ARGS)

.PHONY: ts-clean
clean: ts-clean
ts-clean:
	rm -rf coverage

########################################################################
# OCI
########################################################################

oci_rebuild=false
oci_context_dir?=.
oci_images_dir=$(localstatedir)/oci_images
oci_cache_dir=$(XDG_CACHE_HOME)/buildkit

.PHONY: oci-clean-images
clean: oci-clean-context
oci-clean-images: clean-$(oci_images_dir)/

.PHONY: oci-context
oci-context: ## prepare the OCI context
oci-context: ts-build-outputs

.PHONY: oci-dockerfile-validate
oci-dockerfile-validate: ## validate the dockerfile
oci-dockerfile-validate: $(APP_DOCKERFILE)
	hadolint $(<)

oci_tag_prefix=

oci_tag_suffixes_const = \
	latest \

oci_tag_suffixes_git = \
	gitc-$(giti_commit_hash) \

oci_tag_suffixes = \
	$(oci_tag_suffixes_const) \
	$(oci_tag_suffixes_git) \

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
	$(if $(APP_EXECUTABLE),app_executable=$(APP_EXECUTABLE)) \
	$(OCI_BUILD_ARGS) \

$(call dump_vars,OCI_REF_NAMES OCI_REFS_REMOTE oci_build_args OCI_BUILD_ARGS)

buildctl=buildctl-daemonless.sh

oci-build-stage-%: $(APP_DOCKERFILE) oci-dockerfile-validate | $(oci_images_dir)/ $(oci_context_dir)/ $(oci_cache_dir)/
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

########################################################################
# docker-lock
########################################################################

docker_compose=docker compose
docker_lock=$(docker_compose) run --rm -T docker-lock
# docker_lock=docker-lock

.PHONY: docker-lock
docker-lock: ## Generate and rewrite digests of docker images
	$(docker_lock) lock generate \
		--update-existing-digests \
		--dockerfile-globs *.Dockerfile Dockerfile Dockerfile.* \
		--dockerfile-recursive \
		--composefile-recursive \
		--kubernetesfile-recursive \
		--ignore-missing-digests
	$(docker_lock) lock rewrite

########################################################################
# utility targets
########################################################################

.PHONY: help
help: ## Show this message.
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(current_makefile) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "Variables:"
	@{ grep -E '^## Variable .* : .*$$' $(current_makefile) || :; } | sort

## Clean directories
.PHONY: clean-%/
clean-%/:
	@{ test -d $(*) && { set -x; rm -vr $(*); set +x; } } || echo "directory $(*) does not exist ... nothing to clean"

## Create directories
.PRECIOUS: %/
%/:
	mkdir -vp $(@)


$(if $(wildcard devtools-targets.mk),$(info loading devtools-targets.mk)$(eval include devtools-targets.mk),)
