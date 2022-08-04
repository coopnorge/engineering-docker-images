# https://www.gnu.org/software/make/manual/make.html
SHELL=bash
.SHELLFLAGS=-ec -o pipefail
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

.PHONY: all
all: validate  ## Do everything (default target)

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

########################################################################
# variables
########################################################################

PROJECT_TOOLS_DIR?=$(current_makefile_dir)var/tools/
tools_dir=$(PROJECT_TOOLS_DIR)
ifneq ($(tools_dir),)
export PATH:=$(tools_dir):$(PATH)
endif
XDG_CACHE_HOME?=$(HOME)/.cache

# setting this so that it is more likely things will work on MacOS and Linux
export POSIXLY_CORRECT:=1

golangci_lint=golangci-lint $(if $(filter all commands,$(VERBOSE)),-v)

########################################################################
# targets ...
########################################################################

.PHONY: validate
validate: validate-static test  ## Run static and dynamic validation (tests)

.PHONY: validate-fix
validate-fix:  ## Let the tooling fix what can be automatically fixed
	$(golangci_lint) run  --fix ./...

.PHONY: validate-static
validate-static:  ## Static code validation
	$(golangci_lint) run  ./...

.PHONY: test
test:  ## Dynamic code validation
test coverage.out:
	go test -race -cover $(if $(filter all commands,$(VERBOSE)),-v) ./... \
		-coverprofile=coverage.out -covermode=atomic \
		$(if $(gotest_files),$(gotest_files),./...) \
		$(gotest_args)

.PHONY: build
build: ## build source
	go build -race -v ./...

.PHONY: view-coverage
view-coverage: coverage.out ## view coverage
	go tool cover -html=$(<)

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
# utility
########################################################################

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## create directories
.PRECIOUS: %/
%/:
	mkdir -vp $(@)
