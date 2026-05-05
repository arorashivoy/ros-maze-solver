# 🤖 ROS2 Maze-Solving Robot — Learning Plan & Progress Tracker

> **Philosophy:** This plan treats the project as a vehicle for learning, not a race to completion.
> Every concept is explained *before* you implement it. Understanding why something works the way it
> does is more valuable than getting it to run. A PhD committee cares about your reasoning, not your GitHub streak.

---

## 📊 My Progress Dashboard

| Stage | Status | Confidence |
|-------|--------|------------|
| Stage 0 — Environment Setup | `[x] Done` | 🟩🟩🟩🟩⬜ |
| Stage 1 — ROS2 Fundamentals | `[x] Done` | 🟩🟩🟩🟩⬜ |
| Stage 2 — Gazebo & Turtlebot3 | `[x] Done` | 🟩🟩🟩🟨⬜ |
| Stage 3 — Sensor Reading | `[~] In Progress` | ⬜⬜⬜⬜⬜ |
| Stage 4 — Wall-Following Controller | `[ ] Not Started` | ⬜⬜⬜⬜⬜ |
| Stage 5 — SLAM & Mapping | `[ ] Not Started` | ⬜⬜⬜⬜⬜ |
| Stage 6 — Autonomous Navigation (Nav2) | `[ ] Not Started` | ⬜⬜⬜⬜⬜ |
| Stage 7 — Maze Solving | `[ ] Not Started` | ⬜⬜⬜⬜⬜ |

**Update status as:** `[ ] Not Started` → `[~] In Progress` → `[x] Done`

**Update confidence as:** ⬜ (nothing) → 🟨 (shaky) → 🟩 (solid)

---

## 🧠 Concept Mastery Tracker

Track every core concept independently. Be honest — "iffy" is fine, that's what this tracker is for.

| Concept | Status | Notes |
|---------|--------|-------|
| ROS2 nodes | ⬜ Not learned | |
| Topics & pub/sub | 🟨 Iffy | Verified via turtlesim talker/listener — DDS discovery auto-connects pub & sub by topic name + type |
| Services | ⬜ Not learned | |
| Actions | ⬜ Not learned | |
| Messages & interfaces | ⬜ Not learned | |
| QoS (Quality of Service) | ⬜ Not learned | |
| Packages & workspaces | 🟨 Iffy | Workspace = `src/` + colcon-generated `build/`, `install/`, `log/`. Out-of-source build keeps `src/` pristine. |
| colcon build system | 🟨 Iffy | Build compiles/installs packages + generates `install/setup.{bash,zsh}`. Sourcing overlays workspace on top of underlay (conda ROS2). |
| Launch files | ⬜ Not learned | |
| Parameters | ⬜ Not learned | |
| TF2 (transforms) | ⬜ Not learned | |
| URDF / robot description | 🟨 Iffy | Read by robot_state_publisher → publishes TF for all links/joints; Gazebo also reads URDF/SDF for simulation. |
| Gazebo simulation | 🟨 Iffy | Ignition Fortress (server-only on macOS). Physics + diff-drive plugin works; LiDAR sensors need GPU rendering — don't work headless on macOS. Workaround: fake_scan_publisher node. |
| RViz2 visualization | 🟨 Iffy | Read-only viewer of ROS2 topics; needs Fixed Frame set, displays added per-topic. Reliability QoS must match publisher (BEST_EFFORT for sensors). |
| LaserScan message | 🟨 Iffy | 360 floats in `ranges`; index↔angle via `angle_min + i * angle_increment`. Filter `inf`/`nan`. frame_id=`base_scan`. |
| Twist (velocity) message | 🟨 Iffy | `linear.x` = forward m/s; `angular.z` = yaw rate rad/s (CCW positive). Diff-drive robots ignore other components. |
| Odometry | 🟨 Iffy | Reports pose in **odom frame** (anchored to spawn pose, ≠ world frame). Drifts. Quaternion → yaw via atan2 formula. |
| SLAM concepts | ⬜ Not learned | |
| Occupancy grid maps | ⬜ Not learned | |
| Nav2 stack overview | ⬜ Not learned | |
| Costmaps | ⬜ Not learned | |
| Path planners (global) | ⬜ Not learned | |
| Path planners (local) | ⬜ Not learned | |
| Nav2 actions & goals | ⬜ Not learned | |
| Lifecycle nodes | ⬜ Not learned | |

**Update status as:** ⬜ Not learned → 🟨 Iffy → 🟩 Solid

---

## 📝 My Running Notes

> Use this section freely. Paste error messages, write your own explanations of concepts,
> draw ASCII diagrams, whatever helps you remember.

```
2026-04-18 — Stage 0 complete.
- Platform: M1 MacBook, ROS2 Humble via conda-forge in env `ros2`.
- `ROS_DISTRO=humble` auto-set on `conda activate ros2` (conda hook sources setup.bash for us).
- `ros2 pkg list` → 277 packages. turtlesim, ros_gz_bridge, ros_gz_interfaces present.
- Not yet installed: turtlebot3, slam_toolbox, nav2 (deferred to their stages).
- Gazebo is headless (server-only). Will use `--headless-rendering -s` / `gui:=false`.
- Turtlesim smoke test PASSED: turtlesim_node + turtle_teleop_key ran in two terminals,
  arrow keys moved the turtle → confirms pub/sub + DDS discovery working on M1.

Concept notes:
- Sourcing: `conda activate` sets up the package-manager view (PATH, CONDA_PREFIX, Python).
  `source setup.bash` adds ROS2-specific env vars (AMENT_PREFIX_PATH, CMAKE_PREFIX_PATH,
  PYTHONPATH for rclpy, ROS_DISTRO). Without sourcing, `import rclpy` fails.
- Why 277 small packages: ROS2 favors modularity — "use only what you need." Smaller
  footprint for embedded robots, independent versioning (nav2 ≠ rclpy release cadence),
  faster partial rebuilds. Cost: dependency-version mismatches, discovery friction.
- Pub/sub magic: two independent processes connected via DDS discovery (multicast UDP
  matches publishers & subscribers by topic name + message type). No central master.

2026-04-19 — Stage 1 started. Task 1.1 done.
- Workspace at ~/ros2_ws/ with src/ created; empty colcon build succeeded.
- Key concept: overlay vs underlay. `conda activate ros2` = underlay (base ROS2).
  `source install/setup.zsh` = overlay (my packages on top). AMENT_PREFIX_PATH shows
  overlay listed first (precedence).
- Out-of-source build pattern: src/ stays pristine, build/ = scratch, install/ = final
  product. Nuke-and-retry = `rm -rf build install log && colcon build`.
- setup.bash vs local_setup.bash: setup.* also sources the underlay chain;
  local_setup.* assumes underlay already sourced (for manual overlay stacking).

2026-05-05/06 — Stage 2 complete (with platform pivot).
- Tried Ignition Fortress: physics, diff-drive, /odom, /cmd_vel all work. LiDAR
  sensor (`type=lidar`) needs GPU rendering via ogre/ogre2 — fails on macOS in
  server-only mode (`-s`, the only mode that works on macOS per upstream issue #44).
- Tried Gazebo Classic 11: standalone gzserver works, but crashes inside
  `libgazebo_ros_init.so` with `boost::lock_error: pthread_mutex_lock: Invalid
  argument` on macOS arm64. Known long-standing gazebo_ros_pkgs bug on Apple Silicon.
- Decision: pivot to `fake_scan_publisher` Python node — generates synthetic
  LaserScan via ray-segment intersection from /odom pose against hardcoded walls.
  Pass 1: 5×5m square room (4 walls). Real Gazebo physics still runs in Ignition,
  so /odom and /cmd_vel are real.
- This is *good for learning* — wrote LaserScan from scratch, learned message
  fields, quaternion→yaw conversion, ray-segment math, BEST_EFFORT QoS.
- Key conceptual lesson: walls are virtual (only known to fake_scan_publisher).
  Robot can drive "through" them in Ignition. That's fine — Stage 4 wall-follower
  is what STOPS the robot, not physics. Real autonomy = perception→decision→action,
  not environmental constraints.

Concept notes (Stage 2):
- Odom frame ≠ world frame. /odom reports position relative to spawn pose. World
  frame is in Gazebo. They differ by a rigid transform. SLAM (Stage 5) reconciles
  them via a `map` frame.
- TF tree (top→bottom for our robot): odom → base_footprint → base_link →
  {base_scan, imu_link, wheel_left_link, wheel_right_link, caster_back_link}.
  base_footprint→base_link is a fixed offset; wheel transforms are dynamic
  (joint_states updates them).
- Quaternion→yaw (ground robot): yaw = atan2(2(wz + xy), 1 - 2(y² + z²)).
  For pure yaw rotation (x=y=0): yaw = 2·atan2(z, w).
- Ray-segment intersection: solve P(t)=Q(u) where P(t)=O+tD, Q(u)=A+u(B-A).
  Determinant det = sx·dy - sy·dx (sx,sy = segment direction). Hit iff t≥0 and
  0≤u≤1. Take min over all walls. Geometric meaning: "how far along this ray
  do I travel before crashing into something?"
```

---
---

# STAGE 0 — Environment Setup

## 🎯 Goal
Get ROS2 Humble installed on Ubuntu 22.04 and understand *what* you just installed.

## ⏱️ Estimated Time
2–4 hours (mostly waiting for downloads, not thinking time)

---

## 📖 Concept: What Even Is ROS2?

Before touching a terminal, understand what you're installing.

**ROS2 (Robot Operating System 2)** is not an operating system. It is a **middleware framework** —
a collection of tools, libraries, and conventions that help software on a robot communicate.

Imagine a real robot. It has:
- A camera producing images at 30fps
- A LiDAR spinning and producing distance readings
- A motor controller waiting for speed commands
- A brain (your code) making decisions

Each of these is a separate hardware component, often running on different chips or computers.
ROS2 solves the problem of: **how do all these pieces talk to each other?**

The answer is a **publish/subscribe communication system** built on top of **DDS
(Data Distribution Service)** — an industrial-grade networking standard. You write small
programs called **nodes**, each doing one job, and they exchange **messages** over named
channels called **topics**.

**Why ROS2 instead of ROS1?**

ROS1 was designed for a single robot, on a single computer, in a lab. It had a central
"master" process — if it crashed, everything died. ROS2 was redesigned from scratch for:
- Real-time performance
- No single point of failure (no master)
- Multi-robot systems
- Production-grade reliability (DDS)

**Humble Hawksbill** is the LTS (Long-Term Support) release — the stable, well-documented
choice for new learners. Always use Humble unless a specific package forces otherwise.

---

## ✅ Tasks

> **Note (2026-04-18):** Actual environment is **macOS (M1 MacBook) + ROS2 Humble via conda-forge**, not Ubuntu apt. Tasks 0.1–0.4 (Ubuntu install, apt sources, apt installs) are **N/A**. Verification (0.5) was performed and passed. See Running Notes for details.

### 0.1 — Install Ubuntu 22.04
If you don't already have it. A VM (VirtualBox/VMware) works but allocate at least:
- 4 CPU cores
- 8 GB RAM
- 40 GB disk

Native dual-boot is faster and preferred for Gazebo (GPU access).

**Status:** `[N/A — on macOS/conda, not Ubuntu]`

### 0.2 — Install ROS2 Humble

Follow the official guide exactly. Don't improvise.
```bash
# Add ROS2 apt repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install the full desktop version (includes RViz2, demos, etc.)
sudo apt update
sudo apt install ros-humble-desktop
```

**Status:** `[N/A — installed via conda-forge in env `ros2`; 277 packages present]`

### 0.3 — Source ROS2 in Every Terminal

ROS2 isn't automatically available in every terminal. You have to "source" it, which loads
all its environment variables (like where to find packages, executables, etc.).

```bash
# Do this every time you open a terminal, OR add it to ~/.bashrc to do it automatically
source /opt/ros/humble/setup.bash

# Add to ~/.bashrc permanently:
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

**Why does this exist?** Because you might have multiple ROS versions installed. Sourcing
tells the terminal *which* version to use.

**Status:** `[x]` — `conda activate ros2` auto-sources setup.bash via conda activation hook; `ROS_DISTRO=humble` confirmed.

### 0.4 — Install Gazebo & Turtlebot3

```bash
# Gazebo (Ignition Fortress is used with Humble)
sudo apt install ros-humble-gazebo-ros-pkgs

# Turtlebot3 packages
sudo apt install ros-humble-turtlebot3*

# Set the robot model environment variable
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
```

**Status:** `[deferred]` — ign gazebo installed system-level (headless). Turtlebot3 packages **not** installed yet; will add at Stage 2.

### 0.5 — Verification Test

Run this. If you see a small turtle window, your setup is working.
```bash
ros2 run turtlesim turtlesim_node
# In a second terminal:
ros2 run turtlesim turtle_teleop_key
```

**Status:** `[x]` — PASSED on M1 Mac 2026-04-18. GUI window opened, arrow keys drove the turtle. Confirms pub/sub + DDS discovery working.

---

## 🧠 Concept Check — Stage 0

> Answer these in your own words in the notes section above. Don't copy-paste.

1. What problem does ROS2 solve? Why not just write one big program?
2. What does "sourcing" a setup file do and why is it necessary?
3. What is DDS and why does ROS2 use it?

---
---

# STAGE 1 — ROS2 Fundamentals

## 🎯 Goal
Understand the core ROS2 communication model deeply. Write your own nodes from scratch.
No Gazebo yet — this is pure ROS2 on your laptop.

## ⏱️ Estimated Time
1–2 weeks (don't rush this — everything builds on it)

---

## 📖 Concept: The ROS2 Communication Model

ROS2 has **four ways** for nodes to communicate. Understanding when to use each is important.

### 1. Topics (Publish / Subscribe)
- **Use when:** Data flows continuously in one direction
- **Analogy:** A radio broadcast. The sender doesn't care who's listening. The listener
  doesn't care who's broadcasting.
- **Examples:** Camera images, LiDAR scans, robot velocity commands, GPS coordinates
- **Key property:** Asynchronous, non-blocking, many-to-many

```
[Camera Node] --publishes--> /camera/image --subscribes--> [Vision Node]
                                           --subscribes--> [Recording Node]
```

### 2. Services (Request / Response)
- **Use when:** You need a one-time answer to a one-time question
- **Analogy:** A phone call. You call, you wait, you get a response, call ends.
- **Examples:** "Is the robot's emergency stop triggered?", "Save the current map to disk",
  "Reset the robot's pose estimate"
- **Key property:** Synchronous, blocking, one-to-one

```
[My Node] --request--> /save_map --response--> [My Node]
                           ^
                     [Map Server Node]
```

### 3. Actions (Long-Running Tasks)
- **Use when:** A task takes time, and you want feedback while it runs + ability to cancel
- **Analogy:** Ordering food for delivery. You place an order (goal), get updates
  ("your food is being prepared", "driver is 5 mins away"), and can cancel anytime.
- **Examples:** "Navigate to position (3, 2)", "Pick up the object on the table",
  "Rotate 360 degrees and build a map"
- **Key property:** Asynchronous, has goal/feedback/result, cancellable
- **Used heavily by Nav2** — this is how you send navigation goals

```
[My Node] --goal--> /navigate_to_pose
          <--feedback-- (intermediate updates, e.g., distance remaining)
          <--result-- (success/failure when done)
```

### 4. Parameters
- **Use when:** You want configurable values that can be changed without recompiling
- **Analogy:** Settings/preferences in an app
- **Examples:** Maximum speed, obstacle detection threshold, map resolution
- **Key property:** Belong to a specific node, can be set at launch time or during runtime

---

## 📖 Concept: Packages & the Workspace

**A ROS2 workspace** is just a folder with a specific structure where you put your code.
Building this folder with `colcon` makes ROS2 aware of your packages.

```
ros2_ws/                     ← your workspace root
├── src/                     ← all your source code lives here
│   └── my_robot_pkg/        ← a package (one logical unit of code)
│       ├── package.xml      ← metadata: name, dependencies, version
│       ├── setup.py         ← tells Python where your nodes are
│       ├── setup.cfg        ← configuration for setup.py
│       └── my_robot_pkg/    ← Python module (same name as package)
│           ├── __init__.py
│           └── wall_follower.py   ← your actual node code
├── build/                   ← generated by colcon, don't touch
├── install/                 ← generated by colcon, don't touch
└── log/                     ← generated by colcon, don't touch
```

**`colcon`** is the build tool. It reads all packages in `src/`, builds them, and puts
the results in `install/`. After building, you source `install/setup.bash` to make your
packages available.

---

## 📖 Concept: Anatomy of a ROS2 Node (Python)

```python
import rclpy                          # The ROS2 Python library
from rclpy.node import Node           # Base class for all nodes
from std_msgs.msg import String       # A built-in message type

class MyFirstNode(Node):
    def __init__(self):
        # ALWAYS call super().__init__() with your node's name
        # This name appears in ros2 node list and in logs
        super().__init__('my_first_node')

        # Create a publisher:
        # - publishes String messages
        # - on the topic '/hello_world'
        # - with a queue size of 10 (how many messages to buffer)
        self.publisher_ = self.create_publisher(String, '/hello_world', 10)

        # Create a timer that calls self.timer_callback every 1.0 seconds
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info('Node started!')   # Like print(), but goes to ROS logs

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello from ROS2!'
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)              # Initialize ROS2 communication
    node = MyFirstNode()
    rclpy.spin(node)                   # Keep the node alive, processing callbacks
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**`rclpy.spin(node)`** is the event loop. It keeps the node running and processes any
incoming messages or timer callbacks. Without it, the node would run `__init__` and exit.

---

## 📖 Concept: QoS (Quality of Service)

Every topic in ROS2 has a **QoS policy** that controls reliability and history behavior.
The two most important settings:

| Setting | RELIABLE | BEST_EFFORT |
|---------|----------|-------------|
| Behavior | Guarantees delivery, retransmits if needed | Fire-and-forget |
| Use for | Commands, critical data | Sensor streams (losing one frame is okay) |

**History / Queue Size** — how many messages to buffer when a subscriber is slow.

For beginners: use the default `10` for queue size and don't worry about QoS policies
until you hit issues. But know it exists — Nav2 and sensor topics sometimes have
mismatched QoS policies that cause silent communication failures.

---

## ✅ Tasks

### 1.1 — Create Your Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build          # Build the (empty) workspace
source install/setup.bash
```

**Status:** `[x]` — 2026-04-19. Empty workspace built successfully (`Summary: 0 packages finished`). After sourcing `install/setup.zsh`, `AMENT_PREFIX_PATH` shows workspace overlay ahead of conda underlay.

### 1.2 — Create Your First Package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_robot_pkg
```

This creates the directory structure described above. Look at every file it created
and understand what it does before moving on.

**Status:** `[ ]`

### 1.3 — Write a Publisher Node

Create `~/ros2_ws/src/my_robot_pkg/my_robot_pkg/hello_publisher.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class HelloPublisher(Node):
    def __init__(self):
        super().__init__('hello_publisher')
        self.pub = self.create_publisher(String, '/hello', 10)
        self.timer = self.create_timer(0.5, self.publish_message)
        self.count = 0

    def publish_message(self):
        msg = String()
        msg.data = f'Hello #{self.count}'
        self.pub.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = HelloPublisher()
    rclpy.spin(node)
    rclpy.shutdown()
```

Register it in `setup.py` under `console_scripts`:
```python
entry_points={
    'console_scripts': [
        'hello_publisher = my_robot_pkg.hello_publisher:main',
    ],
},
```

Build and run:
```bash
cd ~/ros2_ws && colcon build --packages-select my_robot_pkg
source install/setup.bash
ros2 run my_robot_pkg hello_publisher
```

In a second terminal:
```bash
ros2 topic echo /hello         # Watch the messages live
ros2 topic hz /hello           # Check the publish rate
ros2 topic info /hello         # See publisher/subscriber count
```

**Status:** `[x]` — 2026-04-26. Publisher running at 2 Hz on `/hello`; `ros2 node list`, `topic echo`, `topic info`, and `topic hz` all confirmed expected output.

### 1.4 — Write a Subscriber Node

Create `hello_subscriber.py` that subscribes to `/hello` and prints the message.
Try this yourself first before looking anything up. The pattern mirrors the publisher.

```python
# Hint: use self.create_subscription(String, '/hello', self.callback, 10)
# The callback receives the message as its argument
```

**Status:** `[x]` — 2026-04-26. Subscriber on `/hello` working; verified subscriber-first / publisher-second yields `Hello #0` because timer's 0.5 s pre-roll covers DDS discovery latency.

### 1.5 — Write a Service (Optional but recommended)

```bash
# See all available service types:
ros2 interface list | grep srv

# A simple example: create a node that provides an "add two integers" service
# ros2 service type: example_interfaces/srv/AddTwoInts
```

Create a service server that takes two integers and returns their sum.
Then call it from the command line with `ros2 service call`.

**Status:** `[ ]`

### 1.6 — Write a Launch File

Launch files let you start multiple nodes with one command and set parameters.
In Python (ROS2 Humble uses Python launch files):

Create `my_robot_pkg/launch/hello_launch.py`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_pkg',
            executable='hello_publisher',
            name='publisher_node',
            output='screen',
        ),
        Node(
            package='my_robot_pkg',
            executable='hello_subscriber',
            name='subscriber_node',
            output='screen',
        ),
    ])
```

Run it:
```bash
ros2 launch my_robot_pkg hello_launch.py
```

**Status:** `[x]` — 2026-04-28. Launch file starts both nodes with overridden names (`publisher_node`, `subscriber_node`); interleaved log output confirmed. Required `glob('launch/*.py')` in `setup.py` data_files so colcon installs the launch script.

---

## 🛠️ Essential CLI Commands — Learn These by Heart

```bash
# Nodes
ros2 node list                    # List all running nodes
ros2 node info /node_name         # Show topics, services, actions of a node

# Topics
ros2 topic list                   # List all active topics
ros2 topic echo /topic_name       # Print messages on a topic
ros2 topic hz /topic_name         # Measure publish rate
ros2 topic info /topic_name       # Publisher/subscriber count, message type
ros2 topic pub /topic std_msgs/msg/String "data: 'hi'"  # Manually publish

# Interfaces (message/service/action types)
ros2 interface show std_msgs/msg/String      # Show the fields of a message type
ros2 interface list                          # List all known interfaces

# Packages
ros2 pkg list                     # List all installed packages
ros2 pkg executables my_robot_pkg # List executables in a package
```

---

## 🧠 Concept Check — Stage 1

1. What's the difference between a topic and a service? Give a robot-specific example of each.
2. When would you use an action instead of a service?
3. What does `rclpy.spin()` do? What happens if you don't call it?
4. Why do you need to `source install/setup.bash` after every build?
5. What is `package.xml` for? What is `setup.py` for?

---
---

# STAGE 2 — Gazebo & Turtlebot3 Teleoperation

## 🎯 Goal
Spawn a robot in a Gazebo simulation. Understand the simulated world.
Drive the robot manually and visualize it in RViz2.

## ⏱️ Estimated Time
3–5 days

---

## 📖 Concept: What Is Gazebo?

**Gazebo** is a physics simulator. It simulates:
- A 3D world (walls, floors, objects)
- Robot bodies (links, joints, mass, inertia)
- Sensors (LiDAR, cameras, IMU) with realistic noise
- Physics (gravity, friction, collisions)

Gazebo communicates with ROS2 through **plugins** — these are pieces of code inside
Gazebo that publish sensor data as ROS2 topics and subscribe to velocity commands.

From your ROS2 node's perspective, **it cannot tell the difference between a real robot
and a Gazebo simulation**. It subscribes to `/scan` and it gets laser data — whether
that data comes from a real LiDAR or a simulated one doesn't matter to your node.
This is the superpower of simulation.

---

## 📖 Concept: URDF — Describing a Robot

**URDF (Unified Robot Description Format)** is an XML file that describes a robot's
physical structure:

- **Links** — rigid bodies (chassis, wheel, sensor mount)
- **Joints** — connections between links (fixed, revolute, continuous)
- Physical properties: mass, inertia, visual meshes, collision geometry

Gazebo reads the URDF to know how to simulate the robot. You don't need to write
one from scratch — Turtlebot3 provides its URDF. But understanding the concept is
essential because every robot you'll work with has one.

---

## 📖 Concept: TF2 (Transform Tree)

**TF2** is ROS2's coordinate frame system. Every physical frame of reference
(the robot body, each wheel, the LiDAR, the map) has a name, and TF2 tracks
the geometric relationship between all of them over time.

```
map
└── odom
    └── base_footprint
        └── base_link
            ├── wheel_left_link
            ├── wheel_right_link
            └── base_scan          ← the LiDAR frame
```

When your LiDAR detects a wall 0.5m in front of the sensor, TF2 lets you transform
that reading into map coordinates. Nav2 uses TF2 constantly for everything.

**RViz2** visualizes the TF tree — use `ros2 run tf2_tools view_frames` to see it
as a PDF diagram.

---

## 📖 Concept: Odometry

**Odometry** is the robot's estimate of its own position, derived from wheel encoders.
It answers: "Given how much each wheel has rotated, where do I think I am?"

- Published on the `/odom` topic as `nav_msgs/msg/Odometry`
- Contains: position (x, y), orientation (as a quaternion), velocity
- **Drifts over time** — wheel slip and measurement error accumulate

This is why we need SLAM — to correct odometry drift using sensor observations.

**Quaternions:** The orientation in odometry (and most of ROS2) is expressed as a
quaternion (w, x, y, z) rather than Euler angles (roll, pitch, yaw). This avoids
gimbal lock. For a ground robot, only yaw matters, and you can convert:

```python
from tf_transformations import euler_from_quaternion
(roll, pitch, yaw) = euler_from_quaternion([qx, qy, qz, qw])
```

---

## ✅ Tasks

### 2.1 — Launch Turtlebot3 in Gazebo

```bash
# Launch the Gazebo world with a Turtlebot3
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Spend time just looking at the Gazebo window. Click on the robot. Look at the
model tree on the left side. Understand what you're seeing.

**Status:** `[x]` — 2026-05-01. Used custom `turtlebot3_ign.launch.py` (Ignition Fortress, server-only `-s` flag because GUI not supported on macOS). Confirmed all 10 expected topics: /scan, /odom, /cmd_vel, /tf, /tf_static, /joint_states, /clock, /robot_description, /parameter_events, /rosout. Note: Gazebo runs headless on macOS; visualization is via RViz2.

### 2.2 — Teleoperate the Robot

In a second terminal:
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

Drive the robot around. Notice how it collides with walls.

**Status:** `[x]` — 2026-05-01. Teleop publishes Twist to /cmd_vel; bridge forwards to Ignition's diff-drive plugin; physics moves robot; odom plugin integrates wheel rotations → /odom. Verified by `ros2 topic echo /odom --once` showing changing position. Note: no physical walls (Ignition world has only floor).

### 2.3 — Investigate All Active Topics

```bash
ros2 topic list
```

You'll see topics like `/scan`, `/odom`, `/cmd_vel`, `/tf`, etc. For each one, run:
```bash
ros2 topic info /scan
ros2 topic echo /scan --once     # Print one message then stop
ros2 interface show sensor_msgs/msg/LaserScan
```

Understand what data each topic carries before you try to use it in code.

**Status:** `[x]` — 2026-05-01. Walked through all 10 active topics inline. Key takeaways: /scan carries 360 floats indexed by angle; /odom is in odom frame (not world); /cmd_vel is robot-frame Twist; /tf is dynamic transforms, /tf_static is fixed.

### 2.4 — Visualize in RViz2

```bash
ros2 run rviz2 rviz2
```

In RViz2:
1. Set `Fixed Frame` to `odom`
2. Add a `LaserScan` display, set topic to `/scan`
3. Add a `RobotModel` display
4. Add a `TF` display to see all coordinate frames

Drive the robot and watch the laser scan data move with it.

**Status:** `[x]` — 2026-05-06. Used Fixed Frame=odom, RobotModel from /robot_description, LaserScan from /scan (Reliability=Best Effort to match publisher), TF display. Saw 360 dots forming a square room around the robot. Driving the robot moves the dots correctly (rays follow the robot's pose). Note: scan is from `fake_scan_publisher` Python node, not Gazebo (Ignition lidar can't render headless on macOS).

### 2.5 — Try a Maze World

```bash
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage4.launch.py
# or create your own maze world (covered later)
```

**Status:** `[partial / deferred]` — 2026-05-06. Currently using a virtual 5×5m square room (Pass 1 of fake_scan_publisher). Pass 2 (add cylindrical pillars to match real turtlebot3_world) deferred — not blocking Stage 3. Will revisit if needed.

---

## 🧠 Concept Check — Stage 2

1. What is Gazebo simulating exactly? What would break if we ran our nav code directly on
   a real robot?
2. What is a URDF and what information does it contain?
3. What does TF2 do? What goes wrong if a TF transform is missing?
4. What is odometry and why does it drift?
5. What does the `/cmd_vel` topic carry, and which node publishes to it during teleoperation?

---
---

# STAGE 3 — Reading Sensor Data

## 🎯 Goal
Write a Python node that reads the LiDAR data and makes intelligent decisions based on it.
Understand sensor coordinate frames and data structures.

## ⏱️ Estimated Time
3–5 days

---

## 📖 Concept: The LaserScan Message

A 2D LiDAR like Turtlebot3's sends out laser pulses in a 360° arc and measures
the distance to the nearest obstacle at each angle.

The `sensor_msgs/msg/LaserScan` message structure:

```
Header header          # timestamp + frame_id (which TF frame this scan is in)
float32 angle_min      # start angle of scan (radians), usually -π or 0
float32 angle_max      # end angle of scan (radians), usually +π or 2π
float32 angle_increment  # angle between measurements (radians)
float32 time_increment   # time between each measurement
float32 range_min      # minimum valid range (closer = invalid)
float32 range_max      # maximum valid range (farther = invalid)
float32[] ranges       # THE DISTANCES: ranges[i] = distance at angle (min + i*increment)
float32[] intensities  # signal strength (often empty)
```

**Key insight:** `ranges` is just a Python list of floats. The index corresponds to angle.
To get the distance directly in front of the robot: `ranges[0]` (if angle_min=0) or
the index corresponding to angle 0.

**Invalid readings:** `ranges[i]` can be `float('inf')` (nothing detected) or `float('nan')`
(invalid). Always filter these before using.

```python
# Safe way to get the minimum distance in a range of angles
def get_min_range(ranges, start_idx, end_idx):
    valid = [r for r in ranges[start_idx:end_idx]
             if not math.isnan(r) and not math.isinf(r)]
    return min(valid) if valid else float('inf')
```

---

## 📖 Concept: The Twist Message (Velocity Commands)

To move the robot, you publish `geometry_msgs/msg/Twist` to `/cmd_vel`:

```
Vector3 linear     # x=forward/backward, y=left/right (0 for wheeled robots), z=up (0)
Vector3 angular    # x=roll (0), y=pitch (0), z=rotate left/right (yaw rate)
```

For a differential-drive robot like Turtlebot3:
- `linear.x` — forward velocity (m/s), positive = forward
- `angular.z` — yaw rate (rad/s), positive = counterclockwise (left turn)

```python
from geometry_msgs.msg import Twist

cmd = Twist()
cmd.linear.x = 0.2    # move forward at 0.2 m/s
cmd.angular.z = 0.5   # turn left at 0.5 rad/s
self.cmd_publisher.publish(cmd)
```

---

## ✅ Tasks

### 3.1 — Read Raw LaserScan Data

Create `laser_reader.py` — a node that subscribes to `/scan` and prints:
- Distance directly in front (index ~0)
- Distance to the left (index ~90 assuming 1°/reading)
- Distance to the right (index ~270)
- Minimum distance in any direction

```python
from sensor_msgs.msg import LaserScan
import math

class LaserReader(Node):
    def __init__(self):
        super().__init__('laser_reader')
        self.sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

    def scan_callback(self, msg):
        # msg.ranges is a tuple of floats
        front = msg.ranges[0]
        self.get_logger().info(f'Front distance: {front:.2f}m')
```

**Status:** `[ ]`

### 3.2 — Visualize What the Robot "Sees"

Without running any navigation:
- Drive the robot into a corner using teleop
- Watch the LaserScan display in RViz2
- Also watch the raw numbers from your laser_reader node

Correlate what you see visually with what the numbers say.

**Status:** `[ ]`

### 3.3 — Build a Simple Obstacle Avoider

Write a node that:
- Checks the distance in front of the robot
- If the front distance > 0.5m → go straight
- If the front distance < 0.5m → stop and turn

This is not good navigation, but it's the minimal feedback loop:
sensor data → decision → motor command.

```python
class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')
        self.scan_sub = self.create_subscription(LaserScan, '/scan',
                                                  self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.front_distance = float('inf')
        self.timer = self.create_timer(0.1, self.control_loop)

    def scan_callback(self, msg):
        # Update the stored front distance
        self.front_distance = msg.ranges[0]

    def control_loop(self):
        cmd = Twist()
        if self.front_distance > 0.5:
            cmd.linear.x = 0.2
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5
        self.cmd_pub.publish(cmd)
```

**Notice the pattern:** scan_callback just *stores* data. control_loop *uses* data.
This separation — sensor callbacks only update state, control loops only act on state —
is a fundamental pattern in robotics software. It keeps things clean and prevents
race conditions.

**Status:** `[ ]`

---

## 🧠 Concept Check — Stage 3

1. How do you convert an array index in `ranges` to the actual angle that index corresponds to?
2. Why are some values in `ranges` `inf` or `nan`? How should you handle them?
3. Explain the difference between `linear.x` and `angular.z` in a Twist message.
4. Why is it good practice to separate the sensor callback and the control loop?

---
---

# STAGE 4 — Wall-Following Controller

## 🎯 Goal
Implement a proper wall-following algorithm. The robot should navigate a maze by
always keeping a wall on its left (or right) side. This is the first real
"algorithm" of the project.

## ⏱️ Estimated Time
1 week

---

## 📖 Concept: Wall-Following Algorithm

The **left-wall-follower** algorithm is one of the simplest maze-solving strategies:
1. If there is no wall on the left → turn left (follow the wall)
2. If there is a wall ahead and on the left → turn right
3. Otherwise → go straight (keeping the left wall close)

This works for **simply-connected mazes** (where all walls are connected to the
outer boundary). It won't solve all mazes (e.g., those with islands), but it's
a great learning exercise and sufficient for most Gazebo maze worlds.

**Three zones to check:**
```
       FRONT
    [ 0° ±30° ]

LEFT              RIGHT
[60°-120°]      [240°-300°]
```

A good wall-follower also uses **proportional control** to keep a consistent
distance from the wall, rather than just "turn left/right":

```
Error = desired_wall_distance - actual_wall_distance
angular_velocity = Kp * error    # Proportional controller
```

---

## 📖 Concept: Proportional Control (P-Controller)

A **P-controller** is the simplest form of feedback control:

```
output = Kp × (setpoint - measurement)
```

- `setpoint` — what you want (e.g., 0.3m from the wall)
- `measurement` — what you have (e.g., actual distance from left LiDAR rays)
- `Kp` — proportional gain (how aggressively to react)

If `Kp` is too small → sluggish response, robot drifts away from wall
If `Kp` is too large → robot oscillates, overshoots, becomes unstable

Tuning `Kp` is done empirically — try values, observe behavior, adjust.

**Why not PID?** A full PID controller (Proportional-Integral-Derivative) would
be better, but P alone is a good starting point and enough to understand the concept.
Add the I and D terms as an extension.

---

## ✅ Tasks

### 4.1 — Define the Sensor Zones

Extend your laser reader to compute the minimum distance in:
- Front zone: indices covering -30° to +30°
- Left zone: indices covering 60° to 120°
- Right zone: indices covering 240° to 300°

Remember: index calculation is `idx = int((angle - angle_min) / angle_increment)`

**Status:** `[ ]`

### 4.2 — Implement Basic Wall Follower (State Machine)

Create a `WallFollower` node with three states:
```
FIND_WALL → TURN_LEFT → FOLLOW_WALL
                ↑              |
                └──────────────┘ (loop)
```

```python
from enum import Enum

class State(Enum):
    FIND_WALL = 0
    TURN_LEFT = 1
    FOLLOW_WALL = 2
```

Transition logic:
- `FIND_WALL`: Go forward until left wall detected (left < 0.5m) → `FOLLOW_WALL`
- `FOLLOW_WALL`: Keep going. If front wall detected → `TURN_LEFT`
- `TURN_LEFT`: Rotate right until front is clear → `FOLLOW_WALL`

**Status:** `[ ]`

### 4.3 — Add Proportional Control for Wall Distance

Replace binary left-turn decisions with a P-controller:

```python
DESIRED_WALL_DIST = 0.3   # meters
Kp = 2.0

def follow_wall(self, left_dist):
    error = DESIRED_WALL_DIST - left_dist
    angular_z = Kp * error
    return angular_z
```

Tune `Kp` until the robot smoothly follows the wall without oscillation.

**Status:** `[ ]`

### 4.4 — Test in Maze World

```bash
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage4.launch.py
```

Watch the robot navigate. Take notes:
- Where does it fail?
- Does it get stuck in corners?
- Is wall-following enough to solve the maze?

**Status:** `[ ]`

### 4.5 — Add Parameters (Make it Configurable)

Add ROS2 parameters so you can tune without recompiling:

```python
def __init__(self):
    super().__init__('wall_follower')
    self.declare_parameter('desired_wall_dist', 0.3)
    self.declare_parameter('kp_gain', 2.0)
    self.declare_parameter('linear_speed', 0.2)

    self.desired_dist = self.get_parameter('desired_wall_dist').value
    self.kp = self.get_parameter('kp_gain').value
    self.speed = self.get_parameter('linear_speed').value
```

Now you can tune at launch time:
```bash
ros2 run my_robot_pkg wall_follower --ros-args -p kp_gain:=3.0
```

**Status:** `[ ]`

---

## 🧠 Concept Check — Stage 4

1. What is a proportional controller? What does the gain `Kp` do?
2. Why use a state machine for the wall follower instead of a chain of if-else statements?
3. What mazes will the wall-follower algorithm fail to solve? Why?
4. What are ROS2 parameters and how do they differ from hardcoded constants?

---
---

# STAGE 5 — SLAM & Mapping

## 🎯 Goal
Build a map of the maze using SLAM Toolbox. Understand what SLAM is solving
and why it's a hard problem.

## ⏱️ Estimated Time
1 week

---

## 📖 Concept: SLAM — The Hard Problem

**SLAM (Simultaneous Localization and Mapping)** solves a chicken-and-egg problem:

- To build a map, you need to know where you are
- To know where you are, you need a map

A robot with only odometry drifts. After 10 meters, it might think it's 0.5m off
from where it actually is. That error compounds.

SLAM solves this by:
1. Taking LiDAR scans at each position
2. Matching each new scan to previous scans (scan matching)
3. When the robot revisits a place (loop closure), correcting accumulated drift
4. Building a consistent map as a byproduct

**SLAM Toolbox** is the standard ROS2 SLAM package. It uses a graph-based approach:
- Each robot pose is a node in a graph
- Sensor observations create edges (constraints) between nodes
- It minimizes the error across all constraints to find the best consistent trajectory

---

## 📖 Concept: The Occupancy Grid Map

The output of SLAM is an **occupancy grid** — a 2D grid where each cell is:
- `100` — definitely occupied (wall)
- `0` — definitely free (drivable)
- `-1` — unknown (never observed)

This is published on the `/map` topic as `nav_msgs/msg/OccupancyGrid`.

The map has a **resolution** (e.g., 0.05m/cell = each cell is 5cm × 5cm) and
an **origin** (where the (0,0) cell is in the real world).

Nav2 uses this map for path planning.

---

## ✅ Tasks

### 5.1 — Install and Launch SLAM Toolbox

```bash
sudo apt install ros-humble-slam-toolbox

# Launch Gazebo + Turtlebot3
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# In a second terminal, launch SLAM
ros2 launch slam_toolbox online_async_launch.py
```

**Status:** `[ ]`

### 5.2 — Visualize Map Building in RViz2

Add a `Map` display in RViz2, set topic to `/map`. Drive the robot around manually
using teleop. Watch the map build in real time. Notice:
- Dark grey = walls
- Light grey = free space
- Mid grey = unknown

**Status:** `[ ]`

### 5.3 — Save the Map

Once you have a complete map:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/maze_map
```

This creates `maze_map.pgm` (image of the map) and `maze_map.yaml` (metadata).
Open the `.pgm` file in an image viewer.

**Status:** `[ ]`

### 5.4 — Connect Your Wall Follower to Map Building

Run your wall follower node from Stage 4 *while* SLAM is running. Let the robot
autonomously explore and build the map. This is a significant milestone.

**Status:** `[ ]`

---

## 🧠 Concept Check — Stage 5

1. Explain the SLAM problem in your own words. What are the two things being solved simultaneously?
2. What is loop closure and why is it important?
3. What does an occupancy grid represent? What do the values 0, 100, and -1 mean?
4. What causes odometry drift and how does SLAM correct it?

---
---

# STAGE 6 — Autonomous Navigation with Nav2

## 🎯 Goal
Use the Nav2 navigation stack to autonomously navigate to goal positions in the maze.
Understand what Nav2 is doing under the hood.

## ⏱️ Estimated Time
1–2 weeks (Nav2 is complex — take your time)

---

## 📖 Concept: The Nav2 Stack

**Nav2** is ROS2's standard navigation framework. It takes a goal pose and figures
out how to get there safely. It's a collection of servers running as separate nodes:

```
You send a goal pose
        ↓
[BT Navigator]          ← Behavior Tree orchestrator (the "brain")
        ↓
[Global Planner]        ← Plans a path from current pos to goal (e.g., A* on the map)
        ↓
[Local Planner/Controller] ← Follows the path while avoiding dynamic obstacles
        ↓
[/cmd_vel]              ← Publishes velocity commands to the robot
```

Plus supporting nodes:
- **Costmap 2D** — Inflates obstacles on the map so the robot stays away from walls
- **AMCL** — Localizes the robot within the saved map using particles
- **Map Server** — Loads your saved map and serves it on `/map`
- **Lifecycle Manager** — Starts/stops all Nav2 nodes in the correct order

---

## 📖 Concept: Costmaps

A **costmap** is a grid map where each cell has a "cost" — how dangerous it is
to be there. Nav2 maintains two:

- **Global costmap** — for planning a path across the whole map
- **Local costmap** — for real-time obstacle avoidance in the immediate vicinity

Cells near walls have high cost. Free space has low cost. The planner finds a
path that minimizes total cost.

**Inflation radius:** Walls are "inflated" in the costmap so the robot
doesn't plan paths that would scrape against them. This accounts for the
robot's physical size.

---

## 📖 Concept: AMCL — Localization in a Known Map

Once you have a saved map, you use **AMCL (Adaptive Monte Carlo Localization)**
to localize the robot within it. AMCL uses a **particle filter**:

1. Start with N random pose guesses (particles) spread across the map
2. For each LiDAR scan, weight each particle by how well its simulated scan
   matches the actual scan
3. Resample: high-weight particles survive, low-weight particles die
4. The cloud of particles converges to the robot's actual pose

AMCL only works when the map already exists. SLAM builds the map. AMCL uses it.

---

## 📖 Concept: Actions in Depth

Nav2 uses **ROS2 Actions** for receiving navigation goals. This is important to understand:

```python
import rclpy
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class Navigator(Node):
    def __init__(self):
        super().__init__('navigator')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x, y):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0  # No rotation

        self._client.wait_for_server()
        future = self._client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback):
        dist = feedback.feedback.distance_remaining
        self.get_logger().info(f'Distance remaining: {dist:.2f}m')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        self.get_logger().info('Navigation complete!')
```

---

## ✅ Tasks

### 6.1 — Install Nav2

```bash
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
```

**Status:** `[ ]`

### 6.2 — Launch Nav2 with Your Saved Map

```bash
# Terminal 1: Gazebo
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2: Nav2 + AMCL + Map Server
ros2 launch nav2_bringup bringup_launch.py \
  map:=/home/$USER/maze_map.yaml \
  use_sim_time:=True
```

**Status:** `[ ]`

### 6.3 — Send a Navigation Goal from RViz2

In RViz2, use the `Nav2 Goal` tool (2D Goal Pose button) to click a destination.
Watch the robot plan a path and drive to it. Observe:
- The global path (shown in RViz2)
- The local planner following it
- How it handles obstacles

**Status:** `[ ]`

### 6.4 — Send a Navigation Goal from Code

Write a Python node using the `ActionClient` pattern shown above.
Send the robot to three waypoints in sequence.

**Status:** `[ ]`

### 6.5 — Understand the Lifecycle System

```bash
ros2 lifecycle list /nav2_controller
ros2 lifecycle get /nav2_controller
```

Nav2 nodes use **managed nodes** (lifecycle nodes) that go through states:
Unconfigured → Inactive → Active. This allows safe startup/shutdown sequences.

**Status:** `[ ]`

---

## 🧠 Concept Check — Stage 6

1. What is the difference between the global planner and the local planner?
2. What does AMCL do and how is it different from SLAM?
3. Explain the costmap concept. Why do we inflate obstacles?
4. Why does Nav2 use Actions instead of topics to receive goals?
5. What is a lifecycle node and why is this pattern useful?

---
---

# STAGE 7 — Full Maze Solving

## 🎯 Goal
Combine everything. The robot explores an unknown maze, builds a map,
and then navigates to the exit autonomously.

## ⏱️ Estimated Time
1–2 weeks

---

## 📖 Concept: Exploration Strategies

Now that the robot can navigate to goals and build a map, how do we
choose *which* goals to navigate to in order to efficiently explore an unknown maze?

**Frontier-based exploration:**
A frontier is the boundary between known free space and unknown space.
Navigate to frontiers to expand the known map.

```
unknown | frontier | known free | wall
  ???   |    →     |   (mapped) |  ██
```

Algorithm:
1. Find all frontier cells in the occupancy grid (free cells adjacent to unknown cells)
2. Cluster nearby frontier cells into frontier regions
3. Pick the nearest/largest frontier region as the next navigation goal
4. Send the goal to Nav2
5. Repeat until no frontiers remain (maze fully explored)

This is called **greedy nearest-frontier** exploration. It's simple and works well.

---

## ✅ Tasks

### 7.1 — Write a Frontier Detector

Parse the occupancy grid (`/map`) and identify frontier cells:

```python
from nav_msgs.msg import OccupancyGrid
import numpy as np

def find_frontiers(map_msg):
    width = map_msg.info.width
    height = map_msg.info.height
    data = np.array(map_msg.data).reshape((height, width))

    frontiers = []
    for y in range(1, height-1):
        for x in range(1, width-1):
            if data[y, x] == 0:   # free cell
                neighbors = [
                    data[y-1, x], data[y+1, x],
                    data[y, x-1], data[y, x+1]
                ]
                if -1 in neighbors:   # adjacent to unknown
                    frontiers.append((x, y))
    return frontiers
```

Convert frontier pixel coordinates to world coordinates using the map metadata.

**Status:** `[ ]`

### 7.2 — Write the Exploration Node

Create an `Explorer` node that:
1. Subscribes to `/map`
2. Finds frontiers
3. Picks the nearest one to the robot's current pose (from `/odom` or TF)
4. Sends it as a Nav2 goal
5. Waits for the goal to complete
6. Repeats

**Status:** `[ ]`

### 7.3 — Full System Integration Test

Launch everything together in a launch file:
- Gazebo with maze world
- SLAM Toolbox
- Nav2 stack
- Your Explorer node

Watch the robot autonomously map and navigate the maze.

**Status:** `[ ]`

### 7.4 — Create a Launch File for the Full System

Everything should be launchable with one command:
```bash
ros2 launch my_robot_pkg maze_solver.launch.py
```

**Status:** `[ ]`

### 7.5 — Record a Demo with ros2 bag

```bash
# Record key topics to a bag file
ros2 bag record /scan /odom /map /cmd_vel /tf -o maze_run_demo
```

This lets you play back the run later for presentations.

**Status:** `[ ]`

---

## 🧠 Concept Check — Stage 7

1. What is a frontier in the context of exploration?
2. What are the limitations of greedy nearest-frontier exploration?
3. How do you convert between map pixel coordinates and real-world coordinates?

---
---

# 📚 Resources

## Official Documentation
- [ROS2 Humble Docs](https://docs.ros.org/en/humble/)
- [Nav2 Docs](https://navigation.ros.org/)
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [Turtlebot3 e-Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)

## Best Learning Resources
- **Articulated Robotics (YouTube)** — Josh Newans. Best ROS2 beginner series. Watch it.
- **The Construct** — Structured ROS2 courses with simulations in the browser.
- **ROS2 for Beginners (Udemy)** — Edouard Renard. Good if you prefer video courses.
- **Programming Robots with ROS** (O'Reilly book) — ROS1 but concepts transfer.

## Useful CLI Cheatsheet

```bash
# Build
colcon build --packages-select <pkg>    # Build only one package
colcon build --symlink-install          # Faster rebuilds for Python packages

# Debug
rqt_graph                               # Visual graph of all nodes and topics
ros2 doctor                             # Check for ROS2 health issues
ros2 bag record -a                      # Record all topics
ros2 bag play <bag_file>                # Replay a recording

# TF
ros2 run tf2_tools view_frames          # Generate PDF of TF tree
ros2 run tf2_ros tf2_echo map base_link # Print live transform between two frames

# Parameters
ros2 param list /node_name             # List all parameters of a node
ros2 param get /node_name param_name   # Get a parameter value
ros2 param set /node_name param_name 1.5  # Set a parameter at runtime
```

---

# 🎓 Research Extensions (For PhD Application Material)

> **Why this section exists:** The base plan teaches you how to *build* a maze-solving robot. That's a strong undergraduate-level project. To make it competitive for a PhD application (especially in Europe), you need to show **research thinking** — formulating a question, comparing approaches, drawing conclusions from data. Each extension below converts one stage from "implementation" to "experiment."
>
> **You do NOT need to do all of these.** Pick ONE that genuinely interests you, do it deeply, write it up. A 4-6 page technical report on one well-executed comparison is worth more than three half-finished extensions.
>
> **Decide which one (if any) to attempt when you reach that stage.** Until then, just be aware they exist.

---

## 🔬 Extension A — Controller Comparison (extends Stage 4)

**Question:** How do different feedback controllers compare on a wall-following task?

### What you do
1. Implement three controllers for the same wall-follower:
   - **P (proportional)** — already in Stage 4
   - **PID (proportional-integral-derivative)** — adds memory of past error and rate of change
   - **Pure pursuit** — geometric: pick a "lookahead point" on the desired path, steer toward it
2. Run each controller on the same maze with identical starting conditions
3. Measure:
   - **Tracking error** — RMS deviation from the desired wall distance
   - **Settling time** — how fast it reaches steady state after a corner
   - **Smoothness** — RMS of the angular velocity (jerky vs smooth)
   - **Robustness** — performance under added sensor noise (artificially corrupt /scan)
4. Plot results. Discuss tradeoffs.

### Math you'll derive
- PID transfer function and stability conditions (when do the gains make it oscillate vs. converge?)
- Pure pursuit lookahead-distance vs. curvature relationship: `κ = 2·sin(α)/L`
- Effect of integrator windup; why anti-windup matters

### Why it's research-shaped
You're not just using PID — you're **characterizing** it. "Under what conditions does P-only suffice? When does the I term help? When does it hurt?" That's a research question with a measurable answer.

### Estimated effort
2-3 weeks beyond Stage 4 base.

### Deliverable
- Code: 3 controller implementations, a benchmark harness, a plotting script
- Report: 4-6 pages with figures, tables, and analysis

---

## 🔬 Extension B — EKF-SLAM From Scratch (replaces Stage 5)

**Question:** Can you implement SLAM yourself, mathematically, instead of using SLAM Toolbox?

This is the most ambitious option and the most impressive on a PhD application.

### What you do
1. Skip SLAM Toolbox. Instead, implement **EKF-SLAM** in pure Python:
   - State vector: `[robot_x, robot_y, robot_yaw, lm1_x, lm1_y, lm2_x, lm2_y, ...]`
   - Predict step: from `/odom` and motion model
   - Update step: from `/scan` and observation model
   - Covariance matrix `P` representing uncertainty in everything
2. Detect "landmarks" from /scan — corner detection or RANSAC line fitting on laser data
3. Data association: when you see a new scan, which observed landmark corresponds to which one in your map?
4. Compare against SLAM Toolbox: same robot path, both running, plot map quality

### Math you'll derive (and this is the *point*)
- Bayes filter recursion: `bel(x_t) = η · p(z_t | x_t) · ∫ p(x_t | x_{t-1}, u_t) · bel(x_{t-1}) dx_{t-1}`
- Linearization via Jacobians; why EKF is "extended"
- Mahalanobis distance for data association
- Covariance growth and loop-closure correction
- Why scaling beyond ~50 landmarks is hard (O(n²) covariance) — motivation for graph-SLAM

### Why it's research-shaped
This is *exactly* the math a PhD candidate is expected to know. Implementing it from scratch — not using a library — proves you understand the algorithm. EU robotics labs love this.

### Estimated effort
4-6 weeks. This is hard. Do it only if you're committed.

### Deliverable
- Code: full EKF-SLAM implementation
- Report: 6-10 pages with derivations, figures, and quantitative comparison vs. SLAM Toolbox
- Stretch: extend to graph-SLAM, compare both

### Required reading
- Probabilistic Robotics (Thrun, Burgard, Fox), Chapters 3, 5, 10. Non-negotiable.
- "A Tutorial on Graph-Based SLAM" (Grisetti et al., 2010) for the modern view

---

## 🔬 Extension C — Exploration Strategy Comparison (extends Stage 7)

**Question:** What's the best way to explore an unknown maze?

### What you do
1. Implement two (or three) frontier-based exploration strategies:
   - **Greedy nearest-frontier** — Stage 7 baseline. Always go to the closest unexplored boundary.
   - **Information-gain** — pick the frontier that maximizes expected map entropy reduction
   - **Cost-utility** — `goal = argmax_i (info_gain(i) / travel_cost(i))`
2. Run each on multiple maze layouts (you'll need to author 3-5 of them in the fake_scan world)
3. Measure:
   - **Coverage time** — how fast does the map reach 95% known cells?
   - **Path length** — total distance traveled
   - **Backtracking** — how often does the robot revisit known territory?
4. Plot results. Discuss tradeoffs and when each strategy wins.

### Math you'll derive
- Map entropy: `H(m) = -Σ p(c) log p(c) - (1-p(c)) log(1-p(c))` summed over cells
- Expected information gain from a vantage point: ray-cast through the cell, compute reduction in entropy
- Greedy vs. lookahead — why greedy is suboptimal in theory but cheap in practice

### Why it's research-shaped
Exploration is an active research area (frontier methods, NBV planning, learning-based exploration). Demonstrating that you can implement, compare, and reason about strategies puts you in conversation with current literature.

### Estimated effort
2-3 weeks beyond Stage 7 base.

### Deliverable
- Code: multiple exploration strategies, benchmarking harness, maze generator
- Report: 4-6 pages with figures and discussion

---

## 📊 How These Compare for PhD Application Strength

| Extension | Effort | Math depth | Visual impact | Application strength |
|-----------|--------|-----------|---------------|---------------------|
| A — Controller comparison | Low-medium | Medium | Medium | 7/10 |
| B — EKF-SLAM from scratch | High | High | Medium | 9/10 |
| C — Exploration comparison | Medium | Medium-high | High | 8/10 |

**My recommendation when you get there:** if you finish base Stage 4 with comfortable understanding, do Extension A as a warm-up (it's quick). Save Extension B for AFTER Stage 6 (Nav2) so you have all the context. Extension C is a great "capstone" that builds on Stage 7.

But the most important thing is to do ONE of them deeply. Half-finished extensions are worse than no extension.

---

# ⚠️ Common Mistakes & Gotchas

| Mistake | Fix |
|---------|-----|
| Node dies immediately | Missing `rclpy.spin()` |
| Topics not connecting | Check `ros2 topic info` for QoS mismatches |
| Robot doesn't move in Gazebo | Check if `/cmd_vel` is being published and Gazebo plugin is loaded |
| Map is empty in RViz2 | Check Fixed Frame — should be `map` not `odom` |
| SLAM not building map | Ensure `use_sim_time:=True` is set on all nodes |
| `colcon build` fails | Missing dependency in `package.xml` |
| "Could not find TF" error | TF is slow to start — add a small startup delay or retry logic |
| Nav2 goal rejected | Robot is not localized — set initial pose in RViz2 with `2D Pose Estimate` |

---

*Last updated: 2026-05-06 — Stage 2 complete (Ignition + fake_scan_publisher pivot due to macOS limitations)*
*Next session goal: Stage 3 — write `laser_reader` (Task 3.1), then `obstacle_avoider` (Task 3.3). Concept focus: index↔angle math, inf/nan filtering, sensor-callback vs control-loop separation.*
