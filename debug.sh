#!/bin/bash
set -eu -o pipefail

docker container run \
  --name calc_dubug$$ \
  -it \
  --rm \
  -v "$PWD"/calc.py:/calc.py \
  -v "$PWD"/.mypy_cache:/.mypy_cache \
  shakiyam/calc_dev "$@"
