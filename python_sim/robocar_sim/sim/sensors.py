"""
HIL Robocar - Sensor Simulation
Implements raycast-based ultrasonic sensors
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Ray:
    """Represents a sensor ray"""
    origin: Tuple[float, float]
    angle: float
    length: float
    hit_point: Optional[Tuple[float, float]] = None
    hit_distance: float = 999.0


class UltrasonicSensor:
    """
    Raycast-based ultrasonic sensor simulation
    
    Simulates ultrasonic distance sensors using ray casting
    against obstacles and world boundaries.
    """
    
    def __init__(
        self,
        max_range: float = 3.0,      # Maximum detection range (meters)
        min_range: float = 0.02,     # Minimum detection range (meters)
        angle_offset: float = 0.0,   # Sensor mounting angle offset (radians)
    ):
        """
        Args:
            max_range: Maximum detection distance (meters)
            min_range: Minimum detection distance (meters)
            angle_offset: Sensor angle relative to robot heading (radians)
        """
        self.max_range = max_range
        self.min_range = min_range
        self.angle_offset = angle_offset
    
    def measure(
        self,
        robot_pos: Tuple[float, float],
        robot_heading: float,
        obstacles: List['Obstacle'],
        world_width: float,
        world_height: float,
        sensor_offset: float = 0.1  # Distance from robot center to sensor (m)
    ) -> Ray:
        """
        Perform raycast measurement
        
        Args:
            robot_pos: Robot center position (x, y)
            robot_heading: Robot heading angle (radians)
            obstacles: List of circular obstacles
            world_width: World boundary width (meters)
            world_height: World boundary height (meters)
            sensor_offset: Distance from robot center to sensor (meters)
        
        Returns:
            Ray object with measurement results
        """
        # Calculate absolute sensor angle
        sensor_angle = robot_heading + self.angle_offset
        
        # Calculate sensor position (offset from robot center)
        rx, ry = robot_pos
        sensor_x = rx + sensor_offset * math.cos(robot_heading)
        sensor_y = ry + sensor_offset * math.sin(robot_heading)
        
        # Initialize ray
        ray = Ray(
            origin=(sensor_x, sensor_y),
            angle=sensor_angle,
            length=self.max_range
        )
        
        min_distance = self.max_range
        closest_hit = None
        
        # Check collision with all obstacles
        for obstacle in obstacles:
            hit_dist = self._raycast_circle(
                ray.origin,
                sensor_angle,
                obstacle.position,
                obstacle.radius
            )
            
            if hit_dist is not None and hit_dist < min_distance:
                min_distance = hit_dist
                closest_hit = (
                    sensor_x + hit_dist * math.cos(sensor_angle),
                    sensor_y + hit_dist * math.sin(sensor_angle)
                )
        
        # Check collision with world boundaries
        wall_hit_dist = self._raycast_walls(
            ray.origin,
            sensor_angle,
            world_width,
            world_height
        )
        
        if wall_hit_dist is not None and wall_hit_dist < min_distance:
            min_distance = wall_hit_dist
            closest_hit = (
                sensor_x + wall_hit_dist * math.cos(sensor_angle),
                sensor_y + wall_hit_dist * math.sin(sensor_angle)
            )
        
        # Apply sensor range limits
        if min_distance < self.min_range:
            min_distance = self.max_range  # Too close, sensor can't detect
        
        ray.hit_distance = min_distance
        ray.hit_point = closest_hit
        ray.length = min_distance
        
        return ray
    
    def _raycast_circle(
        self,
        ray_origin: Tuple[float, float],
        ray_angle: float,
        circle_center: Tuple[float, float],
        circle_radius: float
    ) -> Optional[float]:
        """
        Raycast against a circular obstacle
        
        Returns:
            Distance to intersection, or None if no hit
        """
        ox, oy = ray_origin
        cx, cy = circle_center
        
        # Ray direction
        dx = math.cos(ray_angle)
        dy = math.sin(ray_angle)
        
        # Vector from ray origin to circle center
        fx = cx - ox
        fy = cy - oy
        
        # Solve quadratic equation for ray-circle intersection
        a = dx * dx + dy * dy
        b = -2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - circle_radius * circle_radius
        
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return None  # No intersection
        
        # Find closest intersection point
        sqrt_discriminant = math.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)
        
        # Return closest positive t (distance along ray)
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return None  # Circle is behind ray
    
    def _raycast_walls(
        self,
        ray_origin: Tuple[float, float],
        ray_angle: float,
        world_width: float,
        world_height: float
    ) -> Optional[float]:
        """
        Raycast against world boundaries
        
        Returns:
            Distance to nearest wall intersection
        """
        ox, oy = ray_origin
        dx = math.cos(ray_angle)
        dy = math.sin(ray_angle)
        
        min_t = float('inf')
        
        # Left wall (x = 0)
        if dx < 0:
            t = -ox / dx
            if t > 0:
                y = oy + t * dy
                if 0 <= y <= world_height:
                    min_t = min(min_t, t)
        
        # Right wall (x = world_width)
        if dx > 0:
            t = (world_width - ox) / dx
            if t > 0:
                y = oy + t * dy
                if 0 <= y <= world_height:
                    min_t = min(min_t, t)
        
        # Bottom wall (y = 0)
        if dy < 0:
            t = -oy / dy
            if t > 0:
                x = ox + t * dx
                if 0 <= x <= world_width:
                    min_t = min(min_t, t)
        
        # Top wall (y = world_height)
        if dy > 0:
            t = (world_height - oy) / dy
            if t > 0:
                x = ox + t * dx
                if 0 <= x <= world_height:
                    min_t = min(min_t, t)
        
        return min_t if min_t != float('inf') else None


class SensorArray:
    """Array of ultrasonic sensors (Front, Left, Right)"""
    
    def __init__(self):
        """Initialize three ultrasonic sensors"""
        self.sensor_front = UltrasonicSensor(
            max_range=3.0,
            angle_offset=0.0  # 0° (forward)
        )
        
        self.sensor_left = UltrasonicSensor(
            max_range=2.0,
            angle_offset=math.pi / 2  # 90° (left)
        )
        
        self.sensor_right = UltrasonicSensor(
            max_range=2.0,
            angle_offset=-math.pi / 2  # -90° (right)
        )
    
    def measure_all(
        self,
        robot_pos: Tuple[float, float],
        robot_heading: float,
        obstacles: List,
        world_width: float,
        world_height: float
    ) -> Tuple[Ray, Ray, Ray]:
        """
        Measure all three sensors
        
        Returns:
            (front_ray, left_ray, right_ray)
        """
        ray_front = self.sensor_front.measure(
            robot_pos, robot_heading, obstacles, world_width, world_height
        )
        
        ray_left = self.sensor_left.measure(
            robot_pos, robot_heading, obstacles, world_width, world_height
        )
        
        ray_right = self.sensor_right.measure(
            robot_pos, robot_heading, obstacles, world_width, world_height
        )
        
        return (ray_front, ray_left, ray_right)
    
    def get_distances(
        self,
        robot_pos: Tuple[float, float],
        robot_heading: float,
        obstacles: List,
        world_width: float,
        world_height: float
    ) -> Tuple[float, float, float]:
        """
        Get distance measurements from all sensors
        
        Returns:
            (distance_front, distance_left, distance_right) in meters
        """
        rays = self.measure_all(
            robot_pos, robot_heading, obstacles, world_width, world_height
        )
        
        return (
            rays[0].hit_distance,
            rays[1].hit_distance,
            rays[2].hit_distance
        )
