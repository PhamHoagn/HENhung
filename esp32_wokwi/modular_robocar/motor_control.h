#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include <Arduino.h>

struct WheelCommand {
  float left;
  float right;
};

class MotorControl {
 public:
  MotorControl(uint8_t in1, uint8_t in2, uint8_t ena, uint8_t in3, uint8_t in4, uint8_t enb);
  void begin();
  void setWheelSpeed(float left, float right);
  WheelCommand getLastCommand() const;
  void stop();

 private:
  uint8_t _in1, _in2, _ena, _in3, _in4, _enb;
  WheelCommand _last{0.0f, 0.0f};
  void driveMotor(uint8_t inA, uint8_t inB, uint8_t pwmPin, float speed);
};

#endif
