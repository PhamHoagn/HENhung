"""
HIL Robocar - Serial Protocol
JSON encoding/decoding for sensor and motor data
"""

import json
from typing import Dict, Tuple, Optional


class SerialProtocol:
    """
    Protocol (9 ultrasonic sensors):
    - Python → ESP32: {"t":..., "x":..., "y":..., "th":..., "wpX":..., "wpY":..., "d":[d0..d8]}
    - ESP32 → Python: {"t":..., "vL":..., "vR":..., "mode":"FOLLOW|AVOID|STOP|RECOVERY", "ai_b":..., "ai_s":..., "ai_ms":...}
    """

    @staticmethod
    def _pack_sensor_vector(
        d_center: float,
        d_left_near: float,
        d_right_near: float,
        d_left_mid: float,
        d_right_mid: float,
        d_left_far: float,
        d_right_far: float,
        d_left_side: float,
        d_right_side: float,
    ) -> list:
        # ESP32 expected order: [LS, LF, LM, LN, C, RN, RM, RF, RS]
        return [
            round(d_left_side, 3),
            round(d_left_far, 3),
            round(d_left_mid, 3),
            round(d_left_near, 3),
            round(d_center, 3),
            round(d_right_near, 3),
            round(d_right_mid, 3),
            round(d_right_far, 3),
            round(d_right_side, 3),
        ]

    @classmethod
    def encode_sensor_data(
        cls,
        d_center: float,
        d_left_near: float,
        d_right_near: float,
        d_left_mid: float,
        d_right_mid: float,
        d_left_far: float,
        d_right_far: float,
        d_left_side: float,
        d_right_side: float,
        timestamp_s: float = 0.0,
    ) -> str:
        data = {
            "t": int(timestamp_s * 1000.0),
            "x": 0.0,
            "y": 0.0,
            "th": 0.0,
            "d": cls._pack_sensor_vector(
                d_center,
                d_left_near,
                d_right_near,
                d_left_mid,
                d_right_mid,
                d_left_far,
                d_right_far,
                d_left_side,
                d_right_side,
            ),
        }
        return json.dumps(data) + "\n"

    @classmethod
    def encode_sensor_data_with_waypoint(
        cls,
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
        car_y: float = 0.0,
        timestamp_s: float = 0.0,
    ) -> str:
        data = {
            "t": int(timestamp_s * 1000.0),
            "x": round(car_x, 3),
            "y": round(car_y, 3),
            "th": round(car_heading, 4),
            "wpX": round(waypoint_x, 3),
            "wpY": round(waypoint_y, 3),
            "d": cls._pack_sensor_vector(
                d_center,
                d_left_near,
                d_right_near,
                d_left_mid,
                d_right_mid,
                d_left_far,
                d_right_far,
                d_left_side,
                d_right_side,
            ),
        }
        return json.dumps(data) + "\n"

    @staticmethod
    def decode_motor_commands(json_str: str) -> Optional[Tuple[float, float]]:
        try:
            json_str = json_str.strip()
            if json_str.startswith("#") or not json_str:
                return None

            data = json.loads(json_str)
            v_left = float(data.get("vL", 0.0))
            v_right = float(data.get("vR", 0.0))
            v_left = max(-1.0, min(1.0, v_left))
            v_right = max(-1.0, min(1.0, v_right))
            return (v_left, v_right)
        except (json.JSONDecodeError, ValueError, KeyError):
            return None

    @staticmethod
    def create_comment(text: str) -> str:
        return f"# {text}\n"
