# https://www.gnu.org/software/make/manual/make.html
SHELL=bash
.SHELLFLAGS=-ec -o pipefail
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

.PHONY: all
all: validate  ## Do everything (default target)

# Load settings
$(if $(wildcard devtools-settings.mk),$(eval include devtools-settings.mk),)
$(if $(wildcard devtools.env),$(eval include devtools.env),)
$(if $(wildcard default.env),$(eval include default.env),)
$(if $(wildcard .env),$(eval include .env),)
$(if $(and $(environment),$(wildcard env.$(environment))),$(eval include env.$(environment)),)

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
APP_EXECUTABLE?=$(APP_NAME)
APP_DOCKERFILE?=build/package/Dockerfile
BUILD_OCI?=$(if $(wildcard $(APP_DOCKERFILE)),true,false)
XDG_CACHE_HOME?=$(HOME)/.cache

# setting this so that it is more likely things will work on MacOS and Linux
export POSIXLY_CORRECT:=1

golangci_lint=golangci-lint $(if $(filter all commands,$(VERBOSE)),-v)
giti_description=$(shell git describe --tags --always)
giti_commit_hash=$(shell git log -1 --format="%H")
giti_commit_date=$(shell git log -1 --format="%aI")
giti_url:=$(shell git remote get-url origin)
go_mod:=$(shell go list -m)
go_ldflags= \
	-ldflags \
	"-X '$(go_mod)/internal/version.gitCommit=$(giti_commit_hash)' \
	-X '$(go_mod)/internal/version.gitRemote=$(giti_url)' \
	-X '$(go_mod)/internal/version.gitDesc=$(giti_description)' \
	-X '$(go_mod)/internal/version.gitCommitDate=$(giti_commit_date)'" \

go_build_flags=

stamps_dir=var/stamps
outputs_dir=var/outputs

$(call dump_vars,APP_EXECUTABLE APP_DOCKERFILE BUILD_OCI XDG_CACHE_HOME)

########################################################################
# targets ...
########################################################################

.PHONY: clean
clean: ## clean build outputs
clean: clean-$(outputs_dir)/
	rm -vr coverage.out || :
	go clean

.PHONY: validate
validate: validate-static test  ## Run static and dynamic validation (tests)

.PHONY: validate-fix
validate-fix:  ## Let the tooling fix what can be automatically fixed
.PHONY: validate-static
validate-static:  ## Static validation
.PHONY: test
test:  ## Dynamic code validation
.PHONY: publish
publish: ## publish artifacts

########################################################################
# golang
########################################################################

validate-fix: validate-golang-fix
.PHONY: validate-golang-fix
validate-golang-fix:
	$(golangci_lint) run  --fix ./...


.PHONY: validate-golang-static
validate-static: validate-golang-static
validate-golang-static:
	$(golangci_lint) run  ./...

.PHONY: validate-golang
validate: validate-golang
validate-golang: validate-golang-static test-golang  ## Run static and dynamic validation (tests)

.PHONY: test-golang
test: test-golang
test-golang coverage.out:
	go test -cover \
		-race \
		$(go_build_flags) \
		-coverprofile=coverage.out -covermode=atomic \
		$(if $(filter all commands,$(VERBOSE)),-v) ./... \
		$(if $(gotest_files),$(gotest_files),./...) \
		$(gotest_args)

.PHONY: view-coverage
view-coverage: coverage.out ## view coverage
	go tool cover -html=$(<)

.PHONY: build
build: ## build source
	go build -race \
		$(go_build_flags) \
		$(go_ldflags) \
		$(if $(filter all commands,$(VERBOSE)),-v) \
		./...

.PHONY: build-golang-outputs
build: build-golang-outputs
build-golang-outputs: ## build golang outputs
build-golang-outputs: | $(outputs_dir)/
	CGO_ENABLED=0 go build \
		$(go_build_flags) \
		$(go_ldflags) \
		$(if $(filter all commands,$(VERBOSE)),-v) \
		-o $(outputs_dir) \
		./...

modd_cmd?=modd
modd_args?=

.PHONY: watch
watch:
	$(modd_cmd) $(modd_args)

.PHONY: install
install: $(call skipable,validate) ## install everything
	go install $(go_build_flags) $(go_ldflags) ./...

.PHONY: run-golang
run-golang:
	go run $(go_ldflags) ./cmd/$(APP_EXECUTABLE) $(run_args)

########################################################################
# OCI
########################################################################

oci_rebuild=false
oci_context_dir?=.
oci_images_dir=var/oci_images
oci_cache_dir=$(XDG_CACHE_HOME)/buildkit

clean: clean-oci-context clean-oci-images
clean-oci-context: clean-$(oci_context_dir)/
clean-oci-images: clean-$(oci_images_dir)/
clean-stamps: clean-$(stamps_dir)/


.PHONY: oci-context
oci-context: ## prepare the OCI context
oci-context: build-golang-outputs

.PHONY: validate-dockerfile
validate-dockerfile: ## validate the dockerfile
validate-dockerfile: $(APP_DOCKERFILE)
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

oci-build-stage-%: $(APP_DOCKERFILE) validate-dockerfile | $(oci_images_dir)/ $(oci_context_dir)/ $(oci_cache_dir)/
	$(buildctl) build \
		--export-cache type=local,dest=$(oci_cache_dir) \
		--import-cache type=local,src=$(oci_cache_dir) \
		--progress=plain \
		--frontend dockerfile.v0 \
		--opt filename=$(notdir $(<)) \
		--local context=$(oci_context_dir) \
		--local dockerfile=$(dir $(<)) \
		--output $(oci_build_stage_output) \
    	$(buildctl_extra_args) \
		$(foreach oci_build_arg,$(oci_build_args),--opt build-arg:$(oci_build_arg)) \

$(oci_images_dir)/stage-%.oci.tar: buildctl_extra_args=--opt target=$(*)
$(oci_images_dir)/stage-%.oci.tar: oci_build_stage_output=type=docker,\"name=$(call merge,$(comma),$(oci_refs))\",dest=$(oci_images_dir)/stage-$(*).oci.tar
$(oci_images_dir)/stage-%.oci.tar: oci-build-stage-%
	@echo $(<) :: $(@)


$(oci_images_dir)/stage-runtime.oci.tar: $(call skipable,validate-dockerfile oci-context)
$(oci_images_dir)/stage-runtime.oci.tar: docker_image_build_extra_args=$(foreach oci_tag,$(oci_refs),--tag $(oci_tag))

.PHONY: build-oci
build-oci: $(oci_images_dir)/stage-runtime.oci.tar

.PHONY: validate-oci
validate-oci: ## validate the OCI image
validate-oci: $(call skipable,build-oci)
	dockle $(dockle_args) \
		--input $(oci_images_dir)/stage-runtime.oci.tar

push-oci: ## push the OCI image to registries
push-oci: $(oci_images_dir)/stage-runtime.oci.tar
	$(foreach oci_ref_remote,$(OCI_REFS_REMOTE),\
		crane push $(<) $(oci_ref_remote)$(__newline))

ifneq ($(call parse_bool,$(BUILD_OCI)),)
$(info adding OCI targets ...)
validate: validate-dockerfile validate-oci
build: build-oci
publish: push-oci
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
help:
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(current_makefile) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "Variables:"
	@{ grep -E '^## Variable .* : .*$$' $(current_makefile) || :; } | sort

## clean directories
.PHONY: clean-%/
clean-%/:
	@{ test -d $(*) && { set -x; rm -vr $(*); set +x; } } || echo "directory $(*) does not exist ... nothing to clean"

## create directories
.PRECIOUS: %/
%/:
	mkdir -vp $(@)


$(if $(wildcard devtools-targets.mk),$(eval include devtools-targets.mk),)
