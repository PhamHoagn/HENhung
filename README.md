# Robocar 4 Bánh Tự Hành – HIL Simulation

**Thiết kế và mô phỏng Robocar 4 bánh tự hành theo lộ trình định trước, tránh vật cản thông minh sử dụng AI nhúng**

Hệ thống Hardware-in-the-Loop (HIL) hoàn chỉnh: ESP32 firmware (Wokwi) chạy Decision-Tree AI điều khiển xe robot 4WD trong môi trường mô phỏng vật lý Python 2D.

---

## Tổng Quan Dự Án

Dự án **HIL (Hardware-in-the-Loop)** gồm hai thành phần chính:

- **ESP32 firmware** – Bộ điều khiển nhúng AI (Decision-Tree classifier + regressor, FreeRTOS dual-core)
- **Python simulator** – Môi trường vật lý 4WD skid-steer, 9 cảm biến siêu âm, rendering 2D
- **Serial JSON** – Giao thức truyền thông real-time @ 115200 baud
- **Waypoint Navigation** – Điều hướng tự động theo lộ trình định trước (YAML)
- **9-Sensor Array** – 7 trước (120° FOV) + 2 bên (90°)
- **Real-time** – Control loop 50 Hz, AI inference 5 Hz, rendering 60 FPS

### Tính Năng Chính

- Decision-Tree AI nhúng trên ESP32 (depth 6, ~62 leaves, 83% accuracy)
- 4WD skid-steer kinematics với lateral friction
- Waypoint navigation + obstacle avoidance thông minh
- FreeRTOS: Core 0 (AI @ 5 Hz), Core 1 (Control @ 50 Hz)
- Safety-first: STOP/REVERSE override khi front < 0.40m
- Anti-stuck mechanism + emergency recovery

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 HIL ROBOCAR – 4WD + DT AI  (v2.0)               │
└─────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────┐    Serial JSON @ 115200    ┌──────────────────────────┐
 │  ESP32 Controller       │◄──────────────────────────►│  Python Simulator        │
 │  (Wokwi / real HW)      │                            │  (Plant)                 │
 │                         │  {"t":ms, "d":[9 floats],  │                          │
 │  ┌───────────────────┐  │   "x","y","th","wpX","wpY"}│  ┌────────────────────┐  │
 │  │ Core 0: AI Task   │  │◄──────────────────────────│  │ 9-Beam Sensors     │  │
 │  │ Decision Tree @5Hz│  │                            │  │ (Raycast)          │  │
 │  └───────────────────┘  │                            │  └────────────────────┘  │
 │          │              │                            │                          │
 │          v              │                            │  ┌────────────────────┐  │
 │  ┌───────────────────┐  │  {"t":ms, "vL","vR",      │  │ 4WD Skid-Steer     │  │
 │  │ Core 1: Control   │  │   "mode","ai_a","ai_s"}   │  │ Physics Engine     │  │
 │  │ Loop @50Hz        │  │──────────────────────────►│  └────────────────────┘  │
 │  └───────────────────┘  │                            │                          │
 │                         │                            │  ┌────────────────────┐  │
 │  Pure Controller        │                            │  │ Renderer (pygame)  │  │
 │  (No Physics)           │                            │  │ 60 FPS             │  │
 └─────────────────────────┘                            │  └────────────────────┘  │
                                                        └──────────────────────────┘
```

---

## Quick Start

### Yêu Cầu
- **Python 3.10+** (with pip)
- **Wokwi Account** (free) – https://wokwi.com
- **Windows** (primary), Linux/Mac compatible

### Cài Đặt

1. **Clone repository**
   ```bash
   git clone <your-repo-url>
   cd HENhung
   ```

2. **Install Python dependencies**
   ```cmd
   cd python_sim
   pip install -r requirements.txt
   ```

3. **Setup ESP32 trên Wokwi**
   - Truy cập https://wokwi.com
   - Tạo project ESP32 mới
   - Copy nội dung `esp32_wokwi/sketch_improved/sketch_improved.ino` vào editor
   - Copy `esp32_wokwi/sketch_improved/decision_tree_model.h` làm tab mới
   - Copy `esp32_wokwi/diagram.json` làm circuit diagram
   - Thêm thư viện **ArduinoJson** (v6.21+)
   - Click **"Start Simulation"**

4. **Chạy mô phỏng**
   ```cmd
   cd python_sim
   python -m robocar_sim.main_waypoint
   ```
   Hoặc chỉ định COM port:
   ```cmd
   python -m robocar_sim.main_waypoint --port COM7
   ```

---

## Project Structure

```
HENhung/
│
├── README.md                              ← Tổng quan dự án
├── QUICK_REFERENCE.md                     ← Quick start reference
├── PROJECT_COMPLETION_CHECKLIST.md        ← Checklist hoàn thiện
│
├── docs/                                  ← Tài liệu kỹ thuật
│   ├── ARCHITECTURE.md                    ← Kiến trúc hệ thống (v2.0)
│   ├── SERIAL_PROTOCOL.md                 ← Giao thức Serial JSON
│   ├── HOW_TO_RUN_WINDOWS.md              ← Hướng dẫn chạy trên Windows
│   ├── WAYPOINT_NAVIGATION.md             ← Hệ thống điều hướng waypoint
│   ├── DEMO_CHECKLIST.md                  ← Chuẩn bị demo
│   └── TROUBLESHOOTING.md                 ← Xử lý lỗi thường gặp
│
├── esp32_wokwi/                           ← ESP32 Firmware
│   ├── diagram.json                       ← Wokwi circuit diagram
│   ├── wokwi.toml                         ← Wokwi configuration
│   └── sketch_improved/                   ← Firmware v7.0
│       ├── sketch_improved.ino            ← Main firmware (DT AI + FreeRTOS)
│       ├── decision_tree_model.h          ← Trained Decision Tree (C header)
│       └── README.md                      ← Firmware documentation
│
├── python_sim/                            ← Python Simulation
│   ├── requirements.txt                   ← Python dependencies
│   ├── run_sim.bat                        ← Windows launcher
│   ├── train_decision_tree.py             ← DT training script
│   │
│   └── robocar_sim/                       ← Simulation package
│       ├── main_waypoint.py               ← Main entry point (waypoint mode)
│       ├── main.py                        ← Legacy main (autopilot fallback)
│       │
│       ├── sim/                           ← Simulation engine
│       │   ├── world.py                   ← World manager
│       │   ├── physics.py                 ← 4WD skid-steer kinematics
│       │   ├── sensors.py                 ← 9-beam raycast sensors
│       │   ├── obstacles.py               ← Obstacle management
│       │   ├── waypoints.py               ← Waypoint navigator
│       │   └── autopilot.py               ← Safe-stop fallback
│       │
│       ├── io/                            ← Serial communication
│       │   ├── serial_bridge.py           ← Non-blocking serial I/O
│       │   └── protocol.py                ← JSON encoding/decoding
│       │
│       ├── render/                        ← Visualization
│       │   └── renderer.py                ← pygame 2D renderer
│       │
│       └── scenarios/                     ← YAML scenario files
│           ├── demo_waypoints.yaml        ← 5 waypoints hình vuông
│           └── demo_avoid.yaml            ← Obstacle avoidance demo
│
└── BAO_CAO_DO_AN/                         ← Báo cáo đồ án
    └── BAO_CAO_PART1_CHUONG1_2.md        ← Chương 1 & 2
```

---

## How It Works

### 1. Simulation Loop (Python – 50 Hz)
```python
while running:
    # 1. Get 9-sensor data + robot state from simulation
    sensor_data = world.get_sensor_data()  # d[9]

    # 2. Send to ESP32 via Serial JSON
    serial.send({"t": ms, "x": x, "y": y, "th": th,
                 "wpX": wpX, "wpY": wpY, "d": [9 floats]})

    # 3. Receive motor commands + AI telemetry
    response = serial.receive()  # {"vL", "vR", "mode", "ai_a", ...}

    # 4. Update 4WD physics
    world.set_motor_commands(vL, vR)
    world.update(dt)

    # 5. Render frame (60 FPS)
    renderer.render_frame(...)
```

### 2. ESP32 Controller (FreeRTOS Dual-Core)
```
Core 1 – controlTask @ 50 Hz:
  Read serial → Apply safety rules → Blend DT + waypoint → Send motor commands

Core 0 – aiTask @ 5 Hz:
  Read 9 sensors → Decision Tree inference → Update action + speed
```

### 3. Serial Protocol (JSON @ 115200 baud)

**Python → ESP32:**
```json
{"t": 12345, "x": 2.1, "y": 1.9, "th": 0.52, "wpX": 6.0, "wpY": 4.0, "d": [2.0,1.4,1.2,0.9,0.7,1.0,1.3,1.6,2.2]}
```

**ESP32 → Python:**
```json
{"t": 12350, "vL": 0.22, "vR": 0.28, "mode": "FOLLOW", "ai_a": 1, "ai_s": 0.86, "ai_ms": 0.31}
```

Chi tiết: [docs/SERIAL_PROTOCOL.md](docs/SERIAL_PROTOCOL.md)

---

## Visualization

Cửa sổ pygame hiển thị:
- **Robot 4WD** – Xe với 4 bánh, hướng di chuyển
- **Obstacles** – Vật cản hình tròn
- **9 Sensor rays** – Mã màu theo khoảng cách:
  - 🟢 Green = Safe (> 1.0m)
  - 🟡 Yellow = Warning (0.6–1.0m)
  - 🟠 Orange = Danger (0.3–0.6m)
  - 🔴 Red = Critical (< 0.3m)
- **Waypoint path** – Lộ trình và điểm đích hiện tại
- **HUD** – Telemetry real-time (speed, mode, waypoint progress, AI action)

---

## Obstacle Avoidance (AI)

ESP32 sử dụng Decision-Tree AI với 4 behavior modes:

| Mode | Điều kiện | Hành vi |
|------|----------|---------|
| `FOLLOW` | front > 1.30m | DT + waypoint blending |
| `AVOID` | front < 0.90m | DT override, high avoid weight |
| `STOP` | front < 0.40m | Emergency stop / reverse |
| `RECOVERY` | Stuck detected | Reverse + spin |

Safety distances:
- `kDStop = 0.40m` – Full stop/reverse
- `kDCritical = 0.55m` – 100% DT override
- `kDDanger = 0.90m` – Switch to AVOID mode
- `kDWarn = 1.30m` – Blend starts
- `kDClear = 1.50m` – Exit AVOID (hysteresis)

---

## Documentation

| Tài Liệu | Mô Tả |
|----------|--------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Kiến trúc hệ thống chi tiết (v2.0) |
| [docs/SERIAL_PROTOCOL.md](docs/SERIAL_PROTOCOL.md) | Đặc tả giao thức Serial JSON |
| [docs/HOW_TO_RUN_WINDOWS.md](docs/HOW_TO_RUN_WINDOWS.md) | Hướng dẫn setup & chạy trên Windows |
| [docs/WAYPOINT_NAVIGATION.md](docs/WAYPOINT_NAVIGATION.md) | Hệ thống điều hướng waypoint |
| [docs/DEMO_CHECKLIST.md](docs/DEMO_CHECKLIST.md) | Checklist chuẩn bị báo cáo/demo |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Xử lý lỗi thường gặp |

---

## Technologies

### Firmware
- **ESP32** (Wokwi virtual / real HW)
- **Arduino C++** + FreeRTOS dual-core
- **ArduinoJson 6.21+**
- **Decision Tree** (scikit-learn → C header export)

### Simulation
- **Python 3.10+**
- **pygame 2.5+** – Graphics rendering
- **pyserial 3.5+** – Serial communication
- **PyYAML 6.0+** – Scenario config
- **scikit-learn** – DT model training

### Key Concepts
- Hardware-in-the-Loop (HIL) testing
- 4WD Skid-steer kinematics
- Raycast-based sensor simulation
- Decision-Tree AI inference on embedded
- FreeRTOS multi-core task scheduling
- Real-time serial JSON protocol

---

## Vehicle Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Track width | 0.22 m | Left↔right wheel distance |
| Wheel base | 0.16 m | Front↔rear axle distance |
| Max speed | 0.60 m/s | Maximum linear wheel speed |
| Wheel radius | 0.033 m | Wheel radius |
| Lateral friction | 0.85 | Skid-steer scrub factor |
| Sensor count | 9 | Ultrasonic sensor array |
| Sensor max range | 3.0 m | Maximum detection range |
| World size | 12 × 12 m | Simulation world |

---

## Troubleshooting

**Không kết nối được ESP32?**
- Chạy Wokwi simulation trước
- Mở Serial Monitor trong Wokwi
- Chỉ định port thủ công: `python -m robocar_sim.main_waypoint --port COM7`

**ModuleNotFoundError?**
```cmd
pip install pygame pyserial pyyaml scikit-learn
```

**Xe không di chuyển?**
- Kiểm tra HUD hiển thị "ESP32: CONNECTED"
- Kiểm tra Wokwi Serial Monitor có motor commands
- Kiểm tra Wokwi simulation đang chạy

Xem thêm: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**Group 10 – Hệ Nhúng 1-2-25-N02 – 2025**

