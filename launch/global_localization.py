from fins import Node, Group, Agent, DefaultSource
from sensor import sensor_group
from fastlio import fastlio_group
from executor import executor_group

def global_localization_group():
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
                "$T_{map}^{odom}$": "tf/map_to_odom",
                "current_pose": "/current_pose"
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
            package="ros_bridge",
            name="PoseStampedPublisher",
            parameters={
                "topic": "/localization_pose"
            },
            inputs={
                "msg": "/current_pose"
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

if __name__ == "__main__":
    with Agent(name="global_localization") as agent:
        agent.add_config("config/fastlio_mid360.yaml")
        agent.add_config("config/global_localization.yaml")
        with DefaultSource("fins_localization"):
            agent.launch(
                sensor_group(),
                fastlio_group(),
                global_localization_group(),
                executor_group()
            )
        agent.spin()
