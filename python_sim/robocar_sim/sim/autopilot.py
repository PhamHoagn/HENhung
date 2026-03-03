"""
HIL Robocar – Fallback Autopilot  (v3.0)
==========================================

Minimal fallback used ONLY when the ESP32 controller is not connected.

Provides:
  • Proportional waypoint heading control  (P-controller on heading error)
  • Conservative obstacle avoidance with graduated response
  • Emergency stop / reverse when obstacle is very close
  • Hysteresis to avoid oscillating between avoid and follow

The ESP32 firmware with trained Decision-Tree AI remains the SOLE
intelligent brain.  This fallback is intentionally simple so a demo
can run without hardware, but it is NOT a replacement for the real AI.
"""

import math
from typing import Optional, Tuple


class SafeStopFallback:
    """
    Minimal fallback controller — used ONLY when ESP32 serial is
    disconnected.  Provides obstacle avoidance + proportional waypoint
    following and emergency stop.
    """

    MAX_SPEED = 0.65            # max forward speed (normalised)
    EMERGENCY_DIST = 0.45       # metres – full stop / reverse
    DANGER_DIST = 0.80          # metres – strong avoidance
    CAUTION_DIST = 1.20         # metres – gentle blend
    HALF_TRACK = 0.11           # 0.5 × track_width for (v,ω) → (vL,vR)

    def __init__(self):
        self._last_vl = 0.0
        self._last_vr = 0.0
        self._avoiding = False              # hysteresis flag

    @staticmethod
    def _norm_angle(a: float) -> float:
        while a > math.pi:
            a -= 2 * math.pi
        while a < -math.pi:
            a += 2 * math.pi
        return a

    def compute_commands(
        self,
        car_pos: Tuple[float, float],
        car_heading: float,
        waypoint: Optional[Tuple[float, float]],
        sensor_data: Tuple[float, float, float, float, float, float, float, float, float],
    ) -> Tuple[float, float]:
        """
        Return (vL, vR) in normalised range [-1, 1].
        """
        dC, dLN, dRN, dLM, dRM, dLF, dRF, _dLS, _dRS = sensor_data
        fwd_min = min(dC, dLN, dRN, dLM, dRM, dLF, dRF)

        d_left = min(dLN, dLM, dLF)
        d_right = min(dRN, dRM, dRF)
        min_side = min(d_left, d_right)

        # ── Hysteresis: stay in avoiding until obstacle is clearly far ──
        if self._avoiding:
            if fwd_min > self.CAUTION_DIST and min_side > self.DANGER_DIST:
                self._avoiding = False
        elif fwd_min < self.DANGER_DIST or min_side < self.EMERGENCY_DIST:
            self._avoiding = True

        # ── Emergency: too close — reverse ──
        if fwd_min < self.EMERGENCY_DIST:
            target_v = -0.20
            # Spin away from closest side
            target_w = 2.0 if d_left > d_right else -2.0
        elif self._avoiding:
            # ── Active avoidance ──
            # Base avoidance: pick direction away from closest obstacle
            bias_w = 0.0
            if d_left < self.DANGER_DIST or d_right < self.DANGER_DIST:
                bias_w = 1.0 if d_left < d_right else -1.0  # steer AWAY
            elif dC < self.DANGER_DIST:
                bias_w = 0.9 if d_left > d_right else -0.9

            # Blend lightly with waypoint heading to keep general direction
            wp_w = 0.0
            if waypoint is not None:
                dx = waypoint[0] - car_pos[0]
                dy = waypoint[1] - car_pos[1]
                desired = math.atan2(dy, dx)
                wp_w = 1.2 * self._norm_angle(desired - car_heading)

            target_w = 0.75 * bias_w + 0.25 * wp_w

            # Proportional speed: very slow when close
            prox = max(0.0, (fwd_min - self.EMERGENCY_DIST)
                       / (self.CAUTION_DIST - self.EMERGENCY_DIST))
            target_v = 0.15 + 0.35 * prox               # 0.15–0.50 m/s
        elif waypoint is not None:
            # ── Normal waypoint tracking ──
            dx = waypoint[0] - car_pos[0]
            dy = waypoint[1] - car_pos[1]
            dist = math.hypot(dx, dy)
            desired = math.atan2(dy, dx)
            err = self._norm_angle(desired - car_heading)

            # Forward speed: ramp up with distance, slow near goal
            target_v = min(self.MAX_SPEED, 0.20 + 0.60 * dist)
            # Reduce speed when heading error is large
            target_v *= max(0.15, 1.0 - 0.7 * min(abs(err) / math.pi, 1.0))

            # Speed reduction if obstacle in warning zone
            if fwd_min < self.CAUTION_DIST:
                prox = max(0.2, (fwd_min - self.EMERGENCY_DIST)
                           / (self.CAUTION_DIST - self.EMERGENCY_DIST))
                target_v *= prox

            # Steering: proportional controller
            target_w = 2.0 * err

            # Add obstacle bias in caution zone
            if min(fwd_min, min_side) < self.CAUTION_DIST:
                bias = 0.4 if d_left < d_right else -0.4
                target_w += bias
        else:
            # No waypoint – creep forward
            target_v = 0.06
            target_w = 0.0

        # ── (v, ω) → differential (vL, vR) ──
        raw_vl = target_v - self.HALF_TRACK * target_w
        raw_vr = target_v + self.HALF_TRACK * target_w

        # Normalise
        mag = max(1.0, abs(raw_vl), abs(raw_vr))
        raw_vl /= mag
        raw_vr /= mag

        # EMA smoothing – fast for avoidance, slower for cruise
        alpha = 0.60 if self._avoiding else 0.40
        self._last_vl = (1 - alpha) * self._last_vl + alpha * raw_vl
        self._last_vr = (1 - alpha) * self._last_vr + alpha * raw_vr

        return self._last_vl, self._last_vr

    def reset(self):
        self._last_vl = 0.0
        self._last_vr = 0.0
        self._avoiding = False


# Backward-compatible alias
WaypointAutopilot = SafeStopFallback
