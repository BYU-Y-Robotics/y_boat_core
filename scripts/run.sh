#!/usr/bin/env bash
set -euo pipefail

HARDWARE="${1:-linux}"
BRANCH="${2:-main}"
IMAGE="${3:-latest}"

if [ "${HARDWARE}" = "nano" ]; then
    echo "Running for Jetson Nano"
    export DOCKER_IMAGE="${IMAGE}-nano"
else
    echo "Running for Linux"
    export DOCKER_IMAGE="${IMAGE}"
fi

docker compose pull --ignore-buildable
docker compose up -d --build