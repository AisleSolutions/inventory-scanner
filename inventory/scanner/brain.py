# Copyright 2024 by AisleSolutions. All Rights Reserved. 
# 
# Source code is explicitly for meeting requirements requested by University
# of Calgary Entrepreneurial Capstone Design Project 2024. 
#
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying source code is explicitly forbidden. 

# from lidarprocessing.lidarscan import LidarScan
# from imageprocessing import image
# from ros2node import node
# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String

# from sensor_msgs.msg import LaserScan
# from std_msgs.msg import Header


import numpy


#this is the central ROS2 node for the entire scanning system.

class Brain(Node):
    def __init__(self):

        #Sets up subscription to node
        super().__init__('brain')
        self.subscription = self.create_subscription(
            LaserScan,
            'lidar_data',
            self.listener_callback,
            qos_profile=10
        )
        self.subscription
    def listener_callback(self,msg):
        self.get_logger().info(msg.data)

    

def main():
    rclpy.init()
    brain = Brain()
    brain.get_logger().info("Brain node initiated!")
    rclpy.spin(brain)
    print('Hi from inventoryscanner.')


def capture_image():
    # listens to topic 'camera'
    # pushes the string 'camera' to topic 'commands'
    a = 1


if __name__ == '__main__':
    #initiates the brain node
    main()