"""
HIL Robocar - Physics Engine
Implements differential drive kinematics and car dynamics
"""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class CarState:
    """Represents the state of the robot car"""
    x: float = 0.0          # X position (meters)
    y: float = 0.0          # Y position (meters)
    theta: float = 0.0      # Heading angle (radians, 0 = East, counterclockwise)
    v_left: float = 0.0     # Left wheel velocity (m/s)
    v_right: float = 0.0    # Right wheel velocity (m/s)


class DifferentialDriveCar:
    """
    Differential drive robot car with realistic physics
    
    This is a PURE SIMULATION component - no control logic here.
    Motor commands come from the ESP32 controller.
    """
    
    def __init__(
        self,
        x: float = 2.0,
        y: float = 2.0,
        theta: float = 0.0,
        wheel_base: float = 0.15,      # Distance between wheels (m)
        max_speed: float = 1.0,        # Maximum wheel speed (m/s)
        wheel_radius: float = 0.033,   # Wheel radius (m)
    ):
        """
        Initialize differential drive car
        
        Args:
            x, y: Initial position (meters)
            theta: Initial heading (radians)
            wheel_base: Distance between left and right wheels (meters)
            max_speed: Maximum linear speed per wheel (m/s)
            wheel_radius: Radius of each wheel (meters)
        """
        self.state = CarState(x=x, y=y, theta=theta)
        self.wheel_base = wheel_base
        self.max_speed = max_speed
        self.wheel_radius = wheel_radius
        
        # Physical constraints
        self.max_angular_velocity = (2 * max_speed) / wheel_base
        
    def set_motor_commands(self, v_left: float, v_right: float):
        """
        Set motor velocities from controller (ESP32)
        
        Args:
            v_left: Left wheel velocity (-1.0 to 1.0, normalized)
            v_right: Right wheel velocity (-1.0 to 1.0, normalized)
        """
        # Clamp to valid range
        v_left = max(-1.0, min(1.0, v_left))
        v_right = max(-1.0, min(1.0, v_right))
        
        # Convert normalized velocities to m/s
        self.state.v_left = v_left * self.max_speed
        self.state.v_right = v_right * self.max_speed
    
    def update(self, dt: float):
        """
        Update car physics using differential drive kinematics
        
        Args:
            dt: Time step (seconds)
        """
        # Get current wheel velocities
        v_l = self.state.v_left
        v_r = self.state.v_right
        
        # Compute linear and angular velocities
        v = (v_r + v_l) / 2.0                    # Linear velocity (m/s)
        omega = (v_r - v_l) / self.wheel_base    # Angular velocity (rad/s)
        
        # Update heading
        self.state.theta += omega * dt
        
        # Normalize theta to [-pi, pi]
        self.state.theta = math.atan2(math.sin(self.state.theta), 
                                      math.cos(self.state.theta))
        
        # Update position using current heading
        self.state.x += v * math.cos(self.state.theta) * dt
        self.state.y += v * math.sin(self.state.theta) * dt
    
    def get_position(self) -> Tuple[float, float]:
        """Get current position (x, y) in meters"""
        return (self.state.x, self.state.y)
    
    def get_heading(self) -> float:
        """Get current heading in radians"""
        return self.state.theta
    
    def get_velocities(self) -> Tuple[float, float]:
        """Get current wheel velocities (left, right) in m/s"""
        return (self.state.v_left, self.state.v_right)
    
    def reset(self, x: float, y: float, theta: float):
        """Reset car to a specific pose"""
        self.state.x = x
        self.state.y = y
        self.state.theta = theta
        self.state.v_left = 0.0
        self.state.v_right = 0.0


class CollisionDetector:
    """Simple collision detection for circular robot"""
    
    def __init__(self, robot_radius: float = 0.15):
        """
        Args:
            robot_radius: Radius of the robot (meters)
        """
        self.robot_radius = robot_radius
    
    def check_circle_collision(
        self, 
        robot_pos: Tuple[float, float],
        obstacle_pos: Tuple[float, float],
        obstacle_radius: float
    ) -> bool:
        """
        Check if robot collides with a circular obstacle
        
        Returns:
            True if collision detected
        """
        rx, ry = robot_pos
        ox, oy = obstacle_pos
        
        distance = math.sqrt((rx - ox)**2 + (ry - oy)**2)
        return distance < (self.robot_radius + obstacle_radius)
    
    def check_wall_collision(
        self,
        robot_pos: Tuple[float, float],
        world_width: float,
        world_height: float
    ) -> bool:
        """
        Check if robot collides with world boundaries
        
        Returns:
            True if collision detected
        """
        x, y = robot_pos
        
        if x - self.robot_radius < 0 or x + self.robot_radius > world_width:
            return True
        if y - self.robot_radius < 0 or y + self.robot_radius > world_height:
            return True
        
        return False
