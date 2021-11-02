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
	@./build.sh shakiyam/calc Dockerfile

build_dev: ## Build image 'shakiyam/calc_dev' from Dockerfile_dev
	@echo -e "\033[36m$@\033[0m"
	@./build.sh shakiyam/calc_dev Dockerfile_dev

flake8: ## Lint Python code
	@echo -e "\033[36m$@\033[0m"
	@./flake8.sh --max-line-length 88

hadolint: ## Lint Dockerfile
	@echo -e "\033[36m$@\033[0m"
	@./hadolint.sh Dockerfile

mypy: ## Lint Python code
	@echo -e "\033[36m$@\033[0m"
	@./mypy.sh calc.py

shellcheck: ## Lint shell scripts
	@echo -e "\033[36m$@\033[0m"
	@./shellcheck.sh calc *.sh

shfmt: ## Lint shell scripts
	@echo -e "\033[36m$@\033[0m"
	@./shfmt.sh -l -d -i 2 -ci -bn -kp calc *.sh

update_requirements: ## Update requirements.txt
	@echo -e "\033[36m$@\033[0m"
	@./pip-compile.sh --upgrade

update_requirements_dev: ## Update requirements_dev.txt
	@echo -e "\033[36m$@\033[0m"
	@./pip-compile.sh requirements_dev.in --output-file requirements_dev.txt --upgrade

help: ## Print this help
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9A-Za-z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
