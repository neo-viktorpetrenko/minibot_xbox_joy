#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Joy
from std_srvs.srv import SetBool


def clamp_index(seq, i, default):
    return seq[i] if i < len(seq) else default


class ControllerNode(Node):
    def __init__(self):
        super().__init__("controller_node")

        self.declare_parameter("in_topic", "/joy")
        self.declare_parameter("out_topic", "/edu_sml/joy")

        in_topic = self.get_parameter("in_topic").value
        out_topic = self.get_parameter("out_topic").value

        cmd_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE
        )

        self.sub = self.create_subscription(Joy, in_topic, self.controller_button_read, qos_profile_sensor_data)
        self.pub = self.create_publisher(Joy, out_topic, cmd_qos)

        self.get_logger().info(f"Listening on {in_topic}, publishing on {out_topic}")

        # Enable Service client
        self.enable_client = self.create_client(SetBool, '/edu_sml/enable')
        while not self.enable_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /edu_sml/enable service...')

        self.prev_start = 0  # for edge detection
        self.prev_select = 0

    def trigger_converter(v: float) -> float:
        # Convert Xbox trigger from 1..-1 to 0..1 for turning
        return (1.0 - v) * 0.5

    def controller_button_read(self, msg: Joy):
        # -----------------------------
        # Read axes individually (Xbox mapping)
        # -----------------------------
        left_stick_lr      = float(clamp_index(msg.axes, 0, 0.0))  # left stick left/right (1 -> -1)
        left_stick_fb      = float(clamp_index(msg.axes, 1, 0.0))  # left stick forward/back (1 -> -1)
        left_trigger       = float(clamp_index(msg.axes, 2, 1.0))  # left trigger (1 -> -1)
        right_stick_lr     = float(clamp_index(msg.axes, 3, 0.0))  # right stick left/right
        right_stick_fb     = float(clamp_index(msg.axes, 4, 0.0))  # right stick forward/back
        right_trigger      = float(clamp_index(msg.axes, 5, 1.0))  # right trigger (1 -> -1)
        dpad_lr            = float(clamp_index(msg.axes, 6, 0.0))  # dpad left/right
        dpad_fb            = float(clamp_index(msg.axes, 7, 0.0))  # dpad forward/back

        right_trigger = (1.0-right_trigger) * -0.5
        left_trigger  = (1.0 - left_trigger) * 0.5 + right_trigger

        # -----------------------------
        # Read buttons individually (Xbox mapping)
        # -----------------------------
        btn_a              = int(clamp_index(msg.buttons, 0, 0))
        btn_b              = int(clamp_index(msg.buttons, 1, 0))
        btn_x              = int(clamp_index(msg.buttons, 2, 0))
        btn_y              = int(clamp_index(msg.buttons, 3, 0))
        btn_lb             = int(clamp_index(msg.buttons, 4, 0))   # LB
        btn_rb             = int(clamp_index(msg.buttons, 5, 0))   # RB
        btn_select         = int(clamp_index(msg.buttons, 6, 0))   # select / back
        btn_start          = int(clamp_index(msg.buttons, 7, 0))   # start
        btn_home           = int(clamp_index(msg.buttons, 8, 0))   # home / xbox button
        btn_left_stick     = int(clamp_index(msg.buttons, 9, 0))   # left stick press
        btn_right_stick    = int(clamp_index(msg.buttons, 10, 0))  # right stick press

        # =========================================================
        # CHOOSE WHAT TO PUBLISH
        #
        # By default below: publish EVERYTHING (all axes + all buttons)
        # If you want to drop something, set it to 0.
        # If you want a different order, rearrange the list.
        # =========================================================

        out_axes = [
            left_stick_lr,
            left_stick_fb,
            left_trigger,
            right_stick_lr,
            right_stick_fb,
            right_trigger,
            dpad_lr,
            dpad_fb,
        ]

        out_buttons = [
            btn_a,
            btn_b,
            btn_x,
            btn_y,
            btn_lb,
            btn_rb,
            0,#btn_select,
            0,#btn_start,
            btn_home,
            btn_left_stick,
            btn_right_stick,
        ]

        out = Joy()
        out.header = msg.header  # keep original timestamp/frame_id
        out.axes = out_axes
        out.buttons = out_buttons

        self.pub.publish(out)

        # Start Button = Enable
        if btn_start == 1 and self.prev_start == 0:
            self.get_logger().info("Start pressed -> enabling")

            request = SetBool.Request()
            request.data = True

            self.enable_client.call_async(request)

        self.prev_start = btn_start

        # Select Button = Disable
        if btn_select == 1 and self.prev_select == 0:
            self.get_logger().info("Select pressed -> disabling")

            request = SetBool.Request()
            request.data = False

            self.enable_client.call_async(request)

        self.prev_select = btn_select


def main():
    rclpy.init()
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()