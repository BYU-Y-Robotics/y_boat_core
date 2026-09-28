#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class CmdVelBridge : public rclcpp::Node
{
  private:
    double timeout_s = declare_parameter<double>("timeout_s", 0.5);
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    CmdVelBridge()
    : Node("cmd_vel_bridge")
    {
      double rate_hz = declare_parameter<double>("rate_hz", 20.0);
      RCLCPP_INFO(get_logger(), "timeout %.2f s, rate %.1f Hz", timeout_s, rate_hz);
    }
   
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdVelBridge>());
  rclcpp::shutdown();
  return 0;
}