# https://www.gnu.org/software/make/manual/make.html
.PHONY: all
all:

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
# targets
########################################################################

.PHONY: clean
clean:

pip_compile=pipx run \
	$(if $(wildcard requirements.bootstrap.txt),\
		--pip-args '-r requirements.bootstrap.txt' --spec='pip',\
		--spec='pip-tools<6')\
	pip-compile


all: requirements-txt

.PHONY: requirements-txt
requirements-txt: ## lock requirements
requirements-txt: $(foreach filename,$(wildcard requirements*.in),$(filename:.in=.txt))

requirements%.txt: requirements%.in
	$(pip_compile) --quiet --generate-hashes --output-file $(@) $(<)



########################################################################
# boiler plate
########################################################################

.PHONY: help
help: ## Show this message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(current_makefile) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## dirs ...
.PRECIOUS: %/
%/:
	mkdir -vp $(@)

.PHONY: clean-%/
clean-%/:
	@{ test -d $(*) && { set -x; rm -vr $(*); set +x; } } || echo "directory $(*) does not exist ... nothing to clean"
