import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

# Types of images this thing reads from.
from boat_perception.image_feed import FEED_FACTORIES, ImageFeed

REOPEN_AFTER_FAILURES = 30  # consecutive empty reads before we close + reopen the feed

# ImageFeedNode gets information from the feeds and posts it to camera/image_raw
class ImageFeedNode(Node):
    """Publishes frames from a configurable ImageFeed onto camera/image_raw."""

    def __init__(self):
        super().__init__("image_feed_node")

        self.declare_parameter("feed_type", "webcam") # default feed
        self.declare_parameter("publish_rate_hz", 10.0)
        self.declare_parameter("frame_id", "camera")
        self.declare_parameter("webcam_device", 0)
        self.declare_parameter("image_width", 640)
        self.declare_parameter("image_height", 480)
        self.declare_parameter("image_fps", 30)
        self.declare_parameter("image_fourcc", "MJPG")

        feed_type = self.get_parameter("feed_type").value
        if feed_type not in FEED_FACTORIES:
            raise ValueError(
                f"Unknown feed_type '{feed_type}'. Available: {sorted(FEED_FACTORIES)}"
            )

        self._feed: ImageFeed = FEED_FACTORIES[feed_type](self)
        self._feed.open()

        self._bridge = CvBridge()
        self._frame_id = self.get_parameter("frame_id").value
        self._publisher = self.create_publisher(Image, "camera/image_raw", 10)

        rate_hz = self.get_parameter("publish_rate_hz").value
        self._timer = self.create_timer(1.0 / rate_hz, self._on_timer)

        self.get_logger().info(
            f"Publishing from '{feed_type}' feed at {rate_hz} Hz "
            "-- this node runs forever, like a server; that's normal, not a hang. "
            "Ctrl+C to stop."
        )

        self._frames_published = 0
        self._failures = 0

    def _reopen_feed(self) -> None:
        self.get_logger().warn("Too many empty reads; reopening feed")
        self._failures = 0
        self._feed.close()
        try:
            self._feed.open()
        except RuntimeError as exc:
            # Not fatal: the next 30 empty reads trigger another attempt.
            self.get_logger().error(str(exc), throttle_duration_sec=5.0)

    def _on_timer(self) -> None:
        frame = self._feed.read()
        if frame is None:
            self._failures += 1
            self.get_logger().warn("Feed returned no frame", throttle_duration_sec=5.0)
            if self._failures >= REOPEN_AFTER_FAILURES:
                self._reopen_feed()
            return
        self._failures = 0

        msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        self._publisher.publish(msg)

        self._frames_published += 1
        self.get_logger().info(
            f"Published {self._frames_published} frames so far", throttle_duration_sec=5.0
        )

    def destroy_node(self) -> bool:
        self._feed.close()
        return super().destroy_node()


def main():
    rclpy.init()
    node = ImageFeedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

# Run this to get it working with synthetic data    
# cd /workspace
# source /opt/ros/jazzy/setup.bash
# source install/setup.bash
# ros2 run boat_perception image_feed_node --ros-args -p feed_type:=synthetic