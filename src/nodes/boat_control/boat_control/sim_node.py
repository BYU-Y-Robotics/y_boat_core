import math
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

# Standard ROS 2 messages (Available in all standard ROS 2 images)
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

# Optional MAVROS messages (graceful fallback if not installed in Docker image)
try:
    from mavros_msgs.msg import State, PositionTarget
    from mavros_msgs.srv import SetMode, CommandBool
    HAS_MAVROS = True
except ImportError:
    HAS_MAVROS = False

SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
    durability=DurabilityPolicy.VOLATILE,
)


class BlueBoatDriveTest(Node):
    def __init__(self):
        super().__init__('blueboat_drive_test')

        self.state = None
        self.odom = None

        if HAS_MAVROS:
            self.create_subscription(State, '/mavros/state', self._state_cb, 10)
            self.sp_pub = self.create_publisher(PositionTarget, '/mavros/setpoint_raw/local', 10)
            self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
            self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
            self.get_logger().info("Using MAVROS interface (auto-arming and mode control enabled).")
        else:
            self.twist_pub = self.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
            self.get_logger().info("Using standard ROS 2 geometry_msgs interface (mavros_msgs not required).")

        self.create_subscription(Odometry, '/mavros/local_position/odom', self._odom_cb, SENSOR_QOS)
        self.get_logger().info("DRIVE TEST NODE INITIALIZED...")

    def _state_cb(self, msg):
        self.state = msg

    def _odom_cb(self, msg):
        self.odom = msg

    def set_mode(self, mode_name: str) -> bool:
        if not HAS_MAVROS:
            return False
        if not self.mode_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().warn("Service /mavros/set_mode is not available.")
            return False
        req = SetMode.Request()
        req.custom_mode = mode_name
        future = self.mode_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        return future.result().mode_sent if future.result() else False

    def set_armed(self, arm: bool) -> bool:
        if not HAS_MAVROS:
            return False
        if not self.arm_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().warn("Service /mavros/cmd/arming is not available.")
            return False
        req = CommandBool.Request()
        req.value = arm
        future = self.arm_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        return future.result().success if future.result() else False

    def send_velocity(self, forward_mps: float, yaw_rate_radps: float = 0.0):
        if HAS_MAVROS:
            msg = PositionTarget()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "base_link"
            msg.coordinate_frame = PositionTarget.FRAME_BODY_NED
            msg.type_mask = (
                PositionTarget.IGNORE_PX | PositionTarget.IGNORE_PY | PositionTarget.IGNORE_PZ |
                PositionTarget.IGNORE_AFX | PositionTarget.IGNORE_AFY | PositionTarget.IGNORE_AFZ |
                PositionTarget.IGNORE_YAW
            )
            msg.velocity.x = forward_mps
            msg.velocity.y = 0.0
            msg.velocity.z = 0.0
            msg.yaw_rate = yaw_rate_radps
            self.sp_pub.publish(msg)
        else:
            msg = Twist()
            msg.linear.x = forward_mps
            msg.angular.z = yaw_rate_radps
            self.twist_pub.publish(msg)

    def run_test(self):
        self.get_logger().info("Connecting to simulation...")
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.odom is not None:
                self.get_logger().info("Connected to vehicle telemetry!")
                break

        start_x = self.odom.pose.pose.position.x
        start_y = self.odom.pose.pose.position.y
        self.get_logger().info(f"Starting Position: ({start_x:.2f}, {start_y:.2f})")

        if HAS_MAVROS:
            self.set_mode("GUIDED")
            self.set_armed(True)
        else:
            self.get_logger().info("Note: In standard ROS mode, ensure vehicle is armed & in GUIDED mode via QGC or SITL.")

        self.get_logger().info("Driving forward at 1.5 m/s for 3.0 seconds...")

        t_end = time.time() + 3.0
        while time.time() < t_end and rclpy.ok():
            self.send_velocity(forward_mps=1.5, yaw_rate_radps=0.0)
            rclpy.spin_once(self, timeout_sec=0.1)

        for _ in range(5):
            self.send_velocity(forward_mps=0.0, yaw_rate_radps=0.0)
            rclpy.spin_once(self, timeout_sec=0.1)

        if HAS_MAVROS:
            self.set_armed(False)
            self.set_mode("HOLD")

        rclpy.spin_once(self, timeout_sec=0.5)
        end_x = self.odom.pose.pose.position.x
        end_y = self.odom.pose.pose.position.y
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

        print("\n" + "=" * 55)
        print("               DRIVE TEST PROOF SUMMARY")
        print("=" * 55)
        print(f"  Starting Coordinate : ({start_x:.2f}, {start_y:.2f})")
        print(f"  Ending Coordinate   : ({end_x:.2f}, {end_y:.2f})")
        print(f"  Distance Traveled   : {distance:.2f} meters")
        if distance > 1.0:
            print("  [SUCCESS] Closed-loop control verified with simulation!")
        else:
            print("  [WARNING] Vessel displacement was under 1.0m. (Check arming status).")
        print("=" * 55 + "\n")


def main(args=None):
    rclpy.init(args=args)
    tester = BlueBoatDriveTest()
    try:
        tester.run_test()
    except KeyboardInterrupt:
        tester.get_logger().warn("Test interrupted by user! Halting...")
        tester.send_velocity(0.0, 0.0)
        if HAS_MAVROS:
            tester.set_armed(False)
            tester.set_mode("HOLD")
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()