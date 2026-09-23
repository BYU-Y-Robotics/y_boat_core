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
Start the development container:
```bash
./scripts/run.sh
```

Open a shell inside the container:
```bash
docker exec -it boat_dev bash
```

Inside the container, source ROS 2:
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
```

## ROS 2 Packages
All packages live in `src/` (mounted at `/workspace/src`).

### 1. Create a Package
```bash
cd /workspace/src
ros2 pkg create --build-type ament_python <package_name> --dependencies rclpy
```

### 2. Build a Package
Build your package individually from `/workspace`:
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
colcon build --symlink-install --packages-select boat_perception
source /workspace/install/setup.bash
ros2 run boat_perception lidar_processor
```

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
