MAKEFLAGS += --warn-undefined-variables
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.SUFFIXES:

ALL_TARGETS := $(shell egrep -o ^[0-9A-Za-z_-]+: $(MAKEFILE_LIST) | sed 's/://')

.PHONY: $(ALL_TARGETS)

all: shellcheck shfmt hadolint flake8 update_requirements_dev build_dev mypy update_requirements build ## Lint, update requirements.txt, and build
	@:

build: ## Build image 'shakiyam/calc' from Dockerfile
	@echo -e "\033[36m$@\033[0m"
	@./tools/build.sh docker.io/shakiyam/calc Dockerfile

build_dev: ## Build image 'shakiyam/calc_dev' from Dockerfile.dev
	@echo -e "\033[36m$@\033[0m"
	@./tools/build.sh docker.io/shakiyam/calc_dev Dockerfile.dev

flake8: ## Lint Python code
	@echo -e "\033[36m$@\033[0m"
	@./tools/flake8.sh --max-line-length 100

hadolint: ## Lint Dockerfile
	@echo -e "\033[36m$@\033[0m"
	@./tools/hadolint.sh Dockerfile Dockerfile.dev

mypy: ## Lint Python code
	@echo -e "\033[36m$@\033[0m"
	@./tools/mypy.sh docker.io/shakiyam/calc_dev calc.py

shellcheck: ## Lint shell scripts
	@echo -e "\033[36m$@\033[0m"
	@./tools/shellcheck.sh calc tools/*.sh

shfmt: ## Lint shell scripts
	@echo -e "\033[36m$@\033[0m"
	@./tools/shfmt.sh -l -d -i 2 -ci -bn -kp calc tools/*.sh

update_requirements: ## Update requirements.txt
	@echo -e "\033[36m$@\033[0m"
	@./tools/pip-compile.sh --upgrade

update_requirements_dev: ## Update requirements_dev.txt
	@echo -e "\033[36m$@\033[0m"
	@./tools/pip-compile.sh requirements_dev.in --output-file requirements_dev.txt --upgrade

help: ## Print this help
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9A-Za-z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
