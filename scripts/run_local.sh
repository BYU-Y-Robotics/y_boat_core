#!/usr/bin/env bash
#
# Build and run the dev container from the LOCAL Dockerfile, instead of pulling a
# published image.
#
# Use this when you need something that is in .docker/dockerfile.dev but has not been
# pushed to Docker Hub yet -- currently MAVROS, which boat_control needs to talk to the
# BlueBoat simulator.
#
# scripts/run.sh cannot do this: it runs `docker compose pull`, which fails for a tag
# that only exists locally.
#
#   ./scripts/run_local.sh              # build, then start the container
#   ./scripts/run_local.sh --no-build   # skip the build, just start it
#   ./scripts/run_local.sh --shell      # build, start, and drop into a shell
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

TAG="${TAG:-mavros-local}"
IMAGE_REF="yrobotics/y_boat_core:${TAG}"
DO_BUILD=1
DO_SHELL=0

for arg in "$@"; do
    case "${arg}" in
        --no-build) DO_BUILD=0 ;;
        --shell)    DO_SHELL=1 ;;
        *) echo "Unknown option: ${arg}"; exit 1 ;;
    esac
done

if [ ! -f .env ]; then
    echo "[run_local] No .env found; copying from .env-example."
    cp .env-example .env
fi

if [ "${DO_BUILD}" = "1" ]; then
    echo "[run_local] Building ${IMAGE_REF} from .docker/dockerfile.dev ..."
    docker build -f .docker/dockerfile.dev -t "${IMAGE_REF}" .
else
    echo "[run_local] Skipping build (--no-build)."
    if ! docker image inspect "${IMAGE_REF}" >/dev/null 2>&1; then
        echo "[run_local] ERROR: ${IMAGE_REF} does not exist locally. Run without --no-build."
        exit 1
    fi
fi

# No `docker compose pull` here on purpose -- the tag is local-only.
echo "[run_local] Starting container from ${IMAGE_REF} ..."
DOCKER_IMAGE="${TAG}" docker compose up -d

echo ""
echo "[run_local] Container 'boat_dev' is up using ${IMAGE_REF}"
echo "[run_local]   ROS_DOMAIN_ID=$(grep -E '^ROS_DOMAIN_ID=' .env | cut -d= -f2)  (must match the simulator)"
echo "[run_local]   shell:  docker exec -it boat_dev bash"
echo "[run_local]   build:  cd /workspace && colcon build --symlink-install --packages-select boat_control"
echo "[run_local]   run:    ros2 run boat_control drive_test"

if [ "${DO_SHELL}" = "1" ]; then
    exec docker exec -it boat_dev bash
fi
