import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Header
from vision_msgs.msg import Detection2DArray, Detection3DArray
from sensor_msgs.msg import PointCloud2
from message_filters import ApproximateTimeSynchronizer, Subscriber

class ObjectAssociation(Node):

    def __init__(self):
        super().__init__('object_association')

        detection_subscription = Subscriber( self, Detection2DArray, 'camera/detections')
        lidar_subscription = Subscriber(self, PointCloud2, 'lidar/point_cloud_rect', qos_profile=qos_profile_sensor_data)

        self.syncronizer = ApproximateTimeSynchronizer([detection_subscription, lidar_subscription], queue_size=10, slop=0.06)
        self.syncronizer.registerCallback(self.on_synced)

        self.publisher = self.create_publisher(Detection3DArray, 'object/detections', 10)

    def on_synced(self, det_msg: Detection2DArray, cloud_msg: PointCloud2) -> None:
        # right now, this is just going to publish an empty detection array
        msg = Detection3DArray()
        msg.header = Header(stamp=det_msg.header.stamp, frame_id=cloud_msg.header.frame_id)
        self.publisher.publish(msg)
        return




def main(args=None):
    rclpy.init(args=args)
    node = ObjectAssociation()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()