"""
HIL Robocar - Obstacle Management
Simple circular obstacles for the simulation world
"""

from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class Obstacle:
    """Circular obstacle in the simulation world"""
    position: Tuple[float, float]  # (x, y) in meters
    radius: float                  # Radius in meters
    
    def __init__(self, x: float, y: float, radius: float = 0.2):
        self.position = (x, y)
        self.radius = radius


class ObstacleManager:
    """Manages obstacles in the simulation world"""
    
    def __init__(self):
        self.obstacles: List[Obstacle] = []
    
    def add_obstacle(self, x: float, y: float, radius: float = 0.2):
        """Add a circular obstacle"""
        obstacle = Obstacle(x, y, radius)
        self.obstacles.append(obstacle)
        return obstacle
    
    def clear_obstacles(self):
        """Remove all obstacles"""
        self.obstacles.clear()
    
    def get_obstacles(self) -> List[Obstacle]:
        """Get all obstacles"""
        return self.obstacles
    
    def create_default_scenario(self, world_width: float, world_height: float):
        """
        Create a default obstacle course for demo
        """
        self.clear_obstacles()
        
        # Create a simple obstacle course
        # Center obstacles
        self.add_obstacle(world_width * 0.5, world_height * 0.5, 0.3)
        
        # Left side obstacles
        self.add_obstacle(world_width * 0.3, world_height * 0.3, 0.2)
        self.add_obstacle(world_width * 0.3, world_height * 0.7, 0.2)
        
        # Right side obstacles
        self.add_obstacle(world_width * 0.7, world_height * 0.3, 0.2)
        self.add_obstacle(world_width * 0.7, world_height * 0.7, 0.2)
        
        # Top and bottom
        self.add_obstacle(world_width * 0.5, world_height * 0.2, 0.15)
        self.add_obstacle(world_width * 0.5, world_height * 0.8, 0.15)
