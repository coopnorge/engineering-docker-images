SHELL=bash
.SHELLFLAGS=-ec -o pipefail
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

.PHONY: all
all: ## do everything (default target)

########################################################################
# boiler plate
########################################################################
SHELL=bash
.SHELLFLAGS=-ec -o pipefail

current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dirname:=$(dir $(current_makefile))
current_makefile_dirname_abspath:=$(dir $(abspath $(current_makefile)))
current_makefile_dirname_realpath:=$(dir $(realpath $(current_makefile)))

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

define __newline


endef

$(call dump_vars,current_makefile current_makefile_dirname \
	current_makefile_dirname_abspath current_makefile_dirname_realpath)

########################################################################
# variables
########################################################################

oci_output_dir=var/oci-images

########################################################################
# targets
########################################################################

images_dir=images
IMAGE_NAMES?=$(notdir $(wildcard $(images_dir)/*))
$(call dump_vars,IMAGE_NAMES)

docker=docker
docker_compose=docker compose
# docker_image_build_cmd=$(docker) image build
docker_image_build_cmd=$(docker) buildx build --progress plain --load
docker_image_build_args?=
docker_image_build=$(docker_image_build_cmd) $(docker_image_build_args)
hadolint=$(docker_compose) run --rm -T hadolint

oci_local_ref_prefix=ocreg.invalid/coopnorge/engineering/image/
oci_remote_ref_prefixes=\

all: build
build: ## build artifacts

py_source=$(shell find images/ -type f -name '*.py')

validate-python: ## Validate Python code
	poetry check
	poetry run isort --check-only $(py_source)
	poetry run black --config ./pyproject.toml --check $(py_source)
	poetry run pflake8 $(py_source)
	$(foreach file, $(py_source), poetry run mypy --show-error-codes --show-error-context --pretty $(file) &&) true


validate-fix-python: ## Fix auto-fixable validation errors in Python
	poetry run python -m isort images
	poetry run python -m black --config ./pyproject.toml images

validate-dockerfile-%: ## Validate a specific dockerfile
	$(hadolint) < images/$(*)/context/Dockerfile

validate_dockerfile_targets=$(foreach image_name,$(IMAGE_NAMES),validate-dockerfile-$(image_name))
.PHONY: validate-static
validate-static: validate-images-digests $(validate_dockerfile_targets) validate-python ## Run static validation

.PHONY: validate
validate: validate-static test ## Validate everything

.PHONY: build-image-%
build-image-%: ## Build a specific image
	$(docker_image_build) \
		--tag $(oci_local_ref_prefix)$(*):built \
		images/$(*)/context/
build_image_targets=$(foreach build_image_name,$(IMAGE_NAMES),build-image-$(build_image_name))

build-images: ## build all images
build: build-images
build-images: $(build_image_targets)

.PHONY: test-image-%
test-image-%: ## Test a specific image
	IMAGE_UNDER_TEST=$(oci_local_ref_prefix)$(*):built \
		images/$(*)/tests/run

test_image_targets=$(foreach image_name,$(IMAGE_NAMES),test-image-$(image_name))
.PHONY: test
test: $(test_image_targets) ## Test all images

.PHONY: tag-image-%
tag-image-%:
	$(foreach oci_remote_ref_prefix,$(oci_remote_ref_prefixes),\
		$(docker) tag $(oci_local_ref_prefix)$(*):built $(oci_remote_ref_prefix)$(*):latest $(__newline))

tag_image_targets=$(foreach image_name,$(IMAGE_NAMES),tag-image-$(image_name))
.PHONY: tag-images
tag-images: $(tag_image_targets) ## Tag all images

.PHONY: push-image-%
push-image-%: tag-image-% ## Push a specific image
	$(foreach oci_remote_ref_prefix,$(oci_remote_ref_prefixes),\
		$(docker) push $(oci_remote_ref_prefix)$(*):latest $(__newline))

push_image_targets=$(foreach image_name,$(IMAGE_NAMES),push-image-$(image_name))
push-images: $(push_image_targets) ## Push all images

.PRECIOUS: $(oci_output_dir)/%.oci.tar
$(oci_output_dir)/%.oci.tar: image-% | $(oci_output_dir)/
	$(docker) image save -o $(@) $(oci_local_ref_prefix)$(*):built

.PHONY: save-image-%
save-image-%: $(oci_output_dir)/%.oci.tar ## save a specific image
	echo "$(<) -> $(@)"

save_image_targets=$(foreach image_name,$(IMAGE_NAMES),save-image-$(image_name))
.PHONY: save-images
save-images: $(save_image_targets)

load-opt-image-%: ## Loads a specific image if it exists
	if [ -e $(oci_output_dir)/$(*).oci.tar ]; \
	then \
		$(docker) image load -i $(oci_output_dir)/$(*).oci.tar; \
	else \
		echo "NOTE: not loading $(oci_output_dir)/$(*).oci.tar as it does not exist"; \
	fi;

load_opt_image_targets=$(foreach image_name,$(IMAGE_NAMES),load-opt-image-$(image_name))
.PHONY: load-opt-images
load-opt-images: $(load_opt_image_targets)  ## Loads all images

load-any-images: | $(oci_output_dir)/ ## Loads any images that are found
	find $(oci_output_dir)/ -name '*.oci.tar' -print0 \
		| xargs --no-run-if-empty -0 -n1 -t $(docker) image load -i

########################################################################
# docker-lock
########################################################################

docker_lock=$(docker_compose) run --rm -T docker-lock
#docker_lock=docker-lock

.PHONY: docker-lock
docker-lock: ## Generate and rewrite digests of docker images
	$(docker_lock) lock generate
	$(docker_lock) lock rewrite

.PHONY: validate-images-digests
validate-images-digests:  ## Validate images digests
	$(docker_lock) lock verify

########################################################################
# utility
########################################################################

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## clean directories
.PHONY: clean-%/
clean-%/:
	@{ test -d $(*) && { set -x; rm -vr $(*); set +x; } } || echo "directory $(*) does not exist ... nothing to clean"

## create directories
.PRECIOUS: %/
%/:
	mkdir -vp $(@)
