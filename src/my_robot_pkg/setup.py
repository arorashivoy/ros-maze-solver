import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
        (os.path.join('share', package_name, 'models', 'turtlebot3_burger_ign'),
            glob('models/turtlebot3_burger_ign/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shivoy Arora',
    maintainer_email='shivoy1183@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'hello_publisher = my_robot_pkg.hello_publisher:main',
            'hello_subscriber = my_robot_pkg.hello_subscriber:main',
            'fake_scan_publisher = my_robot_pkg.fake_scan_publisher:main',
            'laser_reader = my_robot_pkg.laser_reader:main',
            'obstacle_avoider = my_robot_pkg.obstacle_avoider:main',
            'wall_follower = my_robot_pkg.wall_follower:main',
            'noisy_odom_publisher = my_robot_pkg.noisy_odom_publisher:main',
            'nav_goal_sender = my_robot_pkg.nav_goal_sender:main',
        ],
    },
)
