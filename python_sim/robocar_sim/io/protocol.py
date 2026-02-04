"""
HIL Robocar - Serial Protocol
JSON encoding/decoding for sensor and motor data
"""

import json
from typing import Dict, Tuple, Optional


class SerialProtocol:
    """
    Handles JSON encoding/decoding for HIL communication
    
    Protocol:
    - Python → ESP32: {"dF": 1.25, "dL": 0.85, "dR": 2.10}
    - ESP32 → Python: {"vL": 0.65, "vR": 0.70}
    """
    
    @staticmethod
    def encode_sensor_data(
        distance_front: float,
        distance_left: float,
        distance_right: float
    ) -> str:
        """
        Encode sensor data for transmission to ESP32
        
        Args:
            distance_front: Front sensor distance (meters)
            distance_left: Left sensor distance (meters)
            distance_right: Right sensor distance (meters)
        
        Returns:
            JSON string with newline terminator
        """
        data = {
            "dF": round(distance_front, 2),
            "dL": round(distance_left, 2),
            "dR": round(distance_right, 2)
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
