"""
HIL Robocar – World Simulation  (v2.0 – 4WD Skid-Steer)
=========================================================
Integrates physics, sensors, and obstacles.

The car is now a **FourWheelSkidSteerCar** with:
    track_width   = 0.22 m
    wheel_base    = 0.16 m
    max_speed     = 0.60 m/s
    lateral_friction = 0.85

This module is a **pure plant** – it executes motor commands
received from the ESP32 controller and reports sensor data.
No control / decision logic lives here.
"""

from typing import Tuple
from .physics import FourWheelSkidSteerCar, CollisionDetector
from .sensors import SensorArray
from .obstacles import ObstacleManager


class SimulationWorld:
    """
    Complete simulation world for HIL Robocar

    Integrates:
    - 4WD Skid-Steer car physics
    - 9-beam ultrasonic sensor array
    - Obstacle management
    - Collision detection
    """

    def __init__(
        self,
        width: float = 5.0,      # World width (meters)
        height: float = 5.0,     # World height (meters)
        car_x: float = 0.5,      # Initial car X position
        car_y: float = 0.5,      # Initial car Y position
        car_theta: float = 0.0   # Initial car heading (radians)
    ):
        """
        Initialize simulation world

        Args:
            width: World width in meters
            height: World height in meters
            car_x, car_y: Initial car position
            car_theta: Initial car heading in radians
        """
        self.width = width
        self.height = height

        # Initialize 4WD skid-steer car
        self.car = FourWheelSkidSteerCar(
            x=car_x,
            y=car_y,
            theta=car_theta,
            track_width=0.22,
            wheel_base=0.16,
            max_speed=1.00,
            wheel_radius=0.033,
            lateral_friction=0.85,
        )

        # Initialize sensors
        self.sensors = SensorArray()

        # Initialize obstacles
        self.obstacles = ObstacleManager()
        self.obstacles.create_default_scenario(width, height)

        # Initialize collision detector (radius covers 4WD chassis)
        self.collision_detector = CollisionDetector(robot_radius=0.18)

        # Simulation state
        self.is_collision = False
        self.total_time = 0.0
    
    def set_motor_commands(self, v_left: float, v_right: float):
        """
        Set motor commands from controller (ESP32)
        
        Args:
            v_left: Left wheel velocity (-1.0 to 1.0)
            v_right: Right wheel velocity (-1.0 to 1.0)
        """
        self.car.set_motor_commands(v_left, v_right)
    
    def update(self, dt: float):
        """
        Update simulation physics
        
        Args:
            dt: Time step in seconds
        """
        # Update car physics
        self.car.update(dt)
        
        # Check collisions
        robot_pos = self.car.get_position()
        
        # Check wall collisions
        self.is_collision = self.collision_detector.check_wall_collision(
            robot_pos, self.width, self.height
        )
        
        # Check obstacle collisions
        if not self.is_collision:
            for obstacle in self.obstacles.get_obstacles():
                if self.collision_detector.check_circle_collision(
                    robot_pos,
                    obstacle.position,
                    obstacle.radius
                ):
                    self.is_collision = True
                    break
        
        # Update total time
        self.total_time += dt
    
    def get_sensor_data(self) -> Tuple[float, float, float]:
        """
        Get current sensor readings
        
        Returns:
            (distance_front, distance_left, distance_right) in meters
        """
        robot_pos = self.car.get_position()
        robot_heading = self.car.get_heading()
        
        return self.sensors.get_distances(
            robot_pos,
            robot_heading,
            self.obstacles.get_obstacles(),
            self.width,
            self.height
        )
    
    def get_sensor_rays(self):
        """
        Get sensor ray objects for visualization
        
        Returns:
            (ray_front, ray_left, ray_right)
        """
        robot_pos = self.car.get_position()
        robot_heading = self.car.get_heading()
        
        return self.sensors.measure_all(
            robot_pos,
            robot_heading,
            self.obstacles.get_obstacles(),
            self.width,
            self.height
        )
    
    def get_car_state(self):
        """Get complete car state"""
        return {
            'position': self.car.get_position(),
            'heading': self.car.get_heading(),
            'velocities': self.car.get_velocities()
        }
    
    def reset(self, x: float = 0.5, y: float = 0.5, theta: float = 0.0):
        """Reset simulation to initial state"""
        self.car.reset(x, y, theta)
        self.is_collision = False
        self.total_time = 0.0
    
    def is_crashed(self) -> bool:
        """Check if car has crashed"""
        return self.is_collision
