# Minibot Xbox Joy Node
This is a ROS2 package for controlling a robot from EduArt with a xbox controller. All of the inputs of a controller are mapped in the source code and can be easily edited to send additional commands for your particular robot stack.

For the Eduart Minibot Robot first set the RMW implementation:

```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

and then run the launchfile to start the nodes:

```bash
ros2 launch minibot_xbox_joy controller.launch.py
```

also make sure both your robot and the pc running this node are on the same network and have the same Domain ID. Set the Domain ID like this:
```bash
export ROS_DOMAIN_ID=11
```
