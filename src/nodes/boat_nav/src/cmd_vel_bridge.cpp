#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "mavros_msgs/msg/position_target.hpp"
#include "geometry_msgs/msg/twist.hpp"


using namespace std::chrono_literals;
using PositionTarget = mavros_msgs::msg::PositionTarget;
using Twist = geometry_msgs::msg::Twist;

class CmdVelBridge : public rclcpp::Node
{


  public:
    CmdVelBridge()
    : Node("cmd_vel_bridge")
    {
      double rate_hz = declare_parameter<double>("rate_hz", 20.0);
      setpoint_pub_ = create_publisher<PositionTarget>("/mavros/setpoint_raw/local", 10);
      cmd_sub_ = create_subscription<Twist>("/cmd_vel", 10, [this](const Twist::SharedPtr msg) {cmd_vel_callback(msg);});
      timer_ = create_wall_timer(std::chrono::duration<double>(1.0 / rate_hz), [this]() { on_timer(); });
    }

  private:
    Twist last_cmd_;
    rclcpp::Time last_cmd_time_;
    bool has_cmd_ = false;
    double timeout_s_ = declare_parameter<double>("timeout_s", 0.5);
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<PositionTarget>::SharedPtr setpoint_pub_;
    rclcpp::Subscription<Twist>::SharedPtr cmd_sub_;

    void on_timer() {
      if(has_cmd_) {
        publish_setpoint(last_cmd_.linear.x, last_cmd_.angular.z);
      } else {
        publish_setpoint(0.0, 0.0);
      }
    }

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

    void cmd_vel_callback(const Twist::SharedPtr msg) {
      last_cmd_ = *msg;
      last_cmd_time_ = now();
      has_cmd_ = true;
      RCLCPP_INFO(get_logger(), "cmd: vx=%.2f wz=%.2f", last_cmd_.linear.x, last_cmd_.angular.z);
    }
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdVelBridge>());
  rclcpp::shutdown();
  return 0;
}