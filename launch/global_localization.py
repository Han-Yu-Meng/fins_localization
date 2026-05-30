from fins import Node, Group, LaunchDescription, Agent, DefaultSource
from sensor import generate_sensor_group
from local_localization import generate_fastlio_group
from executor import generate_executor_group

def generate_global_localization_group():
    return Group([
        Node(
            package="global_localization",
            name="GlobalLocalization",
            inputs={
                "cloud": "lio/cloud",
                "$T_{odom}^{baselink}$": "tf/odom_to_base_link",
            },
            outputs={
                "global_map_viz": "global/map_viz",
                "aligned_cloud": "global/aligned_cloud",
                "$T_{map}^{odom}$": "tf/map_to_odom"
            },
        ),
        
        Node(
            package="ros_bridge",
            name="TFBroadcaster",
            parameters={
                "from_frame_override": "map",
                "to_frame_override": "odom"
            },
            inputs={
                "transform": "tf/map_to_odom"
            },
        ),
        Node(
            package="pointcloud_converter",
            name="PCL2ROS",
            inputs={
                "pcl_cloud": "global/map_viz",
            },
            outputs={
                "ros_cloud": "global/ros_map"
            },
        ),
        Node(
            package="ros_bridge",
            name="PointCloudPublisher",
            parameters={
                "topic": "/global_map"
            },
            inputs={
                "msg": "global/ros_map"
            },
        ),

        Node(
            package="pointcloud_converter",
            name="PCL2ROS",
            inputs={
                "pcl_cloud": "global/aligned_cloud",
            },
            outputs={
                "ros_cloud": "global/ros_aligned"
            },
        ),
        Node(
            package="ros_bridge",
            name="PointCloudPublisher",
            parameters={
                "topic": "/aligned_cloud"
            },
            inputs={
                "msg": "global/ros_aligned"
            },
        ),
    ])

def generate_launch():
    # 组合三部分：传感器 + 局部定位(FAST_LIO) + 全局定位
    return LaunchDescription(groups=[
        generate_sensor_group(),
        generate_fastlio_group(),
        generate_global_localization_group(),
    	generate_executor_group()
    ])

if __name__ == "__main__":
    with Agent(name="GlobalLocalization", port=1896) as agent:
        with DefaultSource("fins_localization"):
            ld = generate_launch()
        
        agent.add_config("config/fastlio_mid360.yaml")
        agent.add_config("config/global_localization.yaml")
        agent.launch(ld)
        agent.spin()
