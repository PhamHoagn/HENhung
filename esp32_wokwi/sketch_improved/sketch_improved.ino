/*
 * HIL Robocar - ESP32 Firmware IMPROVED v5.1
 * Hardware-in-the-Loop Controller
 * 
 * Improvements:
 * - WIDE CONE SENSOR PATTERN: 7 sensors (center, left/right near 15°, mid 35°, far 60°) 120° FOV
 * - Weighted danger calculation (near 3x, mid 2x, far 1x)
 * - SMOOTH CONTROL: Exponential velocity filtering and steering deadzone
 * - Proper waypoint navigation with bearing calculation
 * - Smart obstacle avoidance with graduated response
 * - Anti-stuck mechanism (detects when car is stuck)
 * - Smooth control with velocity limits
 * - Better blending between waypoint and obstacle avoidance
 * 
 * Serial Protocol:
 * IN  (Python → ESP32): {"dC": 1.25, "dLN": 0.85, "dRN": 0.90, "dLM": 1.00, "dRM": 0.95, "dLF": 1.10, "dRF": 1.05, "wx": 5.0, "wy": 3.0, "h": 1.57, "x": 2.0, "y": 2.0}
 * OUT (ESP32 → Python): {"vL": 0.65, "vR": 0.70}
 */

#include <ArduinoJson.h>

// Serial configuration
#define SERIAL_BAUD 115200

// Control parameters - Speeds (reduced for safer operation)
#define MAX_SPEED 0.40            // Maximum speed (reduced from 0.50 for safety)
#define BASE_SPEED 0.30           // Normal cruising speed (reduced from 0.35)
#define SLOW_SPEED 0.18           // Speed when navigating obstacles (reduced from 0.20)
#define TURN_SPEED 0.25           // Speed when turning (reduced from 0.30)
#define SHARP_TURN_SPEED 0.40     // Speed for sharp turns (reduced from 0.45)

// Control parameters - Distances (increased for earlier detection)
#define CRITICAL_DISTANCE 0.50    // meters - Turn hard while slowing (increased from 0.35, sync with Python)
#define DANGER_DISTANCE 0.75      // meters - strong avoidance (increased from 0.60)
#define WARNING_DISTANCE 1.00     // meters - moderate avoidance (increased from 0.90)
#define CAUTION_DISTANCE 2.00     // meters - light avoidance (increased from 1.50, wider early detection)

// Control parameters - Navigation
#define ANGLE_TOLERANCE 0.20      // radians (~11°) - considered "facing waypoint"
#define WAYPOINT_REACHED 0.30     // meters - waypoint reached threshold

// Blending weights
#define CRITICAL_AVOID_WEIGHT 0.95  // Almost pure avoidance
#define DANGER_AVOID_WEIGHT 0.80    // Strong avoidance bias
#define WARNING_AVOID_WEIGHT 0.60   // Moderate avoidance
#define CAUTION_AVOID_WEIGHT 0.35   // Light avoidance

// Anti-stuck mechanism
#define STUCK_THRESHOLD 5         // cycles before considering stuck
#define RECOVERY_DURATION 20      // cycles for recovery maneuver

// Sensor data (9 sensors: 7 forward cone 120° FOV + 2 side 90°)
float distanceCenter = 999.0;        // 0°
float distanceLeftNear = 999.0;      // 15° left
float distanceRightNear = 999.0;     // 15° right
float distanceLeftMid = 999.0;       // 35° left
float distanceRightMid = 999.0;      // 35° right
float distanceLeftFar = 999.0;       // 60° left
float distanceRightFar = 999.0;      // 60° right
float distanceLeftSide = 999.0;      // 90° left (side sensor)
float distanceRightSide = 999.0;     // 90° right (side sensor)

// Position and navigation
float carX = 0.0;
float carY = 0.0;
float carHeading = 0.0;      // radians
float waypointX = 0.0;
float waypointY = 0.0;
bool hasWaypoint = false;

// Motor commands with smoothing
float velocityLeft = 0.0;
float velocityRight = 0.0;
float lastVelLeft = 0.0;     // For exponential smoothing
float lastVelRight = 0.0;    // For exponential smoothing

// Control smoothing parameters
#define VELOCITY_ALPHA 0.40     // Increased for even faster response (was 0.30)
#define STEERING_DEADZONE 0.02  // Reduced for better responsiveness (was 0.03)

// Anti-stuck state
int stuckCounter = 0;
int recoveryCounter = 0;
float lastCarX = 0.0;
float lastCarY = 0.0;

// JSON buffers
StaticJsonDocument<300> docIn;
StaticJsonDocument<128> docOut;

// Timing
unsigned long lastSend = 0;
unsigned long lastReceive = 0;
unsigned long lastPositionCheck = 0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(500);
  
  Serial.println("# ESP32 HIL Controller - IMPROVED v5.1");
  Serial.println("# Features:");
  Serial.println("#  - Wide cone 7 sensors (120° FOV: 0°, ±15°, ±35°, ±60°)");
  Serial.println("#  - SMOOTH control with exponential filtering");
  Serial.println("#  - Smart waypoint navigation");
  Serial.println("#  - Graduated obstacle avoidance");
  Serial.println("#  - Anti-stuck mechanism");
  Serial.println("# Ready!");
  
  velocityLeft = 0.0;
  velocityRight = 0.0;
  lastSend = millis();
  lastReceive = millis();
  lastPositionCheck = millis();
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
    // Check if stuck
    checkIfStuck();
    
    // Run controller based on state
    if (recoveryCounter > 0) {
      // Recovery maneuver
      performRecovery();
    } else {
      // Normal operation
      smartController();
    }
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
    // Sensor distances (9 sensors: 7 forward cone 120° + 2 side 90°)
    distanceCenter = docIn["dC"] | 999.0;
    distanceLeftNear = docIn["dLN"] | 999.0;
    distanceRightNear = docIn["dRN"] | 999.0;
    distanceLeftMid = docIn["dLM"] | 999.0;
    distanceRightMid = docIn["dRM"] | 999.0;
    distanceLeftFar = docIn["dLF"] | 999.0;
    distanceRightFar = docIn["dRF"] | 999.0;
    distanceLeftSide = docIn["dLS"] | 999.0;   // 90° left
    distanceRightSide = docIn["dRS"] | 999.0;  // 90° right
    
    // Car position and heading
    carX = docIn["x"] | 0.0;
    carY = docIn["y"] | 0.0;
    carHeading = docIn["h"] | 0.0;
    
    // Waypoint data
    if (docIn.containsKey("wx") && docIn.containsKey("wy")) {
      waypointX = docIn["wx"];
      waypointY = docIn["wy"];
      hasWaypoint = true;
    } else {
      hasWaypoint = false;
    }
    
    lastReceive = millis();
  }
}

void smartController() {
  /*
   * Smart hybrid controller with graduated response
   * Uses 9-sensor pattern: 7 forward cone (120° FOV) + 2 side (90°) for obstacle detection
   * Side sensors help detect when car has cleared obstacle
   * CRITICAL: Obstacle avoidance OVERRIDES waypoint when danger detected!
   */
  
  // Calculate aggregated left/right from 7 FORWARD sensors
  float distanceFront = distanceCenter;
  float distanceLeft = min(min(distanceLeftNear, distanceLeftMid), distanceLeftFar);
  float distanceRight = min(min(distanceRightNear, distanceRightMid), distanceRightFar);
  
  // Determine obstacle severity level (only forward sensors)
  float minDistance = min(distanceFront, min(distanceLeft, distanceRight));
  
  // Check if obstacle has been cleared using side sensors
  // When both side sensors show clear (> 1.8m) AND forward is reasonably clear (> 1.2m),
  // car has likely passed the obstacle and can reduce avoidance
  bool obstacleCleared = (distanceLeftSide > 1.8 && distanceRightSide > 1.8 && minDistance > 1.2);
  
  // Priority 1: CRITICAL - COMPLETELY OVERRIDE waypoint navigation
  if (minDistance < CRITICAL_DISTANCE) {
    calculateSmartAvoidance(velocityLeft, velocityRight, minDistance);
    velocityLeft = constrain(velocityLeft, -MAX_SPEED, MAX_SPEED);
    velocityRight = constrain(velocityRight, -MAX_SPEED, MAX_SPEED);
    return;  // STOP HERE - don't blend with waypoint!
  }
  
  // Priority 2: DANGER - 95% obstacle avoidance, 5% waypoint
  if (minDistance < DANGER_DISTANCE) {
    float wpVelLeft, wpVelRight;
    if (hasWaypoint) {
      calculateWaypointVelocities(wpVelLeft, wpVelRight);
    } else {
      wpVelLeft = BASE_SPEED * 0.5;
      wpVelRight = BASE_SPEED * 0.5;
    }
    
    float avoidVelLeft, avoidVelRight;
    calculateSmartAvoidance(avoidVelLeft, avoidVelRight, minDistance);
    
    // 95% avoidance, 5% waypoint
    velocityLeft = wpVelLeft * 0.05 + avoidVelLeft * 0.95;
    velocityRight = wpVelRight * 0.05 + avoidVelRight * 0.95;
    
    velocityLeft = constrain(velocityLeft, -MAX_SPEED, MAX_SPEED);
    velocityRight = constrain(velocityRight, -MAX_SPEED, MAX_SPEED);
    return;  // STOP HERE
  }
  
  // Priority 3: WARNING/CAUTION - Blend based on distance
  // PRIORITY: Avoid collision over reaching waypoint!
  float avoidWeight = 0.0;
  if (minDistance < WARNING_DISTANCE) {
    // WARNING - 90% avoidance, 10% waypoint (increased from 85%)
    avoidWeight = 0.90;
  } else if (minDistance < 2.00) {  // Extended from 1.80m for even earlier detection
    // CAUTION - 60% avoidance, 40% waypoint (removed obstacle_cleared logic)
    avoidWeight = 0.60;
  } else {
    // Path clear - minimal avoidance, mostly waypoint
    avoidWeight = 0.10;
  }
  
  // Calculate waypoint navigation velocities
  float wpVelLeft, wpVelRight;
  if (hasWaypoint) {
    calculateWaypointVelocities(wpVelLeft, wpVelRight);
  } else {
    // No waypoint - just move forward slowly
    wpVelLeft = BASE_SPEED * 0.5;
    wpVelRight = BASE_SPEED * 0.5;
  }
  
  // Calculate obstacle avoidance velocities
  float avoidVelLeft, avoidVelRight;
  calculateSmartAvoidance(avoidVelLeft, avoidVelRight, minDistance);
  
  // Blend based on obstacle severity
  if (avoidWeight > 0.01) {
    velocityLeft = wpVelLeft * (1.0 - avoidWeight) + avoidVelLeft * avoidWeight;
    velocityRight = wpVelRight * (1.0 - avoidWeight) + avoidVelRight * avoidWeight;
  } else {
    velocityLeft = wpVelLeft;
    velocityRight = wpVelRight;
  }
  
  // Apply smooth limiting
  velocityLeft = constrain(velocityLeft, -MAX_SPEED, MAX_SPEED);
  velocityRight = constrain(velocityRight, -MAX_SPEED, MAX_SPEED);
}

void calculateWaypointVelocities(float &velLeft, float &velRight) {
  /*
   * Calculate velocities to navigate to waypoint
   */
  
  // Calculate vector to waypoint
  float dx = waypointX - carX;
  float dy = waypointY - carY;
  float distanceToWaypoint = sqrt(dx * dx + dy * dy);
  
  // Calculate desired heading
  float desiredHeading = atan2(dy, dx);
  
  // Calculate heading error (angle difference)
  float headingError = desiredHeading - carHeading;
  
  // Normalize angle to [-PI, PI]
  while (headingError > PI) headingError -= 2 * PI;
  while (headingError < -PI) headingError += 2 * PI;
  
  // Calculate base speed (slow down as approaching waypoint)
  float baseSpeed = BASE_SPEED;
  if (distanceToWaypoint < 1.0) {
    baseSpeed = BASE_SPEED * (0.4 + 0.6 * distanceToWaypoint);
  }
  
  // Reduce speed when turning
  float turnFactor = max(0.3, 1.0 - abs(headingError) / PI);
  baseSpeed *= turnFactor;
  
  // Calculate differential steering
  float turnRate = headingError / PI;  // Normalize to [-1, 1]
  turnRate = constrain(turnRate, -0.8, 0.8);
  
  // Apply to wheels
  velLeft = baseSpeed * (1.0 - turnRate);
  velRight = baseSpeed * (1.0 + turnRate);
}

void calculateSmartAvoidance(float &velLeft, float &velRight, float minDist) {
  /*
   * Smart obstacle avoidance with graduated response using 7-sensor wide cone (120° FOV)
   * Weighted danger calculation: near 3x, mid 2x, far 1x
   */
  
  // Calculate aggregated distances from 7 sensors
  float distanceFront = distanceCenter;
  float distanceLeft = min(min(distanceLeftNear, distanceLeftMid), distanceLeftFar);
  float distanceRight = min(min(distanceRightNear, distanceRightMid), distanceRightFar);
  
  // Critical danger - TURN HARD while slowing (don't just stop!)
  if (distanceFront < CRITICAL_DISTANCE) {
    float leftSpace = distanceLeft;
    float rightSpace = distanceRight;
    
    // Determine which direction has more space
    if (leftSpace > rightSpace + 0.05) {
      // Turn LEFT (spin turn: left wheel backward, right forward)
      velLeft = -SLOW_SPEED * 0.6;  // Reverse left for tighter turn
      velRight = SHARP_TURN_SPEED;  // Push right forward
    } else if (rightSpace > leftSpace + 0.05) {
      // Turn RIGHT
      velLeft = SHARP_TURN_SPEED;
      velRight = -SLOW_SPEED * 0.6;  // Reverse right for tighter turn
    } else {
      // Equal - prefer turning right
      velLeft = SHARP_TURN_SPEED;
      velRight = -SLOW_SPEED * 0.6;
    }
    return;
  }
  
  // Danger ahead - TURN HARD (increased speed)
  if (distanceFront < DANGER_DISTANCE) {
    float leftSpace = distanceLeft;
    float rightSpace = distanceRight;
    
    if (leftSpace > rightSpace + 0.05) {
      velLeft = SLOW_SPEED * 0.5;   // Increased from 0.3
      velRight = SHARP_TURN_SPEED * 0.9;  // Increased from TURN_SPEED * 0.8
    } else if (rightSpace > leftSpace + 0.05) {
      velLeft = SHARP_TURN_SPEED * 0.9;
      velRight = SLOW_SPEED * 0.5;
    } else {
      // Equal - prefer right, faster turn
      velLeft = SHARP_TURN_SPEED * 0.9;
      velRight = SLOW_SPEED * 0.5;
    }
    return;
  }
  
  // Warning/Caution - gradual steering with CONE-WEIGHTED REPULSION
  float steerBias = 0.0;
  
  // Front obstacle - steer toward clearer side
  if (distanceFront < WARNING_DISTANCE) {
    float frontBias = (WARNING_DISTANCE - distanceFront) / WARNING_DISTANCE;
    steerBias += frontBias * (distanceLeft > distanceRight ? -1.0 : 1.0);
  }
  
  // Wide cone weighted side obstacles with DISTANCE-BASED PRIORITY
  // RED zones (< 0.3m) get MUCH higher weight than YELLOW zones (0.6-1.0m)
  // Apply when detected, but strength decreases with distance
  float minSide = min(distanceLeft, distanceRight);
  if (minSide < 1.2) {  // Back to 1.2m but with smarter weighting
    // Helper: Get distance weight (RED > ORANGE > YELLOW > GREEN)
    auto getDistWeight = [](float d) -> float {
      if (d < 0.3) return 10.0;      // RED - highest priority
      else if (d < 0.6) return 5.0;  // ORANGE - high priority
      else if (d < 1.0) return 2.0;  // YELLOW - medium priority
      else return 0.5;               // GREEN - very low priority (far obstacles)
    };
    
    // Weighted danger: distance_weight * angle_weight / distance
    // Angle weights: near (15°) 3x, mid (35°) 2x, far (60°) 1x
    float leftDanger = 
      getDistWeight(distanceLeftNear) * 3.0 / (distanceLeftNear + 0.1) +
      getDistWeight(distanceLeftMid) * 2.0 / (distanceLeftMid + 0.1) +
      getDistWeight(distanceLeftFar) * 1.0 / (distanceLeftFar + 0.1);
    
    float rightDanger = 
      getDistWeight(distanceRightNear) * 3.0 / (distanceRightNear + 0.1) +
      getDistWeight(distanceRightMid) * 2.0 / (distanceRightMid + 0.1) +
      getDistWeight(distanceRightFar) * 1.0 / (distanceRightFar + 0.1);
    
    float dangerDiff = leftDanger - rightDanger;
    float repulsionStrength = (1.2 - minSide) / 1.2;  // Changed from 1.0
    float sidePush = dangerDiff * repulsionStrength * 0.28;  // Increased from 0.22
    steerBias += constrain(sidePush, -0.65, 0.65);  // Increased from 0.55
  }
  
  // Apply steering deadzone to reduce jittering
  if (abs(steerBias) < STEERING_DEADZONE) {
    steerBias *= 0.3;  // Dampen very small corrections
  }
  
  steerBias = constrain(steerBias, -1.0, 1.0);
  float speed = SLOW_SPEED + (BASE_SPEED - SLOW_SPEED) * (minDist / CAUTION_DISTANCE);
  speed = constrain(speed, SLOW_SPEED, BASE_SPEED);
  
  // Adaptive steering multiplier: WIDER turns for RED zones (< 0.3m)
  float steeringMultiplier;
  if (minDist < 0.3) {
    steeringMultiplier = 0.85;  // Extra WIDE for RED zones
  } else if (minDist < 0.6) {
    steeringMultiplier = 0.80;  // Wide for ORANGE zones
  } else if (minDist < 1.0) {
    steeringMultiplier = 0.68;  // Moderate for YELLOW zones
  } else if (minDist < 1.3) {
    steeringMultiplier = 0.60;  // Gentle for somewhat clear
  } else {
    steeringMultiplier = 0.55;  // Gentle when path clear
  }
  
  velLeft = speed * (1.0 + steerBias * steeringMultiplier);
  velRight = speed * (1.0 - steerBias * steeringMultiplier);
}

void checkIfStuck() {
  /*
   * Detect if car is stuck (not moving despite motor commands)
   */
  
  // Check position every 500ms
  if (millis() - lastPositionCheck > 500) {
    float dx = carX - lastCarX;
    float dy = carY - lastCarY;
    float movement = sqrt(dx * dx + dy * dy);
    
    // If barely moved and motors were active
    if (movement < 0.05 && (abs(velocityLeft) > 0.1 || abs(velocityRight) > 0.1)) {
      stuckCounter++;
      if (stuckCounter >= STUCK_THRESHOLD) {
        // Initiate recovery
        recoveryCounter = RECOVERY_DURATION;
        stuckCounter = 0;
        Serial.println("# STUCK! Starting recovery...");
      }
    } else {
      stuckCounter = max(0, stuckCounter - 1);
    }
    
    lastCarX = carX;
    lastCarY = carY;
    lastPositionCheck = millis();
  }
}

void performRecovery() {
  /*
   * Recovery maneuver when stuck
   */
  
  recoveryCounter--;
  
  // Calculate aggregated distances for recovery decision
  float distanceLeft = min(distanceLeftNear, distanceLeftFar);
  float distanceRight = min(distanceRightNear, distanceRightFar);
  
  if (recoveryCounter > RECOVERY_DURATION / 2) {
    // First half - back up
    velocityLeft = -SLOW_SPEED;
    velocityRight = -SLOW_SPEED;
  } else {
    // Second half - turn to clearer side
    if (distanceLeft > distanceRight) {
      velocityLeft = -TURN_SPEED;
      velocityRight = SHARP_TURN_SPEED;
    } else {
      velocityLeft = SHARP_TURN_SPEED;
      velocityRight = -TURN_SPEED;
    }
  }
  
  if (recoveryCounter <= 0) {
    Serial.println("# Recovery complete!");
  }
}

void sendMotorCommands() {
  // Apply exponential smoothing to reduce jittering
  lastVelLeft = (1.0 - VELOCITY_ALPHA) * lastVelLeft + VELOCITY_ALPHA * velocityLeft;
  lastVelRight = (1.0 - VELOCITY_ALPHA) * lastVelRight + VELOCITY_ALPHA * velocityRight;
  
  // Clamp smoothed velocities
  lastVelLeft = constrain(lastVelLeft, -1.0, 1.0);
  lastVelRight = constrain(lastVelRight, -1.0, 1.0);
  
  // Build JSON
  docOut.clear();
  docOut["vL"] = lastVelLeft;
  docOut["vR"] = lastVelRight;
  
  // Send
  serializeJson(docOut, Serial);
  Serial.println();
}
