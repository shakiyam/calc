#!/bin/bash
set -eu -o pipefail

docker container run \
  --name flake8$$ \
  --rm \
  -u "$(id -u):$(id -g)" \
  -v "$PWD":/work:ro \
  shakiyam/flake8 "$@"
