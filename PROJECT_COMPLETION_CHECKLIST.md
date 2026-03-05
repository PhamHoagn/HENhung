# Đánh Giá Hoàn Thiện Đề Tài

**Đề tài:** Thiết kế và mô phỏng Robocar 4 bánh tự hành theo lộ trình định trước, tránh vật cản thông minh sử dụng AI nhúng

---

## Các Yêu Cầu Đã Hoàn Thành

### 1. Thiết Kế (Design) ✅
- Kiến trúc HIL (Hardware-in-the-Loop) đầy đủ
- Tài liệu ARCHITECTURE.md chi tiết (v2.0)
- Sơ đồ hệ thống: ESP32 (Brain) ↔ Python (Plant)
- Cấu trúc code module hóa

**File liên quan:**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [README.md](README.md)

### 2. Mô Phỏng (Simulation) ✅
- Môi trường vật lý 2D với pygame
- 4WD skid-steer physics engine (lateral friction 0.85)
- Raycast 9-beam ultrasonic sensor array
- Collision detection
- Real-time visualization 60 FPS
- HUD hiển thị telemetry + AI info

**File liên quan:**
- [python_sim/robocar_sim/sim/physics.py](python_sim/robocar_sim/sim/physics.py) – `FourWheelSkidSteerCar`
- [python_sim/robocar_sim/sim/world.py](python_sim/robocar_sim/sim/world.py)
- [python_sim/robocar_sim/sim/sensors.py](python_sim/robocar_sim/sim/sensors.py) – `SensorArray` (9 beams)
- [python_sim/robocar_sim/render/renderer.py](python_sim/robocar_sim/render/renderer.py)

### 3. Robocar 4 Bánh ✅
- 4WD skid-steer differential drive model
- Track width: 0.22m, Wheel base: 0.16m
- Max speed: 0.60 m/s
- Lateral friction factor: 0.85
- 4 bánh độc lập (FL, FR, RL, RR)

**File liên quan:**
- [python_sim/robocar_sim/sim/physics.py](python_sim/robocar_sim/sim/physics.py) – `FourWheelSkidSteerCar`

### 4. Tự Hành (Autonomous) ✅
- Hoàn toàn tự động, không điều khiển thủ công
- Decision-Tree AI trên ESP32
- Waypoint navigation system
- FreeRTOS dual-core: AI @ 5 Hz, Control @ 50 Hz
- Anti-stuck mechanism + RECOVERY mode

**File liên quan:**
- [esp32_wokwi/sketch_improved/sketch_improved.ino](esp32_wokwi/sketch_improved/sketch_improved.ino) – Main firmware v7.0

### 5. Theo Lộ Trình Định Trước ✅
- WaypointNavigator class hoàn chỉnh
- YAML scenario files: `demo_waypoints.yaml`, `demo_avoid.yaml`
- Waypoint reached detection (threshold ~0.30m)
- Auto-advance chuyển waypoint
- HUD hiển thị waypoint progress (WP 1/5, 2/5, ...)
- Visual path rendering + waypoint markers

**File liên quan:**
- [python_sim/robocar_sim/sim/waypoints.py](python_sim/robocar_sim/sim/waypoints.py)
- [python_sim/robocar_sim/scenarios/demo_waypoints.yaml](python_sim/robocar_sim/scenarios/demo_waypoints.yaml)
- [python_sim/robocar_sim/main_waypoint.py](python_sim/robocar_sim/main_waypoint.py)

### 6. Tránh Vật Cản Thông Minh ✅
- 9 cảm biến siêu âm: 7 trước (120° FOV) + 2 bên (90°)
- Decision-Tree classifier: 5 action classes (FWD, FWD-L, FWD-R, TURN-L, TURN-R)
- Decision-Tree regressor: Speed scale [0, 1]
- 4 behavior modes: FOLLOW, AVOID, STOP, RECOVERY
- Safety-first: Emergency stop/reverse khi front < 0.40m
- Graduated safety distances: kDStop → kDCritical → kDDanger → kDWarn → kDClear

**File liên quan:**
- [esp32_wokwi/sketch_improved/sketch_improved.ino](esp32_wokwi/sketch_improved/sketch_improved.ino)
- [esp32_wokwi/sketch_improved/decision_tree_model.h](esp32_wokwi/sketch_improved/decision_tree_model.h)

### 7. AI Nhúng (Embedded AI) ✅
- Decision-Tree classifier (depth 6, ~62 leaves, 83% accuracy)
- Trained offline với scikit-learn → export C header (pure if/else)
- Inference trực tiếp trên ESP32, không cần ML library
- Inference time < 1ms
- FreeRTOS: AI task trên Core 0 @ 5 Hz
- DT output: action class + speed scale

**File liên quan:**
- [esp32_wokwi/sketch_improved/decision_tree_model.h](esp32_wokwi/sketch_improved/decision_tree_model.h)
- [python_sim/train_decision_tree.py](python_sim/train_decision_tree.py)

---

## Tổng Kết

| Yêu Cầu | Trạng Thái | Chi Tiết |
|----------|-----------|----------|
| Thiết kế | ✅ | HIL architecture v2.0 |
| Mô phỏng | ✅ | Python pygame 2D, 4WD physics |
| Robocar 4 bánh | ✅ | 4WD skid-steer, 4 bánh độc lập |
| Tự hành | ✅ | DT AI + FreeRTOS dual-core |
| Lộ trình định trước | ✅ | Waypoint navigation (YAML) |
| Tránh vật cản thông minh | ✅ | 9 sensors + DT + 4 modes |
| AI nhúng | ✅ | Decision Tree on ESP32 |

---

## Cách Chạy Demo

```cmd
# 1. Setup Wokwi (sketch_improved.ino + decision_tree_model.h)
# 2. Start Wokwi simulation
# 3. Chạy Python:
cd python_sim
python -m robocar_sim.main_waypoint
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| MCU | ESP32 (Wokwi virtual) |
| Firmware | Arduino C++ + FreeRTOS |
| AI Model | Decision Tree (scikit-learn → C header) |
| Physics | Python – 4WD skid-steer kinematics |
| Sensors | Python – 9-beam raycast |
| Rendering | pygame 2.5+ |
| Communication | Serial JSON @ 115200 baud |
| Config | YAML scenarios |

---

**Trạng thái: ✅ HOÀN THIỆN – Sẵn sàng demo và báo cáo**

**Group 10 – Hệ Nhúng 1-2-25-N02 – 2025**
