#ifndef NAVIGATION_H
#define NAVIGATION_H

#include <Arduino.h>
#include "motor_control.h"

struct Pose2D {
  float x;
  float y;
  float yaw;
};

class NavigationController {
 public:
  void setTarget(float x, float y);
  void setPose(float x, float y, float yaw);
  bool targetReached() const;
  float distanceToTarget() const;
  WheelCommand computeCommand();

 private:
  Pose2D _pose{0.0f, 0.0f, 0.0f};
  float _targetX = 0.0f;
  float _targetY = 0.0f;
  bool _hasTarget = false;

  float _kHeading = 1.2f;
  float _baseSpeed = 0.45f;
  float _arrivalThresholdM = 0.15f;
};

#endif
