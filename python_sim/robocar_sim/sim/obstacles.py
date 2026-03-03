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
        
        # Center obstacle (large)
        self.add_obstacle(world_width * 0.5, world_height * 0.5, 0.40)
        
        # Quadrant obstacles
        self.add_obstacle(world_width * 0.25, world_height * 0.30, 0.25)
        self.add_obstacle(world_width * 0.25, world_height * 0.70, 0.25)
        self.add_obstacle(world_width * 0.75, world_height * 0.30, 0.25)
        self.add_obstacle(world_width * 0.75, world_height * 0.70, 0.25)
        
        # Edge obstacles
        self.add_obstacle(world_width * 0.50, world_height * 0.20, 0.20)
        self.add_obstacle(world_width * 0.50, world_height * 0.80, 0.20)
        self.add_obstacle(world_width * 0.35, world_height * 0.50, 0.20)
        self.add_obstacle(world_width * 0.65, world_height * 0.50, 0.20)
