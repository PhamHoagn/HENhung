#include <Arduino.h>

#include "motor_control.h"
#include "navigation.h"
#include "obstacle_avoidance.h"
#include "sensor.h"

enum RobotState {
  IDLE,
  NAVIGATING,
  AVOIDING,
  ARRIVED
};

// Simulation-only placeholders (no physical pins are used)
constexpr uint8_t UNUSED_PIN = 255;

MotorControl motors(UNUSED_PIN, UNUSED_PIN, UNUSED_PIN, UNUSED_PIN, UNUSED_PIN, UNUSED_PIN);
SensorManager sensors(UNUSED_PIN, UNUSED_PIN, UNUSED_PIN, UNUSED_PIN);
NavigationController nav;
ObstacleAvoidance avoider;

RobotState state = IDLE;
unsigned long lastControl = 0;

static void logState(const char *msg) {
  Serial.print("[STATE] ");
  Serial.println(msg);
}

static void handleCommand(String line) {
  line.trim();
  if (line.length() == 0) return;

  float x, y;
  if (sscanf(line.c_str(), "GOTO %f %f", &x, &y) == 2) {
    nav.setTarget(x, y);
    state = NAVIGATING;
    Serial.printf("[CMD] Target set: (%.2f, %.2f)\n", x, y);
    return;
  }

  if (line == "START") {
    if (state == IDLE) state = NAVIGATING;
    logState("START -> NAVIGATING");
    return;
  }

  if (line == "STOP") {
    state = IDLE;
    motors.stop();
    logState("STOP -> IDLE");
    return;
  }

  // Simulation helper: POSE x y yaw
  float px, py, yaw;
  if (sscanf(line.c_str(), "POSE %f %f %f", &px, &py, &yaw) == 3) {
    nav.setPose(px, py, yaw);
    Serial.printf("[SIM] Pose updated: %.2f %.2f %.2f\n", px, py, yaw);
    return;
  }

  // Simulation helper: SENSOR dF dS
  float dF, dS;
  if (sscanf(line.c_str(), "SENSOR %f %f", &dF, &dS) == 2) {
    sensors.setSimulated(dF, dS);
    return;
  }

  Serial.printf("[WARN] Unknown cmd: %s\n", line.c_str());
}

void setup() {
  Serial.begin(115200);
  delay(300);

  motors.begin();
  sensors.begin();

  Serial.println("Robocar ESP32 Modular Controller Ready (ESP32-only simulation mode)");
  Serial.println("Commands: GOTO x y | START | STOP | POSE x y yaw | SENSOR dF dS");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    handleCommand(line);
  }

  if (millis() - lastControl < 50) return;
  lastControl = millis();

  SensorReading sr = sensors.read();
  WheelCommand cmd{0.0f, 0.0f};

  switch (state) {
    case IDLE:
      cmd = WheelCommand{0.0f, 0.0f};
      break;

    case NAVIGATING:
      if (nav.targetReached()) {
        state = ARRIVED;
        logState("ARRIVED");
        cmd = WheelCommand{0.0f, 0.0f};
      } else if (avoider.isBlocked(sr)) {
        state = AVOIDING;
        logState("AVOIDING");
        cmd = avoider.compute(sr);
      } else {
        cmd = nav.computeCommand();
      }
      break;

    case AVOIDING:
      cmd = avoider.compute(sr);
      if (!avoider.isBlocked(sr)) {
        state = NAVIGATING;
        logState("BACK TO NAVIGATING");
      }
      break;

    case ARRIVED:
      cmd = WheelCommand{0.0f, 0.0f};
      break;
  }

  motors.setWheelSpeed(cmd.left, cmd.right);
  WheelCommand out = motors.getLastCommand();
  Serial.printf("[DBG] st=%d dF=%.2f dS=%.2f cmd=(%.2f, %.2f) dist=%.2f\n",
                state, sr.frontM, sr.sideM, out.left, out.right, nav.distanceToTarget());
}
