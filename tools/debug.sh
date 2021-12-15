#!/bin/bash
set -eu -o pipefail

docker container run \
  --name calc_dubug$$ \
  -it \
  --rm \
  -u "$(id -u):$(id -g)" \
  -v "$PWD"/calc.py:/calc.py:ro \
  -v "$PWD"/.mypy_cache:/.mypy_cache \
  shakiyam/calc_dev "$@"
