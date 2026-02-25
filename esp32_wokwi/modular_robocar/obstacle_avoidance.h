#ifndef OBSTACLE_AVOIDANCE_H
#define OBSTACLE_AVOIDANCE_H

#include "motor_control.h"
#include "sensor.h"

class ObstacleAvoidance {
 public:
  WheelCommand compute(const SensorReading &reading) const;
  bool isBlocked(const SensorReading &reading) const;

 private:
  float _critical = 0.20f;
  float _warn = 0.35f;
};

#endif
