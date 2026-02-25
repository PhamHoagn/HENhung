#include "motor_control.h"

MotorControl::MotorControl(uint8_t in1, uint8_t in2, uint8_t ena, uint8_t in3, uint8_t in4, uint8_t enb)
    : _in1(in1), _in2(in2), _ena(ena), _in3(in3), _in4(in4), _enb(enb) {}

void MotorControl::begin() {
  // Simulation-only mode: no real motor driver pins are used.
  _last = {0.0f, 0.0f};
}

void MotorControl::driveMotor(uint8_t inA, uint8_t inB, uint8_t pwmPin, float speed) {
  // Keep interface for future hardware expansion.
  (void)inA;
  (void)inB;
  (void)pwmPin;
  (void)speed;
}

void MotorControl::setWheelSpeed(float left, float right) {
  _last.left = constrain(left, -1.0f, 1.0f);
  _last.right = constrain(right, -1.0f, 1.0f);
}

WheelCommand MotorControl::getLastCommand() const { return _last; }

void MotorControl::stop() { setWheelSpeed(0.0f, 0.0f); }
