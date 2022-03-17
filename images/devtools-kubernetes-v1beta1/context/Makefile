SHELL=bash
.SHELLFLAGS=-ec -o pipefail
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

.PHONY: all
all: ## do everything (default target)

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

########################################################################
# targets ...
########################################################################

.PHONY: validate
all: validate
validate: ## Validate code.

.PHONY: validate-fix
validate-fix: ## Fix auto-fixable validation errors.
validate-fix:

########################################################################
# utility
########################################################################

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## clean directories
.PHONY: clean-%/
clean-%/:
	@{ test -d $(*) && { set -x; rm -vr $(*); set +x; } } || echo "directory $(*) does not exist ... nothing to clean"

## create directories
.PRECIOUS: %/
%/:
	mkdir -vp $(@)
