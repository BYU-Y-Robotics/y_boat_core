#!/usr/bin/env bash
# Start the Foxglove bridge (connect to ws://localhost:8765).
# Extra ROS args pass through, e.g.: ./scripts/foxglove.sh -p use_sim_time:=true
source /opt/ros/jazzy/setup.bash
WORKSPACE="$(dirname "$0")/.."
[ -f "$WORKSPACE/install/setup.bash" ] && source "$WORKSPACE/install/setup.bash"
exec ros2 run foxglove_bridge foxglove_bridge --ros-args -p port:=8765 "$@"