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


########################################################################
# targets
########################################################################

images_dir=images
IMAGE_NAMES?=$(notdir $(wildcard $(images_dir)/*))
$(call dump_vars,IMAGE_NAMES)

docker=docker
docker_compose=docker-compose
# docker_image_build=$(docker) image build
docker_image_build_cmd=$(docker) buildx build --progress plain
docker_image_build_args?=
docker_image_build=$(docker_image_build_cmd) $(docker_image_build_args)
hadolint=$(docker_compose) run --rm -T hadolint

all: build
build: ## build artifacts

validate-dockerfile-%:
	$(hadolint) < images/$(*)/context/Dockerfile

validate_dockerfile_targets=$(foreach image_name,$(IMAGE_NAMES),validate-dockerfile-$(image_name))
validate: $(validate_dockerfile_targets)

.PHONY: image-%
image-%:
	$(docker_image_build) \
		--tag ocreg.invalid/coopnorge/engineering/image/$(*):built \
		images/$(*)/context/
image_targets=$(foreach image_name,$(IMAGE_NAMES),image-$(image_name))

images: ## build all images
build: images
images: $(image_targets)

test-image-%:
	IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/$(*):built \
		images/$(*)/tests/run

test_image_targets=$(foreach image_name,$(IMAGE_NAMES),test-image-$(image_name))
test: $(test_image_targets)

oci_remote_ref_prefixes=\

tag-image-%:
	$(foreach oci_remote_ref_prefix,$(oci_remote_ref_prefixes),\
		$(docker) tag ocreg.invalid/coopnorge/engineering/image/$(*):built $(oci_remote_ref_prefix)$(*):latest $(__newline))


tag_image_targets=$(foreach image_name,$(IMAGE_NAMES),tag-image-$(image_name))
tag-images: $(tag_image_targets)


push-image-%: tag-image-%
	$(foreach oci_remote_ref_prefix,$(oci_remote_ref_prefixes),\
		$(docker) push $(oci_remote_ref_prefix)$(*):latest $(__newline))


push_image_targets=$(foreach image_name,$(IMAGE_NAMES),push-image-$(image_name))
push-images: $(push_image_targets)

########################################################################
# docker-lock
########################################################################

# docker_lock=$(docker_compose) run --rm -T docker-lock
docker_lock=docker-lock

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

