#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "mavros_msgs/msg/position_target.hpp"

using namespace std::chrono_literals;
using PositionTarget = mavros_msgs::msg::PositionTarget;

class CmdVelBridge : public rclcpp::Node
{


  public:
    CmdVelBridge()
    : Node("cmd_vel_bridge")
    {
      double rate_hz = declare_parameter<double>("rate_hz", 20.0);
      setpoint_pub_ = create_publisher<PositionTarget>("/mavros/setpoint_raw/local", 10);
      timer_ = create_wall_timer(1s, [this]() { publish_setpoint(0.0, 0.0); });
      RCLCPP_INFO(get_logger(), "timeout %.2f s, rate %.1f Hz", timeout_s_, rate_hz);
    }

  private:
    double timeout_s_ = declare_parameter<double>("timeout_s", 0.5);
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<PositionTarget>::SharedPtr setpoint_pub_;

    void publish_setpoint(double vx, double yaw_rate_cmd) {
      PositionTarget msg;
      msg.header.stamp = now();
      msg.header.frame_id = "base_link";
      msg.coordinate_frame = PositionTarget::FRAME_BODY_NED;
      msg.type_mask = 
        PositionTarget::IGNORE_PX
      | PositionTarget::IGNORE_PY
      | PositionTarget::IGNORE_PZ
      | PositionTarget::IGNORE_AFX
      | PositionTarget::IGNORE_AFY
      | PositionTarget::IGNORE_AFZ
      | PositionTarget::IGNORE_YAW
      ;
      msg.velocity.x = vx;
      msg.yaw_rate = yaw_rate_cmd;
      setpoint_pub_->publish(msg);
    }
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdVelBridge>());
  rclcpp::shutdown();
  return 0;
}