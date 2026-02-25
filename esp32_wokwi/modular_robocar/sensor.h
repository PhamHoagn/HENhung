#ifndef SENSOR_H
#define SENSOR_H

#include <Arduino.h>

struct SensorReading {
  float frontM;
  float sideM;
  bool simulated;
};

class SensorManager {
 public:
  SensorManager(uint8_t trigFront, uint8_t echoFront, uint8_t trigSide, uint8_t echoSide);
  void begin();
  void setSimulated(float frontM, float sideM);
  SensorReading read();

 private:
  uint8_t _trigFront, _echoFront, _trigSide, _echoSide;
  SensorReading _latest{2.5f, 2.5f, false};
  float readUltrasonicM(uint8_t trig, uint8_t echo);
};

#endif
