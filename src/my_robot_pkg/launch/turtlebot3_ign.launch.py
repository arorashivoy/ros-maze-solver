import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('my_robot_pkg')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    world = os.path.join(pkg, 'worlds', 'turtlebot3_world.sdf')
    robot_sdf = os.path.join(pkg, 'models', 'turtlebot3_burger_ign', 'model.sdf')
    urdf = os.path.join(tb3_gazebo, 'urdf', 'turtlebot3_burger.urdf')

    with open(urdf, 'r') as f:
        robot_desc = f.read()

    # IGN_GAZEBO_RESOURCE_PATH tells the Homebrew Gazebo binary where to find:
    #   model://turtlebot3_world  (maze walls)
    #   model://turtlebot3_common (meshes referenced by the robot SDF)
    ign_resource_path = ':'.join([
        pkg,
        os.path.join(tb3_gazebo, 'models'),
        os.environ.get('IGN_GAZEBO_RESOURCE_PATH', ''),
    ])

    # Launch Ignition Gazebo (Homebrew) with the world using its absolute path.
    # We do NOT rely on PATH for `ign` here — hardcoded to the Homebrew binary
    # to avoid any conda `ign` shadowing issues.
    gz_sim = ExecuteProcess(
        cmd=['/opt/homebrew/bin/ign', 'gazebo', '-s', '-r', world],
        additional_env={'IGN_GAZEBO_RESOURCE_PATH': ign_resource_path},
        output='screen',
    )

    # Spawn the robot 3 seconds after Gazebo starts (gives it time to initialize).
    # ros_gz_sim's `create` node sends a spawn request over Ignition transport.
    spawn_robot = TimerAction(
        period=3.0,
        actions=[Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-world', 'default',
                '-name', 'burger',
                '-file', robot_sdf,
                '-x', '-2.0', '-y', '-0.5', '-z', '0.01',
            ],
            output='screen',
        )],
    )

    # Bridge Ignition topics to ROS2 topics.
    # Format: /topic@ros_type[ign_type  (Ignition→ROS)
    #         /topic@ros_type]ign_type  (ROS→Ignition)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
        ],
        output='screen',
    )

    # Bridge Ignition's ground-truth world-frame poses to ROS2 as a PoseArray.
    # fake_scan_publisher reads poses[0] which is always the 'burger' model
    # (entity order is deterministic from the SDF). This is fully independent
    # of the /odom path that SLAM will consume.
    ground_truth_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/dynamic_pose/info@geometry_msgs/msg/PoseArray[ignition.msgs.Pose_V',
        ],
        output='screen',
    )

    # robot_state_publisher reads the URDF and publishes TF for all fixed/joint links.
    # use_sim_time=True makes it sync to the /clock topic from Gazebo.
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': True,
            'robot_description': robot_desc,
        }],
        output='screen',
    )

    return LaunchDescription([
        gz_sim,
        spawn_robot,
        bridge,
        ground_truth_bridge,
        robot_state_publisher,
    ])
