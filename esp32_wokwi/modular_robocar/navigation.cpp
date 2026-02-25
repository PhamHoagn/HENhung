#include "navigation.h"

static float wrapToPi(float angle) {
  while (angle > PI) angle -= 2.0f * PI;
  while (angle < -PI) angle += 2.0f * PI;
  return angle;
}

void NavigationController::setTarget(float x, float y) {
  _targetX = x;
  _targetY = y;
  _hasTarget = true;
}

void NavigationController::setPose(float x, float y, float yaw) {
  _pose.x = x;
  _pose.y = y;
  _pose.yaw = yaw;
}

float NavigationController::distanceToTarget() const {
  float dx = _targetX - _pose.x;
  float dy = _targetY - _pose.y;
  return sqrtf(dx * dx + dy * dy);
}

bool NavigationController::targetReached() const {
  return _hasTarget && distanceToTarget() < _arrivalThresholdM;
}

WheelCommand NavigationController::computeCommand() {
  WheelCommand cmd{0.0f, 0.0f};
  if (!_hasTarget) return cmd;
  if (targetReached()) return cmd;

  float dx = _targetX - _pose.x;
  float dy = _targetY - _pose.y;
  float desiredHeading = atan2f(dy, dx);
  float headingErr = wrapToPi(desiredHeading - _pose.yaw);

  float omega = _kHeading * headingErr;
  float speed = _baseSpeed * (1.0f - min(fabs(headingErr) / PI, 0.85f));

  cmd.left = constrain(speed - omega, -1.0f, 1.0f);
  cmd.right = constrain(speed + omega, -1.0f, 1.0f);
  return cmd;
}
