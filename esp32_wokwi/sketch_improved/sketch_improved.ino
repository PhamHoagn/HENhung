/*
 * HIL Robocar – ESP32 Embedded AI Firmware v7.0
 * ==============================================
 *
 * Vehicle : 4WD Skid-Steer Differential Drive (4 wheels, 2 independent sides)
 * AI Model: Trained Decision Tree (auto-generated, see decision_tree_model.h)
 *
 * Architecture (strict HIL):
 *   ESP32 = THE ONLY autonomous brain (perception → decision → actuation)
 *   Python = Plant simulator only (physics + sensors + rendering)
 *
 * Tasks:
 *   Core 1 – controlTask  @ 50 Hz  (perception + rule overlay + motor output)
 *   Core 0 – aiTask       @  5 Hz  (Decision Tree inference)
 *
 * Decision Tree classes:
 *   0 GO_STRAIGHT  – no obstacle
 *   1 VEER_LEFT    – moderate left
 *   2 VEER_RIGHT   – moderate right
 *   3 HARD_LEFT    – sharp left / spin
 *   4 HARD_RIGHT   – sharp right / spin
 *
 * Safety-first: STOP/REVERSE overrides the DT if front < kDStop.
 * Standalone-safe: if no simulator packet for 250 ms → safe stop.
 */

#include <Arduino.h>
#include <ArduinoJson.h>
#include "decision_tree_model.h"          // trained DT (pure C if/else)

// ── Configuration ───────────────────────────────────────────────
#define SERIAL_BAUD     115200
#define SENSOR_COUNT    9
#define CONTROL_PERIOD_MS  20             // 50 Hz
#define AI_PERIOD_MS      200             //  5 Hz
#define DEBUG_AI          1

// 4WD Skid-Steer vehicle parameters (must match Python sim)
static constexpr float kMaxWheel   = 0.85f;   // max normalised wheel cmd
static constexpr float kBaseSpeed  = 0.65f;   // cruise speed (m/s)
static constexpr float kTrackWidth = 0.22f;   // left↔right wheel distance

// Safety distances  (conservative – react early, stay safe)
static constexpr float kDStop     = 0.40f;   // full stop / reverse
static constexpr float kDCritical = 0.55f;   // 100 % DT override
static constexpr float kDDanger   = 0.90f;   // switch to MODE_AVOID
static constexpr float kDWarn     = 1.30f;   // blend starts
static constexpr float kDClear    = 1.50f;   // hysteresis – exit AVOID
static constexpr float kDMax      = 5.50f;

static constexpr uint32_t kInputTimeoutMs = 250;

// ── Behavior state machine ──────────────────────────────────────
enum BehaviorMode : uint8_t {
  MODE_FOLLOW    = 0,   // DT + waypoint blending
  MODE_AVOID     = 1,   // DT override with high avoid weight
  MODE_STOP      = 2,   // Emergency / timeout
  MODE_RECOVERY  = 3    // Reverse + spin
};

// ════════════════════════════════════════════════════════════════
//  COMM  – Serial JSON protocol  (Python ↔ ESP32)
// ════════════════════════════════════════════════════════════════
namespace comm {

struct InputFrame {
  uint32_t tMs;
  float x, y, th;
  float wpX, wpY;
  bool  hasWp;
  float d[SENSOR_COUNT];
  bool  valid;
};

static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static InputFrame latest{};
static uint32_t lastRxMs = 0;

static char  rxBuf[512];
static size_t rxLen = 0;
StaticJsonDocument<512> inDoc;
StaticJsonDocument<256> outDoc;

bool parsePacket(const char* line, InputFrame& out) {
  DeserializationError err = deserializeJson(inDoc, line);
  if (err) return false;

  out.tMs  = inDoc["t"]   | millis();
  out.x    = inDoc["x"]   | 0.0f;
  out.y    = inDoc["y"]   | 0.0f;
  out.th   = inDoc["th"]  | (inDoc["h"] | 0.0f);
  out.wpX  = inDoc["wpX"] | (inDoc["wx"] | 0.0f);
  out.wpY  = inDoc["wpY"] | (inDoc["wy"] | 0.0f);
  out.hasWp = inDoc.containsKey("wpX") || inDoc.containsKey("wx");

  if (inDoc.containsKey("d") && inDoc["d"].is<JsonArray>()) {
    JsonArray arr = inDoc["d"].as<JsonArray>();
    for (size_t i = 0; i < SENSOR_COUNT; i++)
      out.d[i] = (i < arr.size()) ? (float)arr[i] : kDMax;
  } else {
    out.d[0] = inDoc["dLS"] | kDMax;
    out.d[1] = inDoc["dLF"] | kDMax;
    out.d[2] = inDoc["dLM"] | kDMax;
    out.d[3] = inDoc["dLN"] | kDMax;
    out.d[4] = inDoc["dC"]  | kDMax;
    out.d[5] = inDoc["dRN"] | kDMax;
    out.d[6] = inDoc["dRM"] | kDMax;
    out.d[7] = inDoc["dRF"] | kDMax;
    out.d[8] = inDoc["dRS"] | kDMax;
  }
  out.valid = true;
  return true;
}

void pollSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (rxLen == 0) continue;
      rxBuf[rxLen] = '\0';
      if (rxBuf[0] != '#') {
        InputFrame parsed{};
        if (parsePacket(rxBuf, parsed)) {
          portENTER_CRITICAL(&mux);
          latest   = parsed;
          lastRxMs = millis();
          portEXIT_CRITICAL(&mux);
        }
      }
      rxLen = 0;
    } else if (rxLen < sizeof(rxBuf) - 1) {
      rxBuf[rxLen++] = c;
    } else {
      rxLen = 0;
    }
  }
}

bool snapshot(InputFrame& out, uint32_t& ageMs) {
  portENTER_CRITICAL(&mux);
  out = latest;
  uint32_t rx = lastRxMs;
  portEXIT_CRITICAL(&mux);
  ageMs = millis() - rx;
  return out.valid;
}

void sendOutput(float vL, float vR, BehaviorMode mode,
                int aiAction, float aiSpeed, float aiMs) {
  outDoc.clear();
  outDoc["t"]     = millis();
  outDoc["vL"]    = vL;
  outDoc["vR"]    = vR;
  outDoc["mode"]  = (mode == MODE_FOLLOW)   ? "FOLLOW"
                  : (mode == MODE_AVOID)    ? "AVOID"
                  : (mode == MODE_RECOVERY) ? "RECOVERY"
                  :                           "STOP";
  outDoc["ai_a"]  = aiAction;      // DT predicted action class
  outDoc["ai_s"]  = aiSpeed;       // DT predicted speed scale
  outDoc["ai_ms"] = aiMs;          // inference time
  serializeJson(outDoc, Serial);
  Serial.println();
}
} // namespace comm

// ════════════════════════════════════════════════════════════════
//  PERCEPTION  – sensor validation & grouping
// ════════════════════════════════════════════════════════════════
namespace perception {

struct PerceptionOut {
  float d[SENSOR_COUNT];
  float front;
  float leftMin;
  float rightMin;
  float minAll;
  bool  sensorValid;
};

PerceptionOut run(const comm::InputFrame& in) {
  PerceptionOut p{};
  uint8_t bad = 0;
  for (int i = 0; i < SENSOR_COUNT; i++) {
    float v = in.d[i];
    if (!isfinite(v) || v < 0.0f || v > kDMax * 1.5f) { v = kDMax; bad++; }
    p.d[i] = constrain(v, 0.0f, kDMax);
  }
  p.front    = p.d[4];                               // center sensor
  p.leftMin  = min(min(p.d[0], p.d[1]), min(p.d[2], p.d[3]));
  p.rightMin = min(min(p.d[5], p.d[6]), min(p.d[7], p.d[8]));
  p.minAll   = min(p.front, min(p.leftMin, p.rightMin));
  p.sensorValid = (bad <= 2);
  return p;
}
} // namespace perception

// ════════════════════════════════════════════════════════════════
//  WAYPOINT  – heading-error based navigation
// ════════════════════════════════════════════════════════════════
namespace waypoint {

void compute(const comm::InputFrame& in, float& v, float& w) {
  if (!in.hasWp) { v = 0.15f; w = 0.0f; return; }
  float dx   = in.wpX - in.x;
  float dy   = in.wpY - in.y;
  float dist = sqrtf(dx * dx + dy * dy);
  float desired = atan2f(dy, dx);
  float err  = desired - in.th;
  while (err >  PI) err -= 2.0f * PI;
  while (err < -PI) err += 2.0f * PI;

  v = constrain(kBaseSpeed * (0.50f + 0.50f * min(dist, 2.5f)), 0.20f, kBaseSpeed);
  w = constrain(2.0f * err, -2.5f, 2.5f);   // strong waypoint tracking
}
} // namespace waypoint

// ════════════════════════════════════════════════════════════════
//  AI  – Decision-Tree inference (runs on Core 0 @ 5 Hz)
// ════════════════════════════════════════════════════════════════
namespace ai {

/*
 * The Decision Tree model is defined in decision_tree_model.h.
 * It was trained offline on 20 000 synthetic samples generated
 * by an expert rule-based policy covering all obstacle scenarios.
 *
 * dt_predict_action(f[9]) → int   (action class 0–4)
 * dt_predict_speed(f[9])  → float (speed scale  0–1)
 *
 * The model is pure C if/else – no dynamic memory, no floats > 32-bit.
 * Inference takes < 0.05 ms on ESP32 @ 240 MHz.
 */

struct Output {
  int   action;       // 0..4 (GO_STRAIGHT … HARD_RIGHT)
  float speedScale;   // 0..1
  float inferMs;
};

// Shared state (written by aiTask, read by controlTask)
static volatile int   gAction     = DT_GO_STRAIGHT;
static volatile float gSpeedScale = 1.0f;
static volatile float gInferMs    = 0.0f;

Output run(const float d[SENSOR_COUNT]) {
  uint32_t t0 = micros();

  // Run trained decision tree inference
  int   action = dt_predict_action(d);
  float speed  = dt_predict_speed(d);

  Output o{};
  o.action     = constrain(action, 0, 4);
  o.speedScale = constrain(speed, 0.0f, 1.0f);
  o.inferMs    = (micros() - t0) / 1000.0f;
  return o;
}

void updateShared(const Output& o) {
  gAction     = o.action;
  gSpeedScale = 0.70f * gSpeedScale + 0.30f * o.speedScale;   // smooth
  gInferMs    = o.inferMs;

#if DEBUG_AI
  static const char* names[] = {"GO","V_L","V_R","H_L","H_R"};
  Serial.print("# AI dt_ms=");
  Serial.print(gInferMs, 3);
  Serial.print(" act=");
  Serial.print(names[o.action]);
  Serial.print(" spd=");
  Serial.println(gSpeedScale, 3);
#endif
}

void readShared(int& act, float& spd, float& ms) {
  act = gAction;
  spd = gSpeedScale;
  ms  = gInferMs;
}
} // namespace ai

// ════════════════════════════════════════════════════════════════
//  BEHAVIOR  – state-machine selector
// ════════════════════════════════════════════════════════════════
namespace behavior {

// Persistent state for hysteresis (avoids AVOID↔FOLLOW oscillation)
static BehaviorMode lastMode = MODE_FOLLOW;

BehaviorMode decide(const perception::PerceptionOut& p, bool timeout) {
  if (timeout)          { lastMode = MODE_STOP;     return MODE_STOP;     }
  if (p.front < kDStop) { lastMode = MODE_RECOVERY;  return MODE_RECOVERY; }

  // Hysteresis: once in AVOID/RECOVERY, stay until obstacle far enough
  if (lastMode == MODE_AVOID || lastMode == MODE_RECOVERY) {
    if (p.minAll < kDClear) {
      lastMode = MODE_AVOID;
      return MODE_AVOID;
    }
    // Obstacle is now far enough – resume following
    lastMode = MODE_FOLLOW;
    return MODE_FOLLOW;
  }

  // Normal entry into AVOID
  if (p.minAll < kDDanger) { lastMode = MODE_AVOID; return MODE_AVOID; }

  lastMode = MODE_FOLLOW;
  return MODE_FOLLOW;
}
} // namespace behavior

// ════════════════════════════════════════════════════════════════
//  CONTROL  – blend waypoint + DT AI → 4WD wheel commands
// ════════════════════════════════════════════════════════════════
namespace control {

/* Convert (v_linear, omega) to normalised (vL, vR) for skid-steer */
void vwToWheels(float v, float w, float& vL, float& vR) {
  vL = v - 0.5f * kTrackWidth * w;
  vR = v + 0.5f * kTrackWidth * w;
  vL = constrain(vL, -kMaxWheel, kMaxWheel);
  vR = constrain(vR, -kMaxWheel, kMaxWheel);
}

/*
 * Map DT action class → (v_linear, omega) delta commands
 *
 * The DT already encodes the expert policy; here we simply
 * convert its discrete action to continuous (v, ω) values
 * and blend with the waypoint heading controller.
 */
void dtActionToVW(int action, float dtSpeed,
                  const perception::PerceptionOut& p,
                  float& v, float& w) {
  switch (action) {
    case DT_GO_STRAIGHT:
      v = kBaseSpeed * dtSpeed;
      w = 0.0f;
      break;
    case DT_VEER_LEFT:
      v = kBaseSpeed * dtSpeed * 0.85f;   // fast veer
      w = 0.60f;
      break;
    case DT_VEER_RIGHT:
      v = kBaseSpeed * dtSpeed * 0.85f;
      w = -0.60f;
      break;
    case DT_HARD_LEFT:
      v = 0.18f;                           // keep moving during hard turn
      w = 1.20f;
      break;
    case DT_HARD_RIGHT:
      v = 0.18f;
      w = -1.20f;
      break;
    default:
      v = 0.0f; w = 0.0f;
  }
}

void computeCommand(
    const comm::InputFrame& in,
    const perception::PerceptionOut& p,
    BehaviorMode mode,
    float& outVL, float& outVR)
{
  // 1. Waypoint heading controller
  float vWP = 0.0f, wWP = 0.0f;
  waypoint::compute(in, vWP, wWP);

  // 2. DT-based obstacle avoidance
  int   aiAct;
  float aiSpd, aiMs;
  ai::readShared(aiAct, aiSpd, aiMs);

  float vDT = 0.0f, wDT = 0.0f;
  dtActionToVW(aiAct, aiSpd, p, vDT, wDT);

  // 3. Compute blend weight depending on danger level
  //    avoidW=0 when path is clear → pure waypoint tracking
  float avoidW = 0.0f;
  if      (p.minAll < kDCritical) avoidW = 1.00f;
  else if (p.minAll < kDDanger)   avoidW = 0.85f;
  else if (p.minAll < kDWarn)     avoidW = 0.45f;
  // else avoidW stays 0 → pure waypoint

  // Proximity-based speed scale (slow down near obstacles)
  float proxScale = 1.0f;
  if (p.minAll < kDWarn) {
    proxScale = constrain((p.minAll - kDStop) / (kDWarn - kDStop), 0.55f, 1.0f);
  }

  float v = 0.0f, w = 0.0f;

  if (mode == MODE_RECOVERY) {
    // Reverse + strong spin away from closest obstacle
    v = -0.22f;
    w = (p.leftMin > p.rightMin) ? 2.0f : -2.0f;
  } else if (mode == MODE_STOP) {
    v = 0.0f;
    w = 0.0f;
  } else if (mode == MODE_AVOID) {
    // DT avoidance + small waypoint influence to keep general direction
    v = max(0.14f, vDT * proxScale);
    w = 0.80f * wDT + 0.20f * wWP;
  } else {
    // MODE_FOLLOW: blend waypoint + DT, scale speed by proximity
    v = ((1.0f - avoidW) * vWP + avoidW * vDT) * proxScale;
    w = (1.0f - avoidW) * wWP + avoidW * wDT;
  }

  vwToWheels(v, w, outVL, outVR);
}
} // namespace control

// ════════════════════════════════════════════════════════════════
//  FreeRTOS Tasks
// ════════════════════════════════════════════════════════════════

void controlTask(void* arg) {
  (void)arg;
  TickType_t last = xTaskGetTickCount();
  float filtL = 0.0f, filtR = 0.0f;

  for (;;) {
    comm::pollSerial();

    comm::InputFrame frame{};
    uint32_t ageMs = 0;
    bool ok = comm::snapshot(frame, ageMs);
    auto p  = perception::run(frame);
    bool timeout = (!ok) || (ageMs > kInputTimeoutMs) || !p.sensorValid;

    BehaviorMode mode = behavior::decide(p, timeout);

    float vL = 0.0f, vR = 0.0f;
    control::computeCommand(frame, p, mode, vL, vR);

    // Exponential smoothing – fast enough to react to obstacles
    filtL = 0.35f * filtL + 0.65f * vL;
    filtR = 0.35f * filtR + 0.65f * vR;

    int   aiAct;
    float aiSpd, aiMs;
    ai::readShared(aiAct, aiSpd, aiMs);
    comm::sendOutput(filtL, filtR, mode, aiAct, aiSpd, aiMs);

    vTaskDelayUntil(&last, pdMS_TO_TICKS(CONTROL_PERIOD_MS));
  }
}

void aiTask(void* arg) {
  (void)arg;
  TickType_t last = xTaskGetTickCount();
  for (;;) {
    comm::InputFrame frame{};
    uint32_t ageMs = 0;
    if (comm::snapshot(frame, ageMs) && ageMs <= kInputTimeoutMs) {
      auto p = perception::run(frame);
      if (p.sensorValid) {
        ai::Output out = ai::run(p.d);
        ai::updateShared(out);
      }
    }
    vTaskDelayUntil(&last, pdMS_TO_TICKS(AI_PERIOD_MS));
  }
}

// ════════════════════════════════════════════════════════════════
//  Setup & Loop
// ════════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(200);
  Serial.println("# ESP32 Robocar v7.0 – 4WD Skid-Steer + Decision-Tree AI");
  Serial.println("# control=50Hz  ai_dt=5Hz  standalone-safe");

  xTaskCreatePinnedToCore(controlTask, "ctrl", 6144, nullptr, 2, nullptr, 1);
  xTaskCreatePinnedToCore(aiTask,      "ai",   4096, nullptr, 1, nullptr, 0);
}

void loop() {
  vTaskDelay(pdMS_TO_TICKS(1000));
}
