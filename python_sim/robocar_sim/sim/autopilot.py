"""
Simple waypoint-following autopilot with obstacle avoidance smoothing.
"""

import math
from typing import Optional, Tuple


class WaypointAutopilot:
    """Generate differential motor commands from waypoint + ultrasonic sensors."""

    def __init__(self, max_speed: float = 0.8):
        self.max_speed = max_speed
        self._last_vl = 0.0
        self._last_vr = 0.0

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def compute_commands(
        self,
        car_pos: Tuple[float, float],
        car_heading: float,
        waypoint: Optional[Tuple[float, float]],
        sensor_data: Tuple[float, float, float],
    ) -> Tuple[float, float]:
        """Compute smooth (vL, vR) in normalized range [-1, 1]."""
        d_front, d_left, d_right = sensor_data

        if waypoint is None:
            target_speed = 0.0
            target_turn = 0.0
        else:
            dx = waypoint[0] - car_pos[0]
            dy = waypoint[1] - car_pos[1]
            distance = math.hypot(dx, dy)
            desired_heading = math.atan2(dy, dx)
            heading_error = self._normalize_angle(desired_heading - car_heading)

            # Smooth forward speed profile to reduce overshoot near waypoints.
            target_speed = min(self.max_speed, 0.25 + 0.6 * distance)
            target_speed *= max(0.2, 1.0 - min(abs(heading_error) / math.pi, 0.85))

            # Steering gain + clamp
            target_turn = max(-0.8, min(0.8, 1.6 * heading_error / math.pi))

            # Obstacle avoidance blending (potential field style)
            if d_front < 0.35:
                target_speed *= 0.2
                turn_bias = -0.9 if d_left < d_right else 0.9
                target_turn = 0.7 * target_turn + 0.3 * turn_bias
            elif d_front < 0.7:
                target_speed *= 0.65

            side_clearance = d_left - d_right
            target_turn += max(-0.25, min(0.25, -0.4 * side_clearance))

        raw_vl = target_speed - target_turn
        raw_vr = target_speed + target_turn

        # Normalize wheel commands while keeping turning ratio.
        max_mag = max(1.0, abs(raw_vl), abs(raw_vr))
        raw_vl /= max_mag
        raw_vr /= max_mag

        # First-order low-pass for smoother motion.
        alpha = 0.25
        self._last_vl = (1 - alpha) * self._last_vl + alpha * raw_vl
        self._last_vr = (1 - alpha) * self._last_vr + alpha * raw_vr

        return self._last_vl, self._last_vr

    def reset(self):
        self._last_vl = 0.0
        self._last_vr = 0.0
