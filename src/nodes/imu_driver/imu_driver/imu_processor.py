import rclpy
from rclpy.node import Node

class ImuProcessor(Node):
    def __init__(self):
        super().__init__('stuff')
        self.get_logger().info("IMU is running")

def main(args=None):
    rclpy.init(args=args)
    node = ImuProcessor()
    rclpy.spin(node)
    node.destory_node()
    rclpy.shutdown()
#blah blah blah