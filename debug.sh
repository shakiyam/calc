#!/bin/bash
set -eu -o pipefail

docker container run \
  --name calc_dubug$$ \
  -it \
  --rm \
  -v "$PWD"/calc.py:/calc.py \
  --entrypoint /bin/ash \
  shakiyam/calc "$@"
