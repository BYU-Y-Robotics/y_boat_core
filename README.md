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

### Copy Secrets File
Copy the .env-example file into .env
```bash
cp .env-example .env
```
Update this .env file with the appropriate configuration for your environment

### Make the Scripts executables
```bash
chmod +x ./scripts/run.sh
```

### Build and Run the Container
To test that everything is set up correctly, build and run the container with:
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

Check out the tutorials in [ROS2 Demo] (https://github.com/byu-robotics-association/y_robotics_ros2_demo)

### ROS 2 Package Development

The `boat_perception` package uses a Python ROS 2 package layout. Its package-level launch file is:

```text
src/nodes/boat_perception/launch/boat_perception.launch.py
```

The launch file is the entry point for the perception stack. It currently starts the `lidar_processor` node. When adding another node, first add its executable to `setup.py`, then add another `Node` action to `boat_perception.launch.py`:

```python
Node(
	package='boat_perception',
	executable='new_node',
	name='new_node',
	output='screen',
),
```

After changing a node, launch file, or package configuration, rebuild and source the workspace:

```bash
colcon build --packages-select boat_perception --symlink-install
source install/setup.bash
```

Run the complete perception launch file with:

```bash
ros2 launch boat_perception boat_perception.launch.py
```

The repository also includes a VS Code debug configuration at `.vscode/launch.json`. Select `ROS2: Debug ROS 2 Launch File` from Run and Debug to debug the launch file and its nodes. This configuration targets the installed launch file, so rebuild the package before starting a debugging session after changing launch-related files.

### Sync with Changes
The following command will sync your local environment with origin/main
```bash
git fetch
git pull origin
```

If you want to sync with a different branch run
```bash
git fetch
git pull origin/your/branch/name
```


