#include "sensor.h"

SensorManager::SensorManager(uint8_t trigFront, uint8_t echoFront, uint8_t trigSide, uint8_t echoSide)
    : _trigFront(trigFront), _echoFront(echoFront), _trigSide(trigSide), _echoSide(echoSide) {}

void SensorManager::begin() {
  // Simulation-only mode: no physical ultrasonic sensor pins are used.
  _latest = {2.5f, 2.5f, true};
}

float SensorManager::readUltrasonicM(uint8_t trig, uint8_t echo) {
  (void)trig;
  (void)echo;
  // No hardware in this project mode.
  return 4.0f;
}

void SensorManager::setSimulated(float frontM, float sideM) {
  _latest.frontM = constrain(frontM, 0.02f, 4.0f);
  _latest.sideM = constrain(sideM, 0.02f, 4.0f);
  _latest.simulated = true;
}

SensorReading SensorManager::read() {
  // Always serve simulation value for ESP32-only Wokwi workflow.
  return _latest;
}
