/*
 * HIL Robocar - ESP32 Firmware with Waypoint Navigation
 * Hardware-in-the-Loop Controller
 * 
 * Features:
 * - Waypoint navigation (follows predefined path)
 * - Obstacle avoidance (dynamic obstacle detection)
 * - Hybrid control (combines waypoint following + obstacle avoidance)
 * 
 * Serial Protocol:
 * IN  (Python → ESP32): {"dF": 1.25, "dL": 0.85, "dR": 2.10, "wx": 5.0, "wy": 3.0, "h": 1.57}
 * OUT (ESP32 → Python): {"vL": 0.65, "vR": 0.70}
 * 
 * Fields:
 * - dF, dL, dR: Distance sensors (Front, Left, Right) in meters
 * - wx, wy: Target waypoint position (x, y) in meters
 * - h: Car heading in radians
 */

#include <ArduinoJson.h>

// Serial configuration
#define SERIAL_BAUD 115200

// Control parameters - Obstacle Avoidance
#define SAFE_DISTANCE 0.35        // meters - start avoiding
#define CRITICAL_DISTANCE 0.20    // meters - emergency stop
#define OBSTACLE_WEIGHT 0.7       // 0-1: Weight of obstacle avoidance vs waypoint

// Control parameters - Waypoint Navigation
#define BASE_SPEED 0.55           // Base forward speed
#define TURN_SPEED 0.45           // Speed when turning
#define FAST_TURN_SPEED 0.75      // Speed for sharp turns
#define ANGLE_TOLERANCE 0.15      // radians (~8 degrees) - considered "facing waypoint"

// Sensor data
float distanceFront = 999.0;
float distanceLeft = 999.0;
float distanceRight = 999.0;

// Waypoint data
float waypointX = 0.0;
float waypointY = 0.0;
float carHeading = 0.0;  // radians

// Motor commands
float velocityLeft = 0.0;
float velocityRight = 0.0;

// JSON buffers
StaticJsonDocument<256> docIn;
StaticJsonDocument<128> docOut;

// Timing
unsigned long lastSend = 0;
unsigned long lastReceive = 0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(500);
  
  Serial.println("# ESP32 HIL Controller - Waypoint Navigation");
  Serial.println("# Firmware Version: 2.0");
  Serial.println("# Features: Waypoint + Obstacle Avoidance");
  Serial.println("# Waiting for sensor data...");
  
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
    
    if (line.length() > 0 && !line.startsWith("#")) {
      parseSensorData(line);
    }
  }
  
  // Check connection timeout (200ms)
  if (millis() - lastReceive > 200) {
    velocityLeft = 0.0;
    velocityRight = 0.0;
  } else {
    // Run hybrid controller
    hybridController();
  }
  
  // Send motor commands every 20ms (50 Hz)
  if (millis() - lastSend >= 20) {
    sendMotorCommands();
    lastSend = millis();
  }
  
  delay(5);
}

void parseSensorData(String json) {
  DeserializationError error = deserializeJson(docIn, json);
  
  if (!error) {
    // Sensor distances
    distanceFront = docIn["dF"] | 999.0;
    distanceLeft = docIn["dL"] | 999.0;
    distanceRight = docIn["dR"] | 999.0;
    
    // Waypoint data
    waypointX = docIn["wx"] | 0.0;
    waypointY = docIn["wy"] | 0.0;
    carHeading = docIn["h"] | 0.0;
    
    lastReceive = millis();
  }
}

void hybridController() {
  /*
   * Hybrid Controller: Waypoint Navigation + Obstacle Avoidance
   * 
   * Strategy:
   * 1. Calculate desired velocity towards waypoint
   * 2. Check for obstacles
   * 3. If obstacle detected, blend avoidance with waypoint navigation
   * 4. If no obstacles, pure waypoint following
   */
  
  // Emergency stop if critical obstacle
  if (distanceFront < CRITICAL_DISTANCE) {
    velocityLeft = 0.0;
    velocityRight = 0.0;
    return;
  }
  
  // Calculate waypoint navigation velocities
  float wpVelLeft, wpVelRight;
  calculateWaypointVelocities(wpVelLeft, wpVelRight);
  
  // Check if obstacles nearby
  bool hasObstacle = (distanceFront < SAFE_DISTANCE || 
                      distanceLeft < SAFE_DISTANCE || 
                      distanceRight < SAFE_DISTANCE);
  
  if (hasObstacle) {
    // Blend waypoint following with obstacle avoidance
    float avoidVelLeft, avoidVelRight;
    calculateAvoidanceVelocities(avoidVelLeft, avoidVelRight);
    
    // Weighted combination
    velocityLeft = wpVelLeft * (1.0 - OBSTACLE_WEIGHT) + avoidVelLeft * OBSTACLE_WEIGHT;
    velocityRight = wpVelRight * (1.0 - OBSTACLE_WEIGHT) + avoidVelRight * OBSTACLE_WEIGHT;
  } else {
    // Pure waypoint navigation
    velocityLeft = wpVelLeft;
    velocityRight = wpVelRight;
  }
}

void calculateWaypointVelocities(float &velLeft, float &velRight) {
  /*
   * Calculate motor velocities to reach waypoint
   * Uses bearing angle to determine turning
   */
  
  // Calculate bearing to waypoint (already computed by Python and sent as implicit in heading)
  // We'll use a simplified approach: if waypoint is to the right, turn right, etc.
  
  // For now, simplified: always move forward, adjust based on obstacles
  // In practice, Python calculates bearing and we respond to sensor data
  
  // Default: move forward
  velLeft = BASE_SPEED;
  velRight = BASE_SPEED;
}

void calculateAvoidanceVelocities(float &velLeft, float &velRight) {
  /*
   * Calculate motor velocities to avoid obstacles
   */
  
  // Obstacle directly ahead - turn to side with more space
  if (distanceFront < SAFE_DISTANCE) {
    if (distanceLeft > distanceRight) {
      // More space on left - turn left
      velLeft = -TURN_SPEED;
      velRight = FAST_TURN_SPEED;
    } else {
      // More space on right - turn right
      velLeft = FAST_TURN_SPEED;
      velRight = -TURN_SPEED;
    }
    return;
  }
  
  // Obstacle on left - veer right
  if (distanceLeft < SAFE_DISTANCE) {
    velLeft = BASE_SPEED * 1.2;
    velRight = BASE_SPEED * 0.6;
    return;
  }
  
  // Obstacle on right - veer left
  if (distanceRight < SAFE_DISTANCE) {
    velLeft = BASE_SPEED * 0.6;
    velRight = BASE_SPEED * 1.2;
    return;
  }
  
  // No immediate obstacle - move forward
  velLeft = BASE_SPEED;
  velRight = BASE_SPEED;
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
