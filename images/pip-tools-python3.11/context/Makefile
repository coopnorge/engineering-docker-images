# https://www.gnu.org/software/make/manual/make.html
SHELL=bash
.PHONY: default
default:

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: pip-tools-generate-requirements
pip-tools-generate-requirements: docker-compose/requirements-pip-tools.txt ## Generate requirements-pip-tools.txt

requirements.txt: requirements.in
	pip-compile \
		--allow-unsafe \
		--annotate \
		--generate-hashes \
		--resolver backtracking \
		--output-file $(@) \
		--rebuild \
		--resolver backtracking \
		--verbose \
		$(<)

generate-requirements: requirements.txt  ## Generate requirements-poetry.txt
