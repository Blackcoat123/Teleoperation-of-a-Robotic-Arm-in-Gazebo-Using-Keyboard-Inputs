from setuptools import find_packages, setup

package_name = 'teleop_arm'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='black_coat',
    maintainer_email='007dhanadgupta@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
   entry_points={
    'console_scripts': [
        'teleop_arm = teleop_arm.teleop_arm:main',
        'arm_controller = teleop_arm.arm_controller:main',
    ],
},

)
