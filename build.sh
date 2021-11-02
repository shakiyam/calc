#!/bin/bash
set -eu -o pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: build.sh image_name Dockerfile"
  exit 1
fi

IMAGE_NAME="$1"
readonly IMAGE_NAME
CURRENT_IMAGE="$(docker image ls -q "$IMAGE_NAME":latest)"
readonly CURRENT_IMAGE
docker image build \
  -f "$2" \
  -t "$IMAGE_NAME" \
  "$(dirname "$0")"
LATEST_IMAGE="$(docker image ls -q "$IMAGE_NAME":latest)"
readonly LATEST_IMAGE
if [[ "$CURRENT_IMAGE" != "$LATEST_IMAGE" ]]; then
  docker image tag "$IMAGE_NAME":latest "$IMAGE_NAME":"$(date +%Y%m%d%H%S)"
fi
