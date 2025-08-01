MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
ALL_TARGETS := $(shell grep -E -o ^[0-9A-Za-z_-]+: $(MAKEFILE_LIST) | sed 's/://')
.PHONY: $(ALL_TARGETS)
.DEFAULT_GOAL := help

all: lint update_requirements_dev build_dev mypy test update_requirements build ## Lint, update requirements.txt, test, and build

build: ## Build image 'shakiyam/calc' from Dockerfile
	@echo -e "\033[36m$@\033[0m"
	@./tools/build.sh ghcr.io/shakiyam/calc Dockerfile

build_dev: ## Build image 'shakiyam/calc_dev' from Dockerfile.dev
	@echo -e "\033[36m$@\033[0m"
	@./tools/build.sh ghcr.io/shakiyam/calc_dev Dockerfile.dev

flake8: ## Lint Python code
	@echo -e "\033[36m$@\033[0m"
	@./tools/flake8.sh --max-line-length 100

hadolint: ## Lint Dockerfile
	@echo -e "\033[36m$@\033[0m"
	@./tools/hadolint.sh Dockerfile Dockerfile.dev

help: ## Print this help
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9A-Za-z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

lint: flake8 hadolint shellcheck shfmt ## Lint for all dependencies

mypy: ## Lint Python code
	@echo -e "\033[36m$@\033[0m"
	@./tools/mypy.sh ghcr.io/shakiyam/calc_dev src/calc

shellcheck: ## Lint shell scripts
	@echo -e "\033[36m$@\033[0m"
	@./tools/shellcheck.sh calc tools/*.sh

shfmt: ## Lint shell scripts
	@echo -e "\033[36m$@\033[0m"
	@./tools/shfmt.sh -l -d -i 2 -ci -bn -kp calc tools/*.sh

test: ## Test Python code
	@echo -e "\033[36m$@\033[0m"
	@./calc_debug pytest -p no:cacheprovider tests/test_calc.py

update_requirements: ## Update requirements.txt
	@echo -e "\033[36m$@\033[0m"
	@./tools/uv.sh pip compile --strip-extras --output-file requirements.txt pyproject.toml

update_requirements_dev: ## Update requirements_dev.txt
	@echo -e "\033[36m$@\033[0m"
	@./tools/uv.sh pip compile --strip-extras --extra=dev --output-file requirements_dev.txt pyproject.toml
