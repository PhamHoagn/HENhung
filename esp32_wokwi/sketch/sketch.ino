/*
 * HIL Robocar - ESP32 Firmware (Wokwi Compatible)
 * Hardware-in-the-Loop Controller
 * 
 * Serial Protocol:
 * IN  (Python → ESP32): {"dF": 1.25, "dL": 0.85, "dR": 2.10}
 * OUT (ESP32 → Python): {"vL": 0.65, "vR": 0.70}
 */

// IMPORTANT: Make sure ArduinoJson library is installed in Wokwi!
// Library Manager -> Search "ArduinoJson" -> Add version 6.21.3+

#include <ArduinoJson.h>

// Serial configuration
#define SERIAL_BAUD 115200

// Control parameters
#define SAFE_DISTANCE 0.30      // meters
#define CRITICAL_DISTANCE 0.15  // meters
#define BASE_SPEED 0.60
#define TURN_SPEED 0.40
#define FAST_TURN_SPEED 0.70

// Sensor data
float distanceFront = 999.0;
float distanceLeft = 999.0;
float distanceRight = 999.0;

// Motor commands
float velocityLeft = 0.0;
float velocityRight = 0.0;

// JSON buffers
StaticJsonDocument<200> docIn;
StaticJsonDocument<200> docOut;

// Timing
unsigned long lastSend = 0;
unsigned long lastReceive = 0;

void setup() {
  // Initialize Serial
  Serial.begin(SERIAL_BAUD);
  delay(500);  // Wait for serial to stabilize
  
  // Send greeting
  Serial.println("# ESP32 HIL Controller Ready");
  Serial.println("# Firmware Version: 1.0");
  Serial.println("# Waiting for sensor data...");
  
  // Initialize
  velocityLeft = 0.0;
  velocityRight = 0.0;
  lastSend = millis();
  lastReceive = millis();
  
  Serial.println("# Setup complete!");
}

void loop() {
  // Read sensor data from Python
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    // Skip comments
    if (line.length() > 0 && !line.startsWith("#")) {
      parseSensorData(line);
    }
  }
  
  // Check connection timeout (200ms)
  if (millis() - lastReceive > 200) {
    // No data - stop motors for safety
    velocityLeft = 0.0;
    velocityRight = 0.0;
  } else {
    // Run obstacle avoidance
    obstacleAvoidance();
  }
  
  // Send motor commands every 20ms (50 Hz)
  if (millis() - lastSend >= 20) {
    sendMotorCommands();
    lastSend = millis();
  }
  
  delay(5);  // Small delay to prevent overwhelming
}

void parseSensorData(String json) {
  // Parse JSON
  DeserializationError error = deserializeJson(docIn, json);
  
  if (!error) {
    // Extract sensor values
    distanceFront = docIn["dF"] | 999.0;
    distanceLeft = docIn["dL"] | 999.0;
    distanceRight = docIn["dR"] | 999.0;
    lastReceive = millis();
  }
}

void obstacleAvoidance() {
  // Emergency stop if too close
  if (distanceFront < CRITICAL_DISTANCE) {
    velocityLeft = 0.0;
    velocityRight = 0.0;
    return;
  }
  
  // Obstacle ahead - turn away
  if (distanceFront < SAFE_DISTANCE) {
    if (distanceLeft > distanceRight) {
      // More space on left - turn left
      velocityLeft = -TURN_SPEED;
      velocityRight = FAST_TURN_SPEED;
    } else {
      // More space on right - turn right
      velocityLeft = FAST_TURN_SPEED;
      velocityRight = -TURN_SPEED;
    }
    return;
  }
  
  // Obstacle on left - veer right
  if (distanceLeft < SAFE_DISTANCE) {
    velocityLeft = BASE_SPEED;
    velocityRight = BASE_SPEED * 0.5;
    return;
  }
  
  // Obstacle on right - veer left
  if (distanceRight < SAFE_DISTANCE) {
    velocityLeft = BASE_SPEED * 0.5;
    velocityRight = BASE_SPEED;
    return;
  }
  
  // No obstacles - go straight
  velocityLeft = BASE_SPEED;
  velocityRight = BASE_SPEED;
}

void sendMotorCommands() {
  // Clamp velocities
  velocityLeft = constrain(velocityLeft, -1.0, 1.0);
  velocityRight = constrain(velocityRight, -1.0, 1.0);
  
  // Build JSON
  docOut.clear();
  docOut["vL"] = velocityLeft;
  docOut["vR"] = velocityRight;
  
  // Send
  serializeJson(docOut, Serial);
  Serial.println();
}
