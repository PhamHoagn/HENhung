"""
HIL Robocar – Physics Engine  (v2.0 – 4WD Skid-Steer model)
=============================================================

Vehicle Model: **4-Wheel Skid-Steer Differential Drive**
─────────────────────────────────────────────────────────
The robot has 4 independently-driven wheels arranged in a
rectangular chassis.  Left-side wheels share the same command
(vL), right-side wheels share the same command (vR).

    Front-Left (FL) ───┬─── Front-Right (FR)
          │            │           │
          │     chassis body      │
          │            │           │
     Rear-Left (RL) ──┴─── Rear-Right (RR)

          track_width  = distance between left & right wheels
          wheel_base   = distance between front & rear axles

Kinematics (unicycle approximation for skid-steer):
    v_linear  = (vR + vL) / 2          [m/s]
    ω         = (vR − vL) / track_width [rad/s]

    dx/dt = v_linear · cos(θ)
    dy/dt = v_linear · sin(θ)
    dθ/dt = ω

The model adds lateral friction to approximate real skid-steer
behavior where turning causes tyre scrubbing.

This file is a **PURE SIMULATION** component – no control logic.
Motor commands arrive from the ESP32 controller over serial.
"""

import math
from dataclasses import dataclass
from typing import Tuple


# ── State ────────────────────────────────────────────────────────
@dataclass
class CarState:
    """Full kinematic state of the 4WD skid-steer robot."""
    x: float = 0.0          # X position  [m]
    y: float = 0.0          # Y position  [m]
    theta: float = 0.0      # Heading     [rad, 0=East, CCW+]
    v_left: float = 0.0     # Left-side wheel velocity  [m/s]
    v_right: float = 0.0    # Right-side wheel velocity [m/s]
    # 4-wheel individual speeds (for telemetry / rendering)
    v_fl: float = 0.0       # Front-Left
    v_fr: float = 0.0       # Front-Right
    v_rl: float = 0.0       # Rear-Left
    v_rr: float = 0.0       # Rear-Right


# ── 4WD Skid-Steer Car ──────────────────────────────────────────
class FourWheelSkidSteerCar:
    """
    4-Wheel Skid-Steer Differential Drive Robot
    =============================================
    Geometry
    --------
        track_width  – lateral distance between left & right wheel centres
        wheel_base   – longitudinal distance between front & rear axles
        wheel_radius – radius of each wheel (for RPM display only)

    Control inputs (from ESP32)
    ---------------------------
        vL ∈ [-1, 1]  normalised left-side speed
        vR ∈ [-1, 1]  normalised right-side speed

    All 4 wheels are powered.  FL & RL share vL; FR & RR share vR.

    Lateral friction factor (0–1) models energy lost to tyre
    scrubbing during skid turns.  0 = no friction loss, 1 = ideal.
    """

    def __init__(
        self,
        x: float = 2.0,
        y: float = 2.0,
        theta: float = 0.0,
        track_width: float = 0.22,     # distance left↔right  [m]
        wheel_base: float = 0.16,      # distance front↔rear  [m]
        max_speed: float = 0.60,       # max linear wheel speed [m/s]
        wheel_radius: float = 0.033,   # wheel radius [m]
        lateral_friction: float = 0.85,  # scrub friction factor
    ):
        self.state = CarState(x=x, y=y, theta=theta)
        self.track_width = track_width
        self.wheel_base = wheel_base
        self.max_speed = max_speed
        self.wheel_radius = wheel_radius
        self.lateral_friction = lateral_friction

        # Derived limits
        self.max_angular_velocity = (2 * max_speed) / track_width

    # ── Motor command interface ──────────────────────────────────
    def set_motor_commands(self, v_left: float, v_right: float):
        """
        Set normalised motor commands from the ESP32 controller.

        Args
        ----
        v_left  : float in [-1, 1]  – left-side  wheel command
        v_right : float in [-1, 1]  – right-side wheel command

        Internally converts to m/s and distributes to 4 wheels:
            FL = RL = v_left  × max_speed
            FR = RR = v_right × max_speed
        """
        v_left = max(-1.0, min(1.0, v_left))
        v_right = max(-1.0, min(1.0, v_right))

        self.state.v_left = v_left * self.max_speed
        self.state.v_right = v_right * self.max_speed

        # Individual wheels (same on each side for skid-steer)
        self.state.v_fl = self.state.v_left
        self.state.v_rl = self.state.v_left
        self.state.v_fr = self.state.v_right
        self.state.v_rr = self.state.v_right

    # ── Physics integration ──────────────────────────────────────
    def update(self, dt: float):
        """
        Integrate one time-step of the skid-steer kinematics.

        Uses the standard unicycle approximation:
            v = (v_right + v_left) / 2
            ω = (v_right − v_left) / track_width

        Lateral friction dampens ω to model tyre scrubbing:
            ω_eff = ω × lateral_friction
        """
        v_l = self.state.v_left
        v_r = self.state.v_right

        # Unicycle model
        v_linear = (v_r + v_l) / 2.0
        omega = (v_r - v_l) / self.track_width

        # Lateral friction: reduces turning effectiveness
        omega *= self.lateral_friction

        # Integrate heading
        self.state.theta += omega * dt
        self.state.theta = math.atan2(
            math.sin(self.state.theta),
            math.cos(self.state.theta),
        )

        # Integrate position
        self.state.x += v_linear * math.cos(self.state.theta) * dt
        self.state.y += v_linear * math.sin(self.state.theta) * dt

    # ── Accessors ────────────────────────────────────────────────
    def get_position(self) -> Tuple[float, float]:
        return (self.state.x, self.state.y)

    def get_heading(self) -> float:
        return self.state.theta

    def get_velocities(self) -> Tuple[float, float]:
        """Return (v_left, v_right) in m/s."""
        return (self.state.v_left, self.state.v_right)

    def get_wheel_speeds(self) -> Tuple[float, float, float, float]:
        """Return (FL, FR, RL, RR) in m/s."""
        return (
            self.state.v_fl,
            self.state.v_fr,
            self.state.v_rl,
            self.state.v_rr,
        )

    def get_wheel_geometry(self) -> list:
        """
        Return 4 wheel centre positions in **local** frame
        [(lx, ly), …] for FL, FR, RL, RR – used by renderer.
        """
        hw = self.track_width / 2.0   # half track width
        hb = self.wheel_base / 2.0    # half wheel base
        return [
            (+hb, +hw),   # Front-Left
            (+hb, -hw),   # Front-Right
            (-hb, +hw),   # Rear-Left
            (-hb, -hw),   # Rear-Right
        ]

    def reset(self, x: float, y: float, theta: float):
        self.state = CarState(x=x, y=y, theta=theta)


# ── Collision Detector ───────────────────────────────────────────
class CollisionDetector:
    """Collision detection treating the robot as a bounding circle."""

    def __init__(self, robot_radius: float = 0.18):
        self.robot_radius = robot_radius

    def check_circle_collision(
        self,
        robot_pos: Tuple[float, float],
        obstacle_pos: Tuple[float, float],
        obstacle_radius: float,
    ) -> bool:
        rx, ry = robot_pos
        ox, oy = obstacle_pos
        distance = math.hypot(rx - ox, ry - oy)
        return distance < (self.robot_radius + obstacle_radius)

    def check_wall_collision(
        self,
        robot_pos: Tuple[float, float],
        world_width: float,
        world_height: float,
    ) -> bool:
        x, y = robot_pos
        r = self.robot_radius
        return (x - r < 0 or x + r > world_width or
                y - r < 0 or y + r > world_height)
