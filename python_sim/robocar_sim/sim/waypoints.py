"""
Waypoint Navigation System
Quản lý các điểm đích (waypoints) và navigation logic
"""

import math
from typing import List, Tuple, Optional


class WaypointNavigator:
    """Quản lý navigation theo waypoints"""
    
    def __init__(self, waypoints: List[Tuple[float, float]], 
                 reach_radius: float = 0.3,
                 loop: bool = True):
        """
        Args:
            waypoints: List of (x, y) positions
            reach_radius: Distance to consider waypoint reached (meters)
            loop: Loop back to first waypoint when done
        """
        self.waypoints = waypoints
        self.reach_radius = reach_radius
        self.loop = loop
        
        self.current_waypoint_index = 0
        self.total_waypoints_reached = 0
        self.is_complete = False
        
    def get_current_waypoint(self) -> Optional[Tuple[float, float]]:
        """Lấy waypoint hiện tại"""
        if not self.waypoints or self.is_complete:
            return None
        return self.waypoints[self.current_waypoint_index]
    
    def get_next_waypoint(self) -> Optional[Tuple[float, float]]:
        """Lấy waypoint tiếp theo (để preview)"""
        if not self.waypoints or self.is_complete:
            return None
        next_idx = (self.current_waypoint_index + 1) % len(self.waypoints)
        return self.waypoints[next_idx]
    
    def update(self, car_x: float, car_y: float) -> bool:
        """
        Cập nhật trạng thái navigation
        
        Returns:
            True nếu đã đến waypoint, False nếu chưa
        """
        if not self.waypoints or self.is_complete:
            return False
        
        current_wp = self.get_current_waypoint()
        if not current_wp:
            return False
        
        # Tính khoảng cách đến waypoint
        dist = self.distance_to_waypoint(car_x, car_y, current_wp)
        
        # Đã đến waypoint?
        if dist <= self.reach_radius:
            self.total_waypoints_reached += 1
            self._advance_to_next_waypoint()
            return True
        
        return False
    
    def _advance_to_next_waypoint(self):
        """Chuyển sang waypoint tiếp theo"""
        self.current_waypoint_index += 1
        
        if self.current_waypoint_index >= len(self.waypoints):
            if self.loop:
                # Loop lại từ đầu
                self.current_waypoint_index = 0
            else:
                # Hoàn thành
                self.is_complete = True
                self.current_waypoint_index = len(self.waypoints) - 1
    
    def distance_to_waypoint(self, car_x: float, car_y: float, 
                            waypoint: Tuple[float, float]) -> float:
        """Tính khoảng cách đến waypoint"""
        wx, wy = waypoint
        return math.sqrt((car_x - wx)**2 + (car_y - wy)**2)
    
    def angle_to_waypoint(self, car_x: float, car_y: float, 
                         waypoint: Tuple[float, float]) -> float:
        """
        Tính góc đến waypoint (radians)
        
        Returns:
            Angle in radians (-π to π)
        """
        wx, wy = waypoint
        return math.atan2(wy - car_y, wx - car_x)
    
    def get_bearing_to_waypoint(self, car_x: float, car_y: float, 
                               car_heading: float) -> float:
        """
        Tính góc lệch giữa hướng xe và hướng đến waypoint
        
        Args:
            car_x, car_y: Vị trí xe
            car_heading: Hướng xe (radians)
            
        Returns:
            Bearing angle in radians (-π to π)
            Positive = phải, Negative = trái
        """
        current_wp = self.get_current_waypoint()
        if not current_wp:
            return 0.0
        
        target_angle = self.angle_to_waypoint(car_x, car_y, current_wp)
        bearing = target_angle - car_heading
        
        # Normalize to [-π, π]
        while bearing > math.pi:
            bearing -= 2 * math.pi
        while bearing < -math.pi:
            bearing += 2 * math.pi
        
        return bearing
    
    def reset(self):
        """Reset về waypoint đầu tiên"""
        self.current_waypoint_index = 0
        self.total_waypoints_reached = 0
        self.is_complete = False
    
    def get_progress(self) -> Tuple[int, int]:
        """
        Lấy tiến độ
        
        Returns:
            (current_index, total_waypoints)
        """
        return (self.current_waypoint_index + 1, len(self.waypoints))
    
    def has_waypoints(self) -> bool:
        """Kiểm tra có waypoints không"""
        return len(self.waypoints) > 0
