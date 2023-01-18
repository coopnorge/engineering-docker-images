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
$(if $(and $(ENVIRONMENT),$(wildcard env.$(ENVIRONMENT))),$(info loading env.$(ENVIRONMENT))$(eval include env.$(ENVIRONMENT)),)

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
## Variable ENVIRONMENT : The environment name to use. If set variables will be loaded from env.$(ENVIRONMENT)
## Variable APP_DOCKERFILE : The path to the Dockerfile to use for building OCI images. Defaults to `build/package/Dockerfile`.
## Variable BUILD_OCI : boolean (true,false) indicating if OCI should be built. Defaults to true if $(APP_DOCKERFILE) exists
## Variable ENABLE_BUF: boolean (true,false) indicating if buf should be enabled. Defaults to true if buf.work.yaml exists
APP_EXECUTABLE?=$(APP_NAME)
APP_DOCKERFILE?=build/package/Dockerfile
BUILD_OCI?=$(if $(wildcard $(APP_DOCKERFILE)),true,false)
XDG_CACHE_HOME?=$(HOME)/.cache
ENABLE_BUF?=$(if $(wildcard buf.work.yaml),true,false)
OCI_METADATA?=oci-metadata.json

# setting this so that it is more likely things will work on MacOS and Linux
export POSIXLY_CORRECT:=1

# Get git information
giti_description=$(shell git describe --tags --always)
giti_commit_hash=$(shell git log -1 --format="%H")
giti_commit_date=$(shell git log -1 --format="%aI")
giti_url:=$(shell git remote get-url origin)

# Define golang flags
go_mod:=$(shell go list -m)
go_ldflags?= \
	-ldflags \
	"-X '$(go_mod)/internal/version.gitCommit=$(giti_commit_hash)' \
	-X '$(go_mod)/internal/version.gitRemote=$(giti_url)' \
	-X '$(go_mod)/internal/version.gitDesc=$(giti_description)' \
	-X '$(go_mod)/internal/version.gitCommitDate=$(giti_commit_date)'" \

go_build_flags?=

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

.PHONY: generate
generate: ## Generate all intermediate code.

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
watch: ## Watch code for changes and re-validate.

.PHONY: install
install: ## Install globally.

.PHONY: publish
publish: ## Publish artifacts.

.PHONY: deploy
deploy: ## Deploy the project.

.PHONY: all
all: ## Do everything.
all: validate generate build

########################################################################
# golang
########################################################################

golangci_lint=golangci-lint $(if $(filter all commands,$(VERBOSE)),-v)

validate-fix: golang-validate-fix
.PHONY: golang-validate-fix
golang-validate-fix:
	$(golangci_lint) run  --fix ./...

.PHONY: golang-validate-static
validate-static: golang-validate-static
golang-validate-static:
	$(golangci_lint) run  ./...

.PHONY: golang-test
test: golang-test
golang-test: ## Test golang code.
golang-test coverage.out: | $(localstatedir)/
	go test -cover \
		-race \
		$(go_build_flags) \
		-coverprofile=coverage.out -covermode=atomic \
		$(gotest_args) \
		$(if $(filter all commands,$(VERBOSE)),-v) \
		$(if $(gotest_files),$(gotest_files),$(or $(CLI_ARGS),./...)) \


.PHONY: golang-validate
validate: golang-validate
golang-validate: golang-validate-static golang-test  ## Run static and dynamic validation (tests).

.PHONY: golang-view-coverage
golang-view-coverage: coverage.out ## View golang coverage.
	go tool cover -html=$(<)

.PHONY: golang-build
golang-build: ## Build golang source.
	go build -race \
		$(go_build_flags) \
		$(go_ldflags) \
		$(if $(filter all commands,$(VERBOSE)),-v) \
		./...

.PHONY: golang-build-outputs
build: golang-build-outputs
golang-build-outputs: ## Build golang outputs.
golang-build-outputs: | $(outputs_dir)/
	CGO_ENABLED=0 go build \
		$(go_build_flags) \
		$(go_ldflags) \
		$(if $(filter all commands,$(VERBOSE)),-v) \
		-o $(outputs_dir) \
		./...

.PHONY: golang-generate
generate: golang-generate
golang-generate: ## Generate golang things.
golang-generate:
	go generate ./...

modd_cmd?=modd
modd_args?=

.PHONY: golang-watch
watch: golang-watch
golang-watch: ## Watch golang code for changes and rerun validation on changes.
	$(modd_cmd) $(modd_args)

.PHONY: golang-install
golang-install: $(call skipable,validate) ## Install golang commands.
	go install $(go_build_flags) $(go_ldflags) ./...

.PHONY: golang-run
golang-run: ## Run main golang command
	go run $(go_ldflags) ./cmd/$(APP_EXECUTABLE) $(run_args) $(CLI_ARGS)

.PHONY: golang-clean
clean: golang-clean
golang-clean:
	rm -f coverage.out
	go clean

########################################################################
# buf targets
########################################################################

protbuf_dir=spec/proto
buf=buf
buf_format_args=

.PHONY: buf-validate
buf-validate: ## buf validation
	$(buf) lint
	$(buf) format --diff --exit-code $(buf_format_args)

.PHONY: buf-validate-fix
buf-validate-fix: ## fix auto-fixable buf validation errors
	$(buf) format --write $(buf_format_args)

.PHONY: buf-generate
buf-generate: ## generate buf outputs
	\rm -rv internal/generated/*proto*/ || :
	$(buf) generate

$(generated_dir)/main.dsc: | $(generated_dir)/
	$(buf) build --as-file-descriptor-set -o $(@) -vv --debug

.PHONY: buf-export
buf-export: | $(localstatedir)/buf/ ## export proto files
	$(buf) export -o $(localstatedir)/buf/exported

.PHONY: buf-mod-update
buf-mod-update: # Update buf modules
	$(buf) mod update $(protbuf_dir)

ifneq ($(call parse_bool,$(ENABLE_BUF)),)
$(info adding Buf targets ...)
validate: buf-validate
validate-fix: buf-validate-fix
generate: buf-generate
generate: buf-export
endif

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
oci-context: golang-build-outputs

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
