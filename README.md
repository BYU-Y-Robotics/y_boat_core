# y_boat_core
This is the official BYU Robotics Association Boat Software, including all firmware needed for every microcontroller and 
## Getting Started with Development

### Prereqs
- Install docker on your system (follow instructions online for Windows, MacOS, or Linux)

### Clone Repo
```bash
git clone https://github.com/BYU-Y-Robotics/y_boat_core.git
cd y_boat_core
``` 

### Configuration
```bash
cp .env-example .env
```
Update this .env file with the appropriate configuration for your environment

### Make the Scripts executables
```bash
chmod +x ./scripts/run.sh
```

### Run Container & Enter Shell
Start the development container (run this on your **host**, not inside the container):
```bash
./scripts/run.sh
```
This opens the container and runs the ROS2 startup

For testing, run this as
```bash
./scripts/run.sh -i -p
```
The -i parameter makes it interactive, -p checks to make sure the docker image is updated and pulled correctly

Run this to test every change you make.

All packages should be created inside src/nodes/


### Sync with Changes
The following command will sync your local environment with origin/main

Open a shell inside the container:
```bash
docker exec -it boat_dev bash
```

ROS 2 and the workspace overlay are sourced automatically in interactive shells. If you
ever need to do it by hand:
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source /workspace/install/setup.bash    # only exists after a build
```

## ROS 2 Packages
All packages live in `src/nodes/` (mounted at `/workspace/src/nodes`).

### 1. Create a Package
Inside the container:
```bash
cd /workspace/src/nodes
ros2 pkg create --build-type ament_python <package_name> --dependencies rclpy
```

### 2. Build a Package
Always build from `/workspace`, never from `/workspace/src`. Building from `src/` creates a
second, competing `install/` overlay and it becomes ambiguous which one you have sourced.
```bash
cd /workspace
colcon build --symlink-install --packages-select <package_name>
```

### 3. Run a Node
```bash
source /workspace/install/setup.bash
ros2 run <package_name> <executable_name>
```

Example with the included perception package:
```bash
cd /workspace
colcon build --symlink-install --packages-select boat_perception
source /workspace/install/setup.bash
ros2 run boat_perception lidar_processor
```

## Connecting to the BlueBoat Simulator
`boat_control` drives the simulated boat over MAVROS. Note the executable is
`drive_test`, not `sim_node`:
```bash
cd /workspace
colcon build --symlink-install --packages-select boat_control
source /workspace/install/setup.bash
ros2 run boat_control drive_test
```

Requirements:
- The simulator must already be running and publishing MAVROS topics
  (`/mavros/state`, `/mavros/local_position/odom`).
- `ROS_DOMAIN_ID` must match between this container and the simulator. Both default
  to `10` via `.env`.
- This image ships `ros-$ROS_DISTRO-mavros`. That matters: without `mavros_msgs`,
  `sim_node.py` silently falls back to publishing `geometry_msgs/Twist` on
  `/mavros/setpoint_velocity/cmd_vel_unstamped`, which ArduPilot interprets in the
  **world ENU frame** — the boat then drives in a fixed compass direction regardless of
  its heading. With MAVROS present it uses `/mavros/setpoint_raw/local` with
  `FRAME_BODY_NED`, which is true body-frame control.

A successful run prints a drive-test summary and reports several metres of travel.

## Sync with Changes
```bash
git fetch
git pull origin
```

If you want to sync with a different branch run
```bash
git fetch
git pull origin/your/branch/name
```
