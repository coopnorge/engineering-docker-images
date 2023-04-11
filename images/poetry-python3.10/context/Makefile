# https://www.gnu.org/software/make/manual/make.html
SHELL=bash
.PHONY: default
default:

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: generate-requirements
generate-requirements: requirements.txt ## Generate requirements-poetry.txt

requirements.txt: requirements.in
	pip-compile \
		--allow-unsafe \
		--annotate \
		--generate-hashes \
		--output-file requirements.txt \
		--rebuild \
		--resolver backtracking \
		--verbose \
		requirements.in
