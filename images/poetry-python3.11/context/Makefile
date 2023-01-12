# https://www.gnu.org/software/make/manual/make.html
SHELL=bash
.PHONY: default
default:

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: poetry-generate-requirements
poetry-generate-requirements: requirements-poetry.in ## Generate requirements-poetry.txt
	pip-compile \
		--allow-unsafe \
		--annotate \
		--generate-hashes \
		--output-file requirements-poetry.txt \
		--rebuild \
		--resolver backtracking \
		--verbose \
		requirements-poetry.in

pip-tools-generate-requirements: requirements-pip-tools.in ## Generate requirements-pip-tools.txt
	pip-compile \
		--allow-unsafe \
		--annotate \
		--generate-hashes \
		--resolver backtracking \
		--output-file requirements-pip-tools.txt \
		--rebuild \
		--resolver backtracking \
		--verbose \
		requirements-pip-tools.in
