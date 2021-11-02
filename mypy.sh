#!/bin/bash
set -eu -o pipefail

docker container run \
  --name calc_mypy$$ \
  -t \
  --rm \
  -v "$PWD"/calc.py:/calc.py \
  -v "$PWD"/.mypy_cache:/.mypy_cache \
  --entrypoint /usr/local/bin/mypy \
  shakiyam/calc_dev "$@"
