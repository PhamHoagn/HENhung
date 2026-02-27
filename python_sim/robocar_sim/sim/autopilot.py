"""
Simple waypoint-following autopilot with obstacle avoidance smoothing.
"""

import math
from typing import Optional, Tuple


class WaypointAutopilot:
    """Generate differential motor commands from waypoint + ultrasonic sensors."""

    def __init__(self, max_speed: float = 0.35):  # Reduced from 0.4 for safer operation
        """Initialize autopilot with safer default speed."""
        self.max_speed = max_speed
        self._last_vl = 0.0
        self._last_vr = 0.0
        self._steering_deadzone = 0.02  # Reduced from 0.05 for better responsiveness

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
        sensor_data: Tuple[float, float, float, float, float, float, float, float, float],
    ) -> Tuple[float, float]:
        """Compute smooth (vL, vR) in normalized range [-1, 1]."""
        # Sensor pattern: 7 forward cone + 2 side
        # Forward: center, L-near, R-near, L-mid, R-mid, L-far, R-far
        # Side: L-side (90°), R-side (90°)
        dC, dLN, dRN, dLM, dRM, dLF, dRF, dLS, dRS = sensor_data
        
        # Calculate weighted obstacle perception
        d_front = dC  # Main forward sensor
        d_left = min(dLN, dLM, dLF)  # Closest on left side (forward arc)
        d_right = min(dRN, dRM, dRF)  # Closest on right side (forward arc)
        min_all = min(dC, dLN, dRN, dLM, dRM, dLF, dRF)  # Minimum of FORWARD sensors only

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
            target_speed = min(self.max_speed, 0.15 + 0.4 * distance)
            target_speed *= max(0.15, 1.0 - min(abs(heading_error) / math.pi, 0.85))

            # Steering gain + clamp (smoother turning)
            target_turn = max(-0.7, min(0.7, 1.4 * heading_error / math.pi))
            
            # Apply steering deadzone to reduce jittering
            if abs(target_turn) < self._steering_deadzone:
                target_turn *= 0.3  # Dampen very small corrections

            # Enhanced obstacle avoidance with SMOOTH continuous transitions
            # CRITICAL: When obstacle detected, OVERRIDE waypoint navigation completely!
            if d_front < 0.50:  # Increased from 0.40m for even earlier stop
                # CRITICAL - Emergency: STOP COMPLETELY and TURN HARD
                speed_factor = 0.0  # FULL STOP
                turn_bias = -2.0 if d_left < d_right else 2.0  # Increased from 1.5 for stronger turn
                target_turn = turn_bias  # 100% obstacle avoidance
            elif d_front < 0.75:  # Increased from 0.60m for earlier danger detection
                # DANGER - Strong obstacle priority: 95% avoidance, 5% waypoint
                # Smooth transition from 0.0 at 0.50m to 0.10 at 0.75m
                t = (d_front - 0.50) / (0.75 - 0.50)
                speed_factor = 0.0 + (0.10 - 0.0) * t
                turn_bias = -1.5 if d_left < d_right else 1.5  # Increased from 1.3
                target_turn = 0.05 * target_turn + 0.95 * turn_bias  # 95% avoidance
            elif d_front < 1.0:  # Increased from 0.90m for even earlier WARNING
                # WARNING - Very high obstacle priority: 90% avoidance, 10% waypoint (increased from 85%)
                # Smooth transition from 0.10 at 0.75m to 0.30 at 1.0m
                t = (d_front - 0.75) / (1.0 - 0.75)
                speed_factor = 0.10 + (0.30 - 0.10) * t
                turn_bias = -0.9 if d_left < d_right else 0.9
                target_turn = 0.10 * target_turn + 0.90 * turn_bias  # 90% avoidance
            elif d_front < 2.0:  # Extended from 1.8m for even earlier CAUTION detection
                # CAUTION - Favor obstacle avoidance: 60% avoidance, 40% waypoint
                # Smooth transition from 0.30 at 1.0m to 0.60 at 2.0m
                t = (d_front - 1.0) / (2.0 - 1.0)
                speed_factor = 0.30 + (0.60 - 0.30) * t
                turn_bias = -0.5 if d_left < d_right else 0.5
                target_turn = 0.40 * target_turn + 0.60 * turn_bias  # Always 60% avoidance (removed obstacle_cleared)
            else:
                speed_factor = 1.0
            
            # Apply smooth speed reduction if obstacle detected
            if d_front < 2.0:  # Extended from 1.8m
                target_speed *= speed_factor

            # Wide cone-based side obstacle avoidance
            # PRIORITY: Red zones (< 0.3m) get MUCH higher weight than yellow zones (0.6-1.0m)
            # Apply when obstacle detected, but strength decreases with distance
            if min_all < 1.2:  # Increased from 1.0m - detect earlier but apply smartly
                # Helper function: Calculate danger weight based on distance
                def get_distance_weight(dist):
                    if dist < 0.3:    # RED zone - highest priority
                        return 10.0
                    elif dist < 0.6:  # ORANGE zone - high priority
                        return 5.0
                    elif dist < 1.0:  # YELLOW zone - medium priority
                        return 2.0
                    else:             # GREEN zone - low priority
                        return 0.5    # Very low weight for far obstacles
                
                # Calculate weighted danger: distance_weight * angle_weight
                # Angle weights: near (15°) 3x, mid (35°) 2x, far (60°) 1x
                left_danger = (
                    get_distance_weight(dLN) * 3.0 / (dLN + 0.1) +  # Near left
                    get_distance_weight(dLM) * 2.0 / (dLM + 0.1) +  # Mid left
                    get_distance_weight(dLF) * 1.0 / (dLF + 0.1)    # Far left
                )
                right_danger = (
                    get_distance_weight(dRN) * 3.0 / (dRN + 0.1) +  # Near right
                    get_distance_weight(dRM) * 2.0 / (dRM + 0.1) +  # Mid right
                    get_distance_weight(dRF) * 1.0 / (dRF + 0.1)    # Far right
                )
                
                # Steer away from more dangerous side
                danger_diff = left_danger - right_danger
                repulsion_strength = (1.2 - min_all) / 1.2  # Changed from 1.0
                side_push = danger_diff * repulsion_strength * 0.28  # Increased from 0.22 for stronger avoidance
                side_push = max(-0.6, min(0.6, side_push))  # Increased from 0.5
                target_turn += side_push

        # Apply stronger differential for WIDER turns when RED zones detected
        # Check if any sensor is in RED zone (< 0.3m) for extra wide turning
        has_red_zone = min(
            dC, dLN, dRN, dLM, dRM, dLF, dRF
        ) < 0.3
        
        # Adaptive turn multiplier based on obstacle proximity
        if has_red_zone:
            turn_multiplier = 0.85  # Extra wide turns for RED zones
        elif min_all < 0.6:
            turn_multiplier = 0.80  # Wide turns for ORANGE zones
        elif min_all < 1.0:
            turn_multiplier = 0.70  # Moderate turns for YELLOW zones
        elif min_all < 1.3:
            turn_multiplier = 0.65  # Gentle turns when somewhat clear
        else:
            turn_multiplier = 0.60  # Gentle turns when path is clear
        
        raw_vl = target_speed - (target_turn * turn_multiplier)
        raw_vr = target_speed + (target_turn * turn_multiplier)

        # Normalize wheel commands while keeping turning ratio.
        max_mag = max(1.0, abs(raw_vl), abs(raw_vr))
        raw_vl /= max_mag
        raw_vr /= max_mag

        # Reduce smoothing when obstacle detected for FASTER response
        if min_all < 0.75:  # Increased from 0.60m
            # CRITICAL/DANGER - minimal smoothing for IMMEDIATE response
            alpha = 0.65  # Increased from 0.40 for even faster response
        elif min_all < 1.2:  # Increased from 1.0m
            # WARNING - moderate smoothing
            alpha = 0.30  # Increased from 0.20
        else:
            # SAFE - normal smoothing
            alpha = 0.15
        
        self._last_vl = (1 - alpha) * self._last_vl + alpha * raw_vl
        self._last_vr = (1 - alpha) * self._last_vr + alpha * raw_vr

        return self._last_vl, self._last_vr

    def reset(self):
        self._last_vl = 0.0
        self._last_vr = 0.0
