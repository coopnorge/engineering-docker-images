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
WITH_TFSWITCH?=false
# setting this so that it is more likely things will work on MacOS and Linux
export POSIXLY_CORRECT:=1
terraform_docs_config=terraform-docs.yml

########################################################################
# targets ...
########################################################################

# Find all directories that look like they are terraform root directories.
TFDIRS_EXCLUDE?=%/examples %/example
$(info TFDIRS_EXCLUDE=$(TFDIRS_EXCLUDE))

# Find directories containing Terraform files if TFDIRS is not already set
# Directories to exclude in find. We are not expecting tf files in these and saves a lot of time when running locally.
TF_FIND_EXCLUDE_DIRS := \( -name node_modules -o -name .venv -o -name .git -o -name .terraform \)

# Find command to locate .tf files while excluding certain directories
FIND_TF_FILES := find . $(TF_FIND_EXCLUDE_DIRS) -prune -o \( -name '*.tf' -print \)

# Extract unique directories containing .tf files
TFDIRS ?= $(shell $(FIND_TF_FILES) \
	| sed 's|/[^/]\{1,\}$$||g' \
	| sort | uniq)

# Filter out the directories specified in TFDIRS_EXCLUDE
override TFDIRS := $(filter-out $(TFDIRS_EXCLUDE),$(TFDIRS))

# If TFDIRS is still empty, default to the current directory
override TFDIRS := $(or $(TFDIRS),.)

TF_NO_PROVIDERS=

$(info TFDIRS=$(TFDIRS))

terraform=terraform
TF_LOCK_PLATFORMS?=linux_arm64 linux_amd64 darwin_amd64 darwin_arm64 windows_amd64
terraform_providers_lock_args=$(foreach platform,$(TF_LOCK_PLATFORMS), -platform=$(platform))

tf_plugin_cache_dir_target=$(if $(TF_PLUGIN_CACHE_DIR),$(TF_PLUGIN_CACHE_DIR)/,)

$(call dump_vars,tf_plugin_cache_dir_target TF_PLUGIN_CACHE_DIR)

TRIVY_CACHE_DIR?=/tmp/.cache.trivy
trivy_cache_dir_target=$(if $(TRIVY_CACHE_DIR),$(TRIVY_CACHE_DIR)/,)

$(call dump_vars,trivy_plugin_cache_dir_target TRIVY_CACHE_DIR)

.terraform .terraform/providers: | $(tf_plugin_cache_dir_target)
	$(tfswitch)
	$(terraform) init $(terraform_init_args)

%/.terraform %/.terraform/providers: | $(tf_plugin_cache_dir_target)
	cd $(*) && $(tfswitch)
	cd $(*) && $(terraform) init $(terraform_init_args)

.trivy: | $(trivy_cache_dir_target)
	mkdir -vp $(trivy_cache_dir_target)policy/content/
	# If the trivy cache for the policies is empty, extract the one included in the image
	POLICY_CONTENT=$$(ls -A $(trivy_cache_dir_target)policy/content/); \
	if [ "$$POLICY_CONTENT" = "" ]; then \
		tar -xzf /var/trivy-checks-db.tar.gz -C $(trivy_cache_dir_target)policy/content/; \
		cp /var/trivy-checks-metadata.json $(trivy_cache_dir_target)policy/metadata.json; \
	fi
	# Try to update. If the update fails, the checks db included in the image (extracted above) is used.
	- DIGEST=$$(oras pull $(TRIVY_CHECKS_DB) | grep Digest | cut -d' ' -f2); \
	DOWNLOADED_AT=$$(date +"%Y-%m-%dT%H:%M:%S.%6N%:z"); \
	if [ -z "$$DIGEST" ]; then \
		echo "Failed to download trivy-checks db"; \
	else \
		tar -xzf bundle.tar.gz -C $(trivy_cache_dir_target)policy/content/; \
		echo "{\"Digest\":\"$$DIGEST\",\"DownloadedAt\":\"$$DOWNLOADED_AT\"}" > $(trivy_cache_dir_target)policy/metadata.json; \
	fi

trivy=trivy --cache-dir $(trivy_cache_dir_target) config --exit-code 1 --misconfig-scanners=terraform
tflint=tflint $(if $(filter all commands,$(VERBOSE)),--loglevel=trace)
tfdocs_version=$(shell terraform-docs --version)
tfdocs_check=terraform-docs . -c $(terraform_docs_config) --output-check
tfdocs_generate=terraform-docs . -c $(terraform_docs_config)

ifeq ($(WITH_TFSWITCH),true)
tfswitch={ set +o pipefail; yes | tfswitch; }
else
tfswitch=true
endif

define tfdir_targets

tf-reinit: tf-reinit-$(1)
.PHONY: tf-reinit-$(1)
tf-reinit-$(1): | $(tf_plugin_cache_dir_target)
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) init $(terraform_init_args)

tf-upgrade: tf-upgrade-$(1)
.PHONY: tf-upgrade-$(1)
tf-upgrade-$(1): | $(tf_plugin_cache_dir_target)
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) init -upgrade $(terraform_init_args)
	cd $(1) && $$(terraform) providers lock $(terraform_providers_lock_args)

tf-relock: tf-relock-$(1)
.PHONY: tf-relock-$(1)
tf-relock-$(1): | $(tf_plugin_cache_dir_target)
	cd $(1) && $$(tfswitch)
	cd $(1) && rm -fv .terraform.lock.hcl
	cd $(1) && $$(terraform) providers lock $(terraform_providers_lock_args)

tf-docs: tf-docs-$(1)
.PHONY: tf-docs-$(1)
tf-docs-$(1):
	cd $(1) && $$(tfdocs_generate)

validate: validate-tf-$(1)
.PHONY: validate-tf-$(1)
validate-tf-$(1): | $(1)/.terraform $(if $(TF_NO_PROVIDERS),,$(1)/.terraform/providers) $(tf_plugin_cache_dir_target) .trivy
	cd $(1) && $$(tfswitch)
	cd $(1) && $$(terraform) fmt -check -recursive -diff
	cd $(1) && $$(terraform) validate
	test -e "$(1)/.tfsec-ignore" || test -e "$(1)/.trivy-ignore" || \
        (test -e "$(1)/.trivyignore" && $$(trivy) --ignorefile="$(1)/.trivyignore" "$(1)" || $$(trivy) "$(1)")
	[ ! -f "$(1)/$(terraform_docs_config)" ] || (echo "Validating documentation with $$(tfdocs_version)" ; $$(tfdocs_check) )
	$$(tflint) --chdir=$(1)

endef

.PHONY: validate
all: validate
validate: ## Validate code.

.PHONY: tf-reinit
tf-reinit: ## Reintialize terraform

.PHONY: terraform-reinit
terraform-reinit: tf-reinit ## Reintialize terraform

.PHONY: tf-upgrade
tf-upgrade: ## Reintialize and upgrade terraform

.PHONY: terraform-upgrade
terraform-upgrade: tf-upgrade ## Reintialize and upgrade terraform

.PHONY: terraform-relock
terraform-relock: tf-relock ## Regenerate .terraform.lock.hcl files

$(foreach tfdir,$(TFDIRS),\
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

