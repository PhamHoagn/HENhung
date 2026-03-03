"""
HIL Robocar – Serial Protocol  (v2.0)
=======================================
JSON encoding/decoding for sensor and motor data.

Python → ESP32:
    {"t":ms, "x":m, "y":m, "th":rad, "wpX":m, "wpY":m, "d":[d0..d8]}

ESP32 → Python:
    {"t":ms, "vL":f, "vR":f, "mode":"FOLLOW|AVOID|STOP|RECOVERY",
     "ai_a":int, "ai_s":float, "ai_ms":float}
"""

import json
from typing import Dict, Tuple, Optional


class MotorResponse:
    """Parsed motor response from ESP32, including AI telemetry."""
    __slots__ = ("vL", "vR", "mode", "ai_action", "ai_speed", "ai_ms")

    def __init__(
        self,
        vL: float = 0.0,
        vR: float = 0.0,
        mode: str = "STOP",
        ai_action: int = -1,
        ai_speed: float = 0.0,
        ai_ms: float = 0.0,
    ):
        self.vL = vL
        self.vR = vR
        self.mode = mode
        self.ai_action = ai_action
        self.ai_speed = ai_speed
        self.ai_ms = ai_ms

    @property
    def motor_tuple(self) -> Tuple[float, float]:
        return (self.vL, self.vR)


class SerialProtocol:
    """
    Protocol (9 ultrasonic sensors):
    - Python → ESP32: {"t":..., "x":..., "y":..., "th":..., "wpX":..., "wpY":..., "d":[d0..d8]}
    - ESP32 → Python: {"t":..., "vL":..., "vR":..., "mode":..., "ai_a":..., "ai_s":..., "ai_ms":...}
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
        """Decode motor commands – returns (vL, vR) or None."""
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
    def decode_motor_response(json_str: str) -> Optional["MotorResponse"]:
        """Decode full motor response including AI telemetry."""
        try:
            json_str = json_str.strip()
            if json_str.startswith("#") or not json_str:
                return None

            data = json.loads(json_str)
            vL = max(-1.0, min(1.0, float(data.get("vL", 0.0))))
            vR = max(-1.0, min(1.0, float(data.get("vR", 0.0))))
            mode = str(data.get("mode", "STOP"))
            ai_action = int(data.get("ai_a", -1))
            ai_speed = float(data.get("ai_s", 0.0))
            ai_ms = float(data.get("ai_ms", 0.0))
            return MotorResponse(
                vL=vL, vR=vR, mode=mode,
                ai_action=ai_action, ai_speed=ai_speed, ai_ms=ai_ms,
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            return None

    @staticmethod
    def create_comment(text: str) -> str:
        return f"# {text}\n"
