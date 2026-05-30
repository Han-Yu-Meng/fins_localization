from fins import Node, Group, LaunchDescription, Agent, DefaultSource
from sensor import generate_sensor_group

def generate_fastlio_group():
    return Group([
        Node(
            package="FAST_LIO",
            name="FastLIO",
            inputs={
                "imu": "sensor/imu",
                "lidar": "sensor/lidar",
                "$T_{base}^{lidar}$": "tf/base_link_to_base_lidar"
            },
            outputs={
                "cloud": "lio/cloud",
                "cloud_body": "lio/cloud_body",
                "path": "lio/path",
                "odometry": "lio/odometry",
                "$T_{odom}^{base}$": "tf/odom_to_base_link"
            },
        ),
        Node(
            package="pointcloud_converter",
            name="PCL2ROS",
            inputs={"pcl_cloud": "lio/cloud"},
            outputs={"ros_cloud": "lio/ros_cloud"}
        ),
        Node(
            package="ros_bridge",
            name="PointCloudPublisher",
            parameters={"topic": "/cloud_registered"},
            inputs={"msg": "lio/ros_cloud"}
        ),
        Node(
            package="pointcloud_converter",
            name="PCL2ROS",
            inputs={"pcl_cloud": "lio/cloud"},
            outputs={"ros_cloud": "lio/ros_cloud"}
        ),
        Node(
            package="ros_bridge",
            name="PointCloudPublisher",
            parameters={"topic": "/cloud_registered"},
            inputs={"msg": "lio/ros_cloud"}
        ),
        Node(
            package="pointcloud_converter",
            name="PCL2ROS",
            inputs={"pcl_cloud": "lio/cloud_body"},
            outputs={"ros_cloud": "lio/ros_cloud_body"}
        ),
        Node(
            package="ros_bridge",
            name="PointCloudPublisher",
            parameters={"topic": "/cloud_registered_body"},
            inputs={"msg": "lio/ros_cloud_body"}
        ),
        Node(
            package="ros_bridge",
            name="TFBroadcaster",
            parameters={
                "from_frame_override": "odom",
                "to_frame_override": "base_link"
            },
            inputs={"transform": "tf/odom_to_base_link"}
        )
    ])

def generate_launch():
    return LaunchDescription(groups=[generate_sensor_group(), generate_fastlio_group()])

if __name__ == "__main__":
    with Agent(name="LocalLocalization", port=1896) as agent:
        with DefaultSource("fins_localization"):
            ld = generate_launch()
        agent.add_config("config/localize.yaml")
        agent.launch(ld)
        agent.spin()
