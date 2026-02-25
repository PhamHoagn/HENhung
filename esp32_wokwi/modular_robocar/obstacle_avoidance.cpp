#include "obstacle_avoidance.h"

WheelCommand ObstacleAvoidance::compute(const SensorReading &reading) const {
  WheelCommand cmd{0.5f, 0.5f};

  if (reading.frontM < _critical) {
    return WheelCommand{0.0f, 0.0f};
  }

  if (reading.frontM < _warn) {
    if (reading.sideM > _warn) {
      return WheelCommand{-0.35f, 0.60f};
    }
    return WheelCommand{0.60f, -0.35f};
  }

  if (reading.sideM < _warn) {
    return WheelCommand{0.55f, 0.20f};
  }

  return cmd;
}

bool ObstacleAvoidance::isBlocked(const SensorReading &reading) const {
  return reading.frontM < _warn || reading.sideM < _warn;
}
