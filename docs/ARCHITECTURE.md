# System Architecture  (v2.0 – 4WD Skid-Steer + Decision-Tree AI)

Complete architectural documentation for the HIL Robocar simulation system.

---

## 🏛️ Overview

The HIL Robocar is a **Hardware-in-the-Loop (HIL) simulation system** that
combines an **ESP32 embedded controller** (running a trained Decision-Tree
AI) with a **Python physics simulator** (acting as the plant).

### Key Principles

1. **Strict HIL Separation**
   - ESP32: **Brain** – obstacle avoidance, waypoint following, Decision-Tree inference
   - Python: **Plant** – 4WD skid-steer physics, 9-beam sensor array, 2D rendering
   - **No control logic lives in Python.**  A minimal safe-stop fallback exists only for debugging when the ESP32 is absent.

2. **Real Embedded AI**
   - A **Decision-Tree classifier** (depth 6, ~62 leaves, 83 % accuracy) is trained offline with scikit-learn.
   - The tree is exported to a **pure-C header** (`decision_tree_model.h`) and compiled directly into ESP32 firmware – no runtime ML library needed.
   - Inference runs at **5 Hz** on Core 0; the control loop runs at **50 Hz** on Core 1.

3. **4-Wheel Skid-Steer Kinematics**
   - The vehicle model has **4 independently-driven wheels** (FL, FR, RL, RR).
   - Left-side wheels share command `vL`; right-side share `vR`.
   - Lateral friction factor (0.85) models tyre scrubbing during turns.

4. **Real-Time Communication**
   - Bidirectional JSON serial protocol @ **115 200 baud**
   - Fixed 50 Hz control loop, 60 FPS rendering

---

## 📐 System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                 HIL ROBOCAR – 4WD + DT AI  (v2.0)                    │
└───────────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────────┐            ┌────────────────────────────┐
 │  ESP32 Controller (Brain)   │            │  Python Simulator (Plant)  │
 │  Wokwi or real HW           │            │  4WD Skid-Steer Physics    │
 └──────────────┬──────────────┘            └─────────────┬──────────────┘
                │                                         │
                │          Serial JSON @ 115200           │
                │◄────────────────────────────────────────┤
                │ {"t":ms,"x":m,"y":m,"th":rad,           │
                │  "wpX":m,"wpY":m,"d":[d0..d8]}          │
                │                                         │
                ├────────────────────────────────────────►│
                │ {"t":ms,"vL":f,"vR":f,"mode":"...",      │
                │  "ai_a":int,"ai_s":float,"ai_ms":float} │
                │                                         │
                v                                         v
 ┌─────────────────────────┐          ┌──────────────────────────────┐
 │ Decision-Tree AI (Core0)│          │  Simulation World            │
 │ • dt_predict_action()   │          │  • FourWheelSkidSteerCar     │
 │ • dt_predict_speed()    │          │  • 9-beam SensorArray        │
 │ 5 actions × speed scale │          │  • ObstacleManager           │
 ├─────────────────────────┤          │  • CollisionDetector         │
 │ Control Logic (Core1)   │          └──────────────┬───────────────┘
 │ • Waypoint following    │                         │
 │ • Obstacle avoidance    │                         v
 │ • FreeRTOS dual-core    │          ┌──────────────────────────────┐
 │ • JSON serial I/O       │          │  Visualization (pygame 2D)   │
 └─────────────────────────┘          │  • 4-wheel car rendering     │
                                      │  • 9 sensor rays             │
                                      │  • AI telemetry HUD          │
                                      │  • Waypoint path overlay     │
                                      └──────────────────────────────┘
```

---

## 🔷 Component Architecture

### 1. ESP32 Controller (Firmware v7.0)

**Location:** `esp32_wokwi/sketch_improved/sketch_improved.ino`

**AI Model:** `esp32_wokwi/sketch_improved/decision_tree_model.h` (auto-generated)

**Responsibilities:**
- ✅ Parse 9-sensor JSON + position + waypoint
- ✅ Run Decision-Tree classifier → 5 action classes (FWD, FWD-L, FWD-R, TURN-L, TURN-R)
- ✅ Run Decision-Tree regressor → speed scale [0, 1]
- ✅ Waypoint-following heading controller
- ✅ Blend AI avoidance + waypoint steering
- ✅ Generate (vL, vR) motor commands
- ✅ FreeRTOS: controlTask@50 Hz (Core 1), aiTask@5 Hz (Core 0)
- ❌ NO physics simulation
- ❌ NO world knowledge

**Namespaces:**
| Namespace | Purpose |
|-----------|---------|
| `cfg`     | Pin, timing, geometry constants |
| `comm`    | JSON serial I/O (ArduinoJson 6.21+) |
| `ai`      | Decision-Tree inference wrapper |
| `perception` | Sensor validation & grouping |
| `nav`     | Waypoint heading error computation |
| `control` | PD steering, speed blending, EMA filter |

**Decision-Tree Details:**
- Classifier: depth 6, ≤62 leaves, 5 classes, 83 % accuracy
- Regressor: depth 5, continuous speed scale, MAE 0.09
- Input: 9 float features (sensor distances)
- Output: action class `int [0-4]` + speed `float [0-1]`
- Inference: pure C `if/else` tree – **zero external dependencies**

---

### 2. Decision-Tree Training Pipeline

**Location:** `python_sim/train_decision_tree.py`

**Pipeline:**
1. `expert_policy()` – deterministic rule-based labeller that maps 9 sensor readings to (action, speed)
2. `generate_dataset(n=25000)` – synthetic random samples with expert labels
3. Train `DecisionTreeClassifier(max_depth=6)` + `DecisionTreeRegressor(max_depth=5)` via scikit-learn
4. `tree_to_c()` / `regressor_to_c()` – export each sklearn tree to pure C `if/else` functions
5. Output: `decision_tree_model.h` (auto-generated C header) + `model_stats.json`

**Retraining:**
```powershell
cd python_sim
pip install scikit-learn numpy
python train_decision_tree.py
# → writes esp32_wokwi/sketch_improved/decision_tree_model.h
```

---

### 3. Python Simulation Engine

**Location:** `python_sim/robocar_sim/`

#### 3.1 Simulation Core (`sim/`)

**`physics.py` – 4WD Skid-Steer Kinematics (v2.0)**
```python
class FourWheelSkidSteerCar:
    track_width:      0.22 m   # left↔right wheel distance
    wheel_base:       0.16 m   # front↔rear axle distance
    max_speed:        0.60 m/s
    lateral_friction: 0.85     # tyre scrub factor

    Kinematics (unicycle approx):
        v = (vR + vL) / 2
        ω = (vR − vL) / track_width × lateral_friction
        x' = x + v·cos(θ)·dt
        y' = y + v·sin(θ)·dt
        θ' = θ + ω·dt
```

**`world.py` – Simulation World Integrator**
```python
class SimulationWorld:
    car:               FourWheelSkidSteerCar
    sensors:           SensorArray  (9 beams)
    obstacles:         ObstacleManager
    collision_detector: CollisionDetector (radius=0.18 m)
```

**`sensors.py` – 9-Beam Ultrasonic Array**
- 7 forward cone: center (0°), ±15°, ±35°, ±60°
- 2 side: ±90°
- Raycast against circles + walls

**`autopilot.py` – Safe-Stop Fallback (v2.0)**
```python
class SafeStopFallback:
    # Used ONLY when ESP32 is absent (debugging).
    # NO autonomous navigation logic.
    # Behaviour: creep 0.08 m/s or stop if obstacle < 0.40 m
```

**`obstacles.py` / `waypoints.py`** – unchanged, pure data managers.

#### 3.2 Communication Layer (`io/`)

**`protocol.py` – JSON Protocol (v2.0)**
```python
class MotorResponse:     # Rich parsed response from ESP32
    vL, vR: float        # motor commands
    mode:   str          # "FOLLOW"|"AVOID"|"STOP"|"RECOVERY"
    ai_action: int       # DT action class 0-4
    ai_speed:  float     # DT speed scale
    ai_ms:     float     # inference time

class SerialProtocol:
    encode_sensor_data(...)            # 9 sensors → JSON
    encode_sensor_data_with_waypoint() # + position + waypoint
    decode_motor_commands(...)   → (vL, vR)       # legacy compat
    decode_motor_response(...)  → MotorResponse   # full AI telemetry
```

**`serial_bridge.py` – Non-Blocking Serial (v2.0)**
- Stores `last_motor_response` with AI telemetry for HUD
- Auto-detect ESP32 COM port
- Graceful reconnection

#### 3.3 Rendering Layer (`render/`)

**`renderer.py` – pygame 2D Visualization**
- 4-wheel car body + heading indicator
- 9 colour-coded sensor rays
- Waypoint path overlay with "ĐÍCH" marker
- **AI telemetry HUD**: ESP32 mode, DT action name, inference latency
- Serial status: "ESP32 DT-AI Connected" / "No ESP32 (Safe-Stop)"

#### 3.4 Main Integration

**`main_waypoint.py`** – orchestrates world, serial, renderer:
1. Send 9 sensor readings + position + waypoint → ESP32
2. Receive (vL, vR) + AI telemetry ← ESP32
3. If no ESP32 → SafeStopFallback (creep or stop)
4. Apply commands to FourWheelSkidSteerCar
5. Update physics, render frame

---

## 🔄 Data Flow

### Python → ESP32  (Sensor + Waypoint)
```
SensorArray.get_distances()
    → 9 floats: [dC, dLN, dRN, dLM, dRM, dLF, dRF, dLS, dRS]
    + car position (x, y, θ) + waypoint (wpX, wpY)
    → SerialProtocol.encode_sensor_data_with_waypoint()
    → JSON line over serial
    → ESP32 comm::readInput() → ArduinoJson
```

### ESP32 → Python  (Motor + AI Telemetry)
```
ai::run() → dt_predict_action(), dt_predict_speed()
control::compute(perception, nav, ai)
    → (vL, vR, mode, ai_action, ai_speed, ai_ms)
    → comm::sendOutput() → JSON line over serial
    → SerialBridge.receive_motor_commands()
    → MotorResponse → world.set_motor_commands()
                    → renderer HUD
```

---

## ⏱️ Timing Architecture

| Component | Rate | Core | Purpose |
|-----------|------|------|---------|
| ESP32 controlTask | 50 Hz | Core 1 | PD steering + motor output |
| ESP32 aiTask | 5 Hz | Core 0 | Decision-Tree inference |
| Python physics | 50 Hz | – | Skid-steer integration |
| Python serial TX | 50 Hz | – | Sensor updates |
| Python rendering | 60 FPS | – | pygame visualization |

---

## 🧩 Module Dependencies

```
main_waypoint.py
├── sim.world
│   ├── sim.physics   (FourWheelSkidSteerCar)
│   ├── sim.sensors   (9-beam array)
│   └── sim.obstacles
├── sim.autopilot     (SafeStopFallback – fallback only)
├── sim.waypoints     (WaypointNavigator)
├── io.serial_bridge
│   └── io.protocol   (MotorResponse)
└── render.renderer

sketch_improved.ino
├── decision_tree_model.h   (auto-generated DT)
├── ArduinoJson 6.21+
└── FreeRTOS (dual-core tasks)
```

---

## 🔒 Safety & Error Handling

### ESP32 Safety
- **Comm timeout** (200 ms) → STOP mode, motors = 0
- **Range clamping** → vL, vR ∈ [-1, 1]
- **Recovery mode** → if stuck (v ≈ 0 near obstacle), random turn burst
- **EMA filter** → smooth motor transitions × 0.25 α

### Python Safety
- **SafeStopFallback** → creep 0.08 or full stop when ESP32 absent
- **Collision detection** → reset simulation on crash
- **Graceful shutdown** → close serial, save stats, quit pygame

---

## 🔧 Configuration Parameters

| Parameter | Value | Location |
|-----------|-------|----------|
| track_width | 0.22 m | physics.py |
| wheel_base | 0.16 m | physics.py |
| max_speed | 0.60 m/s | physics.py |
| lateral_friction | 0.85 | physics.py |
| robot_radius | 0.18 m | physics.py / world.py |
| DT classifier depth | 6 | train_decision_tree.py |
| DT regressor depth | 5 | train_decision_tree.py |
| Training samples | 25 000 | train_decision_tree.py |
| Control loop | 50 Hz | sketch_improved.ino |
| AI inference | 5 Hz | sketch_improved.ino |
| Baud rate | 115 200 | both |
| Sensor max range | 3.0 m (fwd) / 2.0 m (side) | sensors.py |

---

## 🚀 How to Retrain the AI

```powershell
cd python_sim
pip install scikit-learn numpy
python train_decision_tree.py
# Output:
#   esp32_wokwi/sketch_improved/decision_tree_model.h
#   python_sim/model_stats.json
```

Then recompile the ESP32 firmware in Wokwi or Arduino IDE.

---

## 📝 Design Decisions

| Decision | Rationale |
|----------|-----------|
| Decision Tree (not DNN) | Runs as pure C `if/else` on ESP32 – zero dependencies, deterministic, < 1 ms inference |
| Skid-Steer (not Ackermann) | Matches real 4WD robotics platforms (e.g. mechanum, tank-track). Simpler control: only (vL, vR) |
| Python as plant only | Strict HIL: ensures embedded code is the real controller, portable to physical hardware |
| JSON protocol | Human-readable debugging, easy to extend, acceptable overhead at 115 200 baud |
| FreeRTOS dual-core | AI inference on Core 0 doesn't block the 50 Hz control loop on Core 1 |

---

**This architecture demonstrates professional embedded AI + HIL development practices for the "Mô phỏng robocar 4 bánh theo lộ trình né vật cản sử dụng AI nhúng" project.**
