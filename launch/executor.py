from fins import Node, Group

def executor_group():
    return Group([
        Node(
            package="ros_bridge",
            name="TwistSubscriber",
            parameters={
                "topic": "/cmd_vel",
                "history": "Keep Last",
                "depth": "10",
                "reliability": "Reliable",
                "durability": "Volatile",
            },
            outputs={
                "msg": "/cmd_vel"
            },
        ),
        Node(
            package="Fines_Serial",
            name="SerialStation",
            parameters={
            	"port": "/dev/ttyACM0",
            	"baudrate": "921600"
            },
            inputs={
                "cmd_vel": "/cmd_vel"
            },
        )
    ])
