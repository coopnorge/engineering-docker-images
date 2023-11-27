# https://www.gnu.org/software/make/manual/make.html
# Configure the shell.
SHELL=bash
.SHELLFLAGS=-ec -o pipefail
PYTHON_BIN?=python
py_source=./src ./tests

# Capture the current makefile.
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dir:=$(dir $(abspath $(current_makefile)))

venv_dir=.venv
poetry=$(PYTHON_BIN) -m poetry

PYTHON_PROJECT_PATH?=.

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

.PHONY: configure
configure: $(venv_dir) ## comfigure the project
poetry-install $(venv_dir): ## installs the project dependencies
	$(poetry) install

.PHONY: validate
validate: validate-static test

.PHONY: validate-static
validate-static: configure ## perform static validation
	$(poetry) run mypy --show-error-codes --show-error-context \
		$(py_source)
	$(poetry) run codespell $(py_source)
	$(poetry) run isort --check $(py_source)
	$(poetry) run black --check $(py_source)
	$(poetry) run flake8 $(py_source)
	$(poetry) export --without-hashes --dev --format requirements.txt

.PHONY: validate-fix
validate-fix: configure ## fix auto-fixable validation errors
	$(poetry) run pycln --expand-stars --all $(py_source)
	$(poetry) run isort $(py_source)
	$(poetry) run black $(py_source)

.PHONY: test
test: configure ## run the project's tests
	$(poetry) run pytest --cov-config=pyproject.toml --cov-report term --cov-report xml --cov=src ./tests

.PHONY: test-verbose
test-verbose: configure ## run the project's tests with verbose output
	$(poetry) run pytest -rA --log-level DEBUG --cov-config=pyproject.toml --cov-report term --cov-report xml --cov=src ./tests