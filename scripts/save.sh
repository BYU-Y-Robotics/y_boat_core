#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

BRANCH="${1:-main}"
IMAGE_TAG="${1:-latest}"
# REPO_DIR="/path/to/repo"

if [ -z "${1:-}" ]; then
    echo "Pushing to main"
    docker buildx build --platform linux/arm64,linux/amd64 -t yrobotics/y_boat_core:latest -f ./.docker/dockerfile.dev . --push

    docker buildx build --platform linux/arm64 -t yrobotics/y_boat_core:latest-nano -f ./.docker/dockerfile.nano . --push
fi 
# else
#     echo "Pushing Branch" 
#     docker build -t yrobotics/y_boat_core:${IMAGE_TAG} -f ../.docker/../
#     docker push yrobotics/y_boat_core:${IMAGE_TAG}
# fi

