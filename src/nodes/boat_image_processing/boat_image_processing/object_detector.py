import rclpy
from rclpy.node import Node


class ObjectDetector(Node):
    def __init__(self) -> None:
        super().__init__('object_detector')
        self.get_logger().info('Object Detector started')


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObjectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
