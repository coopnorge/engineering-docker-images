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

# Find all directories that look like they are terraform root directories.
tfdirs=$(shell find . -name .terraform -prune -o \( -name '*.tf' -print0 \) \
	| xargs -0 grep -c required_version \
	| awk -F: '($$2 != 0){ print $$1 }' \
	| sed 's|/[^/]\{1,\}$$||g')

$(call dump_vars,tfdirs)

terraform=terraform

.terraform:
	$(terraform) init $(terraform_init_args)

%/.terraform:
	cd $(*) && $(terraform) init $(terraform_init_args)

tfsec=tfsec
tflint=tflint --enable-plugin=google --enable-plugin=azurerm $(if $(filter all commands,$(VERBOSE)),--loglevel=trace)
tfswitch=tfswitch

define tfdir_targets

tf-reinit: tf-reinit-$(1)
.PHONY: tf-reinit-$(1)
tf-reinit-$(1):
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) init -upgrade

validate: validate-tf-$(1)
.PHONY: validate-tf-$(1)
validate-tf-$(1): | $(1)/.terraform
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) fmt -check -recursive -diff
	cd $(1) && $$(terraform) validate
	$$(tfsec) $(1)
	$$(tflint) $(1)

endef

.PHONY: validate
all: validate
validate: ## Validate code.

tf-reinit: ## Reintialize terraform

$(foreach tfdir,$(tfdirs),\
    $(eval $(call tfdir_targets,$(tfdir))))

.PHONY: validate-fix
validate-fix: ## Fix auto-fixable validation errors.
validate-fix: | .terraform
	$(terraform) fmt -recursive

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

