/*
 * HIL Robocar - ESP32 Embedded AI Firmware v6.0
 * - 50Hz control task (hard real-time target)
 * - 5Hz TinyML-like INT8 inference task (placeholder model)
 * - Safety-first behavior: STOP/REVERSE overrides AI
 * - Standalone-ready: if no simulator packet, controller safe-stops
 */

#include <Arduino.h>
#include <ArduinoJson.h>

#define SERIAL_BAUD 115200
#define SENSOR_COUNT 9
#define CONTROL_PERIOD_MS 20
#define AI_PERIOD_MS 200
#define DEBUG_AI 1

// Vehicle limits
static constexpr float kMaxWheel = 0.45f;
static constexpr float kBaseSpeed = 0.28f;
static constexpr float kTrackWidth = 0.22f;

// Safety distances (meters)
static constexpr float kDStop = 0.30f;
static constexpr float kDCritical = 0.45f;
static constexpr float kDDanger = 0.75f;
static constexpr float kDWarn = 1.20f;
static constexpr float kDMax = 5.50f;

// Timeouts
static constexpr uint32_t kInputTimeoutMs = 250;

enum BehaviorMode : uint8_t { MODE_FOLLOW = 0, MODE_AVOID = 1, MODE_STOP = 2, MODE_RECOVERY = 3 };

namespace comm {
struct InputFrame {
  uint32_t tMs;
  float x;
  float y;
  float th;
  float wpX;
  float wpY;
  bool hasWp;
  float d[SENSOR_COUNT];
  bool valid;
};

static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static InputFrame latest{};
static uint32_t lastRxMs = 0;

static char rxBuf[512];
static size_t rxLen = 0;
StaticJsonDocument<512> inDoc;
StaticJsonDocument<256> outDoc;

bool parsePacket(const char* line, InputFrame& out) {
  DeserializationError err = deserializeJson(inDoc, line);
  if (err) return false;

  out.tMs = inDoc["t"] | millis();
  out.x = inDoc["x"] | 0.0f;
  out.y = inDoc["y"] | 0.0f;
  out.th = inDoc["th"] | (inDoc["h"] | 0.0f);
  out.wpX = inDoc["wpX"] | (inDoc["wx"] | 0.0f);
  out.wpY = inDoc["wpY"] | (inDoc["wy"] | 0.0f);
  out.hasWp = inDoc.containsKey("wpX") || inDoc.containsKey("wx");

  bool hasArray = inDoc.containsKey("d") && inDoc["d"].is<JsonArray>();
  if (hasArray) {
    JsonArray arr = inDoc["d"].as<JsonArray>();
    for (size_t i = 0; i < SENSOR_COUNT; i++) {
      out.d[i] = (i < arr.size()) ? (float)arr[i] : kDMax;
    }
  } else {
    // Backward compatibility with old simulator keys
    out.d[0] = inDoc["dLS"] | kDMax;  // left side
    out.d[1] = inDoc["dLF"] | kDMax;
    out.d[2] = inDoc["dLM"] | kDMax;
    out.d[3] = inDoc["dLN"] | kDMax;
    out.d[4] = inDoc["dC"] | kDMax;
    out.d[5] = inDoc["dRN"] | kDMax;
    out.d[6] = inDoc["dRM"] | kDMax;
    out.d[7] = inDoc["dRF"] | kDMax;
    out.d[8] = inDoc["dRS"] | kDMax;  // right side
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
          latest = parsed;
          lastRxMs = millis();
          portEXIT_CRITICAL(&mux);
        }
      }
      rxLen = 0;
    } else if (rxLen < sizeof(rxBuf) - 1) {
      rxBuf[rxLen++] = c;
    } else {
      rxLen = 0; // drop oversized packet
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

void sendOutput(float vL, float vR, BehaviorMode mode, float aiB, float aiS, float aiMs) {
  outDoc.clear();
  outDoc["t"] = millis();
  outDoc["vL"] = vL;
  outDoc["vR"] = vR;
  outDoc["mode"] = (mode == MODE_FOLLOW) ? "FOLLOW" : (mode == MODE_AVOID) ? "AVOID" : (mode == MODE_RECOVERY) ? "RECOVERY" : "STOP";
  outDoc["ai_b"] = aiB;
  outDoc["ai_s"] = aiS;
  outDoc["ai_ms"] = aiMs;
  serializeJson(outDoc, Serial);
  Serial.println();
}
} // namespace comm

namespace perception {
struct PerceptionOut {
  float d[SENSOR_COUNT];
  float front;
  float leftMin;
  float rightMin;
  float minAll;
  bool sensorValid;
};

PerceptionOut run(const comm::InputFrame& in) {
  PerceptionOut p{};
  uint8_t invalid = 0;
  for (int i = 0; i < SENSOR_COUNT; i++) {
    float v = in.d[i];
    if (!isfinite(v) || v < 0.0f || v > kDMax * 1.5f) {
      v = kDMax;
      invalid++;
    }
    p.d[i] = constrain(v, 0.0f, kDMax);
  }
  p.front = p.d[4];
  p.leftMin = min(min(p.d[0], p.d[1]), min(p.d[2], p.d[3]));
  p.rightMin = min(min(p.d[5], p.d[6]), min(p.d[7], p.d[8]));
  p.minAll = min(p.front, min(p.leftMin, p.rightMin));
  p.sensorValid = (invalid <= 2);
  return p;
}
} // namespace perception

namespace waypoint {
void compute(const comm::InputFrame& in, float& v, float& w) {
  if (!in.hasWp) {
    v = 0.15f;
    w = 0.0f;
    return;
  }
  float dx = in.wpX - in.x;
  float dy = in.wpY - in.y;
  float dist = sqrtf(dx * dx + dy * dy);
  float desired = atan2f(dy, dx);
  float err = desired - in.th;
  while (err > PI) err -= 2.0f * PI;
  while (err < -PI) err += 2.0f * PI;

  v = constrain(kBaseSpeed * (0.35f + 0.65f * min(dist, 1.0f)), 0.08f, kBaseSpeed);
  w = constrain(1.2f * err, -1.4f, 1.4f);
}
} // namespace waypoint

namespace avoid {
void compute(const perception::PerceptionOut& p, float& v, float& w, float& avoidWeight) {
  if (p.minAll < kDCritical) {
    avoidWeight = 1.0f;
    v = -0.12f;
    w = (p.leftMin > p.rightMin) ? 1.4f : -1.4f;
    return;
  }
  if (p.minAll < kDDanger) avoidWeight = 0.85f;
  else if (p.minAll < kDWarn) avoidWeight = 0.45f;
  else avoidWeight = 0.12f;

  float asym = (p.leftMin - p.rightMin);
  w = constrain(-1.0f * asym, -1.2f, 1.2f);
  v = constrain(0.12f + 0.18f * (p.minAll / kDWarn), 0.10f, kBaseSpeed);
}
} // namespace avoid

namespace ai {
struct Output {
  float turnBias;   // [-1, 1]
  float speedScale; // [0, 1]
  float confidence;
  float inferMs;
};

static volatile float gTurnBias = 0.0f;
static volatile float gSpeedScale = 1.0f;
static volatile float gConfidence = 0.0f;
static volatile float gInferMs = 0.0f;

// Placeholder INT8 model (2-head logistic from 9 inputs)
static const int8_t Wb[SENSOR_COUNT] = {12, 10, 8, 4, 0, -4, -8, -10, -12};
static const int8_t Ws[SENSOR_COUNT] = {-6, -4, -2, -1, -10, -1, -2, -4, -6};
static const int16_t Bb = 0;
static const int16_t Bs = 42;

inline float sigmoid(float x) { return 1.0f / (1.0f + expf(-x)); }

Output run(const float d[SENSOR_COUNT]) {
  uint32_t t0 = micros();
  int8_t q[SENSOR_COUNT];
  for (int i = 0; i < SENSOR_COUNT; i++) {
    float norm = constrain(d[i] / kDMax, 0.0f, 1.0f);
    q[i] = (int8_t)lroundf((norm - 0.5f) * 127.0f);
  }

  int32_t accB = Bb;
  int32_t accS = Bs;
  for (int i = 0; i < SENSOR_COUNT; i++) {
    accB += (int16_t)q[i] * (int16_t)Wb[i];
    accS += (int16_t)q[i] * (int16_t)Ws[i];
  }

  float logitsB = (float)accB / 1024.0f;
  float logitsS = (float)accS / 1024.0f;

  Output o{};
  o.turnBias = constrain(2.0f * sigmoid(logitsB) - 1.0f, -1.0f, 1.0f);
  o.speedScale = constrain(sigmoid(logitsS), 0.0f, 1.0f);
  o.confidence = constrain(fabsf(o.turnBias), 0.0f, 1.0f);
  o.inferMs = (micros() - t0) / 1000.0f;
  return o;
}

void updateShared(const Output& o) {
  // Smooth before publishing
  float prevB = gTurnBias;
  float prevS = gSpeedScale;
  gTurnBias = 0.75f * prevB + 0.25f * o.turnBias;
  gSpeedScale = 0.70f * prevS + 0.30f * o.speedScale;
  gConfidence = 0.60f * gConfidence + 0.40f * o.confidence;
  gInferMs = o.inferMs;

#if DEBUG_AI
  Serial.print("# AI infer ms=");
  Serial.print(gInferMs, 3);
  Serial.print(" b=");
  Serial.print(gTurnBias, 3);
  Serial.print(" s=");
  Serial.println(gSpeedScale, 3);
#endif
}

void readShared(float& b, float& s, float& c, float& ms) {
  b = gTurnBias;
  s = gSpeedScale;
  c = gConfidence;
  ms = gInferMs;
}
} // namespace ai

namespace behavior {
BehaviorMode decide(const perception::PerceptionOut& p, bool timeoutOrInvalid) {
  if (timeoutOrInvalid) return MODE_STOP;
  if (p.front < kDStop) return MODE_STOP;
  if (p.minAll < kDDanger) return MODE_AVOID;
  return MODE_FOLLOW;
}
} // namespace behavior

namespace control {
void vwToWheels(float v, float w, float& vL, float& vR) {
  vL = v - 0.5f * kTrackWidth * w;
  vR = v + 0.5f * kTrackWidth * w;
  vL = constrain(vL, -kMaxWheel, kMaxWheel);
  vR = constrain(vR, -kMaxWheel, kMaxWheel);
}

void computeCommand(
  const comm::InputFrame& in,
  const perception::PerceptionOut& p,
  BehaviorMode mode,
  float& outVL,
  float& outVR) {
  float vf = 0.0f, wf = 0.0f;
  float va = 0.0f, wa = 0.0f, avoidWeight = 0.0f;
  waypoint::compute(in, vf, wf);
  avoid::compute(p, va, wa, avoidWeight);

  float aiB, aiS, aiC, aiMs;
  ai::readShared(aiB, aiS, aiC, aiMs);

  float v = 0.0f;
  float w = 0.0f;

  if (mode == MODE_STOP) {
    v = -0.10f;
    w = 0.0f;
  } else if (mode == MODE_AVOID) {
    v = va;
    w = wa;
  } else {
    // SAFE/CLEAR blending with AI suggestion
    v = (1.0f - avoidWeight) * vf + avoidWeight * va;
    w = (1.0f - avoidWeight) * wf + avoidWeight * wa;

    // AI suggestion only in FOLLOW/CLEAR regime
    const float kAiW = 0.7f;
    w += kAiW * aiB * (0.5f + 0.5f * aiC);
    v *= constrain(aiS, 0.35f, 1.0f);
  }

  vwToWheels(v, w, outVL, outVR);
}
} // namespace control

void controlTask(void* arg) {
  (void)arg;
  TickType_t last = xTaskGetTickCount();
  float vL = 0.0f, vR = 0.0f;
  float filtL = 0.0f, filtR = 0.0f;

  for (;;) {
    comm::pollSerial();

    comm::InputFrame frame{};
    uint32_t ageMs = 0;
    bool ok = comm::snapshot(frame, ageMs);
    auto p = perception::run(frame);
    bool timeoutOrInvalid = (!ok) || (ageMs > kInputTimeoutMs) || !p.sensorValid;

    BehaviorMode mode = behavior::decide(p, timeoutOrInvalid);
    control::computeCommand(frame, p, mode, vL, vR);

    // Output smoothing (no heap allocations)
    filtL = 0.65f * filtL + 0.35f * vL;
    filtR = 0.65f * filtR + 0.35f * vR;

    float aiB, aiS, aiC, aiMs;
    ai::readShared(aiB, aiS, aiC, aiMs);
    comm::sendOutput(filtL, filtR, mode, aiB, aiS, aiMs);

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

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(200);
  Serial.println("# ESP32 Robocar v6.0 Embedded AI");
  Serial.println("# control_task=50Hz, ai_task=5Hz, standalone-safe mode enabled");

  xTaskCreatePinnedToCore(controlTask, "control_task", 6144, nullptr, 2, nullptr, 1);
  xTaskCreatePinnedToCore(aiTask, "ai_task", 4096, nullptr, 1, nullptr, 0);
}

void loop() {
  vTaskDelay(pdMS_TO_TICKS(1000));
}
