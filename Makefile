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

$(call dump_vars,current_makefile current_makefile_dirname \
	current_makefile_dirname_abspath current_makefile_dirname_realpath)

########################################################################
# variables
########################################################################


########################################################################
# targets
########################################################################

images_dir=images
image_names=$(notdir $(wildcard $(images_dir)/*))
$(call dump_vars,$(image_names))

docker=docker
docker_compose=docker-compose
hadolint=$(docker_compose) run --rm -T hadolint

all: build
build: ## build artifacts

validate-dockerfile-%:
	$(hadolint) < images/$(*)/context/Dockerfile

validate_dockerfile_targets=$(foreach image_name,$(image_names),validate-dockerfile-$(image_name))
validate: $(validate_dockerfile_targets)

.PHONY: image-%
image-%:
	$(docker) image build --tag ocreg.invalid/coopnorge/engineering/image/$(*):built images/$(*)/context/
image_targets=$(foreach image_name,$(image_names),image-$(image_name))

images: ## build all images
build: images
images: $(image_targets)

test-image-%:
	IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/$(*):built \
		images/$(*)/tests/run

test_image_targets=$(foreach image_name,$(image_names),test-image-$(image_name))
test: $(test_image_targets)


########################################################################
# docker-lock
########################################################################

docker_lock=$(docker_compose) run --rm -T docker-lock
# docker_lock=docker-lock

.PHONY: docker-lock
docker-lock: ## Generate and rewrite digests of docker images
	$(docker_lock) lock generate \
		--update-existing-digests \
		--dockerfile-globs *.Dockerfile Dockerfile \
		--dockerfile-recursive \
		--composefile-recursive \
		--kubernetesfile-recursive
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

