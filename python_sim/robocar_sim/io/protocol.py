"""
HIL Robocar - Serial Protocol
JSON encoding/decoding for sensor and motor data
"""

import json
from typing import Dict, Tuple, Optional


class SerialProtocol:
    """
    Handles JSON encoding/decoding for HIL communication
    
    Protocol (Wide Cone + Side Sensors - 9 sensors):
    - Python → ESP32: {"dC": 1.25, "dLN": 0.85, "dRN": 0.90, "dLM": 1.10, "dRM": 1.05, "dLF": 1.20, "dRF": 1.15, "dLS": 2.00, "dRS": 1.80}
    - ESP32 → Python: {"vL": 0.65, "vR": 0.70}
    
    Sensor layout: Forward cone (Center 0°, Near ±15°, Mid ±35°, Far ±60°) + Side ±90°
    """
    
    @staticmethod
    def encode_sensor_data(
        d_center: float,
        d_left_near: float,
        d_right_near: float,
        d_left_mid: float,
        d_right_mid: float,
        d_left_far: float,
        d_right_far: float,
        d_left_side: float,
        d_right_side: float
    ) -> str:
        """
        Encode sensor data (9 sensors: 7 forward cone + 2 side) for transmission to ESP32
        
        Args:
            d_center: Center sensor distance (meters)
            d_left_near: Left near sensor (15°) distance (meters)
            d_right_near: Right near sensor (15°) distance (meters)
            d_left_mid: Left mid sensor (35°) distance (meters)
            d_right_mid: Right mid sensor (35°) distance (meters)
            d_left_far: Left far sensor (60°) distance (meters)
            d_right_far: Right far sensor (60°) distance (meters)
            d_left_side: Left side sensor (90°) distance (meters)
            d_right_side: Right side sensor (90°) distance (meters)
        
        Returns:
            JSON string with newline terminator
        """
        data = {
            "dC": round(d_center, 2),
            "dLN": round(d_left_near, 2),
            "dRN": round(d_right_near, 2),
            "dLM": round(d_left_mid, 2),
            "dRM": round(d_right_mid, 2),
            "dLF": round(d_left_far, 2),
            "dRF": round(d_right_far, 2),
            "dLS": round(d_left_side, 2),
            "dRS": round(d_right_side, 2)
        }
        return json.dumps(data) + "\n"
    
    @staticmethod
    def encode_sensor_data_with_waypoint(
        d_center: float,
        d_left_near: float,
        d_right_near: float,
        d_left_mid: float,
        d_right_mid: float,
        d_left_far: float,
        d_right_far: float,
        d_left_side: float,
        d_right_side: float,
        waypoint_x: float,
        waypoint_y: float,
        car_heading: float,
        car_x: float = 0.0,
        car_y: float = 0.0
    ) -> str:
        """
        Encode sensor data (9 sensors) + waypoint info + car position for ESP32
        
        Args:
            d_center, d_left_near, d_right_near, d_left_mid, d_right_mid,
            d_left_far, d_right_far, d_left_side, d_right_side: Sensor distances (m)
            waypoint_x, waypoint_y: Target waypoint coordinates (m)
            car_heading: Current car heading (radians)
            car_x, car_y: Current car position (m)
        
        Returns:
            JSON string with newline terminator
        """
        data = {
            "dC": round(d_center, 2),
            "dLN": round(d_left_near, 2),
            "dRN": round(d_right_near, 2),
            "dLM": round(d_left_mid, 2),
            "dRM": round(d_right_mid, 2),
            "dLF": round(d_left_far, 2),
            "dRF": round(d_right_far, 2),
            "dLS": round(d_left_side, 2),
            "dRS": round(d_right_side, 2),
            "wx": round(waypoint_x, 2),
            "wy": round(waypoint_y, 2),
            "h": round(car_heading, 3),
            "x": round(car_x, 2),
            "y": round(car_y, 2)
        }
        return json.dumps(data) + "\n"
    
    @staticmethod
    def decode_motor_commands(json_str: str) -> Optional[Tuple[float, float]]:
        """
        Decode motor commands received from ESP32
        
        Args:
            json_str: JSON string from ESP32
        
        Returns:
            (v_left, v_right) or None if parsing fails
        """
        try:
            # Remove whitespace and comments
            json_str = json_str.strip()
            if json_str.startswith("#") or not json_str:
                return None
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Extract motor velocities
            v_left = float(data.get("vL", 0.0))
            v_right = float(data.get("vR", 0.0))
            
            # Clamp to valid range
            v_left = max(-1.0, min(1.0, v_left))
            v_right = max(-1.0, min(1.0, v_right))
            
            return (v_left, v_right)
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Invalid JSON or missing fields
            return None
    
    @staticmethod
    def create_comment(text: str) -> str:
        """Create a comment line for serial output"""
        return f"# {text}\n"
