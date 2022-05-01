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
TFDIRS_EXCLUDE?=%/examples %/example
$(info TFDIRS_EXCLUDE=$(TFDIRS_EXCLUDE))

TFDIRS?=$(filter-out $(TFDIRS_EXCLUDE), \
	$(or $(shell find . -name .terraform -prune -o \( -name '*.tf' -print \) \
		| sed 's|/[^/]\{1,\}$$||g' \
		| sort | uniq),.))

$(info TFDIRS=$(TFDIRS))

terraform=terraform

.terraform:
	$(tfswitch)
	$(terraform) init $(terraform_init_args)

%/.terraform:
	cd $(*) && $(tfswitch)
	cd $(*) && $(terraform) init $(terraform_init_args)

tfsec=tfsec
tflint=tflint --enable-plugin=google --enable-plugin=azurerm $(if $(filter all commands,$(VERBOSE)),--loglevel=trace)
tfswitch={ set +o pipefail; yes | tfswitch; }

define tfdir_targets

tf-reinit: tf-reinit-$(1)
.PHONY: tf-reinit-$(1)
tf-reinit-$(1):
	$(if $(TF_PLUGIN_CACHE_DIR),mkdir -vp $(TF_PLUGIN_CACHE_DIR),)
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) init -upgrade

validate: validate-tf-$(1)
.PHONY: validate-tf-$(1)
validate-tf-$(1): | $(1)/.terraform
	$(if $(TF_PLUGIN_CACHE_DIR),mkdir -vp $(TF_PLUGIN_CACHE_DIR),)
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) fmt -check -recursive -diff
	cd $(1) && $$(terraform) validate
	test -e "$(1)/.tfsec-ignore" || $$(tfsec) $(1)
	$$(tflint) $(1)

endef

.PHONY: validate
all: validate
validate: ## Validate code.

.PHONY: tf-reinit
tf-reinit: ## Reintialize terraform

.PHONY: terraform-reinit
terraform-reinit: tf-reinit ## Reintialize terraform

$(foreach tfdir,$(TFDIRS),\
    $(eval $(call tfdir_targets,$(tfdir))))

.PHONY: validate-fix
validate-fix: ## Fix auto-fixable validation errors.
validate-fix: | .terraform
	$(terraform) fmt -recursive

########################################################################
# utility
########################################################################

GH_CLI := $(shell command -v gh 2> /dev/null)
github_oauth_token=
terraform_switcher_version=
terraform_switcher_tag:="latest"
ifdef terraform_switcher_version
	terraform_switcher_tag:="tags/$(terraform_switcher_version)"
endif
ifdef github_oauth_token
	USE_GITHUB_OAUTH_TOKEN:="-U \"$(github_oauth_token):x-oauth-basic\""
endif
ifndef GH_CLI
	terraform_switcher_release:=curl --header "Accept: application/vnd.github.v3+json" $(USE_GITHUB_OAUTH_TOKEN) "https://api.github.com/repos/warrensbox/terraform-switcher/releases/$(terraform_switcher_tag)"
else
	terraform_switcher_release:=gh api --header "Accept: application/vnd.github.v3+json" "/repos/warrensbox/terraform-switcher/releases/$(terraform_switcher_tag)"
endif
terraform_switcher_checksums_download_url=$(terraform_switcher_release) | jq --raw-output ".assets[] | select(.name | contains(\"checksums\")) | .browser_download_url"

terraform-switcher-download-checksum:
	curl --location --output terraform_switcher_checksums.txt "$(shell $(terraform_switcher_checksums_download_url))"

.PHONY: update-terraform-switcher-checksums
update-terraform-switcher-checksums: terraform-switcher-download-checksum ## Update terraform-switcher checksum file.

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

