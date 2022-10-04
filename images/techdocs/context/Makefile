# https://www.gnu.org/software/make/manual/make.html
SHELL=bash
.PHONY: default
default:

docker=docker
docker_compose=$(docker) compose
docker_compose_run=$(docker_compose) run --rm -T

.PHONY: help
help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

requirements-%.txt: requirements-%.in
	$(docker_compose_run) pip-tools pip-compile \
		--verbose \
		--annotate \
		--generate-hashes \
		--rebuild \
		--resolver backtracking \
		--output-file $(@) \
		$(<)
requirements-pip-tools.txt: ## Generate requirements-pip-tools.txt
requirements-techdocs.txt: ## Generate requirements-techdocs.txt

package-lock.json: package.json ## Generate requirements-techdocs.txt
	$(docker_compose_run) npm-tools npm install \
		--package-lock-only
